from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.users import Role, User
from app.infrastructure.db.models.user import UserModel, UserRoleModel


def to_domain(row: UserModel) -> User:
    return User(
        id=row.id,
        email=row.email,
        password_hash=row.password_hash,
        full_name=row.full_name,
        preferred_locale=row.preferred_locale,
        preferred_city=row.preferred_city,
        is_active=row.is_active,
        email_verified_at=row.email_verified_at,
        created_at=row.created_at,
        roles=frozenset(Role(r.role) for r in row.roles),
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _row(self, user_id: UUID) -> UserModel:
        row = self._session.get(UserModel, user_id)
        if row is None:
            raise NotFoundError("User not found.", code="user_not_found")
        return row

    def get(self, user_id: UUID) -> User | None:
        row = self._session.get(UserModel, user_id)
        return to_domain(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        row = self._session.scalar(select(UserModel).where(UserModel.email == email))
        return to_domain(row) if row else None

    def add(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                full_name=user.full_name,
                preferred_locale=user.preferred_locale,
                preferred_city=user.preferred_city,
                is_active=user.is_active,
                email_verified_at=user.email_verified_at,
                created_at=user.created_at,
                updated_at=user.created_at,
                roles=[UserRoleModel(role=r.value) for r in sorted(user.roles)],
            )
        )
        try:
            self._session.flush()
        except IntegrityError as exc:  # two sign-ups with the same email at the same moment
            raise ConflictError("An account with this email already exists.", code="email_taken") from exc

    def mark_verified(self, user_id: UUID, at: datetime) -> None:
        self._row(user_id).email_verified_at = at

    def set_password_hash(self, user_id: UUID, password_hash: str) -> None:
        self._row(user_id).password_hash = password_hash

    def update_profile(
        self, user_id: UUID, *, full_name: str, preferred_locale: str, preferred_city: str | None
    ) -> None:
        row = self._row(user_id)
        row.full_name = full_name
        row.preferred_locale = preferred_locale
        row.preferred_city = preferred_city

    def set_roles(self, user_id: UUID, roles: frozenset[Role]) -> None:
        # Keep matching rows and add only the missing ones, so no primary key is deleted
        # and re-inserted in the same flush
        row = self._row(user_id)
        wanted = {r.value for r in roles}
        kept = [r for r in row.roles if r.role in wanted]
        existing = {r.role for r in kept}
        row.roles = kept + [UserRoleModel(role=value) for value in sorted(wanted - existing)]

    def search(self, *, query: str | None, offset: int, limit: int) -> tuple[list[User], int]:
        stmt = select(UserModel)
        if query and query.strip():
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(or_(UserModel.email.ilike(pattern), UserModel.full_name.ilike(pattern)))
        total = self._session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self._session.scalars(stmt.order_by(UserModel.created_at.desc()).offset(offset).limit(limit)).all()
        return [to_domain(r) for r in rows], total
