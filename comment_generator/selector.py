import os
import yaml

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def _load_yaml(filename: str) -> dict:
    with open(os.path.join(_CONFIG_DIR, filename), encoding="utf-8") as f:
        return yaml.safe_load(f)


_config = _load_yaml("t2_comments.yaml")
_labels = _load_yaml("muscle_labels_fr.yaml")

_THRESHOLD = _config["elevated_threshold_ms"]
_CATEGORIES = _config["categories"]


def _get_label(muscle_id: str, side: str) -> str:
    try:
        return _labels[muscle_id][side]
    except KeyError:
        return f"{muscle_id} {side}"


def _format_comment(template: str, elevated: list[dict]) -> str:
    if "{muscles}" not in template:
        return template
    muscle_label = _get_label(elevated[0]["name"], elevated[0]["side"])
    return template.format(muscles=muscle_label)


def select_comment(muscles: list[dict]) -> dict:
    """
    muscles: list from JSON, each entry has 'name', 'side', volume.stats.T2

    Returns: {"category": str, "comment": str}
    """
    t2_values = [
        (m, m["volume"]["stats"]["T2"])
        for m in muscles
        if "T2" in m.get("volume", {}).get("stats", {})
    ]

    if not t2_values:
        return {"category": "unknown", "comment": ""}

    max_T2 = max(v for _, v in t2_values)
    elevated = [m for m, v in t2_values if v >= _THRESHOLD]
    nb_elevated = len(elevated)

    elevated_sorted = sorted(elevated, key=lambda m: m["volume"]["stats"]["T2"], reverse=True)

    if nb_elevated == 0 and max_T2 < _THRESHOLD:
        category = "normal_strict"
    elif nb_elevated == 0:
        category = "normal_borderline"
    elif nb_elevated == 1:
        category = "discrete"
    elif nb_elevated <= 3:
        category = "moderate"
    else:
        category = "significant"

    template = _CATEGORIES[category]["template"]
    comment = _format_comment(template, elevated_sorted)

    return {"category": category, "comment": comment}
