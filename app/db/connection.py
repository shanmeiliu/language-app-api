from contextlib import contextmanager
import psycopg
from app.core.config import settings

@contextmanager
def get_db_cursor():
    if not settings.database_url:
        raise ValueError("DATABASE_URL is not set")

    conn = psycopg.connect(settings.database_url)
    try:
        conn.autocommit = False
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()