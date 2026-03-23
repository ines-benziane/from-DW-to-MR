"""
JSON Writer — concrete class
"""

from pathlib import Path

from models.domain  import Exam
from data_writer.writer_interface import WriterInterface

class JsonWriter(WriterInterface):
    """Writes an Exam domain object to a JSON file."""

    def write(self, exam: Exam, destination: Path) -> None:
        """Serialize the Exam to JSON and write to destination."""
        if destination.is_dir() or not destination.suffix:
            # filename = f"{exam.metadata.patient_id}.{exam.metadata.segment}.{exam.metadata.method}.{exam.metadata.version}.{exam.metadata.exam_date}.json"
            filename = f"{exam.metadata.patient_id}.{exam.metadata.exam_date}.{exam.metadata.segment}.{exam.metadata.method}.{exam.metadata.version}.{exam.metadata.acquisition}.json"
            destination = destination / filename 
        data = exam.model_dump_json(exclude_none=True, indent=2)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as f:
            f.write(data)
