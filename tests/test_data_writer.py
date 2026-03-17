"""
Tests for the DataWriter module.

Covers:
- CSV parsing (volume + slice rows, missing data, label parsing)
- JSON writing (file creation, structure, None stripping)
- Round-trip: CSV → domain → JSON → verify
"""

import json
from pathlib import Path

import pytest

from data_writer.csv_parser import parse_csv, _parse_label
from data_writer.json_writer import JsonWriter

SAMPLE_CSV = """HOW,INDEX,LABEL,X,Y,Z,NPIX,T2,T2STD,T2CINT,FF,OUTLINE
VOLUME,NA,VL_R,-0.22,8.53,414.34,7540.0,46.50,13.04,9.13,0.37,
VOLUME,NA,VL_L,-0.22,8.53,414.34,6354.0,45.90,10.58,9.16,0.37,
SLICE,Z0,VL_R,-0.22,8.53,294.34,,50.89,21.05,,,"[[51.0, 60.5], [50.5, 61.0]]"
SLICE,Z0,VL_L,-0.22,8.53,294.34,,,,,,
SLICE,Z1,VL_R,-0.22,8.53,324.34,,42.48,16.33,,,"[[54.0, 66.5]]"
"""


@pytest.fixture
def sample_csv_path(tmp_path):
    csv_file = tmp_path / "results.csv"
    csv_file.write_text(SAMPLE_CSV.strip())
    return csv_file


@pytest.fixture
def sample_exam(sample_csv_path):
    return parse_csv(sample_csv_path,  "patient_id", "exam_date", "segment", "meth",  "version", "aquisiton" )


class TestParseLabel:
    def test_simple_label(self):
        assert _parse_label("VL_R") == ("VL", "R")

    def test_compound_label(self):
        assert _parse_label("BF_SH_L") == ("BF_SH", "L")
    

    def test_invalid_label_no_side(self):
        with pytest.raises(ValueError):
            _parse_label("VL")

    def test_invalid_label_wrong_side(self):
        with pytest.raises(ValueError):
            _parse_label("VL_X")


# --- Tests: CSV parsing ---


class TestCsvParser:
    def test_muscle_count(self, sample_exam):
        assert len(sample_exam.muscles) == 2  # VL_R and VL_L

    def test_muscle_names(self, sample_exam):
        names = {(m.name, m.side) for m in sample_exam.muscles}
        assert names == {("VL", "R"), ("VL", "L")}

    def test_volume_stats_populated(self, sample_exam):
        vl_r = next(m for m in sample_exam.muscles if m.name == "VL" and m.side == "R")
        assert vl_r.volume is not None
        assert vl_r.volume.stats["T2"] == pytest.approx(46.50)

    def test_slice_count(self, sample_exam):
        vl_r = next(m for m in sample_exam.muscles if m.name == "VL" and m.side == "R")
        assert len(vl_r.slices) == 2  # Z0 and Z1

    def test_slices_sorted(self, sample_exam):
        vl_r = next(m for m in sample_exam.muscles if m.name == "VL" and m.side == "R")
        indices = [s.index for s in vl_r.slices]
        assert indices == ["Z0", "Z1"]

    def test_slice_with_data(self, sample_exam):
        vl_r = next(m for m in sample_exam.muscles if m.name == "VL" and m.side == "R")
        z0 = vl_r.slices[0]
        assert z0.stats["T2"] == pytest.approx(50.89)
        assert z0.outline == [[51.0, 60.5], [50.5, 61.0]]

    def test_slice_empty_data(self, sample_exam):
        vl_l = next(m for m in sample_exam.muscles if m.name == "VL" and m.side == "L")
        z0 = vl_l.slices[0]
        assert "T2" not in z0.stats
        assert z0.outline is None

class TestJsonWriter:
    def test_writes_file(self, sample_exam, tmp_path):
        output = tmp_path / "output.json"
        JsonWriter().write(sample_exam, output)
        assert output.exists()

    def test_valid_json(self, sample_exam, tmp_path):
        output = tmp_path / "output.json"
        JsonWriter().write(sample_exam, output)
        with open(output) as f:
            data = json.load(f)
        assert "muscles" in data

    def test_none_values_stripped(self, sample_exam, tmp_path):
        output = tmp_path / "output.json"
        JsonWriter().write(sample_exam, output)
        with open(output) as f:
            content = f.read()
        assert "null" not in content.lower()

    def test_creates_parent_dirs(self, sample_exam, tmp_path):
        output = tmp_path / "deep" / "nested" / "output.json"
        JsonWriter().write(sample_exam, output)
        assert output.exists()

    def test_muscle_centric_structure(self, sample_exam, tmp_path):
        output = tmp_path / "output.json"
        JsonWriter().write(sample_exam, output)
        with open(output) as f:
            data = json.load(f)

        muscle = data["muscles"][0]
        assert "name" in muscle
        assert "side" in muscle
        assert "volume" in muscle
        assert "slices" in muscle


# --- Test: round-trip with real CSV ---


class TestRoundTrip:
    def test_real_csv(self, tmp_path):
        """Test with the actual uploaded CSV if available."""
        real_csv = Path("/mnt/user-data/uploads/results.csv")
        if not real_csv.exists():
            pytest.skip("Real CSV not available")

        exam = parse_csv(real_csv, "meth", "seg", "pat01")
        assert len(exam.muscles) == 26 

        output = tmp_path / "real_output.json"
        JsonWriter().write(exam, output)

        with open(output) as f:
            data = json.load(f)

        assert len(data["muscles"]) == 26

        # Every muscle should have 9 slices (Z0-Z8)
        for m in data["muscles"]:
            assert len(m["slices"]) == 9, f"{m['name']}_{m['side']} has {len(m['slices'])} slices"
