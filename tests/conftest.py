import json

import pytest


def exam_dict(exam_id="PAT001", exam_date="20250101", segment="thighs", method="dixon3pt",
              version="1.0", acquisition="1.0", biomarker="FF", muscles=None, **metadata):
    """A minimal valid Exam (medical_report.models.domain) as a dict."""
    return {
        "muscles": muscles if muscles is not None else [
            {"name": "VL", "side": "R", "volume": {"stats": {"FF": 0.12}}, "slices": []},
        ],
        "metadata": {"exam_id": exam_id, "exam_date": exam_date, "segment": segment,
                     "method": method, "version": version, "acquisition": acquisition,
                     "segmentation": "museg", "biomarker": biomarker, **metadata},
    }


@pytest.fixture
def write_exam(tmp_path):
    """Write an exam JSON with the pipeline's naming convention; returns the file path."""
    def _write(exam_id="PAT001", exam_date="20250101", segment="thighs", method="dixon3pt",
               version="1.0", acquisition="1.0", content=None, **kwargs):
        path = tmp_path / f"{exam_id}_{exam_date}_{segment}_{method}_{version}_{acquisition}.json"
        if content is None:
            content = json.dumps(exam_dict(exam_id, exam_date, segment, method, version,
                                           acquisition, **kwargs))
        path.write_text(content, encoding="utf-8")
        return path
    return _write
