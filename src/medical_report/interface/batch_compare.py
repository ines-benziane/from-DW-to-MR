"""
Batch compare — generates one PDF per template version per section for a given patient.

For each section defined in config.json, discovers all template versions available on disk
and generates an independent PDF for each (section × version) combination.

Usage:
    python -m interface.batch_compare <exam_id> [data_path]

Output:
    section_generator/reports/<exam_id>/
        T2_5slices_thighs_default.pdf   ← template without version folder
        T2_5slices_thighs_v2.pdf
        T2_5slices_thighs_v3.pdf
        FF_5slices_thighs_v1.pdf
        ...
"""

import json
import sys
from pathlib import Path

from medical_report.interface.orchestrator import get_exam, config as DEFAULT_CONFIG
from medical_report.section_generator import generate_pdf

TEMPLATES_ROOT = Path(__file__).parent.parent / "section_generator" / "templates"
REPORTS_ROOT = Path(__file__).parent.parent / "section_generator" / "reports"


def _discover_versions(biomarker: str, section_name: str, segment: str) -> list[str | None]:
    """
    Scan templates/{biomarker}/{section_name}/{segment}/ and return all available
    template version identifiers.

    Returns None for the default (no-version) template, and strings like "v2", "v3"
    for versioned sub-folders.
    """
    base = TEMPLATES_ROOT / biomarker / section_name / segment
    if not base.exists():
        return []

    versions: list[str | None] = []

    if (base / "section_design.html").exists():
        versions.append(None)  # default, no version folder

    for p in sorted(base.iterdir()):
        if p.is_dir() and (p / "section_design.html").exists():
            versions.append(p.name)

    return versions


def _version_label(version: str | None) -> str:
    return version if version else "default"


def batch_compare(exam_id: str, data_path: str, lang: str = "en") -> None:
    with open(DEFAULT_CONFIG) as f:
        base_config = json.load(f)

    output_dir = REPORTS_ROOT / exam_id
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for section in base_config["section"]:
        biomarker = section["biomarker"]
        section_name = section["section_name"]
        segment = section["segment"]

        versions = _discover_versions(biomarker, section_name, segment)
        if not versions:
            print(f"  [{biomarker}/{section_name}/{segment}] No templates found, skipping.")
            continue

        for version in versions:
            label = _version_label(version)
            output_name = f"{biomarker}_{section_name}_{segment}_{label}.pdf"

            # Build a single-section config with the target template version
            section_override = {**section, "version": version}
            config_data = {"section": [section_override]}

            exams = get_exam(exam_id, data_path, config_data=config_data)
            if not exams:
                print(f"  [{biomarker}/{section_name}/{segment}] No data for {label}, skipping.")
                continue

            print(f"  Generating {output_name} …", end=" ", flush=True)
            generate_pdf.create_pdf(
                exams,
                output_name=output_name,
                output_dir=str(output_dir),
                save_html=False,
                lang=lang,
            )
            print("OK")
            total += 1

    print(f"\n{total} report(s) saved to {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m interface.batch_compare <exam_id> [data_path]")
        sys.exit(1)

    _exam_id = sys.argv[1]
    _data_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "json_output"
    _lang = next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--lang" and i + 1 < len(sys.argv)), "fr")
    batch_compare(_exam_id, _data_path, lang=_lang)
