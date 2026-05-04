"""
Establish a personnalized color_map for T2 values using Crameri palette vik.
Very small T2 values are neutral (medical incertainty = visual neutrality).
T2 between healthy_low_limit and pathologcal_limits are blue.
Above pathological_limit is red.
"""
from cmcrameri import cm
from PIL import Image
import io
import base64
from section_generator.FF_diagram.color import ff_to_color as ff_to_color_raw, FF_ZONES

T2_MEAN_MIN = 10
T2_MEAN_MAX = 60
LOW_THRESHOLD = 24
HIGH_THRESHOLD = 39

BIOMARKER_STAT = {
    "T2": "T2-mean",
    "FF": "FF",
}

BIOMARKER_RANGE = {
    "T2": (T2_MEAN_MIN, T2_MEAN_MAX),
    "FF": (0.0, 1.0),
}

def get_color_from_FF(FF_mean: float, palette_name=None) -> str:
    return ff_to_color_raw(FF_mean)


def get_color_from_T2_mean(T2_mean : float, palette_name) :
    palette_map = {
        'roma': cm.roma,
        'broc': cm.broc,
        'vik': cm.vik,
        'berlin': cm.berlin,
        'cork': cm.cork,
        'bam': cm.bam, 
        "vikO": cm.vikO
    }
    if palette_name not in palette_map:
        raise ValueError(f"Unknown palette: {palette_name}. Available: {list(palette_map.keys())}")
    palette = palette_map[palette_name]
    if T2_mean < LOW_THRESHOLD :
        # t = (T2_mean - T2_MEAN_MIN) / (LOW_THRESHOLD - T2_MEAN_MIN)
        # normalized = 0.51 + t * (0.48 - 0.51)
        return "rgb(180, 180, 180)"
    elif T2_mean >= LOW_THRESHOLD and T2_mean < HIGH_THRESHOLD :
        t = (T2_mean - LOW_THRESHOLD) / (HIGH_THRESHOLD - LOW_THRESHOLD)
        normalized = 0.0 + t * (0.45 - 0.0)
    else :
        t = (T2_mean - HIGH_THRESHOLD) / (T2_MEAN_MAX - HIGH_THRESHOLD)
        normalized = 0.51 + t * (1 - 0.51)
    rgba = palette(normalized)
    r, g, b, a = rgba
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"


def get_color_from_T2_mean_lajolla(T2_mean: float, palette_name: str) -> str:
    palette_map = {
        'roma': cm.roma,
        'broc': cm.broc,
        'vik': cm.vik,
        'berlin': cm.berlin,
        'cork': cm.cork,
        'bam': cm.bam,
        "vikO": cm.vikO
    }
    if palette_name not in palette_map:
        raise ValueError(f"Unknown palette: {palette_name}. Available: {list(palette_map.keys())}")
    palette = palette_map[palette_name]

    LAJOLLA_T2_LOW = 37
    LAJOLLA_T2_HIGH = 41
    LAJOLLA_NORM_START = 0.90  # T2=37 → jaune très clair (fin de lajolla)
    LAJOLLA_NORM_END = 0.60    # T2=41 → jaune doré (milieu de lajolla)

    if T2_mean < LOW_THRESHOLD:
        return "rgb(180, 180, 180)"
    elif T2_mean < LAJOLLA_T2_LOW:
        t = (T2_mean - LOW_THRESHOLD) / (HIGH_THRESHOLD - LOW_THRESHOLD)
        normalized = 0.0 + t * (0.45 - 0.0)
        rgba = palette(normalized)
    elif T2_mean <= LAJOLLA_T2_HIGH:
        t = (T2_mean - LAJOLLA_T2_LOW) / (LAJOLLA_T2_HIGH - LAJOLLA_T2_LOW)
        normalized = LAJOLLA_NORM_START + t * (LAJOLLA_NORM_END - LAJOLLA_NORM_START)
        rgba = cm.lajolla(normalized)
    else:
        t = (T2_mean - HIGH_THRESHOLD) / (T2_MEAN_MAX - HIGH_THRESHOLD)
        normalized = 0.65 + t * (1 - 0.65)
        rgba = palette(normalized)
    r, g, b, a = rgba
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"


