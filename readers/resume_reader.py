"""Turns a resume file into a Resume, whatever its format.

Two jobs, both format-agnostic:
1. Dispatch: "resume.xlsx" -> readers/reader_xlsx.py -> its read() function.
2. Shared logic: turn the plain tables that read() returns into a Resume.

Adding a file type = adding readers/reader_<extension>.py with a read()
function. Nothing in this file changes.

Problems with the file's contents raise ResumeDataError. The message gets
more specific as it travels up:
  _required_text      "'title' is empty"
  _build_each         "Employment tab, row 3: 'title' is empty"
"""

import importlib
import pkgutil
from collections.abc import Callable
from dataclasses import fields
from datetime import date, datetime
from pathlib import Path
from typing import TypeVar

import readers
from resume import Education, Employment, Resume, UserGeneral, UserPersonal
from util.errors import PluginError, ResumeDataError, UnsupportedFileError

# The contract every reader_*.read() returns. Plain Python types only, so
# nothing library-specific (openpyxl, csv, ...) leaks out of a reader.
Cell = str | int | float | datetime | None  # None means "empty cell"
Row = tuple[Cell, ...]
Table = tuple[Row, ...]  # header row first; columns are matched by name
Tables = tuple[Table, Table, Table, Table]  # general, personal, employment, education

ReadFunction = Callable[[Path], Tables]
Record = dict[str, Cell]  # one row, keyed by header: {"employer": "Acme", ...}
T = TypeVar("T")  # "whatever type the build function returns"


def read_resume(path: Path) -> Resume:
    read = _reader_for(path)
    return build_resume(read(path))


def build_resume(tables: Tables) -> Resume:
    # Separate from read_resume so it can be tested with plain tuples, no files.
    general, personal, employment, education = tables
    personal_records = _records(personal)
    if not personal_records:
        raise ResumeDataError("The Personal tab has a header row but no data row.")
    return Resume(
        personal=_personal_from(personal_records[0]),
        general=_general_from(general),
        employment=_build_each("Employment", employment, _employment_from),
        education=_build_each("Education", education, _education_from),
    )


def supported_extensions() -> list[str]:
    # The reader files themselves are the list: readers/reader_xlsx.py -> ["xlsx"]
    return [
        module.name.removeprefix("reader_")
        for module in pkgutil.iter_modules(readers.__path__)
        if module.name.startswith("reader_")
    ]


def _reader_for(path: Path) -> ReadFunction:
    extension = path.suffix.lstrip(".").lower()  # "My Resume.XLSX" -> "xlsx"
    module_name = f"readers.reader_{extension}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        # Two different problems raise the same exception type, so check WHICH
        # module was missing:
        #   error.name == "readers.reader_pdf"  -> no reader for .pdf
        #   error.name == "openpyxl"            -> the reader exists, its library doesn't
        if error.name == module_name:
            supported = ", ".join(f".{ext}" for ext in supported_extensions())
            kind = f".{extension} files" if extension else "Files without an extension"
            raise UnsupportedFileError(
                f"{path.name}: {kind} aren't supported. Supported: {supported}"
            ) from None
        raise PluginError(f"{module_name} needs '{error.name}', which isn't installed.") from None
    read = getattr(module, "read", None)
    if not callable(read):
        raise PluginError(f"{module_name} has no read(path) function.")
    return read


# --- tables -> records -------------------------------------------------------


def _records(table: Table) -> list[Record]:
    # Pair every data row with the header row, so columns are found by NAME.
    # Moving or adding columns in the sheet can't put a value in the wrong field.
    if not table:
        return []  # an empty sheet
    header, *rows = table
    names = [_to_text(name) for name in header]
    # strict=False: a row may be shorter than the header (trailing empty cells).
    return [{name: value for name, value in zip(names, row, strict=False) if name} for row in rows]


def _column(table: Table, name: str) -> list[str]:
    # A list-style column (e.g. "skills"): one item per row, blanks skipped.
    #   skills | certifications        ->  skills = ["Python", "SQL"]
    #   Python | AWS CCP
    #   SQL    | (empty)
    items = (_to_text(record.get(name)) for record in _records(table))
    return [item for item in items if item]


# --- records -> dataclasses --------------------------------------------------


def _build_each(section: str, table: Table, build: Callable[[Record], T]) -> list[T]:
    # Adds WHERE to an error that only knows WHAT: "'title' is empty" becomes
    # "Employment tab, row 3: 'title' is empty". Row 1 is the header, and
    # blank rows were already dropped, so this is the row counting only filled rows.
    built = []
    for row_number, record in enumerate(_records(table), start=2):
        try:
            built.append(build(record))
        except ResumeDataError as error:
            raise ResumeDataError(f"{section} tab, row {row_number}: {error.message}") from None
    return built


def _personal_from(record: Record) -> UserPersonal:
    # Every UserPersonal field is optional text, so build it generically:
    # keep only columns whose header is a real field name.
    known = {f.name for f in fields(UserPersonal)}
    return UserPersonal(**{name: _to_text(value) for name, value in record.items() if name in known})


def _general_from(table: Table) -> UserGeneral:
    clearance = _column(table, "clearance")
    return UserGeneral(
        skills=_column(table, "skills"),
        certifications=_column(table, "certifications"),
        projects=_column(table, "projects"),
        websites=_column(table, "websites"),
        clearance=clearance[0] if clearance else None,
    )


def _employment_from(record: Record) -> Employment:
    return Employment(
        employer=_required_text(record, "employer"),
        title=_required_text(record, "title"),
        location=_required_text(record, "location"),
        start_date=_required_date(record, "start_date"),
        end_date=_optional_date(record, "end_date"),
        responsibilities=_lines(record.get("responsibilities")),
        supervisor=_to_text(record.get("supervisor")),
        supervisor_contact=_to_text(record.get("supervisor_contact")),
    )


def _education_from(record: Record) -> Education:
    return Education(
        school=_required_text(record, "school"),
        degree=_required_text(record, "degree"),
        major=_required_text(record, "major"),
        start_date=_required_date(record, "start_date"),
        end_date=_optional_date(record, "end_date"),
        gpa=_to_text(record.get("gpa")),
        minor=_to_text(record.get("minor")),
    )


# --- single-value conversions ------------------------------------------------


def _to_text(value: Cell) -> str | None:
    text = None if value is None else str(value).strip()
    return text or None  # "" and "   " count as empty


def _optional_date(record: Record, name: str) -> date | None:
    value = record.get(name)
    match value:
        case None:
            return None
        case datetime():  # check datetime first: a datetime is also a date
            return value.date()
        case str():
            try:
                return date.fromisoformat(value.strip())  # "2021-06-01"
            except ValueError:
                pass
    raise ResumeDataError(f"'{name}' should be a date (an Excel date or YYYY-MM-DD), not {value!r}")


def _lines(value: Cell) -> list[str]:
    # A multi-line cell (Alt+Enter in Excel) becomes one list item per line.
    text = _to_text(value)
    return [line.strip() for line in text.splitlines() if line.strip()] if text else []


def _required_text(record: Record, name: str) -> str:
    text = _to_text(record.get(name))
    if text is None:
        raise ResumeDataError(f"'{name}' is empty")
    return text


def _required_date(record: Record, name: str) -> date:
    value = _optional_date(record, name)
    if value is None:
        raise ResumeDataError(f"'{name}' is empty")
    return value
