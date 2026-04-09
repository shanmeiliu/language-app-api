from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.config import settings
from app.repositories.auth_repository import get_session_with_user, touch_session
from app.services.auth_utils import hash_session_token, default_session_expiry


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_token = request.cookies.get(settings.session_cookie_name)

        if session_token:
            session = get_session_with_user(hash_session_token(session_token))

            if session and not session["revoked_at"] and session["is_active"]:
                # Attach user to request (optional but useful)
                request.state.user = {
                    "user_id": session["user_id"],
                    "account_type": session["account_type"],
                    "email": session["email"],
                    "username": session["username"],
                }

                # 🔥 renew session automatically
                touch_session(
                    session_id=session["session_id"],
                    user_id=session["user_id"],
                    expires_at=default_session_expiry(),
                )

        response = await call_next(request)
        return response