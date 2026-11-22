from datetime import UTC, date, datetime, time, timedelta

import pytest

from app.application.prayer_times import DaySchedule, PrayerEntry, PrayerTimesService
from app.domain.exceptions import NotFoundError, ValidationFailedError
from app.domain.prayer import City, HijriDate, OfficialDay, Prayer, PrayerSettings, TimeSource
from tests.fakes import FakeClock, FakeSunCalculator, FakeUnitOfWork

FLORENCE = City(slug="firenze", latitude=43.7696, longitude=11.2558, timezone="Europe/Rome")
SUNDAY = date(2026, 11, 22)
FRIDAY = date(2026, 11, 27)
NOT_IMPORTED = date(2026, 12, 1)

SHEET_ROW = OfficialDay(
    day=SUNDAY,
    times={
        Prayer.FAJR: time(5, 54),
        Prayer.SUNRISE: time(7, 18),
        Prayer.DHUHR: time(12, 1),
        Prayer.ASR: time(14, 24),
        Prayer.MAGHRIB: time(16, 43),
        Prayer.ISHA: time(18, 8),
    },
    hijri=HijriDate(day=12, month=6, year=1448),
)


@pytest.fixture
def uow() -> FakeUnitOfWork:
    fake = FakeUnitOfWork()
    fake.prayer.cities["firenze"] = FLORENCE
    fake.prayer.settings["firenze"] = PrayerSettings(
        iqama_offsets={Prayer.FAJR: 10, Prayer.DHUHR: 10, Prayer.ASR: 10, Prayer.ISHA: 10},
        jumuah_times=(time(12, 0), time(13, 0), time(13, 50)),
        maghrib_adjustment=2,
    )
    fake.prayer.days[("firenze", SUNDAY)] = SHEET_ROW
    return fake


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 11, 22, 10, 0, tzinfo=UTC))


@pytest.fixture
def service(uow: FakeUnitOfWork, clock: FakeClock) -> PrayerTimesService:
    return PrayerTimesService(uow=uow, sun=FakeSunCalculator(), now=clock)


def by_prayer(day: DaySchedule) -> dict[Prayer, PrayerEntry]:
    return {entry.prayer: entry for entry in day.prayers}


def hhmm(moment: datetime | None) -> str | None:
    return moment.strftime("%H:%M") if moment else None


def test_imported_day_uses_the_sheet_and_adds_iqama(service):
    day = service.timetable("firenze", SUNDAY).days[0]
    prayers = by_prayer(day)

    assert day.complete
    assert day.hijri == HijriDate(day=12, month=6, year=1448)
    assert {entry.source for entry in day.prayers} == {TimeSource.OFFICIAL}
    assert (hhmm(prayers[Prayer.FAJR].adhan), hhmm(prayers[Prayer.FAJR].iqama)) == ("05:54", "06:04")
    assert prayers[Prayer.MAGHRIB].iqama is None
    assert prayers[Prayer.SUNRISE].iqama is None
    assert prayers[Prayer.FAJR].adhan.utcoffset() == timedelta(hours=1)
    assert day.jumuah == ()


def test_day_not_imported_shows_only_calculated_churuq_and_maghrib(service):
    day = service.timetable("firenze", NOT_IMPORTED).days[0]
    prayers = by_prayer(day)

    assert not day.complete
    assert set(prayers) == {Prayer.SUNRISE, Prayer.MAGHRIB}
    assert prayers[Prayer.SUNRISE].source is TimeSource.CALCULATED
    assert hhmm(prayers[Prayer.SUNRISE].adhan) == "07:18"  # 07:18:20 rounded down
    assert hhmm(prayers[Prayer.MAGHRIB].adhan) == "16:45"  # 16:43:25 → 16:43, +2 adjustment
    assert day.hijri is None


def test_friday_lists_jumuah_shifts(service):
    day = service.timetable("firenze", FRIDAY).days[0]
    assert [hhmm(t) for t in day.jumuah] == ["12:00", "13:00", "13:50"]


def test_today_follows_florence_not_utc(service, clock):
    clock.current = datetime(2026, 11, 22, 23, 30, tzinfo=UTC)  # 00:30 on the 23rd in Florence
    assert service.timetable("firenze").days[0].day == date(2026, 11, 23)


def test_range_has_one_entry_per_day(service):
    timetable = service.timetable("firenze", date(2026, 11, 1), date(2026, 11, 30))
    assert len(timetable.days) == 30
    assert timetable.days[-1].day == date(2026, 11, 30)


def test_range_limits(service):
    with pytest.raises(ValidationFailedError) as too_long:
        service.timetable("firenze", date(2026, 1, 1), date(2026, 12, 31))
    assert too_long.value.code == "range_too_long"

    with pytest.raises(ValidationFailedError) as backwards:
        service.timetable("firenze", date(2026, 11, 2), date(2026, 11, 1))
    assert backwards.value.code == "invalid_range"


def test_unknown_city(service):
    with pytest.raises(NotFoundError):
        service.timetable("atlantis")
