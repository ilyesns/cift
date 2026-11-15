from dataclasses import replace
from datetime import datetime, timedelta
from types import TracebackType
from typing import Self
from uuid import UUID

from app.domain.auth import AccessClaims, AccessToken, ActionToken, RefreshSession, TokenPurpose
from app.domain.exceptions import ConflictError, NotFoundError, UnauthenticatedError
from app.domain.users import Role, User


class FakeDatabaseProbe:
    def __init__(self, healthy: bool = True) -> None:
        self.healthy = healthy
        self.calls = 0

    def ping(self) -> None:
        self.calls += 1
        if not self.healthy:
            raise ConnectionError("database is down")


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, User] = {}

    def _require(self, user_id: UUID) -> User:
        if user_id not in self.items:
            raise NotFoundError("User not found.", code="user_not_found")
        return self.items[user_id]

    def get(self, user_id: UUID) -> User | None:
        return self.items.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.items.values() if u.email == email), None)

    def add(self, user: User) -> None:
        if self.get_by_email(user.email) is not None:
            raise ConflictError("Email taken.", code="email_taken")
        self.items[user.id] = user

    def mark_verified(self, user_id: UUID, at: datetime) -> None:
        self.items[user_id] = replace(self._require(user_id), email_verified_at=at)

    def set_password_hash(self, user_id: UUID, password_hash: str) -> None:
        self.items[user_id] = replace(self._require(user_id), password_hash=password_hash)

    def update_profile(
        self, user_id: UUID, *, full_name: str, preferred_locale: str, preferred_city: str | None
    ) -> None:
        self.items[user_id] = replace(
            self._require(user_id),
            full_name=full_name,
            preferred_locale=preferred_locale,
            preferred_city=preferred_city,
        )

    def set_roles(self, user_id: UUID, roles: frozenset[Role]) -> None:
        self.items[user_id] = replace(self._require(user_id), roles=roles)

    def search(self, *, query: str | None, offset: int, limit: int) -> tuple[list[User], int]:
        q = (query or "").lower()
        found = [u for u in self.items.values() if q in u.email or q in u.full_name.lower()]
        found.sort(key=lambda u: u.created_at, reverse=True)
        return found[offset : offset + limit], len(found)


class InMemoryActionTokenRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, ActionToken] = {}

    def add(self, token: ActionToken) -> None:
        self.items[token.id] = token

    def get_by_hash(self, token_hash: str, purpose: TokenPurpose) -> ActionToken | None:
        return next(
            (t for t in self.items.values() if t.token_hash == token_hash and t.purpose == purpose),
            None,
        )

    def mark_used(self, token_id: UUID, at: datetime) -> None:
        self.items[token_id].used_at = at

    def invalidate_for_user(self, user_id: UUID, purpose: TokenPurpose, at: datetime) -> None:
        for token in self.items.values():
            if token.user_id == user_id and token.purpose == purpose and token.used_at is None:
                token.used_at = at


class InMemoryRefreshSessionRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, RefreshSession] = {}

    def add(self, session: RefreshSession) -> None:
        self.items[session.id] = session

    def get_by_hash(self, token_hash: str) -> RefreshSession | None:
        return next((s for s in self.items.values() if s.token_hash == token_hash), None)

    def _revoke(self, sessions: list[RefreshSession], at: datetime) -> None:
        for session in sessions:
            if session.revoked_at is None:
                session.revoked_at = at

    def revoke(self, session_id: UUID, at: datetime) -> None:
        self._revoke([self.items[session_id]], at)

    def revoke_family(self, family_id: UUID, at: datetime) -> None:
        self._revoke([s for s in self.items.values() if s.family_id == family_id], at)

    def revoke_all_for_user(self, user_id: UUID, at: datetime) -> None:
        self._revoke([s for s in self.items.values() if s.user_id == user_id], at)


class FakeUnitOfWork:
    """In-memory UnitOfWork. Data survives between 'with' blocks, like a real database."""

    def __init__(self) -> None:
        self.users = InMemoryUserRepository()
        self.action_tokens = InMemoryActionTokenRepository()
        self.refresh_sessions = InMemoryRefreshSessionRepository()
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> Self:
        self.committed = False
        self.rolled_back = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed::{password}"

    def verify(self, password_hash: str, password: str) -> bool:
        return password_hash == f"hashed::{password}"

    def needs_rehash(self, password_hash: str) -> bool:
        return False


class FakeAccessTokenIssuer:
    def issue(self, user: User) -> AccessToken:
        return AccessToken(token=f"access::{user.id}", expires_in=900)

    def decode(self, token: str) -> AccessClaims:
        if not token.startswith("access::"):
            raise UnauthenticatedError("Invalid access token.", code="invalid_token")
        return AccessClaims(user_id=UUID(token.removeprefix("access::")), roles=frozenset())


class FakeAuthNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []  # (kind, email, token)

    def send_verification(self, user: User, token: str) -> None:
        self.sent.append(("verify", user.email, token))

    def send_password_reset(self, user: User, token: str) -> None:
        self.sent.append(("reset", user.email, token))

    def last_token(self, kind: str) -> str | None:
        return next((token for k, _, token in reversed(self.sent) if k == kind), None)


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self.current = start

    def __call__(self) -> datetime:
        return self.current

    def advance(self, **kwargs: float) -> None:
        self.current += timedelta(**kwargs)