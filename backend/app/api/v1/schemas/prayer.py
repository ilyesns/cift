from datetime import date, datetime

from pydantic import BaseModel

from app.application.prayer_times import DaySchedule, Timetable
from app.domain.prayer import City, Prayer, TimeSource


class CityOut(BaseModel):
    slug: str
    name: str
    timezone: str

    @classmethod
    def from_domain(cls, city: City, locale: str) -> "CityOut":
        return cls(slug=city.slug, name=city.name(locale), timezone=city.timezone)


class HijriOut(BaseModel):
    day: int
    month: int  # 1 = Muharram … 12 = Dhu al-Hijjah
    year: int


class PrayerOut(BaseModel):
    prayer: Prayer
    adhan: datetime
    iqama: datetime | None
    source: TimeSource


class DayOut(BaseModel):
    day: date
    weekday: int  # 1 = Monday … 7 = Sunday
    hijri: HijriOut | None
    complete: bool
    prayers: list[PrayerOut]
    jumuah: list[datetime]

    @classmethod
    def from_domain(cls, schedule: DaySchedule) -> "DayOut":
        hijri = schedule.hijri
        return cls(
            day=schedule.day,
            weekday=schedule.day.isoweekday(),
            hijri=HijriOut(day=hijri.day, month=hijri.month, year=hijri.year) if hijri else None,
            complete=schedule.complete,
            prayers=[
                PrayerOut(prayer=p.prayer, adhan=p.adhan, iqama=p.iqama, source=p.source) for p in schedule.prayers
            ],
            jumuah=list(schedule.jumuah),
        )


class TimetableOut(BaseModel):
    city: CityOut
    days: list[DayOut]

    @classmethod
    def from_domain(cls, timetable: Timetable, locale: str) -> "TimetableOut":
        return cls(
            city=CityOut.from_domain(timetable.city, locale),
            days=[DayOut.from_domain(d) for d in timetable.days],
        )
