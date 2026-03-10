from models import request, response
from data_reader.json_reader import JsonReader
import pytest

@pytest.fixture
def Data_Reader():
    return JsonReader("pat001", "json_output")
    
def test_strict_sans_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="strict", generate=False)
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"


def test_strict_avec_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="strict", generate=False, date = "20220101")
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"


def test_version_sans_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.4",  flexibility="version", generate=False, compatible_versions=["1.4", "1.1"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None

def test_version_avec_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.4",  flexibility="version", generate=False,date = "20220101", compatible_versions=["1.4", "1.1"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"


def test_method_sans_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="method", generate=False, compatible_methods=["meth01", "meth02"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None

def test_method_avec_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="method", generate=False, date = "20220101", compatible_methods=["meth01", "meth02"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"
    
    
def test_no_compatible_method(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="method", generate=False, date = "20220101", compatible_methods=["meth10", "meth11"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam  == None

def test_corrupted_file(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="legs", method="meth01", version="1.1",  flexibility="method", generate=False, date = "20220101", compatible_methods=["meth10", "meth11"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam  == None
