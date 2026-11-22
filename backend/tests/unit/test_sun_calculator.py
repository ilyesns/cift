from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.domain.prayer import City
from app.infrastructure.astronomy.sun import AstralSunCalculator

ROME = ZoneInfo("Europe/Rome")
FLORENCE = City(slug="firenze", latitude=43.7696, longitude=11.2558, timezone="Europe/Rome")

# Florence, local time. Includes both 2026 daylight-saving switches (29 March, 25 October).
REFERENCE = [
    (date(2026, 6, 21), "05:33:18", "21:00:16"),
    (date(2026, 12, 21), "07:45:52", "16:40:11"),
    (date(2026, 3, 28), "06:04:13", "18:36:34"),
    (date(2026, 3, 29), "07:02:25", "19:37:47"),
    (date(2026, 10, 24), "07:40:38", "18:17:00"),
    (date(2026, 10, 25), "06:41:54", "17:15:29"),
]


def local(day: date, hhmmss: str) -> datetime:
    return datetime.combine(day, time.fromisoformat(hhmmss), tzinfo=ROME)


@pytest.mark.parametrize(("day", "sunrise", "sunset"), REFERENCE)
def test_florence_matches_reference(day: date, sunrise: str, sunset: str):
    sun = AstralSunCalculator().sun_times(FLORENCE, day)

    assert abs(sun.sunrise - local(day, sunrise)) <= timedelta(minutes=1)
    assert abs(sun.sunset - local(day, sunset)) <= timedelta(minutes=1)


def test_daylight_saving_switch_is_applied():
    calculator = AstralSunCalculator()
    before = calculator.sun_times(FLORENCE, date(2026, 3, 28)).sunrise
    after = calculator.sun_times(FLORENCE, date(2026, 3, 29)).sunrise

    assert before.utcoffset() == timedelta(hours=1)
    assert after.utcoffset() == timedelta(hours=2)
