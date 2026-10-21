"""The shared reader logic (tables -> Resume) and the .xlsx reader."""

from datetime import date, datetime
from pathlib import Path

import openpyxl
import pytest

from readers import resume_reader
from readers.resume_reader import Tables, build_resume, read_resume
from util.errors import PluginError, ResumeDataError, UnsupportedFileError

SAMPLE = Path(__file__).parent.parent / "sample" / "sample_resume.xlsx"

PERSONAL = (("first", "last", "phone"), ("Ada", "Lovelace", "555-010-0199"))
GENERAL = (("skills", "websites"), ("Python", "https://example.com"), ("SQL", None))
EMPLOYMENT = (
    ("employer", "title", "location", "start_date", "end_date", "responsibilities"),
    ("Acme", "Developer", "Remote", datetime(2023, 6, 1), None, "Wrote code\nReviewed code"),
)
EDUCATION = (
    ("school", "degree", "major", "start_date"),
    ("Example University", "BS", "Mathematics", "2019-08-15"),
)


def tables(**overrides) -> Tables:
    parts = {"general": GENERAL, "personal": PERSONAL, "employment": EMPLOYMENT, "education": EDUCATION}
    parts.update(overrides)
    return parts["general"], parts["personal"], parts["employment"], parts["education"]


# --- build_resume: tables -> Resume -------------------------------------------


def test_builds_every_section():
    resume = build_resume(tables())

    assert resume.personal.first == "Ada"
    assert resume.general.skills == ["Python", "SQL"]
    assert resume.general.websites == ["https://example.com"]
    job = resume.employment[0]
    assert job.start_date == date(2023, 6, 1)
    assert job.is_current
    assert job.responsibilities == ["Wrote code", "Reviewed code"]
    assert resume.education[0].start_date == date(2019, 8, 15)  # ISO text works too


def test_columns_are_matched_by_name_not_position():
    reordered = (("phone", "last", "first", "notes"), ("555-010-0199", "Lovelace", "Ada", "ignored"))

    personal = build_resume(tables(personal=reordered)).personal

    assert (personal.first, personal.last, personal.phone) == ("Ada", "Lovelace", "555-010-0199")


def test_blank_required_value_names_the_tab_row_and_field():
    blank_title = (EMPLOYMENT[0], EMPLOYMENT[1], ("Cafe", None, "Here", datetime(2020, 1, 1), None, None))

    with pytest.raises(ResumeDataError, match=r"Employment tab, row 3: 'title' is empty"):
        build_resume(tables(employment=blank_title))


def test_text_that_isnt_a_date_is_reported():
    bad_date = (EDUCATION[0], ("Example University", "BS", "Math", "Fall 2019"))

    with pytest.raises(ResumeDataError, match=r"Education tab, row 2: 'start_date' should be a date"):
        build_resume(tables(education=bad_date))


def test_personal_tab_without_a_data_row_is_reported():
    with pytest.raises(ResumeDataError, match="no data row"):
        build_resume(tables(personal=(PERSONAL[0],)))


# --- read_resume: dispatch by extension -----------------------------------------


def test_reads_the_sample_file():
    resume = read_resume(SAMPLE)

    assert resume.personal.zip_code == "02134"  # stored as text, so the leading 0 survives
    assert resume.personal.linkedin is not None
    assert [job.employer for job in resume.employment] == ["Analytical Engines Ltd", "Example Cafe"]
    assert not resume.employment[1].is_current


def test_unsupported_extension(tmp_path):
    with pytest.raises(UnsupportedFileError, match=r"\.pdf files aren't supported. Supported: \.xlsx"):
        read_resume(tmp_path / "resume.pdf")


def test_reader_whose_own_import_fails_is_a_plugin_error(monkeypatch):
    # The reader module exists, but a library it imports doesn't.
    def broken_import(name):
        raise ModuleNotFoundError("No module named 'openpyxl'", name="openpyxl")

    monkeypatch.setattr(resume_reader.importlib, "import_module", broken_import)

    with pytest.raises(PluginError, match="needs 'openpyxl'"):
        read_resume(SAMPLE)


def test_missing_tab_is_reported(tmp_path):
    workbook = openpyxl.load_workbook(SAMPLE)
    workbook.remove(workbook["Education"])
    path = tmp_path / "no_education.xlsx"
    workbook.save(path)

    with pytest.raises(ResumeDataError, match="missing the tab"):
        read_resume(path)


def test_file_that_isnt_really_xlsx(tmp_path):
    path = tmp_path / "renamed.xlsx"
    path.write_text("not a spreadsheet")

    with pytest.raises(ResumeDataError, match="isn't a readable .xlsx file"):
        read_resume(path)
