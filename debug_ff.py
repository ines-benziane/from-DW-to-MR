import json
from pathlib import Path
from medical_report.data_reader import json_reader
from medical_report.models import domain

config_path = Path("config/config.json")
sections = json.loads(config_path.read_text())["section"]

for section in sections:
    for method, version_str in section["method"].items():
        files = list(Path("json_output").glob(
            f"pat001_*_{section['segment']}_{method}_*_{section['acquisition']}.json"
        ))
        if files:
            sorted_files = sorted(files, key=lambda f: f.stem.split("_")[1])
            latest = sorted_files[-1]
            exam = domain.Exam.model_validate_json(latest.read_text())
            print(f"biomarker={exam.metadata.biomarker} | section_name={section['section_name']} | version_config={section.get('version')} | method={method} | file={latest.name}")
        else:
            print(f"NO FILE for {section['segment']} {method}")
        break
