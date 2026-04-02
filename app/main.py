from fastapi import FastAPI
from app.core.config import settings
from app.api.flashcards import router as flashcards_router

app = FastAPI(title=settings.app_name)

app.include_router(flashcards_router)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}


@app.get("/health")
def health():
    return {"status": "ok"}