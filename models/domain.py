""" Domain models for exam results"""

from pydantic import BaseModel, field_validator
from typing import Optional, Literal
import json

class SliceData(BaseModel):
    """Statistics for a single muscle on a single axial slice."""
    index: str 
    x: float
    y: float
    z: float
    stats: dict[str, float] = {}
    outline: Optional[list[list[float]]] = None
    @field_validator("outline", mode="before")
    @classmethod
    def _parse_outline(cls, value: str) -> Optional[list[list[float]]]:
        """Parse the OUTLINE column — a JSON-encoded list of [x, y] pairs."""
        if not isinstance(value, str) :
            return value
        value = value.strip()
        if not value:
            return None
        return json.loads(value)

class VolumeData(BaseModel):
    """Aggregated statistics for a muscle over the whole volume."""
    stats: dict[str, float] = {}

class MuscleData(BaseModel):
    """A single muscle with its volume summary and per-slice Datas."""
    name: str  
    side: Literal["L", "R"]
    volume: Optional[VolumeData] = None
    slices: list[SliceData] = []

class ExamMetadata(BaseModel):
    """Have to determine where the metadata are coming from """
    patient_id: str
    exam_date : str
    segment : str
    method: str
    version : str
    aquisition : str
    segmentation: str



class Exam(BaseModel):
    """Root domain object — one exam, one biomarker. """
    muscles: list[MuscleData]
    metadata: ExamMetadata
