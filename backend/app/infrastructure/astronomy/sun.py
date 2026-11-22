from datetime import date
from zoneinfo import ZoneInfo

from astral import Observer
from astral.sun import sunrise, sunset

from app.domain.prayer import City, SunTimes


class AstralSunCalculator:
    """Standard sunrise and sunset: the sun's upper edge touching the horizon,
    corrected for atmospheric refraction (0.833°)."""

    def sun_times(self, city: City, day: date) -> SunTimes:
        observer = Observer(latitude=city.latitude, longitude=city.longitude, elevation=city.elevation)
        tz = ZoneInfo(city.timezone)
        return SunTimes(
            sunrise=sunrise(observer, day, tzinfo=tz),
            sunset=sunset(observer, day, tzinfo=tz),
        )
