import xml.etree.ElementTree as ET
from colorbar import add_colorbar

def delete_colors(ns, root) :
    for path in root.iter(f'{{{ns}}}path'):
        path_id = path.get('id', '')
        if path_id.startswith('muscle_'):
            style = path.get('style', '')
            parts = style.split(';')
            new_parts = []
            for part in parts:
                key_value = part.strip().split(':')
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    if key == 'fill':
                        new_parts.append('fill:none')
                    elif key == 'fill-opacity':
                        new_parts.append('fill-opacity:1')
                    else :
                        new_parts.append(part.strip())
            path.set('style', ';'.join(new_parts))

def bands(all_muscles_data, parent, ns) :
    for muscle_data in all_muscles_data:
        bands = muscle_data['bands']
        if len(bands) == 0:
            continue
        band_height = (muscle_data['y_max'] - muscle_data['y_min']) / len(bands)
        g_bands = ET.SubElement(parent, f'{{{ns}}}g')
        g_bands.set('clip-path', 'url(#clip_' + muscle_data['svg_id'] + ')')
        for band in bands:
            rect = ET.SubElement(g_bands, f'{{{ns}}}rect')
            rect.set('x', '0')
            rect.set('y', str(band['Y']))
            rect.set('width', '300')
            rect.set('height', str(band_height + 0.5))
            rect.set('fill', band['color'])

def generate_svg(svg_file, all_muscles_data):
    """ Load original svg, delete colors,  applies bands. """
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
    ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
    ET.register_namespace('svg', 'http://www.w3.org/2000/svg')
    tree = ET.parse(svg_file)
    root = tree.getroot()
    delete_colors(ns, root)
    g_parent = root.find(f'.//{{{ns}}}g')
    defs = ET.SubElement(root, f'{{{ns}}}defs')
    for muscle_data in all_muscles_data:
        clip_path = ET.SubElement(defs, f'{{{ns}}}clipPath')
        clip_path.set('id', 'clip_' + muscle_data['svg_id'])
        clip_elem = ET.SubElement(clip_path, f'{{{ns}}}path')
        clip_elem.set('d', muscle_data['path_data'])
    parent = g_parent if g_parent is not None else root
    bands(all_muscles_data, parent, ns)
    add_colorbar(parent, defs)
    return tree


# if __name__ == '__main__':
#     print("Ce module ne s'exécute pas seul. Utilisez main.py.")