from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.exceptions import ConflictError, NotFoundError


def add_test_routes(app: FastAPI) -> None:
    @app.get("/_test/not-found")
    def not_found() -> None:
        raise NotFoundError("Listing not found.", code="listing_not_found")

    @app.get("/_test/conflict")
    def conflict() -> None:
        raise ConflictError("Listing already published.", details={"status": "published"})

    @app.get("/_test/needs-int")
    def needs_int(n: int) -> dict:
        return {"n": n}


def make_client(app: FastAPI) -> TestClient:
    add_test_routes(app)
    return TestClient(app)


def test_unknown_route(client: TestClient):
    res = client.get("/api/v1/does-not-exist")

    assert res.status_code == 404
    assert res.json() == {"error": {"code": "not_found", "message": "Not Found", "details": None}}


def test_domain_not_found(app: FastAPI):
    with make_client(app) as c:
        res = c.get("/_test/not-found")

    assert res.status_code == 404
    assert res.json()["error"] == {
        "code": "listing_not_found",
        "message": "Listing not found.",
        "details": None,
    }


def test_domain_conflict_keeps_details(app: FastAPI):
    with make_client(app) as c:
        res = c.get("/_test/conflict")

    assert res.status_code == 409
    assert res.json()["error"]["code"] == "conflict"
    assert res.json()["error"]["details"] == {"status": "published"}


def test_validation_error_lists_fields(app: FastAPI):
    with make_client(app) as c:
        res = c.get("/_test/needs-int", params={"n": "abc"})

    assert res.status_code == 422
    body = res.json()["error"]
    assert body["code"] == "validation_error"
    assert body["details"][0]["field"] == "query.n"


def test_wrong_method(client: TestClient):
    res = client.post("/api/v1/health")

    assert res.status_code == 405
    assert res.json()["error"]["code"] == "method_not_allowed"
