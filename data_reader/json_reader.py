"""
JSON Reader : concrete class
"""
from pathlib import Path
from models import domain, response
from data_reader.reader_interface import ReaderInterface

class JsonReader(ReaderInterface):
    """Reads a json file and writes it into an Exam domain"""
    def _no_date(self, request) :
        if request.flexibility == "strict" :
            files = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.{request.version}.*.json"))
        elif request.flexibility == "version" :
            files = []
            try :
                for version in request.compatible_versions :
                    files.extend(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.{version}.*.json"))
            except :
                print("No compatible versions")
        elif request.flexibility =="method" :
            files = []
            try : 
                for method in  request.compatible_methods :
                    files.extend(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{method}.*.*.json"))
            except :
                print("No compatible methods")
        sorted_files = sorted(files, key = lambda f: f.stem.split(".")[-1])
        return sorted_files


    def _with_date(self, request):
        if request.flexibility == "strict" :
            file = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.{request.version}.{request.date}.json"))
        elif request.flexibility == "version" :
            try :
                for version in request.compatible_versions :
                    file = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{request.method}.{version}.{request.date}.json"))
                    if file :
                        return file
            except :
                print("No compatible version")
                return[]
        elif request.flexibility =="method" :
            try :
                for method in request.compatible_methods :
                    file = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.segment}.{method}.*.{request.date}.json"))
                    if file : 
                        return file
            except :
                print("No compatible methods")
                return []
        return file


    def fetch_data(self, request):
        if request.date == None :
            sorted_files = self._no_date(request)
            if len(sorted_files) > 0 :
                file = sorted_files[-1]
                content = file.read_text()
            else :
                return (response.DataResponse(exam=None))  
        else :
            file = self._with_date(request)
            if len(file)>0 :
                file = file[0]
                content = file.read_text()
            else :
                return (response.DataResponse(exam=None))
        try : 
            exam_to_send = domain.Exam.model_validate_json(content)
        except :
            print("file corrumpted")    #error handling will be done later 
            return response.DataResponse(exam = None)
        return response.DataResponse(exam = exam_to_send)