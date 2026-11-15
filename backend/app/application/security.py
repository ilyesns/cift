import hashlib
import secrets
from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def new_opaque_token() -> tuple[str, str]:
    """Random URL-safe token and its hash. Send the raw value, store only the hash."""
    raw = secrets.token_urlsafe(32)
    return raw, hash_token(raw)