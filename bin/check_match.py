from Pydantic import BaseModel 

class check_match(BaseModel):
    def __init__(self, section_name, method, version) :
        self.section_name = section_name
        self.method = method
        self.version = version 

    def get_matching_methods():
        """
            Look into the stats required by the section and identifies a list of methods and version compatible.
            Input : section_name. Output : list of the matching methods for the section
        """
        ...
    def is_a_match():
        """
            Search correspondance between required methods and matching methods for the section.
            Check if methods are compatible or not.
        """
        
    
    def not_matching():
        """
            If i_a_match() founds an uncompatible method for the required section, delets it. 
        """
