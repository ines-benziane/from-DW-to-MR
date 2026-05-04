import json
import os
import sys
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import base64
import unicodedata
import mimetypes
from section_generator.src.infrastructure.color_mappers import get_color, generate_colorbar_image
from tools.smooth_outlines import B_spline
from section_generator.FF_diagram.main_bsplines import generate_ff_svg


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config/report_config.json")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
TEMPLATE_FILE = "report_template.html"
STYLE_FILE = os.path.join(os.path.dirname(__file__), "styles/report_styles.css")
OUTPUT_FILE = "Medical_report.pdf"
DEBUG_HTML_FILE = "report.html"


def clean_nan_values(data):
    if data is None:
        return ''  
    if (isinstance(data, float) and (data != data
                                     or data == float('inf')
                                     or data == float('-inf'))):
        return ''
    if isinstance(data, dict):
        return {k: clean_nan_values(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_nan_values(elem) for elem in data]
    return data


def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # print(f"Configuration loaded : {config}")
            return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}.")
        return {"sequences_to_include": []}
    except json.JSONDecodeError:
        print(f"Error: Configuration file {config_path} is not a valid JSON.")
        return {"sequences_to_include": []}


def generate_html(data):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html_output = template.render(data=data, **data)
    return html_output

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Encoding mistake {e}.")

def save_debug_file(html_content, filename, base_path):
    try:
        debug_path = os.path.join(base_path, filename)
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        print(f"Impossible to save debug file : {e}")

def export_to_pdf(html_content, base_path, output_name, css_rel_path):
    html_doc = HTML(string=html_content, base_url=base_path)
    css_path = os.path.join(base_path, css_rel_path)
    if os.path.exists(css_path):
        css = CSS(filename=css_path)
        html_doc.write_pdf(os.path.join(base_path, output_name), stylesheets=[css])
    else:
        print(f'{"File not found at {css_path}."}')
        html_doc.write_pdf(os.path.join(base_path, output_name))

def normalize(text):
    if not text: return ""
    text = str(text).lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def set_logo(data, base_path, image_encoder):
    logo_path = os.path.join(base_path, 'images', 'logo.jpg')
    if os.path.exists(logo_path):
        data["header"]['logo_base64_uri'] = image_encoder(logo_path)
    else:
        data["header"]['logo_base64_uri'] = ''

def points_to_line_path(points):
    first = points[0]
    m = f"M {first[0]},{first[1]}"
    l = " ".join(f"L {x},{y}" for x, y in points[1:])
    return f"{m} {l} Z"

