from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.flashcards import router as flashcards_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flashcards_router)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}


@app.get("/health")
def health():
    return {"status": "ok"}