import pytest

from app.api.errors import status_for
from app.domain.exceptions import (
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ServiceUnavailableError,
    UnauthenticatedError,
    ValidationFailedError,
)


@pytest.mark.parametrize(
    ("error", "status"),
    [
        (NotFoundError("x"), 404),
        (ConflictError("x"), 409),
        (ValidationFailedError("x"), 422),
        (UnauthenticatedError("x"), 401),
        (PermissionDeniedError("x"), 403),
        (ServiceUnavailableError("x"), 503),
        (DomainError("x"), 400),
    ],
)
def test_status_for(error: DomainError, status: int):
    assert status_for(error) == status


def test_subclass_inherits_parent_status():
    class ListingNotFound(NotFoundError):
        code = "listing_not_found"

    error = ListingNotFound("No such listing.")
    assert status_for(error) == 404
    assert error.code == "listing_not_found"


def test_custom_code_overrides_default():
    error = ConflictError("Already published.", code="listing_published")
    assert error.code == "listing_published"
