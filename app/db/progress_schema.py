from app.db.connection import get_db_cursor


def ensure_progress_schema() -> None:
    with get_db_cursor() as cur:
        cur.execute("""
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";

        CREATE TABLE IF NOT EXISTS public.user_flashcard_attempt (
          attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id UUID NOT NULL REFERENCES public.app_user(user_id) ON DELETE CASCADE,
          flashcard_id UUID NOT NULL REFERENCES public.flashcard(flashcard_id) ON DELETE CASCADE,
          shown_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          answered_at TIMESTAMPTZ,
          selected_option TEXT,
          correct_answer TEXT,
          is_correct BOOLEAN,
          mode VARCHAR(30),
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_pending_user_flashcard_attempt
        ON public.user_flashcard_attempt(user_id, flashcard_id, COALESCE(mode, ''))
        WHERE answered_at IS NULL;
        
        CREATE INDEX IF NOT EXISTS idx_user_flashcard_attempt_user_id
        ON public.user_flashcard_attempt(user_id);

        CREATE INDEX IF NOT EXISTS idx_user_flashcard_attempt_flashcard_id
        ON public.user_flashcard_attempt(flashcard_id);

        CREATE INDEX IF NOT EXISTS idx_user_flashcard_attempt_answered_at
        ON public.user_flashcard_attempt(answered_at);
        """)