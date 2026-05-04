"""Request models — section search parameters, sourced from config.json."""
from pydantic import BaseModel 
from typing import Literal, Optional

class SectionRequest(BaseModel):
    """Criteria to locate and load data for an exam section."""
    section_name : str
    segment : str
    method : str
    version : str
    operator : str
    generate : bool 
    date : Optional[str] = None
    acquisition : str
