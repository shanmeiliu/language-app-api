from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from app.api.deps import require_current_user
from app.core.config import settings
from app.models.auth import LoginPasswordRequest, RegisterLocalUserRequest, UserResponse
from app.repositories.auth_repository import upsert_google_user, create_session
from app.services.auth_service import (
    login_with_password,
    logout_from_session,
    register_local_user,
)
from app.services.auth_utils import (
    default_session_expiry,
    generate_session_token,
    generate_username,
    hash_session_token,
)
from app.services.magic_link_service import (
    create_anonymous_user,
    create_magic_link,
    redeem_magic_link,
)
from app.services.google_oauth import oauth

router = APIRouter(prefix="/auth", tags=["auth"])


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        samesite=settings.session_same_site,
        secure=settings.session_https_only,
        max_age=settings.session_ttl_days * 24 * 60 * 60,
        path="/",
    )


@router.post("/register", response_model=UserResponse)
def register(request: RegisterLocalUserRequest, response: Response):
    user, raw_token = register_local_user(email=request.email, password=request.password)
    set_session_cookie(response, raw_token)
    return user


@router.post("/login/password", response_model=UserResponse)
def login_password(request: LoginPasswordRequest, response: Response):
    user, raw_token = login_with_password(request.username, request.password)
    set_session_cookie(response, raw_token)
    return user


@router.get("/google/login")
async def google_login(request: Request):
    print("Google login called")
    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = await oauth.google.userinfo(token=token)
    
    google_sub = userinfo["sub"]
    email = userinfo.get("email")
    display_name = userinfo.get("name") or email or "Google User"
    username = generate_username("google")

    user = upsert_google_user(
        google_sub=google_sub,
        email=email,
        username=username,
        display_name=display_name,
    )

   
    
    raw_token = generate_session_token()
    create_session(
        user_id=user["user_id"],
        token_hash=hash_session_token(raw_token),
        login_method="google",
        expires_at=default_session_expiry(),
    )

    response = RedirectResponse(url=settings.frontend_base_url)
    set_session_cookie(response, raw_token)
    return response


@router.post("/logout")
def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
):
    if session_token:
        logout_from_session(session_token)
    response.delete_cookie(settings.session_cookie_name, path="/")
    return {"ok": True}

@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(require_current_user)):
    return current_user

@router.post("/magic-link/start")
def start_magic_link():
    user = create_anonymous_user()
    token = create_magic_link(user["user_id"])

    link = f"{settings.frontend_base_url}/magic-login?token={token}"

    return {
        "login_link": link,
        "username": user["username"],
    }

@router.post("/magic-link/redeem")
def redeem_magic(token: str, response: Response):
    user, session_token = redeem_magic_link(token)

    set_session_cookie(response, session_token)
    return {"ok": True}