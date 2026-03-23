import json
from section_generator import generate_pdf
import sys
from pathlib import Path
from models import request
from data_reader import json_reader

config = Path(__file__).parent.parent / "config" / "config.json"

def data_found(patient_id, section, path):
    found = {}
    for method, version in section["method"].items():
        operator, v = parse_version(version)
        versions = compatible_versions(patient_id, section, method, v, operator, path)
        if versions:
            found[method] = versions
    return found

def compatible_versions(patient_id, section, method, version,  operator, path):
    files = list(Path(path).glob(f"{patient_id}_*_{section["segment"]}_{method}_*_{section["acquisition"]}.json"))
    final = []
    versions = []
    for f in files :
        versions.append(f.stem.split("_")[4])
    if operator == ">=" :
        for v in versions :
            if float(v) >= float(version) :
                final.append(v)
    elif operator == "<=":
        for v in versions :
            if float(v) <= float(version) :
                final.append(v)
    else:
        if version in versions:
            final.append(version)
    return final
    
def parse_version(version):
    if "<=" in version :
        v = version.split("<=")
        return "<=", v[1]
    elif ">=" in version :
        v = version.split(">=")
        return ">=", v[1]
    else :
        return "", version

def get_exam(patient_id, path) :
    exams = []
    with open(config, "r") as f:
        sections  = json.load(f)
        print (sections)
    reader = json_reader.JsonReader(patient_id, path)
    for section in sections["section"] :
        available = data_found(patient_id, section, Path(__file__).parent.parent / path)
        print(f"Section {section['section_name']}: {available}")
        for method, version in section["method"].items() :
            operator, v = parse_version(version)
            versions_available = compatible_versions( patient_id, section, method, v, operator, Path(__file__).parent.parent / path)
            if versions_available :
                version = sorted(versions_available)[-1]
            else :
                continue
            req = request.SectionRequest(
                    section_name = section["section_name"],
                    segment = section["segment"],
                    method = method,
                    version = version,
                    operator = operator,
                    generate = section["generate"],
                    date = section["date"],
                    acquisition = section["acquisition"]
                )
            response = reader.fetch_data(req)
            if response.exam != None :
                exams.append(response)
                break
    return exams



exams = get_exam(sys.argv[1], sys.argv[2])
print(sys.argv[1], sys.argv[2])
generate_pdf.create_pdf(exams)
