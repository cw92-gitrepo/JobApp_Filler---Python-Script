"""The remembered resume path."""

import pytest

from util import settings


@pytest.fixture
def last_resume_file(tmp_path, monkeypatch):
    path = tmp_path / "last_resume.txt"
    monkeypatch.setattr(settings, "LAST_RESUME_FILE", path)
    return path


def test_nothing_remembered_on_first_run(last_resume_file):
    assert settings.last_resume() is None


def test_remembers_the_chosen_file(last_resume_file, tmp_path):
    resume = tmp_path / "resume.xlsx"
    resume.write_bytes(b"")

    settings.remember_resume(resume)

    assert settings.last_resume() == resume.resolve()


def test_forgets_a_file_that_was_deleted(last_resume_file, tmp_path):
    resume = tmp_path / "resume.xlsx"
    resume.write_bytes(b"")
    settings.remember_resume(resume)
    resume.unlink()

    assert settings.last_resume() is None