def transform_by_slice(muscles, biomarker):
    """
        Permet la transition entre l'objet "Exam" reçu, qui a une structure "muscle centric" avec ce module le section generator qui a
        une structure par slice 
    """
    slices_map =  {}
    slices = []
    for muscle in muscles:
        for s in muscle["slices"] :
            if s["index"] not in slices_map :
                slices_map[s["index"]] = {"muscles": [], "points_L": [], "points_R": [], "z": s["z"]}
            if s["outline"] == None or s["outline"] == "":
                svg_path = ""
            else :
                smoothed = B_spline(s["outline"])
                svg_path = points_to_line_path(smoothed)
            if muscle["side"] == "L" and s["outline"] :
                slices_map[s["index"]]["points_L"].extend(s["outline"])
            elif muscle["side"] == "R" and s["outline"]:
                slices_map[s["index"]]["points_R"].extend(s["outline"])
            slices_map[s["index"]]["muscles"].append(
                {"id": muscle["name"],
                "side": muscle["side"],
                "stats" : s["stats"],
                "path" : svg_path,
                "color": get_color(biomarker, s["stats"])}
            )
    for key, value in slices_map.items() :
        padding = 2
        if value["points_L"]:
            min_x_L = min(p[0] for p in value["points_L"]) - padding
            min_y_L = min(p[1] for p in value["points_L"]) - padding
            max_x_L = max(p[0] for p in value["points_L"]) + padding
            max_y_L = max(p[1] for p in value["points_L"]) + padding
            viewbox_L = f"{min_x_L} {min_y_L} {max_x_L - min_x_L} {max_y_L - min_y_L}"
            mirror_tx_L = min_x_L + max_x_L
        else:
            viewbox_L = "0 0 600 600"
            mirror_tx_L = 0
        if value["points_R"]:
            min_x_R = min(p[0] for p in value["points_R"]) - padding
            min_y_R = min(p[1] for p in value["points_R"]) - padding
            max_x_R = max(p[0] for p in value["points_R"]) + padding
            max_y_R = max(p[1] for p in value["points_R"]) + padding
            viewbox_R = f"{min_x_R} {min_y_R} {max_x_R - min_x_R} {max_y_R - min_y_R}"
            mirror_tx_R = min_x_R + max_x_R
        else:
            viewbox_R = "0 0 600 600"
            mirror_tx_R = 0

        slices.append({
            "muscles": value["muscles"],
            "slices": {"number": key, "z": value["z"]},
            "viewbox_L": viewbox_L,
            "viewbox_R": viewbox_R,
            "mirror_tx_L": mirror_tx_L,
            "mirror_tx_R": mirror_tx_R
        })

    slices.sort(key=lambda s: s["slices"]["z"], reverse=True)
    if slices:
        z_max = slices[0]["slices"]["z"]
        for s in slices:
            distance_mm = z_max - s["slices"]["z"]
            s["slices"]["distance_cm"] = round(distance_mm / 10,1)
    return slices

