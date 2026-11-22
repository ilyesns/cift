from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.application.auth_service import AuthPolicy, AuthService
from app.domain.exceptions import (
    ConflictError,
    PermissionDeniedError,
    UnauthenticatedError,
    ValidationFailedError,
)
from app.domain.users import Role
from tests.fakes import (
    FakeAccessTokenIssuer,
    FakeAuthNotifier,
    FakeClock,
    FakePasswordHasher,
    FakeUnitOfWork,
)

POLICY = AuthPolicy(
    refresh_ttl=timedelta(days=30),
    verify_email_ttl=timedelta(hours=24),
    reset_password_ttl=timedelta(hours=1),
)
EMAIL = "amina@example.com"
PASSWORD = "correct horse battery"


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 11, 15, 12, 0, tzinfo=UTC))


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def notifier() -> FakeAuthNotifier:
    return FakeAuthNotifier()


@pytest.fixture
def service(uow: FakeUnitOfWork, notifier: FakeAuthNotifier, clock: FakeClock) -> AuthService:
    return AuthService(
        uow=uow,
        hasher=FakePasswordHasher(),
        tokens=FakeAccessTokenIssuer(),
        notifier=notifier,
        policy=POLICY,
        now=clock,
    )


def register(service: AuthService, email: str = EMAIL):
    return service.register(email=email, password=PASSWORD, full_name="Amina Rossi", locale="ar")


def test_register_creates_unverified_member_and_sends_link(service, notifier):
    result = register(service)

    assert result.user.roles == frozenset({Role.MEMBER})
    assert not result.user.is_verified
    assert result.user.preferred_locale == "ar"
    assert result.refresh_token
    assert notifier.last_token("verify") is not None


def test_register_normalizes_email_and_rejects_duplicates(service):
    register(service, " Amina@Example.com ")

    with pytest.raises(ConflictError) as exc:
        register(service, EMAIL)
    assert exc.value.code == "email_taken"


def test_verification_link_works_once(service, notifier, uow):
    result = register(service)
    token = notifier.last_token("verify")

    assert service.verify_email(token).is_verified
    assert uow.users.get(result.user.id).is_verified
    with pytest.raises(ValidationFailedError):
        service.verify_email(token)


def test_expired_verification_link_is_rejected(service, notifier, clock):
    register(service)
    token = notifier.last_token("verify")
    clock.advance(hours=25)

    with pytest.raises(ValidationFailedError) as exc:
        service.verify_email(token)
    assert exc.value.code == "invalid_or_expired_token"


def test_resending_verification_invalidates_the_old_link(service, notifier):
    register(service)
    old = notifier.last_token("verify")
    service.resend_verification(EMAIL)

    with pytest.raises(ValidationFailedError):
        service.verify_email(old)
    assert service.verify_email(notifier.last_token("verify")).is_verified


def test_login_with_wrong_password_fails(service):
    register(service)

    with pytest.raises(UnauthenticatedError) as exc:
        service.login(email=EMAIL, password="wrong")
    assert exc.value.code == "invalid_credentials"


def test_suspended_account_cannot_sign_in(service, uow):
    result = register(service)
    uow.users.items[result.user.id] = replace(result.user, is_active=False)

    with pytest.raises(PermissionDeniedError) as exc:
        service.login(email=EMAIL, password=PASSWORD)
    assert exc.value.code == "account_suspended"


def test_refresh_rotates_the_token(service, uow):
    first = register(service)
    second = service.refresh(first.refresh_token)

    assert second.refresh_token != first.refresh_token
    sessions = list(uow.refresh_sessions.items.values())
    assert len(sessions) == 2
    assert sum(s.revoked_at is None for s in sessions) == 1


def test_reusing_an_old_token_ends_the_whole_family(service, clock):
    first = register(service)
    second = service.refresh(first.refresh_token)
    clock.advance(minutes=1)

    with pytest.raises(UnauthenticatedError) as exc:
        service.refresh(first.refresh_token)
    assert exc.value.code == "session_reused"

    with pytest.raises(UnauthenticatedError):
        service.refresh(second.refresh_token)


def test_reuse_inside_grace_window_keeps_the_session(service, clock):
    first = register(service)
    second = service.refresh(first.refresh_token)
    clock.advance(seconds=2)

    with pytest.raises(UnauthenticatedError) as exc:
        service.refresh(first.refresh_token)
    assert exc.value.code == "session_rotated"
    assert service.refresh(second.refresh_token).refresh_token


def test_expired_refresh_token(service, clock):
    first = register(service)
    clock.advance(days=31)

    with pytest.raises(UnauthenticatedError) as exc:
        service.refresh(first.refresh_token)
    assert exc.value.code == "session_expired"


def test_logout_ends_the_session(service):
    first = register(service)
    service.logout(first.refresh_token)

    with pytest.raises(UnauthenticatedError):
        service.refresh(first.refresh_token)


def test_password_reset_changes_password_and_ends_sessions(service, notifier):
    first = register(service)
    service.forgot_password(EMAIL)
    service.reset_password(notifier.last_token("reset"), "a brand new password")

    with pytest.raises(UnauthenticatedError):
        service.refresh(first.refresh_token)
    with pytest.raises(UnauthenticatedError):
        service.login(email=EMAIL, password=PASSWORD)

    result = service.login(email=EMAIL, password="a brand new password")
    assert result.user.is_verified  # the reset link proved they own the inbox


def test_forgot_password_for_unknown_email_is_silent(service, notifier):
    service.forgot_password("nobody@example.com")
    assert notifier.sent == []
