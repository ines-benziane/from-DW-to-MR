import json
import os
import sys
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import base64
import mimetypes

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
            print(f"Configuration loaded : {config}")
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
import unicodedata

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

def transform_by_slice(muscles):
    """
        Permet la transition entre l'objet "Exam" reçu, qui a une structure "muscle centric" avec ce module le section generator qui a
        une structure par slice 
    """
    slices_map =  {}
    slices = []
    for muscle in muscles:
        for s in muscle["slices"] :
            if s["index"] not in slices_map :
                slices_map[s["index"]] = {"muscles": []}
            if s["outline"] == None or s["outline"] == "": 
                svg_path = ""
            else :  
                svg_path = points_to_line_path(s["outline"])
            slices_map[s["index"]]["muscles"].append(
                {"id": muscle["name"],
                "side": muscle["side"],
                "stats" : s["stats"],
                "outline" : svg_path}
            )
    for key, value in slices_map.items() :
        slices.append({"muscles": value["muscles"], "slices": {"number": key}})
    print(f"Muscle: {muscle['name']}, Side: {muscle['side']}, Stats: {s['stats']}, outline : {svg_path}")
    return  slices

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
            results = transform_by_slice(cleaned_exam["muscles"])
            all_sections.append({
                "results": results, 
                "acquisition": cleaned_exam["metadata"]
            })
            patient_metadata = cleaned_exam["metadata"]

        template_data = {
            "all_reports": all_sections,
            "header": {
                "report_title": "Compte-rendu d'examen",
                "lab_address" : "Institut de Myologie Batiment Babinski",
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

