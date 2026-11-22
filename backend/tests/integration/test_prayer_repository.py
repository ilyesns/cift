from datetime import date, time

import pytest
from sqlalchemy import text

from app.domain.exceptions import NotFoundError
from app.domain.prayer import HijriDate, OfficialDay, Prayer
from app.infrastructure.db.database import Database
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

pytestmark = pytest.mark.integration

# Far-future dates, so the test never touches real timetable rows
DAY_1 = date(2099, 1, 1)
DAY_2 = date(2099, 1, 2)


@pytest.fixture(autouse=True)
def cleanup(database: Database):
    yield
    with database.engine.begin() as conn:
        conn.execute(text("DELETE FROM prayer_days WHERE day >= '2099-01-01'"))


def uow(database: Database) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(database.session_factory)


def test_florence_is_seeded(database: Database):
    with uow(database) as u:
        city = u.prayer.get_city("firenze")
        settings = u.prayer.get_settings("firenze")

    assert city is not None
    assert city.name("ar") == "فلورنسا"
    assert city.timezone == "Europe/Rome"
    assert settings.iqama_offsets == {
        Prayer.FAJR: 10,
        Prayer.DHUHR: 10,
        Prayer.ASR: 10,
        Prayer.ISHA: 10,
    }
    assert settings.jumuah_times == (time(12, 0), time(13, 0), time(13, 50))


def test_upsert_inserts_then_replaces(database: Database):
    first = OfficialDay(
        day=DAY_1,
        times={Prayer.FAJR: time(5, 30), Prayer.MAGHRIB: time(17, 6)},
        hijri=HijriDate(day=21, month=5, year=1448),
    )
    with uow(database) as u:
        u.prayer.upsert_days("firenze", [first])
        u.commit()

    corrected = OfficialDay(day=DAY_1, times={Prayer.FAJR: time(5, 31)})
    with uow(database) as u:
        u.prayer.upsert_days("firenze", [corrected])
        u.commit()

    with uow(database) as u:
        days = u.prayer.get_days("firenze", DAY_1, DAY_2)

    assert list(days) == [DAY_1]
    assert days[DAY_1].times == {Prayer.FAJR: time(5, 31)}
    assert days[DAY_1].hijri is None


def test_unknown_city_is_rejected(database: Database):
    with uow(database) as u, pytest.raises(NotFoundError):
        u.prayer.upsert_days("atlantis", [OfficialDay(day=DAY_1, times={})])
