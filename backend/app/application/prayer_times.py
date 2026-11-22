from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.application.security import utcnow
from app.domain.exceptions import NotFoundError, ValidationFailedError
from app.domain.ports.prayer import SunCalculator
from app.domain.ports.unit_of_work import UnitOfWork
from app.domain.prayer import (
    CALCULATED_PRAYERS,
    PRAYER_ORDER,
    City,
    HijriDate,
    OfficialDay,
    Prayer,
    PrayerSettings,
    TimeSource,
    round_sun_times,
)

MAX_RANGE_DAYS = 62
FRIDAY = 4  # date.weekday()


@dataclass(frozen=True, slots=True)
class PrayerEntry:
    prayer: Prayer
    adhan: datetime
    iqama: datetime | None
    source: TimeSource


@dataclass(frozen=True, slots=True)
class DaySchedule:
    day: date
    prayers: tuple[PrayerEntry, ...]
    hijri: HijriDate | None
    jumuah: tuple[datetime, ...]

    @property
    def complete(self) -> bool:
        return len(self.prayers) == len(PRAYER_ORDER)


@dataclass(frozen=True, slots=True)
class Timetable:
    city: City
    days: list[DaySchedule]


class PrayerTimesService:
    """Official times first; Churuq and Maghrib calculated when the sheet hasn't been imported."""

    def __init__(
        self,
        *,
        uow: UnitOfWork,
        sun: SunCalculator,
        now: Callable[[], datetime] = utcnow,
    ) -> None:
        self._uow = uow
        self._sun = sun
        self._now = now

    def cities(self) -> list[City]:
        with self._uow as uow:
            return uow.prayer.list_cities()

    def timetable(self, city_slug: str, start: date | None = None, end: date | None = None) -> Timetable:
        with self._uow as uow:
            city = uow.prayer.get_city(city_slug)
            if city is None:
                raise NotFoundError("City not found.", code="city_not_found")

            # "Today" is the city's date, not the server's
            start = start or self._now().astimezone(ZoneInfo(city.timezone)).date()
            end = end or start
            if end < start:
                raise ValidationFailedError("'to' must not be before 'from'.", code="invalid_range")
            if (end - start).days + 1 > MAX_RANGE_DAYS:
                raise ValidationFailedError(f"Ask for at most {MAX_RANGE_DAYS} days at a time.", code="range_too_long")

            settings = uow.prayer.get_settings(city_slug)
            official = uow.prayer.get_days(city_slug, start, end)

        days = []
        for offset in range((end - start).days + 1):
            day = start + timedelta(days=offset)
            days.append(self._schedule(city, settings, day, official.get(day)))
        return Timetable(city=city, days=days)

    def _schedule(self, city: City, settings: PrayerSettings, day: date, official: OfficialDay | None) -> DaySchedule:
        tz = ZoneInfo(city.timezone)
        calculated: tuple[datetime, datetime] | None = None
        entries: list[PrayerEntry] = []

        for prayer in PRAYER_ORDER:
            if official is not None and prayer in official.times:
                adhan = datetime.combine(day, official.times[prayer], tzinfo=tz)
                source = TimeSource.OFFICIAL
            elif prayer in CALCULATED_PRAYERS:
                if calculated is None:
                    calculated = round_sun_times(self._sun.sun_times(city, day))
                if prayer is Prayer.SUNRISE:
                    adhan = calculated[0] + timedelta(minutes=settings.sunrise_adjustment)
                else:
                    adhan = calculated[1] + timedelta(minutes=settings.maghrib_adjustment)
                source = TimeSource.CALCULATED
            else:
                continue  # Fajr, Dhuhr, Asr, Isha are never guessed

            gap = settings.iqama_offsets.get(prayer)
            iqama = adhan + timedelta(minutes=gap) if gap is not None else None
            entries.append(PrayerEntry(prayer=prayer, adhan=adhan, iqama=iqama, source=source))

        jumuah: tuple[datetime, ...] = ()
        if day.weekday() == FRIDAY:
            jumuah = tuple(datetime.combine(day, t, tzinfo=tz) for t in settings.jumuah_times)

        return DaySchedule(
            day=day,
            prayers=tuple(entries),
            hijri=official.hijri if official else None,
            jumuah=jumuah,
        )
