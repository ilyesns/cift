"""Check an uploaded timetable before it reaches the database.

The rules live here, independent of file format: the spreadsheet reader turns a
CSV or Excel file into rows, and this module decides whether those rows are a
valid timetable.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any

from app.domain.exceptions import NotFoundError, ValidationFailedError
from app.domain.ports.prayer import SunCalculator
from app.domain.ports.unit_of_work import UnitOfWork
from app.domain.prayer import (
    PRAYER_ORDER,
    City,
    HijriDate,
    OfficialDay,
    Prayer,
    round_sun_times,
)

# (spreadsheet row number, {column header: cell value}); the header is row 1
SheetRow = tuple[int, Mapping[str, Any]]

MAX_ROWS = 400
# A published sunrise or Maghrib further than this from the calculation is probably a typo
SUN_TOLERANCE = timedelta(minutes=3)

# Accepted headers -> canonical column. Includes the spellings used on the Florence sheet.
COLUMN_ALIASES: dict[str, str] = {
    "date": "date",
    "data": "date",
    "hijri_day": "hijri_day",
    "hijri_month": "hijri_month",
    "hijri_year": "hijri_year",
    "fajr": "fajr",
    "fajer": "fajr",
    "sunrise": "sunrise",
    "churuq": "sunrise",
    "churuoq": "sunrise",
    "shuruq": "sunrise",
    "alba": "sunrise",
    "dhuhr": "dhuhr",
    "douhr": "dhuhr",
    "duhr": "dhuhr",
    "zuhr": "dhuhr",
    "asr": "asr",
    "aser": "asr",
    "maghrib": "maghrib",
    "maghreb": "maghrib",
    "tramonto": "maghrib",
    "isha": "isha",
    "ishaa": "isha",
    "eshaa": "isha",
}
REQUIRED_COLUMNS = ("date", *(p.value for p in PRAYER_ORDER))
HIJRI_COLUMNS = ("hijri_day", "hijri_month", "hijri_year")

TIME_PATTERN = re.compile(r"^(\d{1,2})[:.](\d{2})(?::\d{2})?$")
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y")


@dataclass(frozen=True, slots=True)
class Issue:
    code: str
    message: str
    row: int | None = None
    column: str | None = None


@dataclass(slots=True)
class ImportPreview:
    days: list[OfficialDay] = field(default_factory=list)
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and bool(self.days)

    @property
    def start(self) -> date | None:
        return self.days[0].day if self.days else None

    @property
    def end(self) -> date | None:
        return self.days[-1].day if self.days else None


class TimetableImportService:
    def __init__(self, *, uow: UnitOfWork, sun: SunCalculator) -> None:
        self._uow = uow
        self._sun = sun

    def preview(self, city_slug: str, rows: Sequence[SheetRow]) -> ImportPreview:
        with self._uow as uow:
            city = uow.prayer.get_city(city_slug)
        if city is None:
            raise NotFoundError("City not found.", code="city_not_found")
        return validate_timetable(rows, city, self._sun)

    def import_days(self, city_slug: str, rows: Sequence[SheetRow]) -> ImportPreview:
        """Validate again (the file may have changed since the preview), then save."""
        preview = self.preview(city_slug, rows)
        if not preview.ok:
            raise ValidationFailedError(
                "The timetable has errors. Fix them and upload it again.",
                code="timetable_invalid",
                details=[asdict(issue) for issue in preview.errors],
            )
        with self._uow as uow:
            uow.prayer.upsert_days(city_slug, preview.days)
            uow.commit()
        return preview


# --- validation --------------------------------------------------------------------


def validate_timetable(rows: Sequence[SheetRow], city: City, sun: SunCalculator) -> ImportPreview:
    result = ImportPreview()
    if not rows:
        result.errors.append(Issue("no_rows", "The file has no data rows."))
        return result
    if len(rows) > MAX_ROWS:
        result.errors.append(Issue("too_many_rows", f"The file has {len(rows)} rows; the limit is {MAX_ROWS}."))
        return result

    present = {canonical_column(name) for name in rows[0][1]}
    missing = [c for c in REQUIRED_COLUMNS if c not in present]
    if missing:
        for column in missing:
            result.errors.append(Issue("missing_column", f"Column '{column}' is missing.", column=column))
        return result

    row_of: dict[date, int] = {}
    for number, raw in rows:
        row = {canonical_column(k): v for k, v in raw.items()}
        day = _parse_row(number, row, row_of, result)
        if day is not None:
            row_of[day.day] = number
            result.days.append(day)
            _compare_with_sun(number, day, city, sun, result)

    result.days.sort(key=lambda d: d.day)
    _check_missing_dates(result, row_of)
    _check_hijri_sequence(result, row_of)
    return result


def _parse_row(
    number: int, row: dict[str | None, Any], row_of: dict[date, int], result: ImportPreview
) -> OfficialDay | None:
    errors_before = len(result.errors)

    day = _parse_date(row.get("date"))
    if day is None:
        result.errors.append(
            Issue(
                "invalid_date",
                f"'{row.get('date')}' is not a date. Use 2026-11-01 or 01/11/2026.",
                row=number,
                column="date",
            )
        )
        return None
    if day in row_of:
        result.errors.append(
            Issue(
                "duplicate_date",
                f"{day.isoformat()} already appears in row {row_of[day]}.",
                row=number,
                column="date",
            )
        )
        return None

    times: dict[Prayer, time] = {}
    for prayer in PRAYER_ORDER:
        value = row.get(prayer.value)
        if _is_blank(value):
            result.errors.append(Issue("missing_time", "This time is empty.", row=number, column=prayer.value))
            continue
        parsed = _parse_time(value)
        if parsed is None:
            result.errors.append(
                Issue(
                    "invalid_time",
                    f"'{value}' is not a time. Use 5:30 or 17:06.",
                    row=number,
                    column=prayer.value,
                )
            )
            continue
        times[prayer] = parsed

    if len(times) == len(PRAYER_ORDER):
        ordered = [times[p] for p in PRAYER_ORDER]
        for earlier, later, prayer in zip(ordered, ordered[1:], PRAYER_ORDER[1:], strict=False):
            if earlier >= later:
                result.errors.append(
                    Issue(
                        "times_out_of_order",
                        f"{prayer.value} ({later:%H:%M}) must be later than the time before it " f"({earlier:%H:%M}).",
                        row=number,
                        column=prayer.value,
                    )
                )
                break

    hijri = _parse_hijri(number, row, result)

    if len(result.errors) > errors_before:
        return None
    return OfficialDay(day=day, times=times, hijri=hijri)


def _parse_hijri(number: int, row: dict[str | None, Any], result: ImportPreview) -> HijriDate | None:
    values = [row.get(column) for column in HIJRI_COLUMNS]
    if all(_is_blank(v) for v in values):
        return None
    day, month, year = (_parse_int(v) for v in values)
    if (
        day is None
        or month is None
        or year is None
        or not 1 <= day <= 30
        or not 1 <= month <= 12
        or not 1400 <= year <= 1600
    ):
        result.errors.append(
            Issue(
                "invalid_hijri",
                "Hijri date needs a day (1-30), a month (1-12) and a year, e.g. 21 / 5 / 1448.",
                row=number,
                column="hijri_day",
            )
        )
        return None
    return HijriDate(day=day, month=month, year=year)


def _compare_with_sun(number: int, day: OfficialDay, city: City, sun: SunCalculator, result: ImportPreview) -> None:
    sunrise, sunset = round_sun_times(sun.sun_times(city, day.day))
    for prayer, calculated in ((Prayer.SUNRISE, sunrise), (Prayer.MAGHRIB, sunset)):
        official = datetime.combine(day.day, day.times[prayer], tzinfo=calculated.tzinfo)
        gap = abs(official - calculated)
        if gap > SUN_TOLERANCE:
            result.warnings.append(
                Issue(
                    "far_from_calculation",
                    f"{prayer.value} {official:%H:%M} is {int(gap.total_seconds() // 60)} minutes "
                    f"from the calculated {calculated:%H:%M}. Check for a typo.",
                    row=number,
                    column=prayer.value,
                )
            )


def _check_missing_dates(result: ImportPreview, row_of: dict[date, int]) -> None:
    if not result.days:
        return
    start, end = result.days[0].day, result.days[-1].day
    missing = [
        start + timedelta(days=offset)
        for offset in range((end - start).days + 1)
        if start + timedelta(days=offset) not in row_of
    ]
    if missing:
        shown = ", ".join(d.isoformat() for d in missing[:10])
        more = f" and {len(missing) - 10} more" if len(missing) > 10 else ""
        result.errors.append(Issue("missing_dates", f"These dates are missing: {shown}{more}.", column="date"))


def _check_hijri_sequence(result: ImportPreview, row_of: dict[date, int]) -> None:
    for previous, current in zip(result.days, result.days[1:], strict=False):
        if previous.hijri is None or current.hijri is None:
            continue
        if current.day - previous.day != timedelta(days=1):
            continue
        if not _follows(previous.hijri, current.hijri):
            result.errors.append(
                Issue(
                    "hijri_not_continuous",
                    f"Hijri {current.hijri.day}/{current.hijri.month}/{current.hijri.year} does "
                    f"not follow {previous.hijri.day}/{previous.hijri.month}/"
                    f"{previous.hijri.year} from the day before.",
                    row=row_of[current.day],
                    column="hijri_day",
                )
            )


def _follows(previous: HijriDate, current: HijriDate) -> bool:
    """Next day in the same month, or day 1 of the next month after day 29 or 30."""
    if (current.month, current.year) == (previous.month, previous.year):
        return current.day == previous.day + 1
    next_month = previous.month % 12 + 1
    next_year = previous.year + (1 if previous.month == 12 else 0)
    return current.day == 1 and previous.day in (29, 30) and (current.month, current.year) == (next_month, next_year)


# --- cell parsing (CSV gives text; Excel gives dates, times and numbers) ----------------


def canonical_column(name: object) -> str | None:
    key = re.sub(r"[\s\-]+", "_", str(name).strip().lower())
    return COLUMN_ALIASES.get(key)


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _parse_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
    return None


def _parse_time(value: object) -> time | None:
    if isinstance(value, datetime):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, int | float) and not isinstance(value, bool) and 0 <= value < 1:
        minutes = round(value * 24 * 60)  # Excel stores a time as a fraction of a day
        return time(minutes // 60, minutes % 60) if minutes < 24 * 60 else None
    if isinstance(value, str):
        match = TIME_PATTERN.match(value.strip())
        if match:
            hour, minute = int(match[1]), int(match[2])
            if hour < 24 and minute < 60:
                return time(hour, minute)
    return None


def _parse_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None
