import xml.etree.ElementTree as ET
from .color import ff_to_color


NS = 'http://www.w3.org/2000/svg'

def get_zone_gradient(defs, height, proportion, ff_min, ff_max, n_stops, grad_id):
    zone_height = height * proportion
    gradient = ET.SubElement(defs, f'{{{NS}}}linearGradient')
    gradient.set('id', grad_id)
    gradient.set('x1', '0')
    gradient.set('x2', '0')
    gradient.set('y1', '0')
    gradient.set('y2', '1')

    for i in range(n_stops + 1):
        t = i / n_stops
        ff = ff_min + t * (ff_max - ff_min)
        hex_color = ff_to_color(ff)

        stop = ET.SubElement(gradient, f'{{{NS}}}stop')
        stop.set('offset', f'{t * 100:.1f}%')
        stop.set('stop-color', hex_color)
    return zone_height


def draw_border(parent, width, height, x, y):
    border = ET.SubElement(parent, f'{{{NS}}}rect')
    border.set('x', str(x))
    border.set('y', str(y))
    border.set('width', str(width))
    border.set('height', str(height))
    border.set('fill', 'none')
    border.set('stroke', '#333333')
    border.set('stroke-width', '0.3')


def apply_labels(x, y, width, height, parent):
    labels = [
        (0.0, '0%'),
        (0.10, '5%'),
    ]
    for ff_pct in range(10, 45, 5):
        t_in_zone = (ff_pct / 100.0 - 0.05) / (0.40 - 0.05)
        pos = 0.10 + t_in_zone * 0.80 
        labels.append((pos, f'{ff_pct}%'))
    labels.append((1.0, '100%'))

    label_x = x + width + 3
    for t, text in labels:
        label_y = y + t * height
        txt = ET.SubElement(parent, f'{{{NS}}}text')
        txt.set('x', str(label_x))
        txt.set('y', str(label_y + 1))
        txt.set('font-size', '5')
        txt.set('font-family', 'Arial, sans-serif')
        txt.set('fill', '#333333')
        txt.text = text


def set_title(x, y, parent, width):
    title = ET.SubElement(parent, f'{{{NS}}}text')
    title.set('x', str(x + width / 2))
    title.set('y', str(y - 3))
    title.set('font-size', '5')
    title.set('font-family', 'Arial, saNS-serif')
    title.set('fill', '#333333')
    title.set('text-anchor', 'middle')
    title.text = 'FF'


def add_colorbar(parent, defs, x=180, y=40, width=10, height=200, n_stops=30):
    zones = [
        (0.0,  0.05, 0.10, 'colorbar_grad_1'),
        (0.05, 0.40, 0.80, 'colorbar_grad_2'),
        (0.40, 1.00, 0.10, 'colorbar_grad_3'),
    ]
    current_y = y

    for ff_min, ff_max, proportion, grad_id in zones:
        zone_height = get_zone_gradient(defs, height, proportion, ff_min, ff_max, n_stops, grad_id)
        
        rect = ET.SubElement(parent, f'{{{NS}}}rect')
        rect.set('x', str(x))
        rect.set('y', str(current_y))
        rect.set('width', str(width))
        rect.set('height', str(zone_height))
        rect.set('fill', f'url(#{grad_id})')

        current_y += zone_height

    draw_border(parent, width, height, x, y)
    apply_labels(x, y, width, height, parent)
    set_title(x, y, parent, width)
    