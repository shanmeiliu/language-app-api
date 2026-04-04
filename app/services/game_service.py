import json
from app.core.config import settings
from app.db.schema import ensure_schema
from app.models.requests import GameNextQuestionRequest
from app.repositories.flashcard_repository import (
    find_available_topic_flashcards,
    save_flashcards,
)
from app.services.flashcard_service import flashcard_record_to_response
from app.services.llm_service import (
    call_llm,
    make_topic_flashcard_batch_payload,
    sanitize_llm_json_array_response,
)

REFILL_THRESHOLD = 2


def _generate_and_save_batch(request: GameNextQuestionRequest) -> None:
    raw_request = {
        "topic": request.topic,
        "difficulty": request.difficulty,
        "source_language": request.source_language,
        "target_language": request.target_language,
        "num_options": request.num_options,
        "text_type": request.text_type,
        "exclude_source_texts": request.exclude_source_texts,
        "batch_size": request.batch_size,
    }

    prompt = make_topic_flashcard_batch_payload(
        topic=request.topic,
        difficulty=request.difficulty,
        source_language=request.source_language,
        target_language=request.target_language,
        num_options=request.num_options,
        text_type=request.text_type,
        exclude_source_texts=request.exclude_source_texts,
        batch_size=request.batch_size,
    )

    raw_response = call_llm(prompt, "make_flashcard_batch_for_topic.txt")
    sanitized_response = sanitize_llm_json_array_response(raw_response)
    cards_data = json.loads(sanitized_response)

    if not isinstance(cards_data, list) or not cards_data:
        raise ValueError("LLM batch response was not a non-empty JSON array")

    excluded = set(request.exclude_source_texts)
    batch_seen = set()

    filtered_cards = []
    for card in cards_data:
        source_text = card.get("source_text")
        if not source_text:
            continue
        if source_text in excluded:
            continue
        if source_text in batch_seen:
            continue
        batch_seen.add(source_text)
        filtered_cards.append(card)

    if not filtered_cards:
        raise ValueError("LLM batch produced no usable new questions")

    save_flashcards(
        cards_data=filtered_cards,
        model_name=settings.model_name,
        prompt_template="make_flashcard_batch_for_topic.txt",
        raw_request=raw_request,
        raw_response=sanitized_response,
    )


def get_next_game_question(request: GameNextQuestionRequest) -> dict:
    ensure_schema()

    cached_cards = find_available_topic_flashcards(
        source_lang=request.source_language,
        target_lang=request.target_language,
        topic=request.topic,
        difficulty=request.difficulty,
        text_type=request.text_type,
        exclude_source_texts=request.exclude_source_texts,
        limit=request.batch_size,
    )

    if not cached_cards:
        _generate_and_save_batch(request)

        cached_cards = find_available_topic_flashcards(
            source_lang=request.source_language,
            target_lang=request.target_language,
            topic=request.topic,
            difficulty=request.difficulty,
            text_type=request.text_type,
            exclude_source_texts=request.exclude_source_texts,
            limit=request.batch_size,
        )

        if not cached_cards:
            raise ValueError("No game question available after batch generation")

    selected = cached_cards[0]

    # Proactively refill if the remaining pool is getting low.
    remaining_after_return = max(len(cached_cards) - 1, 0)
    if remaining_after_return < REFILL_THRESHOLD:
        refill_excludes = list(request.exclude_source_texts) + [
            card["source_text"] for card in cached_cards
        ]

        refill_request = GameNextQuestionRequest(
            topic=request.topic,
            difficulty=request.difficulty,
            source_language=request.source_language,
            target_language=request.target_language,
            num_options=request.num_options,
            text_type=request.text_type,
            exclude_source_texts=refill_excludes,
            batch_size=request.batch_size,
        )

        try:
            _generate_and_save_batch(refill_request)
        except Exception:
            # Don't fail the current response just because refill failed.
            pass

    return flashcard_record_to_response(selected, cache_hit=True)