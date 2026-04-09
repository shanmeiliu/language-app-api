from fastapi import HTTPException
from app.db.auth_schema import ensure_auth_schema
from app.repositories.auth_repository import (
    create_local_user,
    create_session,
    get_session_with_user,
    get_user_by_username,
    revoke_session,
)
from app.services.auth_utils import (
    default_session_expiry,
    generate_session_token,
    generate_username,
    hash_password,
    hash_session_token,
    verify_password,
)


def register_local_user(email: str | None, password: str) -> tuple[dict, str]:
    ensure_auth_schema()

    username = generate_username("local")
    hashed = hash_password(password)
    user = create_local_user(username=username, password_hash=hashed, email=email)

    raw_token = generate_session_token()
    create_session(
        user_id=user["user_id"],
        token_hash=hash_session_token(raw_token),
        login_method="password",
        expires_at=default_session_expiry(),
    )
    return user, raw_token


def login_with_password(username: str, password: str) -> tuple[dict, str]:
    ensure_auth_schema()

    user = get_user_by_username(username)
    if not user or not user["password_hash"] or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="User is inactive")

    raw_token = generate_session_token()
    create_session(
        user_id=user["user_id"],
        token_hash=hash_session_token(raw_token),
        login_method="password",
        expires_at=default_session_expiry(),
    )

    return {
        "user_id": user["user_id"],
        "account_type": user["account_type"],
        "email": user["email"],
        "username": user["username"],
        "is_active": user["is_active"],
    }, raw_token


def get_current_user_from_session(raw_token: str) -> dict:
    ensure_auth_schema()

    session = get_session_with_user(hash_session_token(raw_token))
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if session["revoked_at"] is not None:
        raise HTTPException(status_code=401, detail="Session has been revoked")

    if not session["is_active"]:
        raise HTTPException(status_code=403, detail="User is inactive")

    from app.repositories.auth_repository import touch_session
    touch_session(
        session_id=session["session_id"],
        user_id=session["user_id"],
        expires_at=default_session_expiry(),
    )

    return {
        "user_id": session["user_id"],
        "account_type": session["account_type"],
        "email": session["email"],
        "username": session["username"],
        "is_active": session["is_active"],
    }


def logout_from_session(raw_token: str) -> None:
    ensure_auth_schema()
    revoke_session(hash_session_token(raw_token))