def get_color_from_T2_mean_simple_version(T2_mean : float, palette_name) :
    palette_map = {
        'roma': cm.roma,
        'broc': cm.broc,
        'vik': cm.vik,
        'berlin': cm.berlin,
        'cork': cm.cork,
        'bam': cm.bam, 
        "vikO": cm.vikO,
        "tokyo": cm.tokyo, 
        "batlow": cm.batlow
    }
    if palette_name not in palette_map:
        raise ValueError(f"Unknown palette: {palette_name}. Available: {list(palette_map.keys())}")
    palette = palette_map[palette_name]
    if T2_mean < LOW_THRESHOLD :
        return "rgb(180, 180, 180)"
    else :
        t = (T2_mean - LOW_THRESHOLD) / (T2_MEAN_MAX - LOW_THRESHOLD)
    # rgba = palette(1 - t) #si on veut inverser la palette
    rgba = palette(t)
    r, g, b, a = rgba
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"


if __name__ == "__main__":
    for t2 in [15, 20, 24, 30, 35, 39, 42, 50, 55]:
        print(f"T2={t2} → {get_color_from_T2_mean(t2, 'vikO')}")


def get_color(biomarker, stats):
    stat_key = BIOMARKER_STAT.get(biomarker)
    if stat_key is None :
        return "rgb(150, 150, 150)"
    value = stats.get(stat_key)
    if value is None :
        return "rgb(150, 150, 150)"
    mapper = BIOMARKER_MAPPER.get(biomarker)
    color = mapper["function"](value, mapper["palette_name"])
    if color :
        return color
    else :
        return "rgb(150, 150, 150)"



def generate_colorbar_image(biomarker, width=500):
    """Generates a colorbar as a base64-encoded PNG using the exact same color function as the muscles."""
    mapper = BIOMARKER_MAPPER.get(biomarker)
    if mapper is None:
        return ""

    img = Image.new("RGB", (width, 1))
    zones = mapper.get("zones")
    if zones:
        pixels = []
        for ff_min, ff_max, proportion in zones:
            zone_width = int(width * proportion)
            for i in range(zone_width):
                t = i / max(zone_width - 1, 1)
                pixels.append(ff_min + t * (ff_max - ff_min))
        while len(pixels) < width:
            pixels.append(pixels[-1])
        pixels = pixels[:width]
    else:
        val_min, val_max = BIOMARKER_RANGE.get(biomarker, (T2_MEAN_MIN, T2_MEAN_MAX))
        pixels = [val_min + (x / (width - 1)) * (val_max - val_min) for x in range(width)]

    for x, value in enumerate(pixels):
        color_val = mapper["function"](value, mapper["palette_name"])
        if color_val.startswith("#"):
            r, g, b = int(color_val[1:3], 16), int(color_val[3:5], 16), int(color_val[5:7], 16)
        else:
            nums = color_val.replace("rgb(", "").replace(")", "").split(",")
            r, g, b = int(nums[0].strip()), int(nums[1].strip()), int(nums[2].strip())
        img.putpixel((x, 0), (r, g, b))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


BIOMARKER_MAPPER = {
    # "T2": {"function" : get_color_from_T2_mean, "palette_name" : "vikO"}, #la color map est split en différentes zones
    # "T2": {"function" : get_color_from_T2_mean_simple_version, "palette_name" : "batlow"},
    "T2": {"function" : get_color_from_T2_mean_lajolla, "palette_name" : "vikO"},
    # "T2": {"function" : get_color_from_T2_mean, "palette_name" : "vikO"},
    "FF": {"function": get_color_from_FF, "palette_name": None, "zones": FF_ZONES}

}
