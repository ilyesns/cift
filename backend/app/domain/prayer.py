from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import StrEnum


class Prayer(StrEnum):
    FAJR = "fajr"
    SUNRISE = "sunrise"
    DHUHR = "dhuhr"
    ASR = "asr"
    MAGHRIB = "maghrib"
    ISHA = "isha"


PRAYER_ORDER: tuple[Prayer, ...] = (
    Prayer.FAJR,
    Prayer.SUNRISE,
    Prayer.DHUHR,
    Prayer.ASR,
    Prayer.MAGHRIB,
    Prayer.ISHA,
)

# Where each time comes from
OFFICIAL_PRAYERS = frozenset({Prayer.FAJR, Prayer.DHUHR, Prayer.ASR, Prayer.ISHA})
CALCULATED_PRAYERS = frozenset({Prayer.SUNRISE, Prayer.MAGHRIB})


class TimeSource(StrEnum):
    OFFICIAL = "official"
    CALCULATED = "calculated"


@dataclass(frozen=True, slots=True)
class City:
    slug: str
    latitude: float
    longitude: float
    timezone: str
    elevation: float = 0.0
    names: dict[str, str] = field(default_factory=dict, compare=False, hash=False)

    def name(self, locale: str) -> str:
        return self.names.get(locale) or self.names.get("it") or self.slug


@dataclass(frozen=True, slots=True)
class SunTimes:
    """Exact (unrounded) local times."""

    sunrise: datetime
    sunset: datetime


def floor_minute(moment: datetime) -> datetime:
    return moment.replace(second=0, microsecond=0)


def ceil_minute(moment: datetime) -> datetime:
    floored = floor_minute(moment)
    return floored if floored == moment else floored + timedelta(minutes=1)


def round_minute(moment: datetime) -> datetime:
    floored = floor_minute(moment)
    if moment - floored >= timedelta(seconds=30):
        return floored + timedelta(minutes=1)
    return floored


def round_sun_times(sun: SunTimes) -> tuple[datetime, datetime]:
    """Rounding that matches the Florence mosque timetable:
    sunrise rounds down, sunset rounds to the nearest minute."""
    return floor_minute(sun.sunrise), round_minute(sun.sunset)


@dataclass(frozen=True, slots=True)
class HijriDate:
    """As published by the association (its own moon-sighting decision), not calculated."""

    day: int
    month: int  # 1 = Muharram … 12 = Dhu al-Hijjah
    year: int


@dataclass(frozen=True, slots=True)
class OfficialDay:
    """One row of the published timetable, in the city's local clock time."""

    day: date
    times: dict[Prayer, time]
    hijri: HijriDate | None = None


@dataclass(frozen=True, slots=True)
class PrayerSettings:
    iqama_offsets: dict[Prayer, int]  # minutes between adhan and iqama
    jumuah_times: tuple[time, ...]
    sunrise_adjustment: int = 0  # minutes added to a calculated sunrise (fallback only)
    maghrib_adjustment: int = 0  # minutes added to a calculated Maghrib (fallback only)
