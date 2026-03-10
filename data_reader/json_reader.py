"""
JSON Reader : concrete class
"""
from pathlib import Path
from models import domain, response
from data_reader.reader_interface import ReaderInterface

def no_date(self, request) :
    if request.flexibility == "strict" :
        files = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.{request.version}.*.json"))
    elif request.flexibility == "version" :
        files = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.*.*.json"))
    elif request.flexibility =="method" :
        files = []
        for method in  request.compatible_methods :
            files.extend(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{method}.*.*.json"))
    sorted_files = sorted(files, key = lambda f: f.stem.split(".")[-1])
    return sorted_files


def with_date(self, request):
    if request.flexibility == "strict" :
        file = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.{request.version}.{request.date}.json"))
    elif request.flexibility == "version" :
        file = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.*.{request.date}.json"))
    elif request.flexibility =="method" :
        for method in request.compatible_methods :
            file = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{method}.*.{request.date}.json"))
            if file : 
                return file
    return file


class JsonReader(ReaderInterface):
    """Reads a json file and writes it into an Exam domain"""
    def fetch_data(self, request):
        if request.generate == False :

        if request.date == None :
            sorted_files = no_date(self, request)
            if len(sorted_files) > 0 :
                file = sorted_files[-1]
                content = file.read_text()
            else :
                return (domain.DataResponse(exam=None))  
        else :
            file = with_date(self, request)
            if len(file)>0 :
                file = file[0]
                content = file.read_text()
            else :
                return (domain.DataResponse(exam=None))
            
        Render = domain.Exam.model_validate_json(content)
        return response.DataResponse(Render)