from app.db.connection import get_db_cursor


def ensure_schema() -> None:
    with get_db_cursor() as cur:
        cur.execute("""
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";

        CREATE TABLE IF NOT EXISTS public.flashcard (
          flashcard_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          source_lang VARCHAR(50) NOT NULL,
          target_lang VARCHAR(50) NOT NULL,
          prompt_type VARCHAR(20) NOT NULL,
          text_type VARCHAR(20),
          difficulty VARCHAR(20),
          topic TEXT,
          source_text TEXT,
          target_text TEXT NOT NULL,
          explanation TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS public.flashcard_option (
          option_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          flashcard_id UUID NOT NULL REFERENCES public.flashcard(flashcard_id) ON DELETE CASCADE,
          option_text TEXT NOT NULL,
          is_correct BOOLEAN NOT NULL DEFAULT FALSE,
          option_order INT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS public.generation_run (
          run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          flashcard_id UUID NOT NULL REFERENCES public.flashcard(flashcard_id) ON DELETE CASCADE,
          model_name VARCHAR(100) NOT NULL,
          prompt_template VARCHAR(255) NOT NULL,
          raw_request JSONB,
          raw_response TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_flashcard_lookup_phrase
        ON public.flashcard (source_lang, target_lang, prompt_type, source_text);

        CREATE INDEX IF NOT EXISTS idx_flashcard_lookup_topic
        ON public.flashcard (source_lang, target_lang, prompt_type, topic, difficulty);
        """)