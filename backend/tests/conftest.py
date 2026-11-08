from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_health_service, get_uow
from app.application.health_service import HealthService
from app.core.config import Settings
from app.main import create_app
from tests.fakes import FakeDatabaseProbe, FakeUnitOfWork


@pytest.fixture
def settings() -> Settings:
    # Explicit values win over environment variables, so tests never depend on .env.
    # The URL points nowhere: API tests must not reach a real database.
    return Settings(
        app_name="CIFT API (test)",
        environment="test",
        database_url="postgresql+psycopg://test:test@127.0.0.1:1/test",
        cors_origins=["http://testserver"],
    )


@pytest.fixture
def fake_probe() -> FakeDatabaseProbe:
    return FakeDatabaseProbe(healthy=True)


@pytest.fixture
def fake_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def app(settings: Settings, fake_probe: FakeDatabaseProbe, fake_uow: FakeUnitOfWork) -> FastAPI:
    """The real app, with every port swapped for a fake."""
    application = create_app(settings)
    application.dependency_overrides[get_health_service] = lambda: HealthService(
        probe=fake_probe, app_name=settings.app_name, environment=settings.environment
    )
    application.dependency_overrides[get_uow] = lambda: fake_uow
    return application


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    # "with" runs the lifespan (startup/shutdown) exactly like the real server
    with TestClient(app) as test_client:
        yield test_client
