"""Small helpers of generate_pdf: time elapsed since the antecedent, sections without a result."""

import pytest

from medical_report.section_generator.generate_pdf import exam_interval, missing_sections


@pytest.mark.parametrize("current, previous, expected", [
    ("2026-11-04", "2023-02-20", (3, 8)),
    ("2026-11-04", "2025-11-04", (1, 0)),
    ("2026-11-04", "2026-10-05", (0, 0)),     # less than a month
    ("2026-01-12", None, None),               # no antecedent
])
def test_exam_interval_in_years_and_months(current, previous, expected):
    assert exam_interval(current, previous) == expected


def _section(segment, biomarker):
    return {"acquisition": {"segment": segment, "biomarker": biomarker}}


def test_missing_sections_lists_the_biomarker_without_result_per_segment():
    sections = [_section("legs", "FF"), _section("legs", "T2"), _section("thighs", "FF")]

    assert missing_sections(sections) == {"legs": [], "thighs": ["T2"]}
