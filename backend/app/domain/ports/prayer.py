from collections.abc import Sequence
from datetime import date
from typing import Protocol

from app.domain.prayer import City, OfficialDay, PrayerSettings, SunTimes


class SunCalculator(Protocol):
    def sun_times(self, city: City, day: date) -> SunTimes:
        """Exact sunrise and sunset for the city, in the city's local time zone."""
        ...


class PrayerRepository(Protocol):
    def list_cities(self) -> list[City]: ...

    def get_city(self, slug: str) -> City | None: ...

    def get_settings(self, city_slug: str) -> PrayerSettings: ...

    def get_days(self, city_slug: str, start: date, end: date) -> dict[date, OfficialDay]:
        """Official rows between start and end, both included. Missing days are simply absent."""
        ...

    def upsert_days(self, city_slug: str, days: Sequence[OfficialDay]) -> int:
        """Insert new days or replace existing ones. Raises NotFoundError for an unknown city."""
        ...
