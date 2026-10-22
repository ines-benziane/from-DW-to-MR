"""JsonReader: picks the result file of a section (exam, segment, method, version, acquisition)."""

from medical_report.data_reader.json_reader import JsonReader
from medical_report.models.request import SectionRequest


def _request(date=None, **overrides):
    kwargs = dict(section_name="FF", segment="thighs", method="dixon3pt", version="1.0",
                  operator="", generate=True, date=date, acquisition="1.0")
    kwargs.update(overrides)
    return SectionRequest(**kwargs)


def test_without_date_returns_the_most_recent_exam(write_exam, tmp_path):
    write_exam(exam_date="20220101")
    write_exam(exam_date="20250101")

    exam = JsonReader("PAT001", tmp_path).fetch_data(_request()).exam

    assert exam.metadata.exam_date == "20250101"


def test_with_date_returns_that_exam(write_exam, tmp_path):
    write_exam(exam_date="20220101")
    write_exam(exam_date="20250101")

    exam = JsonReader("PAT001", tmp_path).fetch_data(_request(date="20220101")).exam

    assert exam.metadata.exam_date == "20220101"


def test_values_are_read_unchanged(write_exam, tmp_path):
    """RES-004 (code side): the value in the result file is the value handed to the report."""
    write_exam(muscles=[{"name": "VL", "side": "L", "volume": {"stats": {"FF": 0.4321}}, "slices": []}])

    exam = JsonReader("PAT001", tmp_path).fetch_data(_request()).exam

    assert exam.muscles[0].volume.stats["FF"] == 0.4321


def test_patient_identity_is_read_unchanged(write_exam, tmp_path):
    """FONC-005 (code side): exam id and date come from the result file, not from elsewhere."""
    write_exam(exam_id="PAT001", exam_date="20250101")

    meta = JsonReader("PAT001", tmp_path).fetch_data(_request()).exam.metadata

    assert (meta.exam_id, meta.exam_date) == ("PAT001", "20250101")


def test_other_patient_is_never_returned(write_exam, tmp_path):
    write_exam(exam_id="PAT002")

    assert JsonReader("PAT001", tmp_path).fetch_data(_request()).exam is None


def test_other_segment_method_or_version_not_returned(write_exam, tmp_path):
    write_exam(segment="legs")
    write_exam(method="t2map_3exp")
    write_exam(version="2.0")

    assert JsonReader("PAT001", tmp_path).fetch_data(_request()).exam is None


def test_missing_date_returns_no_exam(write_exam, tmp_path):
    write_exam(exam_date="20250101")

    assert JsonReader("PAT001", tmp_path).fetch_data(_request(date="19990101")).exam is None


def test_corrupted_file_returns_no_exam(write_exam, tmp_path):
    """FONC-002 (code side): an unreadable result file never produces a report section."""
    write_exam(content="{ not json")

    assert JsonReader("PAT001", tmp_path).fetch_data(_request()).exam is None
