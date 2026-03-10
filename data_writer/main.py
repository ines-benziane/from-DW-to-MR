"""
DataWriter entry point.
Orchestrates: CSV parsing → domain objects → persistence (JSON or DB).
"""

from pathlib import Path

from data_writer.csv_parser import parse_csv
from data_writer.json_writer import JsonWriter

BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR.parent / "results_data" / "aim.pat001.v1.20161104.thighs_dixon3pt_full" / "results.csv"
OUTPUT_PATH = BASE_DIR / "json_output"

def main() -> None:
    """Main pipeline: read CSV → build Exam → write JSON."""

    exam = parse_csv(Path(CSV_PATH), "meth", "segmentation", "patient_id") #Sera géré par l'orchestrateur plus tard
    writer = JsonWriter()
    writer.write(exam, Path(OUTPUT_PATH))
    print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
