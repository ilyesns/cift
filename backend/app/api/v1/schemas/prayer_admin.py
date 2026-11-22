from datetime import date

from pydantic import BaseModel

from app.application.timetable_import import ImportPreview, Issue
from app.domain.prayer import PRAYER_ORDER, OfficialDay


class IssueOut(BaseModel):
    code: str
    message: str
    row: int | None
    column: str | None

    @classmethod
    def from_issue(cls, issue: Issue) -> "IssueOut":
        return cls(code=issue.code, message=issue.message, row=issue.row, column=issue.column)


class TimetableDayOut(BaseModel):
    day: date
    times: dict[str, str]  # {"fajr": "05:30", ...}
    hijri: str | None  # "21/5/1448"

    @classmethod
    def from_day(cls, day: OfficialDay) -> "TimetableDayOut":
        hijri = day.hijri
        return cls(
            day=day.day,
            times={p.value: day.times[p].strftime("%H:%M") for p in PRAYER_ORDER if p in day.times},
            hijri=f"{hijri.day}/{hijri.month}/{hijri.year}" if hijri else None,
        )


class TimetablePreviewOut(BaseModel):
    ok: bool
    start: date | None
    end: date | None
    day_count: int
    errors: list[IssueOut]
    warnings: list[IssueOut]
    days: list[TimetableDayOut]

    @classmethod
    def from_preview(cls, preview: ImportPreview) -> "TimetablePreviewOut":
        return cls(
            ok=preview.ok,
            start=preview.start,
            end=preview.end,
            day_count=len(preview.days),
            errors=[IssueOut.from_issue(i) for i in preview.errors],
            warnings=[IssueOut.from_issue(i) for i in preview.warnings],
            days=[TimetableDayOut.from_day(d) for d in preview.days],
        )


class TimetableImportOut(BaseModel):
    imported: int
    start: date | None
    end: date | None
    warnings: list[IssueOut]
