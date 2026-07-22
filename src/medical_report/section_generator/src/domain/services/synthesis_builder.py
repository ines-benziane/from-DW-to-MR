from medical_report.section_generator.src.infrastructure.color_mappers import get_color_from_evolution

T2_THRESHOLD = 39.0
EVOLUTION_THRESHOLD = {"T2": 1.0, "FF": 5.0}

def compute_evolution(current_val, previous_val, biomarker):
    if current_val is None or previous_val is None:
        return None, "inconnu", "-"
    if biomarker == "FF":
        pct = round((current_val - previous_val) * 100)
    else:
        pct = round(current_val - previous_val)
    threshold = EVOLUTION_THRESHOLD.get(biomarker, 5.0)
    if pct > threshold:
        return pct, "aggravé", "↑"
    elif pct < -threshold:
        return pct, "amélioré", "↓"
    else:
        return pct, "stable", "→"


def build_muscle_evolutions(current_muscles, antecedent_muscles, biomarker):
    stat_key = "FF" if biomarker == "FF" else "T2"
    ant_map = {(m["id"], m["side"]): m for m in antecedent_muscles}

    evolutions = []
    for m in current_muscles:
        key = (m["id"], m["side"])
        current_val = m["stats"].get(stat_key)
        ant_m = ant_map.get(key)
        previous_val = ant_m["stats"].get(stat_key) if ant_m else None

        pct, status, arrow = compute_evolution(current_val, previous_val, biomarker)

        threshold_crossed = (
            biomarker == "T2"
            and previous_val is not None
            and current_val is not None
            and previous_val < T2_THRESHOLD <= current_val
        )

        evolutions.append({
            "id": m["id"],
            "side": m["side"],
            "current": current_val,
            "previous": previous_val,
            "pct": pct,
            "status": status,
            "arrow": arrow,
            "threshold_crossed": threshold_crossed,
            "color": m.get("color", "rgb(150,150,150)"),
            "evolution_color": get_color_from_evolution(pct, biomarker),
            "path": m.get("path", ""),
        })

    return evolutions


def build_synthesis_data(all_sections):
    synthesis_sections = []

    for section in all_sections:
        if section.get("section_name") != "5slices":
            continue
        current_vol = section.get("current_volume_slice")
        antecedent_vol = section.get("antecedent_slice")
        if current_vol is None or antecedent_vol is None:
            continue

        biomarker = section["acquisition"]["biomarker"]
        evolutions = build_muscle_evolutions(
            current_vol["muscles"], antecedent_vol["muscles"], biomarker
        )

        known = [e for e in evolutions if e["pct"] is not None]
        aggravated = sorted([e for e in known if e["status"] == "aggravé"],  key=lambda x: abs(x["pct"]), reverse=True)
        stable     = [e for e in known if e["status"] == "stable"]
        improved   = sorted([e for e in known if e["status"] == "amélioré"], key=lambda x: abs(x["pct"]), reverse=True)
        top_muscles = sorted(known, key=lambda x: abs(x["pct"]), reverse=True)[:3]

        synthesis_sections.append({
            "biomarker": biomarker,
            "segment": section["acquisition"]["segment"],
            "current_date": section["acquisition"]["exam_date"],
            "antecedent_date": section["antecedent_date"],
            "current_volume_slice": current_vol,
            "antecedent_slice": antecedent_vol,
            "evolutions": evolutions,
            "aggravated": aggravated,
            "stable": stable,
            "improved": improved,
            "top_muscles": top_muscles,
            "colorbar": section.get("colorbar"),
        })

    return synthesis_sections if synthesis_sections else None
