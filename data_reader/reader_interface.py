"""Reader interface — abstract port for data persistence."""

from abc import ABC, abstractmethod
from pathlib import Path
from models.request import SectionRequest
from models.response import DataResponse


class ReaderInterface(ABC):
    """Abstract Reader"""

    def __init__(self, patient_id,path_to_data):
        self.patient_id = patient_id
        self.path_to_data = path_to_data

    @abstractmethod
    def fetch_data(self, request: SectionRequest) -> DataResponse:
        """Receive StatRequest, cross requested data with DB/JSON, send DataResponse"""
        ...
