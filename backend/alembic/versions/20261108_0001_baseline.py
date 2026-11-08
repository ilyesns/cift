"""baseline: extensions used by later sprints

Revision ID: 0001
Revises:
Create Date: 2026-11-08
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # unaccent: accent-insensitive Italian search ("città" matches "citta")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    # pg_trgm: fuzzy matching for search and autocomplete
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS unaccent")
