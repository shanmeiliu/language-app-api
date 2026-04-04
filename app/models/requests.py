from pydantic import BaseModel, Field
from typing import List, Optional


class PhraseFlashcardRequest(BaseModel):
    source_items: List[str] = Field(..., min_length=1)
    source_language: str
    target_language: str
    num_options: int = Field(..., ge=2, le=8)
    text_type: Optional[str] = None
    exclude_source_texts: List[str] = Field(default_factory=list)


class TopicFlashcardRequest(BaseModel):
    topic: str
    difficulty: str
    source_language: str
    target_language: str
    num_options: int = Field(..., ge=2, le=8)
    text_type: Optional[str] = None
    exclude_source_texts: List[str] = Field(default_factory=list)


class GameNextQuestionRequest(BaseModel):
    topic: str
    difficulty: str
    source_language: str
    target_language: str
    num_options: int = Field(..., ge=2, le=8)
    text_type: Optional[str] = None
    exclude_source_texts: List[str] = Field(default_factory=list)
    batch_size: int = Field(default=5, ge=1, le=10)