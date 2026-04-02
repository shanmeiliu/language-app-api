from pydantic import BaseModel
from typing import List, Optional


class FlashcardResponse(BaseModel):
    source_language: str
    target_language: str
    prompt_type: str
    text_type: Optional[str] = None
    difficulty: Optional[str] = None
    topic: Optional[str] = None
    source_text: str
    target_text: str
    explanation: Optional[str] = None
    options: List[str]
    cache_hit: bool