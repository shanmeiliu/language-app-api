import json
import uuid
from typing import Optional
from app.db.connection import get_db_cursor


def save_flashcard(
    card_data: dict,
    model_name: str,
    prompt_template: str,
    raw_request: dict,
    raw_response: str,
) -> str:
    flashcard_id = str(uuid.uuid4())

    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.flashcard (
                flashcard_id,
                source_lang,
                target_lang,
                prompt_type,
                text_type,
                difficulty,
                topic,
                source_text,
                target_text,
                explanation
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                flashcard_id,
                card_data.get("source_language"),
                card_data.get("target_language"),
                card_data.get("prompt_type"),
                card_data.get("text_type"),
                card_data.get("difficulty"),
                card_data.get("topic"),
                card_data.get("source_text"),
                card_data.get("target_text"),
                card_data.get("explanation"),
            ),
        )

        for idx, option in enumerate(card_data.get("options", []), start=1):
            cur.execute(
                """
                INSERT INTO public.flashcard_option (
                    option_id,
                    flashcard_id,
                    option_text,
                    is_correct,
                    option_order
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    flashcard_id,
                    option,
                    option == card_data.get("target_text"),
                    idx,
                ),
            )

        cur.execute(
            """
            INSERT INTO public.generation_run (
                run_id,
                flashcard_id,
                model_name,
                prompt_template,
                raw_request,
                raw_response
            )
            VALUES (%s, %s, %s, %s, %s::jsonb, %s)
            """,
            (
                str(uuid.uuid4()),
                flashcard_id,
                model_name,
                prompt_template,
                json.dumps(raw_request, ensure_ascii=False),
                raw_response,
            ),
        )

    return flashcard_id

def save_flashcards(
    cards_data: list[dict],
    model_name: str,
    prompt_template: str,
    raw_request: dict,
    raw_response: str,
) -> list[str]:
    flashcard_ids: list[str] = []

    for card_data in cards_data:
        flashcard_id = save_flashcard(
            card_data=card_data,
            model_name=model_name,
            prompt_template=prompt_template,
            raw_request=raw_request,
            raw_response=raw_response,
        )
        flashcard_ids.append(flashcard_id)

    return flashcard_ids

def get_flashcard_by_id(flashcard_id: str) -> Optional[dict]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT
                flashcard_id,
                source_lang,
                target_lang,
                prompt_type,
                text_type,
                difficulty,
                topic,
                source_text,
                target_text,
                explanation,
                created_at
            FROM public.flashcard
            WHERE flashcard_id = %s
            """,
            (flashcard_id,),
        )
        row = cur.fetchone()

        if not row:
            return None

        cur.execute(
            """
            SELECT option_text, is_correct, option_order
            FROM public.flashcard_option
            WHERE flashcard_id = %s
            ORDER BY option_order ASC
            """,
            (flashcard_id,),
        )
        options = cur.fetchall()

    return {
        "flashcard_id": row[0],
        "source_language": row[1],
        "target_language": row[2],
        "prompt_type": row[3],
        "text_type": row[4],
        "difficulty": row[5],
        "topic": row[6],
        "source_text": row[7],
        "target_text": row[8],
        "explanation": row[9],
        "created_at": row[10].isoformat() if row[10] else None,
        "options": [
            {
                "text": opt[0],
                "is_correct": opt[1],
                "order": opt[2],
            }
            for opt in options
        ],
    }


def find_existing_phrase_flashcard(
    source_lang: str,
    target_lang: str,
    text_type: str | None,
    source_items: list[str],
) -> Optional[dict]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT flashcard_id
            FROM public.flashcard
            WHERE source_lang = %s
              AND target_lang = %s
              AND prompt_type = 'phrase'
              AND text_type IS NOT DISTINCT FROM %s
              AND source_text = ANY(%s)
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (source_lang, target_lang, text_type, source_items),
        )
        row = cur.fetchone()

    if not row:
        return None

    return get_flashcard_by_id(row[0])


def find_existing_topic_flashcard(
    source_lang: str,
    target_lang: str,
    topic: str,
    difficulty: str,
    text_type: str | None,
    exclude_source_texts: list[str] | None = None,
) -> Optional[dict]:
    exclude_source_texts = exclude_source_texts or []

    with get_db_cursor() as cur:
        if exclude_source_texts:
            cur.execute(
                """
                SELECT flashcard_id
                FROM public.flashcard
                WHERE source_lang = %s
                  AND target_lang = %s
                  AND prompt_type = 'topic'
                  AND topic = %s
                  AND difficulty = %s
                  AND text_type IS NOT DISTINCT FROM %s
                  AND NOT (source_text = ANY(%s))
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (
                    source_lang,
                    target_lang,
                    topic,
                    difficulty,
                    text_type,
                    exclude_source_texts,
                ),
            )
        else:
            cur.execute(
                """
                SELECT flashcard_id
                FROM public.flashcard
                WHERE source_lang = %s
                  AND target_lang = %s
                  AND prompt_type = 'topic'
                  AND topic = %s
                  AND difficulty = %s
                  AND text_type IS NOT DISTINCT FROM %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (source_lang, target_lang, topic, difficulty, text_type),
            )

        row = cur.fetchone()

    if not row:
        return None

    return get_flashcard_by_id(row[0])

def find_available_topic_flashcards(
    source_lang: str,
    target_lang: str,
    topic: str,
    difficulty: str,
    text_type: str | None,
    exclude_source_texts: list[str] | None = None,
    limit: int = 5,
) -> list[dict]:
    exclude_source_texts = exclude_source_texts or []

    with get_db_cursor() as cur:
        if exclude_source_texts:
            cur.execute(
                """
                SELECT flashcard_id
                FROM public.flashcard
                WHERE source_lang = %s
                  AND target_lang = %s
                  AND prompt_type = 'topic'
                  AND topic = %s
                  AND difficulty = %s
                  AND text_type IS NOT DISTINCT FROM %s
                  AND NOT (source_text = ANY(%s))
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (
                    source_lang,
                    target_lang,
                    topic,
                    difficulty,
                    text_type,
                    exclude_source_texts,
                    limit,
                ),
            )
        else:
            cur.execute(
                """
                SELECT flashcard_id
                FROM public.flashcard
                WHERE source_lang = %s
                  AND target_lang = %s
                  AND prompt_type = 'topic'
                  AND topic = %s
                  AND difficulty = %s
                  AND text_type IS NOT DISTINCT FROM %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (
                    source_lang,
                    target_lang,
                    topic,
                    difficulty,
                    text_type,
                    limit,
                ),
            )

        rows = cur.fetchall()

    results = []
    for row in rows:
        record = get_flashcard_by_id(row[0])
        if record:
            results.append(record)

    return results