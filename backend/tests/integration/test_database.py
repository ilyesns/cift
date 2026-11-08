import pytest
from sqlalchemy import inspect, text

from app.infrastructure.db.database import Database
from app.infrastructure.db.probe import SqlAlchemyDatabaseProbe
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

pytestmark = pytest.mark.integration

TABLE = "_uow_test_table"


def table_exists(database: Database) -> bool:
    return inspect(database.engine).has_table(TABLE)


@pytest.fixture(autouse=True)
def clean_table(database: Database):
    with database.engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {TABLE}"))
    yield
    with database.engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {TABLE}"))


def test_probe_pings_real_database(database: Database):
    SqlAlchemyDatabaseProbe(database.engine).ping()


def test_baseline_extensions_installed(database: Database):
    with database.engine.connect() as conn:
        names = set(conn.execute(text("SELECT extname FROM pg_extension")).scalars())
    assert {"unaccent", "pg_trgm"} <= names


def test_uow_commit_persists(database: Database):
    with SqlAlchemyUnitOfWork(database.session_factory) as uow:
        uow.session.execute(text(f"CREATE TABLE {TABLE} (x int)"))
        uow.commit()

    assert table_exists(database)


def test_uow_rolls_back_on_error(database: Database):
    # PostgreSQL DDL is transactional, so the table must vanish on rollback
    with pytest.raises(RuntimeError):
        with SqlAlchemyUnitOfWork(database.session_factory) as uow:
            uow.session.execute(text(f"CREATE TABLE {TABLE} (x int)"))
            raise RuntimeError("use case failed")

    assert not table_exists(database)


def test_uow_without_commit_does_not_persist(database: Database):
    with SqlAlchemyUnitOfWork(database.session_factory) as uow:
        uow.session.execute(text(f"CREATE TABLE {TABLE} (x int)"))

    assert not table_exists(database)


def test_uow_session_unavailable_outside_block(database: Database):
    uow = SqlAlchemyUnitOfWork(database.session_factory)
    with pytest.raises(RuntimeError):
        _ = uow.session
