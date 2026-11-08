"""Import every ORM model module here so Alembic autogenerate sees it.

Sprint 1 example:
    from app.infrastructure.db.models.user import UserModel  # noqa: F401
"""

from app.infrastructure.db.base import Base

__all__ = ["Base"]
