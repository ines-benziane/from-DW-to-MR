"""
JSON Reader : concrete class
"""
from pathlib import Path
from models import domain, response
from data_reader.reader_interface import ReaderInterface

class JsonReader(ReaderInterface):
    """Reads a json file and writes it into an Exam domain"""

    def fetch_data(self, request):
        if request.date == None :
            files = list(Path(self.path_to_data).glob(f"{self.patient_id}.*.{request.segment}.{request.method}.{request.version}.{request.aquisition}.json"))
            print(print(f"Pattern: {self.patient_id}.*.{request.segment}.{request.method}.{request.version}.json"))
            print(f"No date files : {files}")
            if len(files) > 0 :
                sorted_files = sorted(files, key=lambda f: f.stem.split(".")[1])
                file = sorted_files[-1]
                content = file.read_text()
            else :
                return (response.DataResponse(exam=None))
        else :
            files = list(Path(self.path_to_data).glob(f"{self.patient_id}.{request.date}.{request.segment}.{request.method}.{request.version}.{request.aquisition}.json"))
            if len(files)>0 :
                file = files[0]
                content = file.read_text()
            else :
                return (response.DataResponse(exam=None))
        try : 
            exam_to_send = domain.Exam.model_validate_json(content)
        except :
            print("file corrumpted")
            return response.DataResponse(exam = None)
        return response.DataResponse(exam = exam_to_send)