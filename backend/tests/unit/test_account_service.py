from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.account_service import AccountService
from app.domain.exceptions import ConflictError, PermissionDeniedError, ValidationFailedError
from app.domain.users import Role, User
from tests.fakes import FakePasswordHasher, FakeUnitOfWork

NOW = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def service(uow: FakeUnitOfWork) -> AccountService:
    return AccountService(uow=uow, hasher=FakePasswordHasher())


def make_user(uow: FakeUnitOfWork, *roles: Role, email: str | None = None) -> User:
    user = User(
        id=uuid4(),
        email=email or f"{uuid4().hex[:8]}@example.com",
        password_hash="hashed::secret123",
        full_name="Test User",
        preferred_locale="it",
        preferred_city=None,
        is_active=True,
        email_verified_at=NOW,
        created_at=NOW,
        roles=frozenset({Role.MEMBER, *roles}),
    )
    uow.users.add(user)
    return user


def test_admin_can_make_someone_an_editor(service, uow):
    admin = make_user(uow, Role.ADMIN)
    member = make_user(uow)

    updated = service.set_roles(admin, member.id, frozenset({Role.EDITOR}))
    assert updated.roles == frozenset({Role.MEMBER, Role.EDITOR})


def test_admin_cannot_grant_admin(service, uow):
    admin = make_user(uow, Role.ADMIN)
    member = make_user(uow)

    with pytest.raises(PermissionDeniedError) as exc:
        service.set_roles(admin, member.id, frozenset({Role.ADMIN}))
    assert exc.value.code == "super_admin_required"


def test_super_admin_can_grant_admin(service, uow):
    boss = make_user(uow, Role.ADMIN, Role.SUPER_ADMIN)
    member = make_user(uow)

    assert Role.ADMIN in service.set_roles(boss, member.id, frozenset({Role.ADMIN})).roles


def test_super_admin_cannot_demote_self(service, uow):
    boss = make_user(uow, Role.ADMIN, Role.SUPER_ADMIN)

    with pytest.raises(ConflictError):
        service.set_roles(boss, boss.id, frozenset({Role.ADMIN}))


def test_change_password_checks_the_current_one(service, uow):
    user = make_user(uow)

    with pytest.raises(ValidationFailedError):
        service.change_password(user.id, current="wrong", new="new-password-1")

    service.change_password(user.id, current="secret123", new="new-password-1")
    assert uow.users.get(user.id).password_hash == "hashed::new-password-1"


def test_update_profile_trims_and_normalizes(service, uow):
    user = make_user(uow)
    updated = service.update_profile(
        user.id, full_name="  Omar  ", preferred_locale="ar-TN", preferred_city="  "
    )
    assert (updated.full_name, updated.preferred_locale, updated.preferred_city) == (
        "Omar",
        "ar",
        None,
    )