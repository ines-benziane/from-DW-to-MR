from Pydantic import BaseModel 

class check_match(BaseModel):
    def __init__(self, section_name, method, version) :
        self.section_name = section_name
        self.method = method
        self.version = version 

    def get_matching_methods():
        