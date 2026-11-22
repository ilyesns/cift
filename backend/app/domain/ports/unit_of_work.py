from types import TracebackType
from typing import Protocol, Self

from app.domain.ports.auth import ActionTokenRepository, RefreshSessionRepository
from app.domain.ports.prayer import PrayerRepository
from app.domain.ports.users import UserRepository


class UnitOfWork(Protocol):
    users: UserRepository
    action_tokens: ActionTokenRepository
    refresh_sessions: RefreshSessionRepository
    prayer: PrayerRepository
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
