from models.domain import Exam 
from pydantic import BaseModel
from typing import Optional 

class DataResponse(BaseModel):
    exam: Optional[Exam]
    template_version: Optional[str] = None
    antecedents: list[Exam] = []
    section_name : Optional[str] = None
