from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.flashcards import router as flashcards_router
from app.api.game import router as game_router
from app.api.auth import router as auth_router
from app.db.auth_schema import ensure_auth_schema
from starlette.middleware.sessions import SessionMiddleware as StarletteSessionMiddleware
from app.middleware.session_middleware import SessionMiddleware


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    StarletteSessionMiddleware,
    secret_key=settings.starlette_session_secret,
    same_site="lax",
    https_only=False,  # set True behind HTTPS
)
app.add_middleware(SessionMiddleware)

@app.on_event("startup")
def startup():
    ensure_auth_schema()

app.include_router(flashcards_router)
app.include_router(game_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}


@app.get("/health")
def health():
    return {"status": "ok"}