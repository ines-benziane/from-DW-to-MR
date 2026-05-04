import csv
import os
import sys

def load_muscle_result(csv_path : str, muscle_name : str) -> list :
    """Retrieve all csv lines of one muscle"""
    results = []
    if not os.path.exists(csv_path):
        print(f"File {csv_path} does not exist.")
        sys.exit(1)
    try :
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',')
            for line in reader : 
                if line['LABEL'] == muscle_name and float(line['NPIX']) != 0:
                    results.append(line)

    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return results


def extract_z_coord(results : list) :
    all_z=[]
    for result in results :
        all_z.append(float(result['Z']))
    z_min = min(all_z)
    z_max = max(all_z)
    return z_min, z_max

# if __name__ == '__main__':
#     csv_path = 'results/aim.pat001.v1.20161104.thighs_dixon3pt_full/results.csv'
#     muscle_name = 'GRA_R'
#     results = load_muscle_result(csv_path, muscle_name)
#     z_min, z_max = extract_z_coord(results)
#     print(f"Zmin: {z_min}, Zmax: {z_max}")
#     print(results[:1])

