import xml.etree.ElementTree as ET
import re

def muscle_hight (matches):
    current_y = 0
    all_y = []
    i = 0
    while i < len(matches):
        if matches[i] == 'm' :
            i += 2
            current_y = float(matches[i])
            all_y.append(current_y)
            i += 1
        elif matches[i] == 'c' :
            i += 1
            while i < len(matches) and not matches[i].isalpha():
                i += 5
                current_y =  current_y + float(matches[i])
                all_y.append(current_y)
                i += 1
        else :
            i += 1
    
    y_min = min(all_y)
    y_max = max(all_y)
    return y_min, y_max

def extract_coord(path_data):
    regex = r'[a-zA-Z]|[-+]?\d*\.?\d+'
    matches = re.findall(regex, path_data)
    ymin, ymax = muscle_hight(matches)
    return ymin, ymax

def load_svg_path (svg_file : str, muscle_name : str) -> str :
    tree = ET.parse(svg_file)
    root = tree.getroot()
    for path in root.iter('{http://www.w3.org/2000/svg}path'):
        if muscle_name == path.get('id', ''):
            return path.get('d', '')

        
# if __name__ == '__main__':
#     svg_file = 'FF_diagram/thighs_quadriceps.svg'
#     muscle_name = 'muscle_VM'
#     path_data = load_svg_path(svg_file, muscle_name)
#     ymin, ymax = extract_coord(path_data)
#     print(f"Ymin: {ymin}, Ymax: {ymax}")