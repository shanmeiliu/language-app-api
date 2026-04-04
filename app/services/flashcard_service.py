import json
from app.core.config import settings
from app.db.schema import ensure_schema
from app.models.requests import PhraseFlashcardRequest, TopicFlashcardRequest
from app.repositories.flashcard_repository import (
    find_existing_phrase_flashcard,
    find_existing_topic_flashcard,
    get_flashcard_by_id,
    save_flashcard,
)
from app.services.llm_service import (
    call_llm,
    make_phrase_flashcard_payload,
    make_topic_flashcard_payload,
    sanitize_llm_json_response,
)

def flashcard_record_to_response(record: dict, cache_hit: bool) -> dict:
    return {
        "source_language": record["source_language"],
        "target_language": record["target_language"],
        "prompt_type": record["prompt_type"],
        "text_type": record["text_type"],
        "difficulty": record["difficulty"],
        "topic": record["topic"],
        "source_text": record["source_text"],
        "target_text": record["target_text"],
        "explanation": record["explanation"],
        "options": [opt["text"] for opt in record["options"]],
        "cache_hit": cache_hit,
    }


def create_phrase_flashcard(request: PhraseFlashcardRequest) -> dict:
    ensure_schema()

    existing = find_existing_phrase_flashcard(
        source_lang=request.source_language,
        target_lang=request.target_language,
        text_type=request.text_type,
        source_items=request.source_items,
    )

    if existing:
        return flashcard_record_to_response(existing, cache_hit=True)

    raw_request = {
        "source_items": request.source_items,
        "source_language": request.source_language,
        "target_language": request.target_language,
        "num_options": request.num_options,
        "text_type": request.text_type,
    }

    prompt = make_phrase_flashcard_payload(
        source_items=request.source_items,
        source_language=request.source_language,
        target_language=request.target_language,
        num_options=request.num_options,
        text_type=request.text_type,
    )

    raw_response = call_llm(prompt, "make_flashcard_for_phrase.txt")
    sanitized_response = sanitize_llm_json_response(raw_response)
    card_data = json.loads(sanitized_response)

    flashcard_id = save_flashcard(
        card_data=card_data,
        model_name=settings.model_name,
        prompt_template="make_flashcard_for_phrase.txt",
        raw_request=raw_request,
        raw_response=sanitized_response,
    )

    saved = get_flashcard_by_id(flashcard_id)
    if not saved:
        raise ValueError("Flashcard was saved but could not be reloaded")

    return flashcard_record_to_response(saved, cache_hit=False)


def create_topic_flashcard(request: TopicFlashcardRequest) -> dict:
    ensure_schema()

    existing = find_existing_topic_flashcard(
        source_lang=request.source_language,
        target_lang=request.target_language,
        topic=request.topic,
        difficulty=request.difficulty,
        text_type=request.text_type,
        exclude_source_texts=request.exclude_source_texts,
    )

    if existing:
        return flashcard_record_to_response(existing, cache_hit=True)

    raw_request = {
        "topic": request.topic,
        "difficulty": request.difficulty,
        "source_language": request.source_language,
        "target_language": request.target_language,
        "num_options": request.num_options,
        "text_type": request.text_type,
        "exclude_source_texts": request.exclude_source_texts,
    }

    prompt = make_topic_flashcard_payload(
        topic=request.topic,
        difficulty=request.difficulty,
        source_language=request.source_language,
        target_language=request.target_language,
        num_options=request.num_options,
        text_type=request.text_type,
        exclude_source_texts=request.exclude_source_texts,
    )

    raw_response = call_llm(prompt, "make_flashcard_for_topic.txt")
    sanitized_response = sanitize_llm_json_response(raw_response)
    card_data = json.loads(sanitized_response)

    if card_data.get("source_text") in request.exclude_source_texts:
        raise ValueError("LLM returned a repeated source_text that was explicitly excluded")

    flashcard_id = save_flashcard(
        card_data=card_data,
        model_name=settings.model_name,
        prompt_template="make_flashcard_for_topic.txt",
        raw_request=raw_request,
        raw_response=sanitized_response,
    )

    saved = get_flashcard_by_id(flashcard_id)
    if not saved:
        raise ValueError("Flashcard was saved but could not be reloaded")

    return flashcard_record_to_response(saved, cache_hit=False)