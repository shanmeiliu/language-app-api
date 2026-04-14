import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    app_name: str = "Language App API"

    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    database_url: Optional[str] = os.getenv("DATABASE_URL")

    port: int = int(os.getenv("PORT", "8000"))

    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", "http://localhost")

    session_cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "language_app_session")
    session_ttl_days: int = int(os.getenv("SESSION_TTL_DAYS", "30"))
    session_same_site: str = os.getenv("SESSION_SAME_SITE", "lax")
    session_https_only: bool = parse_bool(os.getenv("SESSION_HTTPS_ONLY"), False)

    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")

    starlette_session_secret: str = os.getenv(
        "STARLETTE_SESSION_SECRET",
        "dev_only_change_me"
    )

    cors_allow_origins: list[str] = parse_csv(
        os.getenv("CORS_ALLOW_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    )


settings = Settings()