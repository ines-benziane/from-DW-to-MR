from cmcrameri import cm

FF_ZONES = [
    (0.0,  0.05, 0.10),  # (ff_min, ff_max, proportion de la barre)
    (0.05, 0.40, 0.80),
    (0.40, 1.0,  0.10),
]

FF_PALETTE = cm.lajolla_r


def _ff_to_color_with(ff: float, palette, max_pos=0.6) -> str:
    if ff < 0 or ff > 1:
        return '#000000'
    if ff <= 0.05:
        r, g, b, a = palette(0.0)
    elif ff <= 0.40:
        t = (ff - 0.05) / (0.40 - 0.05)
        r, g, b, a = palette(t * max_pos)
    else:
        r, g, b, a = palette(max_pos)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def ff_to_color(ff: float) -> str:
    if ff < 0 or ff > 1:
        print('Warning: FF value should be between 0 and 1.')
        return '#000000'
    return _ff_to_color_with(ff, FF_PALETTE)


def ff_to_color_lapaz(ff: float, _palette_name=None) -> str:
    return _ff_to_color_with(ff, cm.lapaz, max_pos=1.0)


def ff_to_color_davos(ff: float, _palette_name=None) -> str:
    return _ff_to_color_with(ff, cm.davos, max_pos=1.0)


def ff_to_color_grayscale(ff: float, _palette_name=None) -> str:
    if ff < 0 or ff > 1:
        return '#000000'
    v = int(ff * 255)
    return f"#{v:02x}{v:02x}{v:02x}"