import os
import yaml
from functools import lru_cache

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def _load_yaml(filename: str) -> dict:
    with open(os.path.join(_CONFIG_DIR, filename), encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def _config(lang: str) -> dict:
    return _load_yaml(f"t2_comments_{lang}.yaml")


@lru_cache
def _labels(lang: str) -> dict:
    return _load_yaml(f"muscle_labels_{lang}.yaml")


def _get_label(lang: str, muscle_id: str, side: str) -> str:
    return _labels(lang).get(muscle_id, {}).get(side, f"{muscle_id} {side}")


def _format_comment(template: str, elevated: list[dict], lang: str) -> str:
    if "{muscles}" not in template:
        return template
    m = elevated[0]
    return template.format(muscles=_get_label(lang, m["name"], m["side"]))


def select_comment(muscles: list[dict], lang: str = "en") -> dict:
    """
    muscles: list from JSON, each entry has 'name', 'side', volume.stats.T2
    lang: language code ("fr" or "en")

    Returns: {"category": str, "comment": str}
    """
    cfg = _config(lang)
    threshold = cfg["elevated_threshold_ms"]

    t2_values = [
        (m, m["volume"]["stats"]["T2"])
        for m in muscles
        if "T2" in m.get("volume", {}).get("stats", {})
    ]

    if not t2_values:
        return {"category": "unknown", "comment": ""}

    max_T2 = max(v for _, v in t2_values)
    elevated = [m for m, v in t2_values if v >= threshold]
    nb_elevated = len(elevated)

    if nb_elevated == 0 and max_T2 < threshold:
        category = "normal_strict"
    elif nb_elevated == 0:
        category = "normal_borderline"
    elif nb_elevated == 1:
        category = "discrete"
    elif nb_elevated <= 3:
        category = "moderate"
    else:
        category = "significant"

    elevated_sorted = sorted(elevated, key=lambda m: m["volume"]["stats"]["T2"], reverse=True)
    template = cfg["categories"][category]["template"]

    return {"category": category, "comment": _format_comment(template, elevated_sorted, lang)}
