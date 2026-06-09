"""Orchestrator — loads exam data for each section defined in config.json and triggers PDF generation."""

import json
from section_generator import generate_pdf
import sys
from models import domain
from pathlib import Path
from models import request
from data_reader import json_reader

config = Path(__file__).parent.parent / "config" / "config.json"

DEFAULT_DATA_PATH = "json_output"

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

def find_antecedents(patient_id, current_date, section, method, version, path):
    """Retourne les examens antérieurs triés du plus ancien au plus récent."""
    files = list(Path(path).glob(f"{patient_id}_*_{section['segment']}_{method}_{version}_{section['acquisition']}.json"))
    antecedents = []
    for f in files:
        date = f.stem.split("_")[1]
        if date < current_date:
            antecedents.append((date, f))
    antecedents.sort(key=lambda x: x[0])
    return [domain.Exam.model_validate_json(f.read_text()) for _, f in antecedents]


def get_exam(patient_id, path, config_data=None):
    """
    config_data: optional config dict to use instead of reading config.json.
    Enables programmatic config injection (e.g. from batch_compare).
    """
    exams = []
    if config_data is not None:
        sections = config_data
    else:
        with open(config, "r") as f:
            sections = json.load(f)
    reader = json_reader.JsonReader(patient_id, path)
    for section in sections["section"]:
        for method, version in section["method"].items():
            operator, v = parse_version(version)
            versions_available = compatible_versions(patient_id, section, method, v, operator, Path(__file__).parent.parent / path)
            if versions_available:
                version = sorted(versions_available)[-1]
            else:
                continue
            req = request.SectionRequest(
                section_name=section["section_name"],
                segment=section["segment"],
                method=method,
                version=version,
                operator=operator,
                generate=section["generate"],
                date=section["date"],
                acquisition=section["acquisition"],
            )
            response = reader.fetch_data(req)
            response.section_name = section["section_name"]
            if response.exam is not None:
                current_date = response.exam.metadata.exam_date
                response.antecedents = find_antecedents(
                    patient_id, current_date, section, method, version,
                    Path(__file__).parent.parent / path,
                )
                response.template_version = section.get("version")
                exams.append(response)
                break
    return exams


if __name__ == "__main__":
    exams = get_exam(sys.argv[1], sys.argv[2])
    generate_pdf.create_pdf(exams)
