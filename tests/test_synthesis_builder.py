"""Evolution between the current exam and the antecedent, shown in the synthesis page.
Clinical rules as currently coded (see MuReport-regles-cliniques.docx), to be validated by a physician:
T2 change in ms, FF change in points; rounded to an integer, then 'aggravé' / 'amélioré' only if
strictly beyond the threshold (T2: 1 ms, FF: 5 points)."""

import pytest

from medical_report.section_generator.src.domain.services.synthesis_builder import (
    build_muscle_evolutions,
    build_synthesis_data,
    compute_evolution,
)


@pytest.mark.parametrize("current, previous, expected", [
    (42.0, 40.0, (2, "aggravé", "↑")),
    (41.4, 40.0, (1, "stable", "→")),
    (41.6, 40.0, (2, "aggravé", "↑")),
    (40.0, 40.0, (0, "stable", "→")),
    (38.0, 40.0, (-2, "amélioré", "↓")),
])
def test_t2_evolution_in_ms(current, previous, expected):
    assert compute_evolution(current, previous, "T2") == expected


@pytest.mark.parametrize("current, previous, expected", [
    (0.30, 0.20, (10, "aggravé", "↑")),
    (0.25, 0.20, (5, "stable", "→")),
    (0.10, 0.20, (-10, "amélioré", "↓")),
])
def test_ff_evolution_in_points(current, previous, expected):
    assert compute_evolution(current, previous, "FF") == expected


@pytest.mark.parametrize("current, previous", [(None, 40.0), (40.0, None)])
def test_missing_value_gives_unknown_evolution(current, previous):
    assert compute_evolution(current, previous, "T2") == (None, "inconnu", "-")


def _muscle(mid, side, value, key="T2"):
    return {"id": mid, "side": side, "stats": {key: value}}


def test_muscles_are_matched_by_name_and_side():
    current = [_muscle("VL", "R", 45.0), _muscle("VL", "L", 40.0)]
    antecedent = [_muscle("VL", "L", 40.0), _muscle("VL", "R", 40.0)]

    evo = {(e["id"], e["side"]): e for e in build_muscle_evolutions(current, antecedent, "T2")}

    assert evo[("VL", "R")]["status"] == "aggravé"
    assert evo[("VL", "L")]["status"] == "stable"


def test_muscle_absent_from_antecedent_is_unknown():
    [evo] = build_muscle_evolutions([_muscle("VL", "R", 45.0)], [], "T2")

    assert (evo["previous"], evo["status"]) == (None, "inconnu")


@pytest.mark.parametrize("previous, current, crossed", [
    (38.0, 39.0, True),
    (38.0, 45.0, True),
    (39.0, 45.0, False),
    (45.0, 38.0, False),
])
def test_t2_threshold_crossing_flag(previous, current, crossed):
    [evo] = build_muscle_evolutions([_muscle("VL", "R", current)], [_muscle("VL", "R", previous)], "T2")

    assert evo["threshold_crossed"] is crossed


def test_threshold_crossing_only_for_t2():
    [evo] = build_muscle_evolutions([_muscle("VL", "R", 45.0, "FF")], [_muscle("VL", "R", 0.1, "FF")], "FF")

    assert evo["threshold_crossed"] is False


def _section(current, antecedent, name="5slices"):
    return {"section_name": name, "antecedent_date": "20200101",
            "acquisition": {"biomarker": "T2", "segment": "thighs", "exam_date": "20250101"},
            "current_volume_slice": {"muscles": current}, "antecedent_slice": {"muscles": antecedent}}


def test_synthesis_sorts_and_ranks_changes():
    current = [_muscle("VL", "R", 50.0), _muscle("VI", "R", 43.0), _muscle("VM", "R", 40.0),
               _muscle("RF", "R", 30.0)]
    antecedent = [_muscle(m, "R", 40.0) for m in ("VL", "VI", "VM", "RF")]

    [s] = build_synthesis_data([_section(current, antecedent)])

    assert [e["id"] for e in s["aggravated"]] == ["VL", "VI"]
    assert [e["id"] for e in s["improved"]] == ["RF"]
    assert [e["id"] for e in s["stable"]] == ["VM"]
    assert [e["id"] for e in s["top_muscles"]] == ["VL", "RF", "VI"]


def test_synthesis_needs_an_antecedent():
    section = _section([_muscle("VL", "R", 45.0)], None)
    section["antecedent_slice"] = None

    assert build_synthesis_data([section]) is None


def test_synthesis_ignores_other_sections():
    assert build_synthesis_data([_section([_muscle("VL", "R", 45.0)], [], name="FF")]) is None
