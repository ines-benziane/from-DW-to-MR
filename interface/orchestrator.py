import json
import sys
from pathlib import Path
from models import request
from data_reader import json_reader

config = Path(__file__).parent.parent / "config" / "config.json"

def available_data(methods):
    print (methods)

def parse_version(version):
    if "<=" in version :
        v = version.split("<=")
        return "<=", v[1]
    elif ">=" in version :
        v = version.split(">=")
        return ">=", v[1]
    else :
        return "", version

#charger le fichier de config du rapport médical
with open(config, "r") as f:
    sections  = json.load(f)

patient_id = sys.argv[1]
path = sys.argv[2]
reader = json_reader.JsonReader(patient_id, path)
for section in sections["section"] :
    for method, version in  section["method"].items() :
        operator, v = parse_version(version)
        req = request.SectionRequest(
                section_name = section["section_name"],
                segment = section["segment"],
                method = method,
                version = v,
                operator = operator,
                generate = section["generate"],
                date = section["date"],
                aquisition = section["aquisition"]
            )
        response = reader.fetch_data(req)
        print (response)
    if response.exam != None :
        break
