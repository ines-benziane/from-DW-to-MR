"""Scientific color mapper using Crameri palettes"""
from cmcrameri import cm


def get_evolution_color_from_palette(evolution, palette_name='broc', min_percent=-30, max_percent=30):
    """
    Map evolution percentage to a color from a scientific palette.

    Args:
        evolution: MuscleEvolution object
        palette_name: Name of the palette ('roma', 'broc', 'vik', etc.)
        min_percent: Minimum percentage for color mapping (default: -30%)
        max_percent: Maximum percentage for color mapping (default: +30%)

    Returns:
        RGB color string in format "rgb(r, g, b)"
    """
    # Get the palette
    palette_map = {
        'roma': cm.roma,
        'broc': cm.broc,
        'vik': cm.vik,
        'berlin': cm.berlin,
        'cork': cm.cork,
        'bam': cm.bam
    }

    if palette_name not in palette_map:
        raise ValueError(f"Unknown palette: {palette_name}. Available: {list(palette_map.keys())}")

    palette = palette_map[palette_name]

    # Get percentage change
    percent = evolution.percentage_change

    if percent < -5 :
        source_min = min_percent
        target_min = 0.0
        target_max = 0.4
        source_max = -5

        percent_clamped = max(source_min, min(source_max, percent))
        relative_position = (percent_clamped - source_min) / (source_max - source_min)
        normalized = target_min + (relative_position * (target_max - target_min))

    elif percent >= -5 and percent <= 5 :
        target_min = 0.3
        target_max = 0.7
        source_min = -5
        source_max = 5
        percent_clamped = max(source_min, min(source_max, percent))
        relative_position = (percent_clamped - source_min) / (source_max - source_min)
        normalized = target_min + (relative_position * (target_max - target_min))

    else :
        target_min = 0.6
        target_max = 1
        source_min = -5
        source_max = max_percent
        percent_clamped = max(source_min, min(source_max, percent))
        relative_position = (percent_clamped - source_min) / (source_max - source_min)
        normalized = target_min + (relative_position * (target_max - target_min))

    # Get RGBA color from palette
    rgba = palette(normalized)
    r, g, b, a = rgba

    # Convert to RGB string (0-255)
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"