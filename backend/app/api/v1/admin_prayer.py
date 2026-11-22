from typing import Annotated

from fastapi import APIRouter, File, Response, UploadFile

from app.api.deps import AdminUser, TimetableImportServiceDep
from app.api.v1.schemas.prayer_admin import IssueOut, TimetableImportOut, TimetablePreviewOut
from app.application.timetable_import import SheetRow
from app.infrastructure.files.spreadsheet import MAX_UPLOAD_BYTES, read_rows

router = APIRouter(prefix="/admin/prayer", tags=["admin: prayer times"])

TimetableFile = Annotated[UploadFile, File(description="Timetable as .csv or .xlsx")]

TEMPLATE = (
    "date,hijri_day,hijri_month,hijri_year,fajr,sunrise,dhuhr,asr,maghrib,isha\n"
    "2026-11-01,21,5,1448,5:30,6:51,11:59,14:41,17:06,18:26\n"
    "2026-11-02,22,5,1448,5:31,6:52,11:59,14:40,17:04,18:25\n"
)


def _rows(file: UploadFile) -> list[SheetRow]:
    # Read one byte past the limit so "too large" can be detected without loading huge files
    return read_rows(file.filename or "", file.file.read(MAX_UPLOAD_BYTES + 1))


@router.get("/timetable-template.csv")
def timetable_template(_: AdminUser) -> Response:
    return Response(
        content=TEMPLATE,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="timetable-template.csv"'},
    )


@router.post("/{city}/timetable/preview", response_model=TimetablePreviewOut)
def preview_timetable(
    city: str, file: TimetableFile, _: AdminUser, service: TimetableImportServiceDep
) -> TimetablePreviewOut:
    return TimetablePreviewOut.from_preview(service.preview(city, _rows(file)))


@router.post("/{city}/timetable", response_model=TimetableImportOut)
def import_timetable(
    city: str, file: TimetableFile, _: AdminUser, service: TimetableImportServiceDep
) -> TimetableImportOut:
    preview = service.import_days(city, _rows(file))
    return TimetableImportOut(
        imported=len(preview.days),
        start=preview.start,
        end=preview.end,
        warnings=[IssueOut.from_issue(w) for w in preview.warnings],
    )