def build_summary_slice(slices):
    """Construit une slice synthétique : géométrie de la slice du milieu, T2-mean moyenné sur toutes les slices."""
    if not slices:
        return None

    middle = slices[len(slices) // 2]

    t2_sums = {}
    t2_counts = {}
    for s in slices:
        for muscle in s["muscles"]:
            key = (muscle["id"], muscle["side"])
            val = muscle["stats"].get("T2-mean")
            if isinstance(val, (int, float)):
                t2_sums[key] = t2_sums.get(key, 0) + val
                t2_counts[key] = t2_counts.get(key, 0) + 1

    averaged_muscles = []
    for muscle in middle["muscles"]:
        key = (muscle["id"], muscle["side"])
        avg = t2_sums[key] / t2_counts[key] if t2_counts.get(key) else None
        averaged_muscles.append({
            "id": muscle["id"],
            "side": muscle["side"],
            "stats": {"T2-mean": avg},
            "path": muscle["path"],
        })

    return {
        "muscles": averaged_muscles,
        "slices": middle["slices"],
        "viewbox_L": middle["viewbox_L"],
        "viewbox_R": middle["viewbox_R"],
        "mirror_tx_L": middle["mirror_tx_L"],
        "mirror_tx_R": middle["mirror_tx_R"],
    }


def build_volume_slice(slices, muscles_raw, biomarker):
    """Utile pour 1 slice : j'utilise la stat présente dans le volume et pas une moyenne de slices"""
    if not slices:
        return None
    
    middle = slices[len(slices) // 2]
    
    result_muscles = []
    for muscle in middle["muscles"]:
        raw = next((m for m in muscles_raw if m["name"] == muscle["id"] and m["side"] == muscle["side"]), None)
        if raw is None :
            continue
        volume_stats = raw["volume"]["stats"]
        color = get_color(biomarker, volume_stats)
        result_muscles.append({
            "id": muscle["id"],
            "side": muscle["side"],
            "stats": volume_stats,
            "path": muscle["path"],
            "color": color,
        })
    
    return {
        "muscles": result_muscles,
        "slices": middle["slices"],
        "viewbox_L": middle["viewbox_L"],
        "viewbox_R": middle["viewbox_R"],
        "mirror_tx_L": middle["mirror_tx_L"],
        "mirror_tx_R": middle["mirror_tx_R"],
    }


def create_pdf(exams): #exams = list d'examens. 1 examen = 1 section.
    base_path = os.path.abspath(os.path.dirname(__file__))
    try:
        config = load_config(os.path.join(base_path, CONFIG_FILE))
        all_sections = []
        memory = {}
        patient_metadata = None
        for exam in exams:
            exam_dict = exam.exam.model_dump()
            cleaned_exam = clean_nan_values(exam_dict)
            biomarker = cleaned_exam["metadata"]["biomarker"]

            if biomarker == "FF":
                svg_anterior = generate_ff_svg(
                    exam.exam.muscles,
                    os.path.join(base_path, "FF_diagram", "thighs_quadriceps.svg")
                )
                svg_posterior = generate_ff_svg(
                    exam.exam.muscles,
                    os.path.join(base_path, "FF_diagram", "hamstring.svg")
                )
                results = transform_by_slice(cleaned_exam["muscles"], "FF") 
                section_name = exam.section_name
                if section_name == "1slice":
                    summary = build_volume_slice(results, cleaned_exam["muscles"], "FF")
                else:
                    summary = None
                if exam.antecedents:
                    ant = exam.antecedents[-1]
                    ant_dict = clean_nan_values(ant.model_dump())
                    ant_results = transform_by_slice(ant_dict["muscles"], "FF")
                    antecedent_slice = build_volume_slice(ant_results, ant_dict["muscles"], "FF")
                    antecedent_date = ant_dict["metadata"]["exam_date"]
                else:
                    antecedent_slice = None
                    antecedent_date = None
                all_sections.append({
                    "acquisition": cleaned_exam["metadata"],
                    "template_version": exam.template_version,
                    "anterior": {"superficial": svg_anterior, "deep": None},
                    "posterior": {"superficial": svg_posterior, "deep": None},
                    "colorbar": generate_colorbar_image("FF"),
                    "results": results,
                    "summary_slice": summary,
                    "antecedent_slice": antecedent_slice,
                    "antecedent_date": antecedent_date,
                    "section_name" : exam.section_name                })
            else:
                results = transform_by_slice(cleaned_exam["muscles"], biomarker)
                section_name = exam.section_name
                if section_name == "1slice":
                    summary = build_volume_slice(results, cleaned_exam["muscles"], biomarker)
                else:
                    summary = None
                if exam.antecedents:
                    ant = exam.antecedents[-1]
                    ant_dict = clean_nan_values(ant.model_dump())
                    ant_results = transform_by_slice(ant_dict["muscles"], biomarker)
                    antecedent_slice = build_volume_slice(ant_results, ant_dict["muscles"], biomarker)
                    antecedent_date = ant_dict["metadata"]["exam_date"]
                else:
                    antecedent_slice = None
                    antecedent_date = None
                all_sections.append({
                    "results": results,
                    "summary_slice": summary,
                    "antecedent_slice": antecedent_slice,
                    "antecedent_date": antecedent_date,
                    "acquisition": cleaned_exam["metadata"],
                    "template_version": exam.template_version,
                    "colorbar": generate_colorbar_image(biomarker),
                    "section_name" : exam.section_name
                })
            patient_metadata = cleaned_exam["metadata"]

        template_data = {
            "all_reports": all_sections,
            "header": {
                "report_title": "Compte-rendu d'examen",
                "lab_address" : "Institut de Myologie<br> Hôpital Universitaire La Pitié-Salpêtrière<br> Bâtiment Babinski 47/83 Bd de l’hôpital<br> 75013 Paris",
                "logo_base64_uri" : ""
                },
            "patient": patient_metadata,
            "acquisition" : patient_metadata
        }
        set_logo(template_data, base_path, get_image_base64)
        html_content = generate_html(template_data)
        save_debug_file(html_content, DEBUG_HTML_FILE, base_path)
        export_to_pdf(html_content, base_path, OUTPUT_FILE, 'styles/report_styles.css')

    except Exception as e:
        print(f'\n--- ERREUR CRITIQUE ---')
        print(f"Détail : {e}")
        import traceback
        traceback.print_exc(file=sys.stdout)