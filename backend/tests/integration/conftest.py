from collections.abc import Iterator

import pytest

from app.core.config import get_settings
from app.infrastructure.db.database import Database
from app.infrastructure.db.probe import SqlAlchemyDatabaseProbe


@pytest.fixture(scope="session")
def database() -> Iterator[Database]:
    db = Database(get_settings().database_url)
    try:
        SqlAlchemyDatabaseProbe(db.engine).ping()
    except Exception as exc:  # noqa: BLE001
        db.dispose()
        pytest.skip(f"PostgreSQL not reachable: {exc}")
    yield db
    db.dispose()
