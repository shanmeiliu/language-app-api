from fastapi import APIRouter, Depends
from app.api.deps import require_current_user
from app.models.progress import (
    DashboardAttemptResponse,
    RecordAnswerRequest,
    RecordShownRequest,
    RecordShownResponse,
)
from app.repositories.progress_repository import (
    get_user_dashboard_attempts,
    record_flashcard_answer
)

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.post("/shown", response_model=RecordShownResponse)
def record_shown(
    request: RecordShownRequest,
    current_user=Depends(require_current_user),
):
    attempt_id = record_flashcard_shown(
        user_id=current_user["user_id"],
        flashcard_id=request.flashcard_id,
        mode=request.mode,
    )

    return {"attempt_id": attempt_id}


@router.post("/answer")
def record_answer(
    request: RecordAnswerRequest,
    current_user=Depends(require_current_user),
):
    record_flashcard_answer(
        user_id=current_user["user_id"],
        flashcard_id=request.flashcard_id,
        selected_option=request.selected_option,
        correct_answer=request.correct_answer,
        is_correct=request.is_correct,
        mode=request.mode,
    )

    return {"ok": True}


@router.get("/dashboard", response_model=list[DashboardAttemptResponse])
def dashboard(current_user=Depends(require_current_user)):
    return get_user_dashboard_attempts(current_user["user_id"])