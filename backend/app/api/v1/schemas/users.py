from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.users import Role, User

Locale = Literal["it", "ar", "en"]


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    preferred_locale: str
    preferred_city: str | None
    email_verified: bool
    roles: list[Role]
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserOut":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            preferred_locale=user.preferred_locale,
            preferred_city=user.preferred_city,
            email_verified=user.is_verified,
            roles=sorted(user.roles),
            created_at=user.created_at,
        )


class UpdateProfileIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    preferred_locale: Locale
    preferred_city: str | None = Field(default=None, max_length=80)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class SetRolesIn(BaseModel):
    roles: list[Role]


class UserPageOut(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    page_size: int
