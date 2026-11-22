from datetime import datetime
from zoneinfo import ZoneInfo

from app.domain.prayer import (
    SunTimes,
    ceil_minute,
    floor_minute,
    round_minute,
    round_sun_times,
)

ROME = ZoneInfo("Europe/Rome")


def at(hour: int, minute: int, second: int = 0, micro: int = 0) -> datetime:
    return datetime(2026, 6, 21, hour, minute, second, micro, tzinfo=ROME)


def test_floor_drops_seconds():
    assert floor_minute(at(5, 33, 59, 999)) == at(5, 33)


def test_ceil_moves_up_only_when_needed():
    assert ceil_minute(at(21, 0, 1)) == at(21, 1)
    assert ceil_minute(at(21, 0, 0, 1)) == at(21, 1)
    assert ceil_minute(at(21, 0)) == at(21, 0)


def test_round_to_nearest_minute():
    assert round_minute(at(16, 43, 25)) == at(16, 43)
    assert round_minute(at(17, 5, 30)) == at(17, 6)


def test_sunrise_rounds_down_and_sunset_to_nearest():
    rounded = round_sun_times(SunTimes(sunrise=at(7, 18, 20), sunset=at(16, 43, 25)))
    assert rounded == (at(7, 18), at(16, 43))
