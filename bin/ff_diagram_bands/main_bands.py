import csv
import load_data
import load_svg_data
import linear_interpolation
import color
import render_bands

def csv_name_to_svg_id(csv_name):
    """Convertit un nom CSV (ex: 'VM_R') en id SVG (ex: 'muscle_VM').
    Enlève le dernier suffixe (_R ou _L) et ajoute le préfixe muscle_.
    """
    base = csv_name.rsplit('_', 1)[0]
    return 'muscle_' + base


def get_all_csv_muscles(csv_path):
    """Retourne la liste des noms de muscles uniques dans le CSV
    (qui ont au moins une slice avec NPIX > 0).
    """
    muscles = set()
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for line in reader:
            if float(line['NPIX']) != 0:
                muscles.add(line['LABEL'])
    return list(muscles)


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


if __name__ == '__main__':
    csv_path = 'results/aim.pat001.v1.20161104.thighs_dixon3pt_full/results.csv'
    svg_file = 'FF_diagram/thighs_quadriceps.svg'
    ns = 'http://www.w3.org/2000/svg'
    sides = ['R', 'L']
    for side in sides :

        csv_muscles = [m for m in get_all_csv_muscles(csv_path) if m.endswith('_' + side)]
        svg_ids = get_all_svg_muscle_ids(svg_file)

        muscles_to_process = []
        for csv_name in csv_muscles:
            svg_id = csv_name_to_svg_id(csv_name)
            if svg_id in svg_ids:
                muscles_to_process.append((csv_name, svg_id))

        print(f"Muscles à traiter : {[m[0] for m in muscles_to_process]}")

        all_muscles_data = []
        for csv_name, svg_id in muscles_to_process:
            results = load_data.load_muscle_result(csv_path, csv_name)
            if len(results) == 0:
                print(f"  {csv_name} : aucune slice valide, ignoré")
                continue
            z_min, z_max = load_data.extract_z_corrd(results)

            path_data = load_svg_data.load_svg_path(svg_file, svg_id)
            y_min, y_max = load_svg_data.extract_coord(path_data)

            slice_data = []
            for result in results:
                z_value = float(result['Z'])
                y_value = linear_interpolation.linear_interpolation(z_min, z_max, y_min, y_max, z_value)
                ff_color = color.ff_to_color(float(result['FF']))
                slice_data.append({'Y': y_value, 'FF': result['FF'], 'color': ff_color})

            all_muscles_data.append({
                'svg_id': svg_id,
                'path_data': path_data,
                'bands': slice_data,
                'y_min': y_min,
                'y_max': y_max,
            })
            print(f"  {csv_name} -> {svg_id} : {len(slice_data)} slices")


        tree = render_bands.generate_svg(svg_file, all_muscles_data)
        root = tree.getroot()
        if side == 'L':
            g_parent = root.find(f'.//{{{ns}}}g')
            g_parent.set('transform', 'translate(210, 0) scale(-1, 1)')
        tree.write('output' + side +'.svg', xml_declaration=True, encoding='unicode')
        print(f"SVG généré : output.svg ({len(all_muscles_data)} muscles colorés)")