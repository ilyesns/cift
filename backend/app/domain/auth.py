from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.users import Role, User


class TokenPurpose(StrEnum):
    VERIFY_EMAIL = "verify_email"
    RESET_PASSWORD = "reset_password"


@dataclass(slots=True)
class ActionToken:
    """Single-use token sent by email. Only its SHA-256 hash is stored."""

    id: UUID
    user_id: UUID
    purpose: TokenPurpose
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None

    def is_usable(self, now: datetime) -> bool:
        return self.used_at is None and now < self.expires_at


@dataclass(slots=True)
class RefreshSession:
    """One refresh token. Each refresh revokes it and creates the next one in the same family."""

    id: UUID
    user_id: UUID
    family_id: UUID
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    user_agent: str | None = None


@dataclass(frozen=True, slots=True)
class AccessToken:
    token: str
    expires_in: int  # seconds


@dataclass(frozen=True, slots=True)
class AccessClaims:
    user_id: UUID
    roles: frozenset[Role]


@dataclass(frozen=True, slots=True)
class AuthResult:
    user: User
    access_token: AccessToken
    refresh_token: str  # raw value, only ever placed in the httpOnly cookie
    refresh_expires_at: datetime