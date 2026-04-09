import secrets
from datetime import timedelta
from app.db.connection import get_db_cursor
from app.services.auth_utils import (
    hash_session_token,
    generate_username,
    default_session_expiry,
    generate_session_token,
)
from app.repositories.auth_repository import create_session
from app.core.config import settings


def create_anonymous_user() -> dict:
    username = generate_username("anon")

    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.app_user (
                account_type, username,
                last_login_at, last_activity_at,
                expires_at
            )
            VALUES ('anonymous', %s, NOW(), NOW(), NOW() + INTERVAL '30 days')
            RETURNING user_id, account_type, username, is_active
            """,
            (username,),
        )
        row = cur.fetchone()

    return {
        "user_id": str(row[0]),
        "account_type": row[1],
        "username": row[2],
        "is_active": row[3],
    }


def create_magic_link(user_id: str) -> str:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_session_token(raw_token)

    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.magic_link (token_hash, user_id, expires_at)
            VALUES (%s, %s, NOW() + INTERVAL '15 minutes')
            """,
            (token_hash, user_id),
        )

    return raw_token


def redeem_magic_link(raw_token: str) -> tuple[dict, str]:
    token_hash = hash_session_token(raw_token)

    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT user_id, expires_at, used_at
            FROM public.magic_link
            WHERE token_hash = %s
            """,
            (token_hash,),
        )
        row = cur.fetchone()

        if not row:
            raise ValueError("Invalid link")

        user_id, expires_at, used_at = row

        if used_at:
            raise ValueError("Link already used")

        if expires_at < default_session_expiry():
            raise ValueError("Link expired")

        # mark used
        cur.execute(
            "UPDATE public.magic_link SET used_at = NOW() WHERE token_hash = %s",
            (token_hash,),
        )

    # create session
    session_token = generate_session_token()

    create_session(
        user_id=str(user_id),
        token_hash=hash_session_token(session_token),
        login_method="magic_link",
        expires_at=default_session_expiry(),
    )

    return {"user_id": str(user_id)}, session_token