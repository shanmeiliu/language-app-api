from fastapi import APIRouter
from app.models.requests import PhraseFlashcardRequest, TopicFlashcardRequest
from app.models.responses import FlashcardResponse
from app.services.flashcard_service import (
    create_phrase_flashcard,
    create_topic_flashcard,
)

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])

"""“
lazy generation + partial caching”
Input:  ["A", "B", "C"]

System:
- Try to find ANY existing flashcard for A/B/C
- If found → return it
- If not → pick one → generate → store → return
"""
@router.post(
    "/phrase",
    response_model=FlashcardResponse,
    summary="Generate one flashcard from a list of phrases",
    description="Takes a list of phrases and returns ONE flashcard. The system may use any item from the list (cache-first)."
)
def generate_phrase_flashcard(request: PhraseFlashcardRequest):
    return create_phrase_flashcard(request)


@router.post(
    "/topic",
    response_model=FlashcardResponse,
    summary="Generate one flashcard from a topic",
    description="Takes a topic request and returns ONE topic-based flashcard with cache-first lookup.",
)
def generate_topic_flashcard(request: TopicFlashcardRequest):
    return create_topic_flashcard(request)