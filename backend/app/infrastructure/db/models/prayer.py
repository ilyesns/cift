import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, IdMixin, TimestampMixin


class CityModel(IdMixin, TimestampMixin, Base):
    __tablename__ = "cities"

    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name_it: Mapped[str] = mapped_column(String(120))
    name_ar: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    elevation: Mapped[float] = mapped_column(Float, server_default="0")
    timezone: Mapped[str] = mapped_column(String(60), server_default="Europe/Rome")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())


class PrayerDayModel(IdMixin, Base):
    __tablename__ = "prayer_days"
    __table_args__ = (UniqueConstraint("city_id", "day", name="uq_prayer_days_city_id_day"),)

    city_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)

    # Local clock time, exactly as printed on the sheet
    fajr: Mapped[time | None] = mapped_column(Time)
    sunrise: Mapped[time | None] = mapped_column(Time)
    dhuhr: Mapped[time | None] = mapped_column(Time)
    asr: Mapped[time | None] = mapped_column(Time)
    maghrib: Mapped[time | None] = mapped_column(Time)
    isha: Mapped[time | None] = mapped_column(Time)

    hijri_day: Mapped[int | None] = mapped_column(SmallInteger)
    hijri_month: Mapped[int | None] = mapped_column(SmallInteger)
    hijri_year: Mapped[int | None] = mapped_column(SmallInteger)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PrayerSettingsModel(Base):
    __tablename__ = "prayer_settings"

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cities.id", ondelete="CASCADE"), primary_key=True
    )
    iqama_fajr: Mapped[int | None] = mapped_column(SmallInteger)
    iqama_dhuhr: Mapped[int | None] = mapped_column(SmallInteger)
    iqama_asr: Mapped[int | None] = mapped_column(SmallInteger)
    iqama_maghrib: Mapped[int | None] = mapped_column(SmallInteger)
    iqama_isha: Mapped[int | None] = mapped_column(SmallInteger)
    sunrise_adjustment: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    maghrib_adjustment: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    jumuah_times: Mapped[list[time]] = mapped_column(ARRAY(Time), server_default="{}")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
