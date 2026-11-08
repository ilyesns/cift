from types import TracebackType
from typing import Self


class FakeDatabaseProbe:
    """Stands in for SqlAlchemyDatabaseProbe."""

    def __init__(self, healthy: bool = True) -> None:
        self.healthy = healthy
        self.calls = 0

    def ping(self) -> None:
        self.calls += 1
        if not self.healthy:
            raise ConnectionError("database is down")


class FakeUnitOfWork:
    """Stands in for SqlAlchemyUnitOfWork. Records what happened instead of touching a DB."""

    def __init__(self) -> None:
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
