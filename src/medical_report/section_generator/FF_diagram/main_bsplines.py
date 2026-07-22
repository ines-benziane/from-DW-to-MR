from . import load_svg_data
from . import color
from . import render_bsplines
from medical_report.section_generator.src.infrastructure.color_mappers import BIOMARKER_STAT, COLORMAP_REGISTRY
import numpy as np
import bsplines


def get_all_svg_muscle_ids(svg_file):
    """Retourne la liste des ids de muscles présents dans le SVG
    (tous les paths dont l'id commence par 'muscle_').
    """
    import xml.etree.ElementTree as ET
    ns = 'http://www.w3.org/2000/svg'
    tree = ET.parse(svg_file)
    root = tree.getroot()
    ids = []
    for path in root.iter(f'{{{ns}}}path'):
        path_id = path.get('id', '')
        if path_id.startswith('muscle_'):
            ids.append(path_id)
    return ids

def B_spline_1d(values):
    """Interpolation B-spline sur une liste de scalaires (valeurs FF)."""
    if len(values) < 4:
        return values
    pts = np.array(values)
    spl = bsplines.BSpline.prefilter(pts, degree=3, extension='nearest', axes=[0])
    t_fine = np.linspace(0, len(values) - 1, 300)
    return [float(v) for v in spl(t_fine)]



def get_all_muscles_data(svg_file, svg_id, results, all_muscles_data, biomarker, colormap_name="default"):
    """Store of needed data to generates the final svg (svg id, path)"""
    path_data = load_svg_data.load_svg_path(svg_file, svg_id)
    y_min, y_max = load_svg_data.extract_coord(path_data)
    stat_key = BIOMARKER_STAT.get(biomarker)
    mapper = COLORMAP_REGISTRY.get(colormap_name, COLORMAP_REGISTRY["default"]).get(biomarker)
    values = []
    slice_data = []
    for result in results:
        val = result.stats.get(stat_key)
        if val is not None:
            values.append(float(val))
    values_smooth = [max(0.0, min(1.0, v)) for v in B_spline_1d(values)]
    bands = np.linspace(y_min, y_max, 300)
    for y_value, val in zip(bands, values_smooth):
        ff_color = mapper["function"](val, mapper["palette_name"])
        slice_data.append({'Y': y_value, 'color': ff_color})
    all_muscles_data.append({
        'svg_id': svg_id,
        'path_data': path_data,
        'bands': slice_data,
        'y_min': y_min,
        'y_max': y_max,
    })
    return all_muscles_data


def generate_ff_svg(muscles, svg_file, biomarker='FF', colormap_name="default"):
    """
    muscles : liste de MuscleData (depuis Exam.muscles)
    svg_file : chemin absolu vers le SVG anatomique source
    Retourne un dict {'L': svg_string, 'R': svg_string}
    """
    import xml.etree.ElementTree as ET
    NS = 'http://www.w3.org/2000/svg'
    svg_ids = get_all_svg_muscle_ids(svg_file)
    result = {}
    for side in ['L', 'R']:
        all_muscles_data = []
        for muscle in muscles:
            if muscle.side != side:
                continue
            svg_id = 'muscle_' + muscle.name
            if svg_id not in svg_ids:
                continue
            all_muscles_data = get_all_muscles_data(svg_file, svg_id, muscle.slices, all_muscles_data, biomarker, colormap_name)
        tree = render_bsplines.generate_svg(svg_file, all_muscles_data)
        root = tree.getroot()
        if side == 'L':
            g_parent = root.find(f'.//{{{NS}}}g')
            if g_parent is not None:
                g_parent.set('transform', 'translate(210, 0) scale(-1, 1)')
        root.attrib.pop('width', None)
        root.attrib.pop('height', None)
        result[side] = ET.tostring(root, encoding='unicode')


    return result
