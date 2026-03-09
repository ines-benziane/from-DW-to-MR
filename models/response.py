from models.domain import Exam 
from pydantic import BaseModel
from typing import Optional 

class DataResponse(BaseModel):
    exam: Optional[Exam]
