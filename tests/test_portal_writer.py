"""Portal detection by hostname, and saved portal configs."""

import pytest

from util.errors import ConfigError
from writers import portal_writer
from writers.portal_writer import (
    load_config,
    missing_fields,
    portal_for,
    save_config,
    saved_configs,
)


@pytest.mark.parametrize(
    ("url", "portal"),
    [
        ("https://acme.wd5.myworkdayjobs.com/en-US/careers/job/123/apply", "workday"),
        ("https://wd1.myworkdaysite.com/recruiting/acme/jobs", "workday"),
        ("https://www.google.com/search?q=workday+jobs", None),  # only the hostname counts
        ("about:blank", None),
        ("", None),  # tabs opened from about:blank can report an empty URL
    ],
)
def test_portal_for(url, portal):
    assert portal_for(url) == portal


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(portal_writer, "CONFIG_DIR", tmp_path)
    return tmp_path


def test_save_then_load_round_trip(config_dir):
    path = save_config("workday", "default", {"source": "Indeed"})

    assert path == config_dir / "workday" / "default.json"
    assert load_config(path) == {"source": "Indeed"}


def test_most_recently_used_config_comes_first(config_dir):
    older = save_config("workday", "older", {})
    newer = save_config("workday", "newer", {})
    load_config(older)  # using a config marks it as most recent

    assert saved_configs("workday") == [older, newer]


def test_missing_fields_are_only_the_unanswered_questions(config_dir):
    answered = {"source": "Indeed", "previously_worked_here": "No"}

    missing = missing_fields("workday", answered)

    assert "source" not in missing
    assert "skills" in missing


def test_unsafe_config_name_is_rejected(config_dir):
    with pytest.raises(ConfigError):
        save_config("workday", "../escape", {})
