from fastapi import Cookie, HTTPException
from app.core.config import settings
from app.services.auth_service import get_current_user_from_session


def require_current_user(
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return get_current_user_from_session(session_token)