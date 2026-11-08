from typing import Any


class DomainError(Exception):
    """Base class for expected business failures. Has no knowledge of HTTP."""

    code: str = "error"

    def __init__(self, message: str, *, code: str | None = None, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.details = details


class NotFoundError(DomainError):
    code = "not_found"


class ConflictError(DomainError):
    code = "conflict"


class ValidationFailedError(DomainError):
    code = "validation_error"


class UnauthenticatedError(DomainError):
    code = "unauthorized"


class PermissionDeniedError(DomainError):
    code = "forbidden"


class ServiceUnavailableError(DomainError):
    code = "service_unavailable"