"""
Batch presets — generates one PDF per (preset × synthesis_version) for a given patient.

Reads all preset configs from config/presets/ and generates a full report (T2 + FF together)
for each preset. Presets with "synthesis": false generate a single PDF without synthesis
version looping.

Usage:
    python -m interface.batch_presets <patient_id> [data_path]
    python -m interface.batch_presets <patient_id> [data_path] --quick
    python -m interface.batch_presets <patient_id> [data_path] --colormap default

Options:
    --quick              Only generate complet_synth-v1 for each colormap (fast colormap review mode)
    --colormap <name>    Only generate reports for this colormap (e.g. default, hawaii_r, lapaz)

Output:
    section_generator/reports/<patient_id>/
        1slice.pdf
        compact_synth-v1.pdf
        compact_synth-v2.pdf
        complet_synth-v1.pdf
        complet_synth-v2.pdf
"""

import json
import sys
from pathlib import Path

from medical_report.interface.orchestrator import get_exam
from medical_report.section_generator import generate_pdf

PRESETS_DIR = Path(__file__).parent.parent / "config" / "presets"
REPORTS_ROOT = Path(__file__).parent.parent / "section_generator" / "reports"
SYNTHESIS_VERSIONS = ["v1", "v2"]
COLORMAPS = ["default", "hawaii_r", "roma_r", "bam_r", "lapaz", "davos", "grayscale"]

QUICK_PRESET = "complet"
QUICK_SYNTH_VERSION = "v1"

VERSION_NAMES = {
    ("1slice",    None): "1A",
    ("1slice_v2", None): "1B",
    ("compact",   "v1"): "2A",
    ("compact",   "v2"): "2B",
    ("complet",   "v1"): "3A",
    ("complet",   "v2"): "3B",
}


def get_output_name(preset_name: str, synth_version, colormap: str) -> str:
    version = VERSION_NAMES.get((preset_name, synth_version), f"{preset_name}_{synth_version or ''}")
    cm_suffix = f"_{colormap}" if colormap != "default" else ""
    return f"{version}{cm_suffix}.pdf"


def batch_presets(patient_id: str, data_path: str, quick: bool = False, colormap_filter: str = None, lang: str = "fr") -> None:
    output_dir = REPORTS_ROOT / patient_id
    output_dir.mkdir(parents=True, exist_ok=True)

    preset_files = sorted(PRESETS_DIR.glob("*.json"))
    if not preset_files:
        print(f"No preset configs found in {PRESETS_DIR}")
        return

    if quick:
        preset_files = [p for p in preset_files if p.stem == QUICK_PRESET]
        if not preset_files:
            print(f"[quick] No preset named '{QUICK_PRESET}' found.")
            return
        print(f"[quick mode] Only generating {QUICK_PRESET}_synth-{QUICK_SYNTH_VERSION} for all colormaps.")

    active_colormaps = [colormap_filter] if colormap_filter else COLORMAPS
    if colormap_filter and colormap_filter not in COLORMAPS:
        print(f"Unknown colormap '{colormap_filter}'. Available: {COLORMAPS}")
        return

    total = 0
    for preset_path in preset_files:
        preset_name = preset_path.stem
        with open(preset_path) as f:
            config_data = json.load(f)

        exams = get_exam(patient_id, data_path, config_data=config_data)
        if not exams:
            print(f"[{preset_name}] No data found, skipping.")
            continue

        for colormap in active_colormaps:
            if config_data.get("synthesis") is False:
                if quick:
                    continue
                output_name = get_output_name(preset_name, None, colormap)
                print(f"  Generating {output_name} …", end=" ", flush=True)
                generate_pdf.create_pdf(
                    exams,
                    output_name=output_name,
                    output_dir=str(output_dir),
                    synthesis_version=None,
                    save_html=False,
                    colormap_name=colormap,
                    lang=lang,
                )
                print("OK")
                total += 1
            else:
                synth_versions = [QUICK_SYNTH_VERSION] if quick else SYNTHESIS_VERSIONS
                for synth_version in synth_versions:
                    output_name = get_output_name(preset_name, synth_version, colormap)
                    print(f"  Generating {output_name} …", end=" ", flush=True)
                    generate_pdf.create_pdf(
                        exams,
                        output_name=output_name,
                        output_dir=str(output_dir),
                        synthesis_version=synth_version,
                        save_html=False,
                        colormap_name=colormap,
                        lang=lang,
                    )
                    print("OK")
                    total += 1

    print(f"\n{total} report(s) saved to {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m interface.batch_presets <patient_id> [data_path] [--quick]")
        sys.exit(1)

    _patient_id = sys.argv[1]
    _data_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "json_output"
    _quick = "--quick" in sys.argv
    _colormap = next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--colormap" and i + 1 < len(sys.argv)), None)
    _lang = next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--lang" and i + 1 < len(sys.argv)), "fr")
    batch_presets(_patient_id, _data_path, quick=_quick, colormap_filter=_colormap, lang=_lang)
