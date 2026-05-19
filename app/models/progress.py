from pydantic import BaseModel
from typing import Optional


class RecordShownRequest(BaseModel):
    flashcard_id: str
    mode: Optional[str] = None


class RecordShownResponse(BaseModel):
    attempt_id: str
 

class RecordAnswerRequest(BaseModel):
    flashcard_id: str
    selected_option: str
    correct_answer: str
    is_correct: bool
    mode: str | None = None


class DashboardAttemptResponse(BaseModel):
    attempt_id: str
    flashcard_id: str
    source_text: Optional[str]
    target_text: Optional[str]
    selected_option: Optional[str]
    correct_answer: Optional[str]
    is_correct: Optional[bool]
    mode: Optional[str]
    shown_at: str
    answered_at: Optional[str]