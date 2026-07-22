import csv
import json 
import bsplines
import numpy as np 


def extract_contours(file_path):
    contours = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            outline = row.get('OUTLINE', '').strip()
            if not outline:
                continue
            try:
                parsed = json.loads(outline)
                if isinstance(parsed, list) and isinstance(parsed[0], list):
                    contours.append(parsed)
            except (json.JSONDecodeError, IndexError):
                continue
    return contours

# https://www.youtube.com/watch?v=ueUgHvUT2Z0


def B_spline(points):
    cleaned = [points[0]]
    for p in points[1:]:
        if p != cleaned[-1]:
            cleaned.append(p)
    if len(cleaned) < 4:
        return points

    pts = np.array(cleaned)  

    spl = bsplines.bspline(pts, degree=3, axes=[0], s=5,  extension='true-periodic')

    t_fine = np.linspace(0,  spl.shape[0] - 1, 200)
    pts_smooth = spl(t_fine)

    return [(float(x), float(y)) for x, y in pts_smooth]


def points_to_line_path(points):
    first = points[0]
    m = f"M {first[0]},{first[1]}"
    l = " ".join(f"L {x},{y}" for x, y in points[1:])
    return f"{m} {l} Z"


def contours_to_svg(contours):
    all_points = [p for contour in contours for p in contour]
    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    padding = 2
    min_x = min(xs) - padding
    min_y = min(ys) - padding
    width = max(xs) - min_x + padding
    height = max(ys) - min_y + padding

    paths = "\n".join(
        f'  <path d="{points_to_line_path(points)}" fill="white" stroke="black" stroke-width="0.1"/>'
        for points in contours
    )

    return f'''<svg viewBox="{min_x} {min_y} {width} {height}" xmlns="http://www.w3.org/2000/svg">
{paths}
</svg>'''

if __name__ == "__main__":
    contours = [B_spline(contour) for contour in extract_contours('outlines0.csv')]
    print(f"{len(contours)} contour(s) trouvé(s)")
    svg = contours_to_svg(contours)
    with open('output25.svg', 'w') as f:
        f.write(svg)


