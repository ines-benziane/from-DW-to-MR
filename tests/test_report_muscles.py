"""No segmented muscle is lost in the report: every muscle of the report list is in the tables (with a "*"
when absent from the patient's slice shown), a muscle missing from the list is printed under them
(src/domain/report_muscles.py, templates/shared_macros.html). Abbreviations come from the list only."""

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from medical_report.section_generator import generate_pdf
from medical_report.section_generator.generate_pdf import build_volume_slice
from medical_report.section_generator.src.domain.report_muscles import (MUSCLE_NAMES, REPORT_MUSCLES, abbr,
                                                                        diagram_muscle_ids, muscle_ids)
from medical_report.section_generator.src.domain.services.synthesis_builder import EVOLUTION_THRESHOLD
from medical_report.section_generator.src.infrastructure.color_mappers import (EVOLUTION_STABLE_COLOR,
                                                                               get_color_from_evolution, t2_display)

FR = json.loads((Path(generate_pdf.__file__).parent / "config" / "i18n" / "fr.json").read_text(encoding="utf-8"))


def _env():
    env = Environment(loader=FileSystemLoader(generate_pdf.TEMPLATE_DIR))
    env.globals.update(t=FR, muscle_names=MUSCLE_NAMES, abbr=abbr, muscle_ids=muscle_ids, t2_display=t2_display())
    return env


def _render_notes(muscles, muscles_list, biomarker, evolution=False):
    macro = _env().get_template("shared_macros.html").module.muscle_notes
    return str(macro(muscles, muscles_list, biomarker, evolution))


def _text(html):
    """Text as read in the PDF."""
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def _column(html, side):
    """Text of the L or R column of the extra muscles (laid out like the table above)."""
    block = re.search(rf'<div class="metrics-col notes-side-{side}".*?</table>', html, flags=re.S)
    return _text(block.group(0)) if block else ""


def test_every_report_muscle_has_a_name_and_a_diagram_entry():
    for segment, muscles in REPORT_MUSCLES.items():
        assert muscles and all(m["id"] and m["abbr"] and m["name"] and "diagram" in m for m in muscles), segment
        assert len({m["abbr"] for m in muscles}) == len(muscles), f"duplicate abbreviation in {segment}"
        assert len(set(muscle_ids(segment))) == len(muscles), f"duplicate muscle in {segment}"


def test_muscle_absent_from_the_slice_shown_keeps_its_volumetric_value():
    slices = [{"muscles": [{"id": "VL", "side": "R", "path": "M0 0"}], "slices": {},
               "viewbox_L": "", "viewbox_R": "", "mirror_tx_L": 0, "mirror_tx_R": 0}]
    raw = [{"name": "VL", "side": "R", "volume": {"stats": {"FF": 0.10}}},
           {"name": "AL", "side": "R", "volume": {"stats": {"FF": 0.05}}}]

    shown = build_volume_slice(slices, raw, "FF")

    assert [m["id"] for m in shown["muscles"]] == ["VL"]
    assert [(m["id"], m["stats"]["FF"], m["path"]) for m in shown["off_slice_muscles"]] == [("AL", 0.05, None)]


def test_tables_hold_every_muscle_of_the_list_even_those_not_drawn_on_the_diagram():
    assert "BF_SH" not in diagram_muscle_ids("thighs") and "BF_SH" in muscle_ids("thighs")
    assert muscle_ids("legs") == [m["id"] for m in REPORT_MUSCLES["legs"]]


def test_abbreviation_printed_instead_of_the_segmentation_label():
    assert (abbr("GAS_MED"), abbr("GAS_LAT"), abbr("DLPC")) == ("GM", "GL", "DLPC")
    assert abbr("XX") == "XX"   # unknown muscle: its segmentation label


