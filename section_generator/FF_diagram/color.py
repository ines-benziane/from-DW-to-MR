from cmcrameri import cm

FF_ZONES = [
    (0.0,  0.05, 0.10),  # (ff_min, ff_max, proportion de la barre)
    (0.05, 0.40, 0.80),
    (0.40, 1.0,  0.10),
]

# FF_PALETTE = cm.vik
# FF_PALETTE = cm.glasgow_r
# FF_PALETTE = cm.hawaii_r
# FF_PALETTE = cm.tokyo_r
# FF_PALETTE = cm.batlowW
# FF_PALETTE = cm.bamako
FF_PALETTE = cm.lajolla_r


def ff_to_color(ff: float) -> str:
    if ff < 0 or ff > 1:
        print('Warning: FF value should be between 0 and 1.')
        return '#000000'
    if ff <= 0.05:
        r, g, b, a = FF_PALETTE(0.0)
    elif ff <= 0.40:
        t = (ff - 0.05) / (0.4 - 0.05)
        r, g, b, a = FF_PALETTE(t)
    else:
        r, g, b, a = FF_PALETTE(1.0)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"