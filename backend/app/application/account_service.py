from dataclasses import replace
from uuid import UUID

from app.domain.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationFailedError,
)
from app.domain.i18n import normalize_locale
from app.domain.ports.auth import PasswordHasher
from app.domain.ports.unit_of_work import UnitOfWork
from app.domain.users import Role, User

PRIVILEGED_ROLES = frozenset({Role.ADMIN, Role.SUPER_ADMIN})


class AccountService:
    def __init__(self, *, uow: UnitOfWork, hasher: PasswordHasher) -> None:
        self._uow = uow
        self._hasher = hasher

    def update_profile(
        self,
        user_id: UUID,
        *,
        full_name: str,
        preferred_locale: str,
        preferred_city: str | None,
    ) -> User:
        with self._uow as uow:
            uow.users.update_profile(
                user_id,
                full_name=full_name.strip(),
                preferred_locale=normalize_locale(preferred_locale),
                preferred_city=(preferred_city or "").strip() or None,
            )
            user = self._require(uow, user_id)
            uow.commit()
        return user

    def change_password(self, user_id: UUID, *, current: str, new: str) -> None:
        with self._uow as uow:
            user = self._require(uow, user_id)
            if not self._hasher.verify(user.password_hash, current):
                raise ValidationFailedError(
                    "Current password is incorrect.", code="wrong_password"
                )
            uow.users.set_password_hash(user_id, self._hasher.hash(new))
            uow.commit()

    def search_users(
        self, *, query: str | None, page: int, page_size: int
    ) -> tuple[list[User], int]:
        with self._uow as uow:
            return uow.users.search(query=query, offset=(page - 1) * page_size, limit=page_size)

    def set_roles(self, actor: User, user_id: UUID, roles: frozenset[Role]) -> User:
        wanted = frozenset(roles) | {Role.MEMBER}
        with self._uow as uow:
            target = self._require(uow, user_id)
            changed = wanted ^ target.roles
            if changed & PRIVILEGED_ROLES and Role.SUPER_ADMIN not in actor.roles:
                raise PermissionDeniedError(
                    "Only a super admin can change admin roles.", code="super_admin_required"
                )
            if (
                target.id == actor.id
                and Role.SUPER_ADMIN in target.roles
                and Role.SUPER_ADMIN not in wanted
            ):
                raise ConflictError(
                    "You can't remove your own super admin role.", code="cannot_demote_self"
                )
            uow.users.set_roles(user_id, wanted)
            uow.commit()
        return replace(target, roles=wanted)

    @staticmethod
    def _require(uow: UnitOfWork, user_id: UUID) -> User:
        user = uow.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found.", code="user_not_found")
        return user