def test_legend_defines_every_muscle_and_flags_those_not_drawn():
    """Meeting 2026-11-19: all the abbreviations in one place, the legend."""
    html = str(_env().get_template("T2/macros.html").module.anatomical_header("r", "Jambes", REPORT_MUSCLES["legs"]))
    text = _text(html.replace("&nbsp;", " "))

    for m in REPORT_MUSCLES["legs"]:
        assert f"{m['abbr']}{'' if m['diagram'] else '*'} {m['name']}" in text, m["id"]
    assert "POP* Popliteus" in text and "SOL*" not in text
    assert f"* {FR['not_on_diagram_note']}" in text


def test_unknown_muscle_is_printed_with_its_id():
    """A muscle a new segmentation model would add, unknown to report_muscles, is not lost either."""
    html = _render_notes([{"id": "XX", "side": "L", "stats": {"FF": 0.042}, "path": "M0 0"}], ["VL"], "FF")

    assert FR["other_muscles_intro"] in _text(html) and _column(html, "L") == "XX: 4.2%"


def test_listed_muscle_off_the_slice_gets_the_star_note():
    muscles = [{"id": "AL", "side": "R", "stats": {"T2": 35.0}, "path": None}]

    assert FR["off_slice_note"] in _text(_render_notes(muscles, ["AL"], "T2"))


def test_evolution_of_a_muscle_not_in_the_list_is_printed():
    evolutions = [{"id": "XX", "side": "R", "pct": 3, "path": "M0 0"}]

    assert _column(_render_notes(evolutions, ["VL"], "FF", evolution=True), "R") == "XX: +3 pt"


def test_nothing_printed_when_every_muscle_is_listed_and_on_the_slice():
    muscles = [{"id": "VL", "side": "L", "stats": {"FF": 0.10}, "path": "M0 0"}]

    assert _text(_render_notes(muscles, ["VL"], "FF")) == ""


def test_notes_line_uses_the_colour_code_of_the_tables():
    """Same rules as the tables (value_span): FF >= 24 % black on the muscle colour, bold above 50 %;
    T2 bold above 39 ms; evolution red bold when worse."""
    ff = _render_notes([{"id": "AB", "side": "L", "stats": {"FF": 0.60}, "color": "rgb(1, 2, 3)", "path": "M"}],
                       [], "FF")
    t2 = _render_notes([{"id": "AB", "side": "L", "stats": {"T2": 41.0}, "color": "rgb(4, 5, 6)", "path": "M"}],
                       [], "T2")
    evo = _render_notes([{"id": "AB", "side": "L", "pct": 9, "status": "aggravé", "path": "M"}],
                        [], "FF", evolution=True)

    assert "background-color: rgb(1, 2, 3)" in ff and "<strong>AB: 60.0%</strong>" in ff
    assert "color: rgb(4, 5, 6)" in t2 and "<strong>AB: 41.0 ms</strong>" in t2
    assert "#c0392b" in evo and "<strong>AB: +9 pt</strong>" in evo


def test_evolution_table_follows_the_order_of_the_value_table():
    evolutions = [{"id": i, "side": "L", "pct": 0, "status": "stable", "path": "M"} for i in ("SOL", "TA", "GAS_MED")]
    macro = _env().get_template("synthesis/macros.html").module.evolution_muscle_table

    assert _text(str(macro(evolutions, "L", "L", "T2", muscle_ids("legs")))) == "TA: +0 ms SOL: +0 ms GM: +0 ms"


def test_evolution_within_the_threshold_is_grey_on_the_slice_as_in_the_table():
    """Meeting 2026-11-19: +1 ms and +2 ms looked the same. +1 ms is stable (grey text): grey on the slice too."""
    t2 = EVOLUTION_THRESHOLD["T2"]

    assert get_color_from_evolution(1, "T2", t2) == get_color_from_evolution(-1, "T2", t2) == EVOLUTION_STABLE_COLOR
    assert get_color_from_evolution(2, "T2", t2) != EVOLUTION_STABLE_COLOR
    assert get_color_from_evolution(2, "T2", t2) != get_color_from_evolution(-2, "T2", t2)
    assert get_color_from_evolution(5, "FF", EVOLUTION_THRESHOLD["FF"]) == EVOLUTION_STABLE_COLOR
