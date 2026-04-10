from pydantic import BaseModel, Field, model_validator
from typing import List, Optional


class PhraseFlashcardRequest(BaseModel):
    source_items: List[str] = Field(..., min_length=1)
    source_language: str
    target_language: str
    num_options: int = Field(..., ge=2, le=8)
    text_type: Optional[str] = None
    exclude_source_texts: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_languages(self):
        if self.source_language.strip().lower() == self.target_language.strip().lower():
            raise ValueError("Source and target language cannot be the same")
        return self


class TopicFlashcardRequest(BaseModel):
    topic: str
    difficulty: str
    source_language: str
    target_language: str
    num_options: int = Field(..., ge=2, le=8)
    text_type: Optional[str] = None
    exclude_source_texts: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_languages(self):
        if self.source_language.strip().lower() == self.target_language.strip().lower():
            raise ValueError("Source and target language cannot be the same")
        return self


class GameNextQuestionRequest(BaseModel):
    topic: str
    difficulty: str
    source_language: str
    target_language: str
    num_options: int = Field(default=4, ge=2, le=8)
    text_type: Optional[str] = None
    exclude_source_texts: List[str] = Field(default_factory=list)
    batch_size: int = Field(default=5, ge=1, le=10)

    @model_validator(mode="after")
    def validate_languages(self):
        if self.source_language.strip().lower() == self.target_language.strip().lower():
            raise ValueError("Source and target language cannot be the same")
        return self