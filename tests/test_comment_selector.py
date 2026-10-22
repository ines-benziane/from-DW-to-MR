"""T2 comment written in the report, chosen from the number of muscles with elevated T2.
Clinical rules as currently coded (see MuReport-regles-cliniques.docx), to be validated by a physician."""

import pytest

from medical_report.comment_generator.selector import _config, select_comment
from medical_report.section_generator.src.domain.services.synthesis_builder import T2_THRESHOLD


def _muscles(*t2_values):
    return [{"name": name, "side": "R", "volume": {"stats": {"T2": v}}}
            for name, v in zip(("VL", "VI", "VM", "RF", "SAR", "GRA"), t2_values)]


@pytest.mark.parametrize("t2_values, category", [
    ((35, 36, 37), "normal_strict"),
    ((35, 36, 39), "discrete"),
    ((35, 39, 40), "moderate"),
    ((39, 40, 41), "moderate"),
    ((39, 40, 41, 42), "significant"),
])
def test_category_from_number_of_elevated_muscles(t2_values, category):
    assert select_comment(_muscles(*t2_values), lang="fr")["category"] == category


def test_threshold_is_inclusive():
    """39.0 ms exactly counts as elevated, 38.99 does not."""
    assert select_comment(_muscles(38.99), lang="fr")["category"] == "normal_strict"
    assert select_comment(_muscles(39.0), lang="fr")["category"] == "discrete"


def test_discrete_comment_names_the_elevated_muscle():
    comment = select_comment(_muscles(35, 45), lang="fr")["comment"]

    assert "vaste intermédiaire droit" in comment


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_comment_exists_in_both_languages(lang):
    assert select_comment(_muscles(45), lang=lang)["comment"]


def test_no_t2_values_gives_no_comment():
    muscles = [{"name": "VL", "side": "R", "volume": {"stats": {"FF": 0.1}}}]

    assert select_comment(muscles, lang="fr") == {"category": "unknown", "comment": ""}


def test_same_t2_threshold_everywhere():
    """The comment (fr, en) and the evolution synthesis must use the same elevated-T2 threshold."""
    assert _config("fr")["elevated_threshold_ms"] == _config("en")["elevated_threshold_ms"] == T2_THRESHOLD


@pytest.mark.xfail(strict=True, reason="normal_borderline is unreachable: its rule (no elevated muscle "
                                       "AND max T2 >= threshold) is self-contradictory. To decide with a physician.")
def test_normal_borderline_is_reachable():
    categories = {select_comment(_muscles(t2), lang="fr")["category"]
                  for t2 in [x / 10 for x in range(300, 450)]}
    assert "normal_borderline" in categories
