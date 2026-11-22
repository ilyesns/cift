from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Role(StrEnum):
    MEMBER = "member"
    EDITOR = "editor"
    GUIDE = "guide"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass(slots=True)
class User:
    id: UUID
    email: str
    password_hash: str
    full_name: str
    preferred_locale: str
    preferred_city: str | None
    is_active: bool
    email_verified_at: datetime | None
    created_at: datetime
    roles: frozenset[Role] = field(default_factory=lambda: frozenset({Role.MEMBER}))

    @property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None

    def has_any_role(self, *roles: Role) -> bool:
        """Super admins pass every role check."""
        if Role.SUPER_ADMIN in self.roles:
            return True
        return not self.roles.isdisjoint(roles)


def normalize_email(email: str) -> str:
    return email.strip().lower()
