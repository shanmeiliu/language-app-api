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

    if cached_cards:
        return flashcard_record_to_response(cached_cards[0], cache_hit=True)

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

    seen = set(request.exclude_source_texts)
    batch_seen = set()

    for card in cards_data:
        source_text = card.get("source_text")
        if not source_text:
            raise ValueError("One generated card is missing source_text")
        if source_text in seen:
            raise ValueError("LLM returned a repeated source_text that was excluded")
        if source_text in batch_seen:
            raise ValueError("LLM returned duplicate source_text values within the batch")
        batch_seen.add(source_text)

    save_flashcards(
        cards_data=cards_data,
        model_name=settings.model_name,
        prompt_template="make_flashcard_batch_for_topic.txt",
        raw_request=raw_request,
        raw_response=sanitized_response,
    )

    refreshed_cards = find_available_topic_flashcards(
        source_lang=request.source_language,
        target_lang=request.target_language,
        topic=request.topic,
        difficulty=request.difficulty,
        text_type=request.text_type,
        exclude_source_texts=request.exclude_source_texts,
        limit=request.batch_size,
    )

    if not refreshed_cards:
        raise ValueError("Batch was saved but no game question could be retrieved")

    return flashcard_record_to_response(refreshed_cards[0], cache_hit=False)