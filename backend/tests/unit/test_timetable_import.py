from datetime import date, time

import pytest

from app.application.timetable_import import ImportPreview, validate_timetable
from app.domain.exceptions import ValidationFailedError
from app.domain.prayer import City, HijriDate, Prayer
from app.infrastructure.astronomy.sun import AstralSunCalculator
from app.infrastructure.files.spreadsheet import read_rows

FLORENCE = City(slug="firenze", latitude=43.7696, longitude=11.2558, timezone="Europe/Rome")
HEADER = "date,hijri_day,hijri_month,hijri_year,fajr,sunrise,dhuhr,asr,maghrib,isha"
NOV_09 = "2026-11-09,29,5,1448,5:39,7:01,11:59,14:33,16:56,18:18"
NOV_10 = "2026-11-10,30,5,1448,5:41,7:02,11:59,14:32,16:54,18:17"
NOV_11 = "2026-11-11,1,6,1448,5:42,7:04,11:59,14:31,16:53,18:16"


def validate_csv(text: str) -> ImportPreview:
    rows = read_rows("timetable.csv", text.encode())
    return validate_timetable(rows, FLORENCE, AstralSunCalculator())


def check(*lines: str, sep: str = ",") -> ImportPreview:
    return validate_csv("\n".join([HEADER, *lines]).replace(",", sep))


def issues(preview: ImportPreview) -> list[tuple[str, int | None, str | None]]:
    return [(i.code, i.row, i.column) for i in preview.errors]


def test_valid_rows_across_a_hijri_month_change():
    preview = check(NOV_09, NOV_10, NOV_11)

    assert preview.ok
    assert (preview.start, preview.end) == (date(2026, 11, 9), date(2026, 11, 11))
    assert preview.days[0].times[Prayer.MAGHRIB] == time(16, 56)
    assert preview.days[2].hijri == HijriDate(day=1, month=6, year=1448)
    assert preview.warnings == []


def test_semicolon_csv_from_italian_excel():
    assert check(NOV_09, NOV_10, sep=";").ok


def test_column_names_from_the_mosque_sheet():
    preview = validate_csv("data,fajer,churuoq,douhr,aser,maghreb,eshaa\n09/11/2026,5:39,7:01,11:59,14:33,16:56,18:18")
    assert preview.ok
    assert preview.days[0].day == date(2026, 11, 9)
    assert preview.days[0].hijri is None


def test_missing_column():
    preview = validate_csv("date,fajr,sunrise,dhuhr,asr,maghrib\n2026-11-09,5:39,7:01,11:59,14:33,16:56")
    assert issues(preview) == [("missing_column", None, "isha")]


def test_invalid_time_and_wrong_order_point_to_the_cell():
    preview = check(
        "2026-11-09,29,5,1448,5:39,7:61,11:59,14:33,16:56,18:18",
        "2026-11-10,30,5,1448,5:41,7:02,11:59,14:32,18:54,18:17",
    )
    assert ("invalid_time", 2, "sunrise") in issues(preview)
    assert ("times_out_of_order", 3, "isha") in issues(preview)
    assert not preview.ok


def test_duplicate_and_missing_dates():
    preview = check(NOV_09, NOV_09, NOV_11)
    assert {code for code, _, _ in issues(preview)} == {"duplicate_date", "missing_dates"}


def test_hijri_month_can_end_on_day_29():
    assert check(NOV_09, "2026-11-10,1,6,1448,5:41,7:02,11:59,14:32,16:54,18:17").ok


def test_hijri_must_continue_day_by_day():
    preview = check(NOV_10, "2026-11-11,2,6,1448,5:42,7:04,11:59,14:31,16:53,18:16")
    assert issues(preview) == [("hijri_not_continuous", 3, "hijri_day")]


def test_sunrise_typo_is_a_warning_not_an_error():
    preview = check("2026-11-09,29,5,1448,5:39,8:01,11:59,14:33,16:56,18:18")
    assert preview.ok
    assert [(w.code, w.column) for w in preview.warnings] == [("far_from_calculation", "sunrise")]


def test_unsupported_file_type():
    with pytest.raises(ValidationFailedError) as exc:
        read_rows("timetable.pdf", b"%PDF")
    assert exc.value.code == "unsupported_file"
