from app.db.connection import get_db_cursor




def record_flashcard_answer(
    user_id: str,
    flashcard_id: str,
    selected_option: str,
    correct_answer: str,
    is_correct: bool,
    mode: str | None,
) -> str:
    with get_db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.user_flashcard_attempt (
                user_id,
                flashcard_id,
                selected_option,
                correct_answer,
                is_correct,
                mode,
                answered_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING attempt_id
            """,
            (
                user_id,
                flashcard_id,
                selected_option,
                correct_answer,
                is_correct,
                mode,
            ),
        )

        row = cur.fetchone()

    return str(row[0])
        )


def get_user_dashboard_attempts(user_id: str, limit: int = 100) -> list[dict]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT
                a.attempt_id,
                a.flashcard_id,
                f.source_text,
                f.target_text,
                a.selected_option,
                a.correct_answer,
                a.is_correct,
                a.mode,
                a.shown_at,
                a.answered_at
            FROM public.user_flashcard_attempt a
            JOIN public.flashcard f ON f.flashcard_id = a.flashcard_id
            WHERE a.user_id = %s
            ORDER BY a.shown_at DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()

    return [
        {
            "attempt_id": str(row[0]),
            "flashcard_id": str(row[1]),
            "source_text": row[2],
            "target_text": row[3],
            "selected_option": row[4],
            "correct_answer": row[5],
            "is_correct": row[6],
            "mode": row[7],
            "shown_at": row[8].isoformat(),
            "answered_at": row[9].isoformat() if row[9] else None,
        }
        for row in rows
    ]