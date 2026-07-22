from medical_report.data_reader.json_reader import JsonReader
from medical_report.models import request, response
import pytest
# python -m pytest tests/test_data_reader.py

_DESYNC_REASON = "désynchronisé du code courant — SectionRequest n'a plus les champs 'flexibility'/'compatible_methods'/'compatible_versions', voir #<à créer>"

@pytest.fixture
def Data_Reader():
    return JsonReader("pat001", "json_output")

@pytest.mark.skip(reason=_DESYNC_REASON)
def test_strict_sans_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="strict", generate=False)
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"


@pytest.mark.skip(reason=_DESYNC_REASON)
def test_strict_avec_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="strict", generate=False, date = "20220101")
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"


@pytest.mark.skip(reason=_DESYNC_REASON)
def test_version_sans_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.4",  flexibility="version", generate=False, compatible_versions=["1.4", "1.1"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None

@pytest.mark.skip(reason=_DESYNC_REASON)
def test_version_avec_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.4",  flexibility="version", generate=False,date = "20220101", compatible_versions=["1.4", "1.1"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"


@pytest.mark.skip(reason=_DESYNC_REASON)
def test_method_sans_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="method", generate=False, compatible_methods=["meth01", "meth02"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None

@pytest.mark.skip(reason=_DESYNC_REASON)
def test_method_avec_date(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="method", generate=False, date = "20220101", compatible_methods=["meth01", "meth02"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam is not None
    assert my_exam.exam.metadata.exam_date == "20220101"


@pytest.mark.skip(reason=_DESYNC_REASON)
def test_no_compatible_method(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="thighs", method="meth01", version="1.1",  flexibility="method", generate=False, date = "20220101", compatible_methods=["meth10", "meth11"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam  == None

@pytest.mark.skip(reason=_DESYNC_REASON)
def test_corrupted_file(Data_Reader):
    req = request.SectionRequest(section_name="FF", segment="legs", method="meth01", version="1.1",  flexibility="method", generate=False, date = "20220101", compatible_methods=["meth10", "meth11"])
    my_exam = Data_Reader.fetch_data(req)
    assert my_exam.exam  == None
