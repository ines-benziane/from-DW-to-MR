from pathlib import Path
from data_writer.csv_parser import parse_csv
from data_writer.json_writer import JsonWriter

BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "get_results" / "results"
OUTPUT_PATH = BASE_DIR / "json_output"

def main() -> None:
    writer = JsonWriter()
    for result_dir in RESULTS_DIR.iterdir():
        csv_path = result_dir / "results.csv"
        if not csv_path.exists():
            continue
        exam = parse_csv(csv_path)
        writer.write(exam, OUTPUT_PATH)
        print(f"Written {len(exam.muscles)} muscles → {result_dir.name}")

if __name__ == "__main__":
    main()
