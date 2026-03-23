"""
DataWriter entry point.
Orchestrates: CSV parsing → domain objects → persistence (JSON or DB).
"""

from pathlib import Path

from data_writer.csv_parser import parse_csv
from data_writer.json_writer import JsonWriter

BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / "results_data" / "aim.pat001.v1.20161104.thighs_t2map_3exp" / "results.csv"
OUTPUT_PATH = BASE_DIR / "json_output"

def main() -> None:
    """Main pipeline: read CSV → build Exam → write JSON."""

    exam = parse_csv(Path(CSV_PATH), "patient_id", "exam_date", "segment", "meth",  "version", "acquisiton", "section_name") #Sera géré par l'orchestrateur plus tard

    writer = JsonWriter()
    writer.write(exam, Path(OUTPUT_PATH))
    print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")

    exam = parse_csv(Path(CSV_PATH), "pat001", "20260312", "thighs", "t2map", "1.4", "1.0", "T2")
    writer.write(exam, Path(OUTPUT_PATH))
    print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")

    exam = parse_csv(Path(CSV_PATH), "pat001", "20260312", "thighs", "t2map-2epg", "1.0", "1.0", "T2")
    writer.write(exam, Path(OUTPUT_PATH))
    print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")

    exam = parse_csv(Path(CSV_PATH), "pat001", "20260312", "thighs", "t2map-2epg", "2.1", "1.0", "T2")
    writer.write(exam, Path(OUTPUT_PATH))
    print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")

    # exam = parse_csv(Path(CSV_PATH), "pat001", "20260312", "thighs", "dixon3pts", "1.1", "1.0", "FF")
    # writer.write(exam, Path(OUTPUT_PATH))
    # print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")

    
    # exam = parse_csv(Path(CSV_PATH), "pat002", "20260312", "thighs", "dixon3pts", "1.3", "1.0", "FF")
    # writer.write(exam, Path(OUTPUT_PATH))
    # print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")

    
    # exam = parse_csv(Path(CSV_PATH), "pat001", "20260312", "thighs", "t1map-mrf", "1.0", "1.0", "T1")
    # writer.write(exam, Path(OUTPUT_PATH))
    # print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")
    
    
    # exam = parse_csv(Path(CSV_PATH), "pat001", "20260312", "thighs", "t1map-mrf", "2.0", "1.0", "T1")
    # writer.write(exam, Path(OUTPUT_PATH))
    # print(f"Written {len(exam.muscles)} muscles to {OUTPUT_PATH}")

    

if __name__ == "__main__":
    main()
