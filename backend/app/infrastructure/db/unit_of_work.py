from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.repositories.auth import (
    SqlAlchemyActionTokenRepository,
    SqlAlchemyRefreshSessionRepository,
)
from app.infrastructure.db.repositories.prayer import SqlAlchemyPrayerRepository
from app.infrastructure.db.repositories.users import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork:
    users: SqlAlchemyUserRepository
    action_tokens: SqlAlchemyActionTokenRepository
    refresh_sessions: SqlAlchemyRefreshSessionRepository
    prayer: SqlAlchemyPrayerRepository

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork used outside a 'with' block")
        return self._session

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        self.action_tokens = SqlAlchemyActionTokenRepository(self._session)
        self.refresh_sessions = SqlAlchemyRefreshSessionRepository(self._session)
        self.prayer = SqlAlchemyPrayerRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.session.rollback()
        self.session.close()
        self._session = None

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
