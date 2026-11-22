"""Turn an uploaded CSV or Excel file into plain rows. No timetable rules here."""

import csv
import io
from typing import Any

from openpyxl import load_workbook

from app.application.timetable_import import SheetRow
from app.domain.exceptions import ValidationFailedError

MAX_UPLOAD_BYTES = 1_000_000


def read_rows(filename: str, content: bytes) -> list[SheetRow]:
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValidationFailedError("The file is larger than 1 MB.", code="file_too_large")
    name = filename.lower()
    if name.endswith(".csv"):
        return _read_csv(content)
    if name.endswith(".xlsx"):
        return _read_xlsx(content)
    raise ValidationFailedError("Upload a .csv or .xlsx file.", code="unsupported_file")


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _decode(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")  # "CSV UTF-8" from Excel starts with a BOM
    except UnicodeDecodeError:
        return content.decode("cp1252")  # plain "CSV" from Excel on Windows


def _read_csv(content: bytes) -> list[SheetRow]:
    text = _decode(content)
    try:
        # Italian Excel saves CSV with ";" instead of ","
        dialect: type[csv.Dialect] | csv.Dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel

    rows: list[SheetRow] = []
    for number, row in enumerate(csv.DictReader(io.StringIO(text), dialect=dialect), start=2):
        cells = {key: value for key, value in row.items() if key is not None}
        if not all(_is_blank(value) for value in cells.values()):
            rows.append((number, cells))
    return rows


def _read_xlsx(content: bytes) -> list[SheetRow]:
    try:
        workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    except Exception as exc:
        raise ValidationFailedError("The Excel file could not be read.", code="unreadable_file") from exc

    try:
        values = workbook.worksheets[0].iter_rows(values_only=True)
        header = next(values, None)
        if header is None:
            return []
        names = [str(cell).strip() if cell is not None else "" for cell in header]

        rows: list[SheetRow] = []
        for number, cells in enumerate(values, start=2):
            if all(_is_blank(cell) for cell in cells):
                continue
            rows.append((number, {name: cell for name, cell in zip(names, cells, strict=False) if name}))
        return rows
    finally:
        workbook.close()
