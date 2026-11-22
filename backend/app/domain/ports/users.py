from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.users import Role, User


class UserRepository(Protocol):
    def get(self, user_id: UUID) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def add(self, user: User) -> None:
        """Raises ConflictError(code="email_taken") if the email exists."""
        ...

    def mark_verified(self, user_id: UUID, at: datetime) -> None: ...

    def set_password_hash(self, user_id: UUID, password_hash: str) -> None: ...

    def update_profile(
        self, user_id: UUID, *, full_name: str, preferred_locale: str, preferred_city: str | None
    ) -> None: ...

    def set_roles(self, user_id: UUID, roles: frozenset[Role]) -> None: ...

    def search(self, *, query: str | None, offset: int, limit: int) -> tuple[list[User], int]: ...
