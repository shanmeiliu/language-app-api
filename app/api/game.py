from fastapi import APIRouter
from app.models.requests import GameNextQuestionRequest
from app.models.responses import FlashcardResponse
from app.services.game_service import get_next_game_question

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post(
    "/next-question",
    response_model=FlashcardResponse,
    summary="Get the next game question",
    description="Returns one unseen game question, prefilling cache in batches when needed.",
)
def next_game_question(request: GameNextQuestionRequest):
    return get_next_game_question(request)