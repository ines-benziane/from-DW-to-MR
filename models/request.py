from pydantic import BaseModel 
from typing import Literal, Optional

class SectionRequest(BaseModel):
    section_name : str
    segment : str
    method : str
    version : str
    flexibility : Literal["strict", "version", "method"]
    generate : bool 
    date : Optional[str] = None
    compatible_methods : Optional[list[str]] = None
