import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def generate_username(prefix: str = "user") -> str:
    return f"{prefix}_{secrets.token_urlsafe(6).lower()}"


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def default_session_expiry() -> datetime:
    return utcnow() + timedelta(days=settings.session_ttl_days)