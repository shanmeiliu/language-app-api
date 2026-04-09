from typing import Optional
from app.db.connection import get_db_cursor
from app.services.auth_utils import utcnow


def create_local_user(username: str, password_hash: str, email: Optional[str] = None) -> dict:
    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.app_user (
                account_type, email, username, password_hash,
                last_login_at, last_activity_at
            )
            VALUES ('local', %s, %s, %s, NOW(), NOW())
            RETURNING user_id, account_type, email, username, is_active
            """,
            (email, username, password_hash),
        )
        row = cur.fetchone()

    return {
        "user_id": str(row[0]),
        "account_type": row[1],
        "email": row[2],
        "username": row[3],
        "is_active": row[4],
    }


def get_user_by_username(username: str) -> Optional[dict]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT user_id, account_type, email, username, password_hash, is_active
            FROM public.app_user
            WHERE username = %s
            """,
            (username,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "user_id": str(row[0]),
        "account_type": row[1],
        "email": row[2],
        "username": row[3],
        "password_hash": row[4],
        "is_active": row[5],
    }


def get_user_by_google_sub(google_sub: str) -> Optional[dict]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT user_id, account_type, email, username, is_active
            FROM public.app_user
            WHERE google_sub = %s
            """,
            (google_sub,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "user_id": str(row[0]),
        "account_type": row[1],
        "email": row[2],
        "username": row[3],
        "is_active": row[4],
    }


def upsert_google_user(google_sub: str, email: Optional[str], username: str) -> dict:
    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.app_user (
                account_type, email, google_sub, username,
                last_login_at, last_activity_at, expires_at
            )
            VALUES ('google', %s, %s, %s, NOW(), NOW(), NOW() + INTERVAL '1 year')
            ON CONFLICT (google_sub) DO UPDATE
            SET email = EXCLUDED.email,
                last_login_at = NOW(),
                last_activity_at = NOW(),
                expires_at = NOW() + INTERVAL '1 year'
            RETURNING user_id, account_type, email, username, is_active
            """,
            (email, google_sub, username),
        )
        row = cur.fetchone()

    return {
        "user_id": str(row[0]),
        "account_type": row[1],
        "email": row[2],
        "username": row[3],
        "is_active": row[4],
    }


def create_session(user_id: str, token_hash: str, login_method: str, expires_at) -> None:
    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.user_session (
                user_id, session_token_hash, login_method, expires_at
            )
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, token_hash, login_method, expires_at),
        )


def get_session_with_user(token_hash: str) -> Optional[dict]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT
                s.session_id,
                s.user_id,
                s.expires_at,
                s.revoked_at,
                u.account_type,
                u.email,
                u.username,
                u.is_active
            FROM public.user_session s
            JOIN public.app_user u ON u.user_id = s.user_id
            WHERE s.session_token_hash = %s
            """,
            (token_hash,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "session_id": str(row[0]),
        "user_id": str(row[1]),
        "expires_at": row[2],
        "revoked_at": row[3],
        "account_type": row[4],
        "email": row[5],
        "username": row[6],
        "is_active": row[7],
    }


def touch_session(session_id: str, user_id: str, expires_at) -> None:
    with get_db_cursor() as cur:
        cur.execute(
            """
            UPDATE public.user_session
            SET last_seen_at = NOW(),
                expires_at = %s
            WHERE session_id = %s
            """,
            (expires_at, session_id),
        )
        cur.execute(
            """
            UPDATE public.app_user
            SET last_activity_at = NOW()
            WHERE user_id = %s
            """,
            (user_id,),
        )


def revoke_session(token_hash: str) -> None:
    with get_db_cursor() as cur:
        cur.execute(
            """
            UPDATE public.user_session
            SET revoked_at = NOW()
            WHERE session_token_hash = %s
              AND revoked_at IS NULL
            """,
            (token_hash,),
        )