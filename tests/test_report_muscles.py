"""No segmented muscle is lost in the report: muscles missing from the report list, or absent from
the slice shown, still get their value (src/domain/report_muscles.py, templates/shared_macros.html)."""

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from medical_report.section_generator import generate_pdf
from medical_report.section_generator.generate_pdf import build_volume_slice
from medical_report.section_generator.src.domain.report_muscles import (MUSCLE_NAMES, REPORT_MUSCLES, diagram_muscle_ids,
                                                                        muscle_ids)

FR = json.loads((Path(generate_pdf.__file__).parent / "config" / "i18n" / "fr.json").read_text(encoding="utf-8"))


def _render_notes(muscles, muscles_list, biomarker, evolution=False):
    env = Environment(loader=FileSystemLoader(generate_pdf.TEMPLATE_DIR))
    env.globals["t"] = FR
    env.globals["muscle_names"] = MUSCLE_NAMES
    macro = env.get_template("shared_macros.html").module.muscle_notes
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
        assert muscles and all(m["id"] and m["name"] and "diagram" in m for m in muscles), segment
        assert len(set(muscle_ids(segment))) == len(muscles), f"duplicate muscle in {segment}"


def test_muscle_absent_from_the_slice_shown_keeps_its_volumetric_value():
    slices = [{"muscles": [{"id": "VL", "side": "R", "path": "M0 0"}], "slices": {},
               "viewbox_L": "", "viewbox_R": "", "mirror_tx_L": 0, "mirror_tx_R": 0}]
    raw = [{"name": "VL", "side": "R", "volume": {"stats": {"FF": 0.10}}},
           {"name": "AL", "side": "R", "volume": {"stats": {"FF": 0.05}}}]

    shown = build_volume_slice(slices, raw, "FF")

    assert [m["id"] for m in shown["muscles"]] == ["VL"]
    assert [(m["id"], m["stats"]["FF"], m["path"]) for m in shown["off_slice_muscles"]] == [("AL", 0.05, None)]


def test_legend_and_tables_are_the_muscles_of_the_diagram():
    assert "BF_SH" not in diagram_muscle_ids("thighs") and "BF_SH" in muscle_ids("thighs")
    assert diagram_muscle_ids("legs") == [m["id"] for m in REPORT_MUSCLES["legs"] if m["diagram"]]


def test_muscle_not_on_the_diagram_is_named_then_valued_in_its_side_column():
    muscles = [{"id": "VL", "side": "L", "stats": {"FF": 0.10}, "path": "M0 0"},
               {"id": "AB", "side": "R", "stats": {"FF": 0.019}, "path": "M0 0"},
               {"id": "AB", "side": "L", "stats": {"FF": 0.017}, "path": "M0 0"}]

    html = _render_notes(muscles, ["VL"], "FF")

    assert f"{FR['not_on_diagram_intro']} AB (Adductor Brevis)." in _text(html)
    assert _column(html, "L") == "AB: 1.7%" and _column(html, "R") == "AB: 1.9%"
    assert "VL" not in _text(html)


def test_unknown_muscle_is_printed_with_its_id():
    """A muscle a new segmentation model would add, unknown to report_muscles, is not lost either."""
    html = _render_notes([{"id": "XX", "side": "L", "stats": {"FF": 0.042}, "path": "M0 0"}], ["VL"], "FF")

    assert f"{FR['not_on_diagram_intro']} XX." in _text(html) and _column(html, "L") == "XX: 4.2%"


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
