import json
import re
from pathlib import Path
from openai import OpenAI
from app.core.config import settings


def load_prompt_template(filename: str) -> str:
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / filename
    return prompt_path.read_text(encoding="utf-8")


def sanitize_llm_json_response(raw_response: str) -> str:
    if not raw_response:
        return raw_response

    text = raw_response.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text.strip()


def call_llm(prompt: str, prompt_filename: str) -> str:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    system_prompt = load_prompt_template(prompt_filename)

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": "You are a helpful language expert.\n\n" + system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty content")

    return content


def make_phrase_flashcard_payload(
    source_items: list[str],
    source_language: str,
    target_language: str,
    num_options: int,
    text_type: str | None,
) -> str:
    payload = {
        "source_items": source_items,
        "source_language": source_language,
        "target_language": target_language,
        "num_options": num_options,
        "text_type": text_type,
    }
    return json.dumps(payload, ensure_ascii=False)

def make_topic_flashcard_batch_payload(
    topic: str,
    difficulty: str,
    source_language: str,
    target_language: str,
    num_options: int,
    text_type: str | None,
    exclude_source_texts: list[str] | None = None,
    batch_size: int = 5,
) -> str:
    payload = {
        "topic": topic,
        "difficulty": difficulty,
        "source_language": source_language,
        "target_language": target_language,
        "num_options": num_options,
        "text_type": text_type,
        "exclude_source_texts": exclude_source_texts or [],
        "batch_size": batch_size,
    }
    return json.dumps(payload, ensure_ascii=False)


def sanitize_llm_json_array_response(raw_response: str) -> str:
    if not raw_response:
        return raw_response

    text = raw_response.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text.strip()
    
def make_topic_flashcard_payload(
    topic: str,
    difficulty: str,
    source_language: str,
    target_language: str,
    num_options: int,
    text_type: str | None,
    exclude_source_texts: list[str] | None = None,
) -> str:
    payload = {
        "topic": topic,
        "difficulty": difficulty,
        "source_language": source_language,
        "target_language": target_language,
        "num_options": num_options,
        "text_type": text_type,
        "exclude_source_texts": exclude_source_texts or [],
    }
    return json.dumps(payload, ensure_ascii=False)