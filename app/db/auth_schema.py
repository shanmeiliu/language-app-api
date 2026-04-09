from app.db.connection import get_db_cursor


def ensure_auth_schema() -> None:
    with get_db_cursor() as cur:
        cur.execute("""
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";

        CREATE TABLE IF NOT EXISTS public.app_user (
          user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('google', 'local', 'anonymous')),
          email VARCHAR(320),
          google_sub VARCHAR(255),
          username VARCHAR(100) NOT NULL UNIQUE,
          password_hash TEXT,
          is_active BOOLEAN NOT NULL DEFAULT TRUE,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          last_login_at TIMESTAMPTZ,
          last_activity_at TIMESTAMPTZ,
          expires_at TIMESTAMPTZ
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_app_user_google_sub
        ON public.app_user(google_sub)
        WHERE google_sub IS NOT NULL;

        CREATE UNIQUE INDEX IF NOT EXISTS idx_app_user_email
        ON public.app_user(email)
        WHERE email IS NOT NULL;

        CREATE TABLE IF NOT EXISTS public.user_session (
          session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id UUID NOT NULL REFERENCES public.app_user(user_id) ON DELETE CASCADE,
          session_token_hash TEXT NOT NULL UNIQUE,
          login_method VARCHAR(20) NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          expires_at TIMESTAMPTZ NOT NULL,
          revoked_at TIMESTAMPTZ
        );
        CREATE TABLE IF NOT EXISTS public.magic_link (
        token_hash TEXT PRIMARY KEY,
        user_id UUID NOT NULL REFERENCES public.app_user(user_id) ON DELETE CASCADE,
        expires_at TIMESTAMPTZ NOT NULL,
        used_at TIMESTAMPTZ
        );

        CREATE INDEX IF NOT EXISTS idx_user_session_user_id
        ON public.user_session(user_id);

        CREATE INDEX IF NOT EXISTS idx_user_session_token_hash
        ON public.user_session(session_token_hash);
        """)