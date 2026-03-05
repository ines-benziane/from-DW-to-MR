from pydantic import BaseModel 
from typing import Literal

class StatRequest(BaseModel):
    name : str
    scope : Literal["volume", "slice", "both"]
    required : bool 

class SectionRequest(BaseModel):
    stats : list[StatRequest]
    segment : str
    method : str
