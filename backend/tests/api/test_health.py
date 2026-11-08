from fastapi.testclient import TestClient

from tests.fakes import FakeDatabaseProbe


def test_liveness(client: TestClient):
    res = client.get("/api/v1/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok", "app": "CIFT API (test)", "environment": "test"}


def test_database_up(client: TestClient, fake_probe: FakeDatabaseProbe):
    res = client.get("/api/v1/health/db")

    assert res.status_code == 200
    assert res.json() == {"status": "ok", "database": "up"}
    assert fake_probe.calls == 1


def test_database_down_returns_503(client: TestClient, fake_probe: FakeDatabaseProbe):
    fake_probe.healthy = False

    res = client.get("/api/v1/health/db")

    assert res.status_code == 503
    assert res.json()["error"]["code"] == "database_unavailable"


def test_openapi_lists_health_routes(client: TestClient):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/health/db" in paths
