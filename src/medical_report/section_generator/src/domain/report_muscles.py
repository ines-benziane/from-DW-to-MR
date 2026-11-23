"""Muscles of the report, per segment: the single list used by the legend (anatomical landmarks),
the value tables and the evolution tables.

id       : label of the segmentation (labels.txt of the method), as found in the result JSON.
abbr     : abbreviation printed in the report (legend, tables, evolution). Change it here only.
name     : full name.
diagram  : label of the muscle on the cross-section diagram (images/jambe_schema.png,
           images/cuisse_schema.png); None when the muscle is not drawn on it.

The legend defines every abbreviation (the muscles not drawn on the diagram are flagged there).
The tables show every muscle of the list; a muscle absent from the patient's slice shown gets a "*"
(its value is measured over the whole volume). A segmented muscle missing from this list is still
printed under the tables with its id (templates/shared_macros.html, muscle_notes): no value is lost.
"""

REPORT_MUSCLES = {
    "legs": [
        {"id": "TA", "abbr": "TA", "name": "Tibialis Anterior", "diagram": "TA"},
        {"id": "ED", "abbr": "ED", "name": "Extensor Digitorum", "diagram": "ED"},
        {"id": "PER", "abbr": "PER", "name": "Fibularis / Peroneus longus", "diagram": "PER"},
        {"id": "DLPC", "abbr": "DLPC", "name": "Deep Posterior Compartment (TP + long toe & hallux flexors)", "diagram": "TP"},
        {"id": "POP", "abbr": "POP", "name": "Popliteus", "diagram": None},
        {"id": "SOL", "abbr": "SOL", "name": "Soleus", "diagram": "SOL"},
        {"id": "GAS_MED", "abbr": "GM", "name": "Gastrocnemius Medialis", "diagram": "GM"},
        {"id": "GAS_LAT", "abbr": "GL", "name": "Gastrocnemius Lateralis", "diagram": "GL"},
    ],
    "thighs": [
        {"id": "VL", "abbr": "VL", "name": "Vastus Lateralis", "diagram": "VL"},
        {"id": "VI", "abbr": "VI", "name": "Vastus Intermedius", "diagram": "VI"},
        {"id": "VM", "abbr": "VM", "name": "Vastus Medialis", "diagram": "VM"},
        {"id": "RF", "abbr": "RF", "name": "Rectus Femoris", "diagram": "RF"},
        {"id": "SAR", "abbr": "SAR", "name": "Sartorius", "diagram": "SAR"},
        {"id": "GRA", "abbr": "GRA", "name": "Gracilis", "diagram": "GRA"},
        {"id": "SM", "abbr": "SM", "name": "Semimembranosus", "diagram": "SM"},
        {"id": "ST", "abbr": "ST", "name": "Semitendinosus", "diagram": "ST"},
        {"id": "BF", "abbr": "BF", "name": "Biceps Femoris, long head", "diagram": "BF"},
        {"id": "BF_SH", "abbr": "BF_SH", "name": "Biceps Femoris, short head", "diagram": None},
        {"id": "AM", "abbr": "AM", "name": "Adductor Magnus", "diagram": "AM"},
        {"id": "AL", "abbr": "AL", "name": "Adductor Longus", "diagram": None},
        {"id": "AB", "abbr": "AB", "name": "Adductor Brevis", "diagram": None},
    ],
}


def muscle_ids(segment):
    """Ids of every report muscle of a segment, in the report order: the legend and the table rows."""
    return [m["id"] for m in REPORT_MUSCLES.get(segment, [])]


def diagram_muscle_ids(segment):
    """Ids of the muscles drawn on the segment diagram."""
    return [m["id"] for m in REPORT_MUSCLES.get(segment, []) if m["diagram"]]


MUSCLE_NAMES = {m["id"]: m["name"] for muscles in REPORT_MUSCLES.values() for m in muscles}
MUSCLE_ABBR = {m["id"]: m["abbr"] for muscles in REPORT_MUSCLES.values() for m in muscles}


def abbr(muscle_id):
    """Abbreviation printed in the report; the segmentation id for a muscle missing from the list."""
    return MUSCLE_ABBR.get(muscle_id, muscle_id)
