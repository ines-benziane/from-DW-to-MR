"""Muscles of the report, per segment: the single list used by the legend (anatomical landmarks),
the value tables and the evolution tables.

id       : label of the segmentation (labels.txt of the method), as found in the result JSON.
name     : full name.
diagram  : label of the muscle on the cross-section diagram (images/jambe_schema.png,
           images/cuisse_schema.png); None when the muscle is not drawn on it.

The legend and the tables show the muscles drawn on the diagram, so that the reader sees what the
picture shows. Every other segmented muscle (diagram None, or missing from this list) is printed
with its full name and its values on one line under the tables (templates/shared_macros.html,
muscle_notes): no value is lost.
"""

REPORT_MUSCLES = {
    "legs": [
        {"id": "TA", "name": "Tibialis Anterior", "diagram": "TA"},
        {"id": "ED", "name": "Extensor Digitorum", "diagram": "ED"},
        {"id": "PER", "name": "Fibularis / Peroneus longus", "diagram": "PER"},
        {"id": "DLPC", "name": "Deep Posterior Compartment (TP + long toe & hallux flexors)", "diagram": "TP"},
        {"id": "POP", "name": "Popliteus", "diagram": None},
        {"id": "SOL", "name": "Soleus", "diagram": "SOL"},
        {"id": "GAS_MED", "name": "Gastrocnemius Medialis", "diagram": "GM"},
        {"id": "GAS_LAT", "name": "Gastrocnemius Lateralis", "diagram": "GL"},
    ],
    "thighs": [
        {"id": "VL", "name": "Vastus Lateralis", "diagram": "VL"},
        {"id": "VI", "name": "Vastus Intermedius", "diagram": "VI"},
        {"id": "VM", "name": "Vastus Medialis", "diagram": "VM"},
        {"id": "RF", "name": "Rectus Femoris", "diagram": "RF"},
        {"id": "SAR", "name": "Sartorius", "diagram": "SAR"},
        {"id": "GRA", "name": "Gracilis", "diagram": "GRA"},
        {"id": "SM", "name": "Semimembranosus", "diagram": "SM"},
        {"id": "ST", "name": "Semitendinosus", "diagram": "ST"},
        {"id": "BF", "name": "Biceps Femoris, long head", "diagram": "BF"},
        {"id": "BF_SH", "name": "Biceps Femoris, short head", "diagram": None},
        {"id": "AM", "name": "Adductor Magnus", "diagram": "AM"},
        {"id": "AL", "name": "Adductor Longus", "diagram": None},
        {"id": "AB", "name": "Adductor Brevis", "diagram": None},
    ],
}


def muscle_ids(segment):
    """Ids of every report muscle of a segment, in the report order."""
    return [m["id"] for m in REPORT_MUSCLES.get(segment, [])]


def diagram_muscle_ids(segment):
    """Ids of the muscles drawn on the segment diagram: the legend and the table rows."""
    return [m["id"] for m in REPORT_MUSCLES.get(segment, []) if m["diagram"]]


MUSCLE_NAMES = {m["id"]: m["name"] for muscles in REPORT_MUSCLES.values() for m in muscles}
