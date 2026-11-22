from collections.abc import Sequence
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.domain.exceptions import NotFoundError
from app.domain.prayer import (
    PRAYER_ORDER,
    City,
    HijriDate,
    OfficialDay,
    Prayer,
    PrayerSettings,
)
from app.infrastructure.db.models.prayer import CityModel, PrayerDayModel, PrayerSettingsModel

# Column names on prayer_days are the Prayer values: "fajr", "sunrise", ...
TIME_COLUMNS = [p.value for p in PRAYER_ORDER]
HIJRI_COLUMNS = ["hijri_day", "hijri_month", "hijri_year"]
IQAMA_PRAYERS = [p for p in PRAYER_ORDER if p is not Prayer.SUNRISE]


def _city(row: CityModel) -> City:
    return City(
        slug=row.slug,
        latitude=row.latitude,
        longitude=row.longitude,
        timezone=row.timezone,
        elevation=row.elevation,
        names={"it": row.name_it, "ar": row.name_ar, "en": row.name_en},
    )


def _day(row: PrayerDayModel) -> OfficialDay:
    times = {p: getattr(row, p.value) for p in PRAYER_ORDER if getattr(row, p.value) is not None}
    hijri = None
    if row.hijri_day and row.hijri_month and row.hijri_year:
        hijri = HijriDate(day=row.hijri_day, month=row.hijri_month, year=row.hijri_year)
    return OfficialDay(day=row.day, times=times, hijri=hijri)


class SqlAlchemyPrayerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _city_id(self, slug: str) -> UUID:
        city_id = self._session.scalar(select(CityModel.id).where(CityModel.slug == slug))
        if city_id is None:
            raise NotFoundError("City not found.", code="city_not_found")
        return city_id

    def list_cities(self) -> list[City]:
        rows = self._session.scalars(
            select(CityModel).where(CityModel.is_active).order_by(CityModel.name_it)
        )
        return [_city(row) for row in rows]

    def get_city(self, slug: str) -> City | None:
        row = self._session.scalar(
            select(CityModel).where(CityModel.slug == slug, CityModel.is_active)
        )
        return _city(row) if row else None

    def get_settings(self, city_slug: str) -> PrayerSettings:
        row = self._session.scalar(
            select(PrayerSettingsModel)
            .join(CityModel, CityModel.id == PrayerSettingsModel.city_id)
            .where(CityModel.slug == city_slug)
        )
        if row is None:
            return PrayerSettings(iqama_offsets={}, jumuah_times=())
        offsets = {
            p: getattr(row, f"iqama_{p.value}")
            for p in IQAMA_PRAYERS
            if getattr(row, f"iqama_{p.value}") is not None
        }
        return PrayerSettings(
            iqama_offsets=offsets,
            jumuah_times=tuple(row.jumuah_times or ()),
            sunrise_adjustment=row.sunrise_adjustment,
            maghrib_adjustment=row.maghrib_adjustment,
        )

    def get_days(self, city_slug: str, start: date, end: date) -> dict[date, OfficialDay]:
        rows = self._session.scalars(
            select(PrayerDayModel)
            .join(CityModel, CityModel.id == PrayerDayModel.city_id)
            .where(CityModel.slug == city_slug, PrayerDayModel.day.between(start, end))
            .order_by(PrayerDayModel.day)
        )
        return {row.day: _day(row) for row in rows}

    def upsert_days(self, city_slug: str, days: Sequence[OfficialDay]) -> int:
        if not days:
            return 0
        city_id = self._city_id(city_slug)
        values = [
            {
                "id": uuid4(),
                "city_id": city_id,
                "day": d.day,
                **{p.value: d.times.get(p) for p in PRAYER_ORDER},
                "hijri_day": d.hijri.day if d.hijri else None,
                "hijri_month": d.hijri.month if d.hijri else None,
                "hijri_year": d.hijri.year if d.hijri else None,
            }
            for d in days
        ]
        stmt = pg_insert(PrayerDayModel).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_prayer_days_city_id_day",
            set_={
                **{col: stmt.excluded[col] for col in TIME_COLUMNS + HIJRI_COLUMNS},
                "updated_at": func.now(),
            },
        )
        self._session.execute(stmt)
        return len(values)