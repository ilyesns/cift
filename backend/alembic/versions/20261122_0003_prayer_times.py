"""prayer times: cities, official timetable, settings; seeds Florence

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-22
"""

import uuid
from collections.abc import Sequence
from datetime import time

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID = postgresql.UUID(as_uuid=True)
TS = sa.DateTime(timezone=True)
FLORENCE_ID = uuid.UUID("3f6b6a52-6c1d-4b0e-9a8e-0f1c2d3e4f50")


def upgrade() -> None:
    op.create_table(
        "cities",
        sa.Column("id", UUID, nullable=False),
        sa.Column("slug", sa.String(60), nullable=False),
        sa.Column("name_it", sa.String(120), nullable=False),
        sa.Column("name_ar", sa.String(120), nullable=False),
        sa.Column("name_en", sa.String(120), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("elevation", sa.Float(), server_default="0", nullable=False),
        sa.Column("timezone", sa.String(60), server_default="Europe/Rome", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", TS, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", TS, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_cities"),
        sa.UniqueConstraint("slug", name="uq_cities_slug"),
    )

    op.create_table(
        "prayer_days",
        sa.Column("id", UUID, nullable=False),
        sa.Column("city_id", UUID, nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("fajr", sa.Time(), nullable=True),
        sa.Column("sunrise", sa.Time(), nullable=True),
        sa.Column("dhuhr", sa.Time(), nullable=True),
        sa.Column("asr", sa.Time(), nullable=True),
        sa.Column("maghrib", sa.Time(), nullable=True),
        sa.Column("isha", sa.Time(), nullable=True),
        sa.Column("hijri_day", sa.SmallInteger(), nullable=True),
        sa.Column("hijri_month", sa.SmallInteger(), nullable=True),
        sa.Column("hijri_year", sa.SmallInteger(), nullable=True),
        sa.Column("updated_at", TS, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["city_id"], ["cities.id"], name="fk_prayer_days_city_id_cities", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_prayer_days"),
        sa.UniqueConstraint("city_id", "day", name="uq_prayer_days_city_id_day"),
    )

    op.create_table(
        "prayer_settings",
        sa.Column("city_id", UUID, nullable=False),
        sa.Column("iqama_fajr", sa.SmallInteger(), nullable=True),
        sa.Column("iqama_dhuhr", sa.SmallInteger(), nullable=True),
        sa.Column("iqama_asr", sa.SmallInteger(), nullable=True),
        sa.Column("iqama_maghrib", sa.SmallInteger(), nullable=True),
        sa.Column("iqama_isha", sa.SmallInteger(), nullable=True),
        sa.Column("sunrise_adjustment", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("maghrib_adjustment", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column(
            "jumuah_times", postgresql.ARRAY(sa.Time()), server_default="{}", nullable=False
        ),
        sa.Column("updated_at", TS, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["city_id"], ["cities.id"], name="fk_prayer_settings_city_id_cities", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("city_id", name="pk_prayer_settings"),
    )

    # Seed Florence
    cities = sa.table(
        "cities",
        sa.column("id", UUID),
        sa.column("slug", sa.String),
        sa.column("name_it", sa.String),
        sa.column("name_ar", sa.String),
        sa.column("name_en", sa.String),
        sa.column("latitude", sa.Float),
        sa.column("longitude", sa.Float),
        sa.column("timezone", sa.String),
    )
    op.bulk_insert(
        cities,
        [
            {
                "id": FLORENCE_ID,
                "slug": "firenze",
                "name_it": "Firenze",
                "name_ar": "فلورنسا",
                "name_en": "Florence",
                "latitude": 43.7696,
                "longitude": 11.2558,
                "timezone": "Europe/Rome",
            }
        ],
    )

    settings = sa.table(
        "prayer_settings",
        sa.column("city_id", UUID),
        sa.column("iqama_fajr", sa.SmallInteger),
        sa.column("iqama_dhuhr", sa.SmallInteger),
        sa.column("iqama_asr", sa.SmallInteger),
        sa.column("iqama_isha", sa.SmallInteger),
        sa.column("jumuah_times", postgresql.ARRAY(sa.Time())),
    )
    op.bulk_insert(
        settings,
        [
            {
                "city_id": FLORENCE_ID,
                "iqama_fajr": 10,
                "iqama_dhuhr": 10,
                "iqama_asr": 10,
                "iqama_isha": 10,
                "jumuah_times": [time(12, 0), time(13, 0), time(13, 50)],
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("prayer_settings")
    op.drop_table("prayer_days")
    op.drop_table("cities")