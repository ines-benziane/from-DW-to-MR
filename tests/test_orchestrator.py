"""Orchestrator: which result files feed each report section (version rules, antecedents)."""

import pytest

from medical_report.interface.orchestrator import (
    compatible_versions,
    find_antecedents,
    get_exam,
    parse_version,
)

SECTION = {"section_name": "FF", "segment": "thighs", "acquisition": "1.0",
           "generate": True, "date": None, "method": {"dixon3pt": ">=1.0"}}


@pytest.mark.parametrize("raw, expected", [
    (">=1.0", (">=", "1.0")),
    ("<=2.0", ("<=", "2.0")),
    ("1.0", ("", "1.0")),
])
def test_parse_version(raw, expected):
    assert parse_version(raw) == expected


def test_versions_at_or_above(write_exam, tmp_path):
    for v in ("0.9", "1.0", "1.2"):
        write_exam(version=v)

    assert sorted(compatible_versions("PAT001", SECTION, "dixon3pt", "1.0", ">=", tmp_path)) == ["1.0", "1.2"]


def test_versions_at_or_below(write_exam, tmp_path):
    for v in ("0.9", "1.0", "1.2"):
        write_exam(version=v)

    assert sorted(compatible_versions("PAT001", SECTION, "dixon3pt", "1.0", "<=", tmp_path)) == ["0.9", "1.0"]


def test_exact_version(write_exam, tmp_path):
    for v in ("0.9", "1.0"):
        write_exam(version=v)

    assert compatible_versions("PAT001", SECTION, "dixon3pt", "1.0", "", tmp_path) == ["1.0"]


def test_method_name_with_underscore(write_exam, tmp_path):
    """t2map_3exp contains '_': the version must still be read correctly from the file name."""
    write_exam(method="t2map_3exp", version="1.0")

    assert compatible_versions("PAT001", SECTION, "t2map_3exp", "1.0", ">=", tmp_path) == ["1.0"]


def test_antecedents_are_earlier_exams_oldest_first(write_exam, tmp_path):
    for d in ("20250101", "20200101", "20230101", "20260101"):
        write_exam(exam_date=d)

    antecedents = find_antecedents("PAT001", "20250101", SECTION, "dixon3pt", "1.0", tmp_path)

    assert [a.metadata.exam_date for a in antecedents] == ["20200101", "20230101"]


def test_antecedents_belong_to_the_same_patient(write_exam, tmp_path):
    write_exam(exam_id="PAT002", exam_date="20200101")

    assert find_antecedents("PAT001", "20250101", SECTION, "dixon3pt", "1.0", tmp_path) == []


def _config(**method):
    return {"section": [{**SECTION, "method": method or SECTION["method"]}]}


def test_get_exam_returns_current_exam_with_its_antecedents(write_exam, tmp_path):
    write_exam(exam_date="20200101")
    write_exam(exam_date="20250101")

    [section] = get_exam("PAT001", tmp_path, config_data=_config())

    assert section.exam.metadata.exam_date == "20250101"
    assert [a.metadata.exam_date for a in section.antecedents] == ["20200101"]


def test_get_exam_skips_section_without_data(tmp_path):
    assert get_exam("PAT001", tmp_path, config_data=_config()) == []


def test_get_exam_uses_the_highest_compatible_version(write_exam, tmp_path):
    """Versions are numbers: 1.10 is newer than 1.9."""
    write_exam(version="1.9")
    write_exam(version="1.10")

    [section] = get_exam("PAT001", tmp_path, config_data=_config())

    assert section.exam.metadata.version == "1.10"
