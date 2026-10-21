"""The pure helpers in the Workday writer (no browser needed)."""

import pytest

from writers.writer_workday import _best_match, _config_list

STATES = ["Texas", "Virginia", "West Virginia"]


@pytest.mark.parametrize(
    ("wanted", "labels", "expected"),
    [
        ("virginia", STATES, 1),  # exact (ignoring case) beats "West Virginia"
        ("West", STATES, 2),  # the only label containing it
        ("ginia", STATES, None),  # two labels contain it: don't guess
        ("Bachelor's Degree", ["AS", "Bachelor’s Degree"], 1),  # curly apostrophe
        ("PhD", STATES, None),
    ],
)
def test_best_match(wanted, labels, expected):
    assert _best_match(wanted, labels) == expected


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("BS, AS", ["BS", "AS"]),
        (" BS ,, ", ["BS"]),
        ("", ["from resume"]),
        ("Skip", ["from resume"]),
    ],
)
def test_config_list_falls_back_to_the_resume(answer, expected):
    assert _config_list({"degrees": answer}, "degrees", default=["from resume"]) == expected
