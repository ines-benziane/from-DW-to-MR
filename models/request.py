from pydantic import BaseModel 
from typing import Literal, Optional

class SectionRequest(BaseModel):
    section_name : str
    segment : str
    method : str
    version : str
    operator : str
    generate : bool 
    date : Optional[str] = None
    acquisition : str
