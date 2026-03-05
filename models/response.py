from models.domain import Exam 
from pydantic import BaseModel

class DataResponse(BaseModel):
    exam: Exam
    can_generate : bool 
    is_missing : list[str]

