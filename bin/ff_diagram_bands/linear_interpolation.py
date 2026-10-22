import load_data
import load_svg_data

def linear_interpolation (z_min, z_max, y_min, y_max, z_value) :
    if z_max == z_min : 
        print("Warning: z_max and z_min are the same.")
        return
    t = (z_value - z_min) / (z_max - z_min)
    y_value = y_min + t * (y_max - y_min)
    return y_value

# if __name__ == '__main__':
#     # load data
#     csv_path = 'results/aim.pat001.v1.20161104.thighs_dixon3pt_full/results.csv'
#     muscle_name = 'GRA_R'
#     results = load_data.load_muscle_result(csv_path, muscle_name)
#     z_min, z_max = load_data.extract_z_corrd(results)

#     # load svg data
#     svg_file = 'FF_diagram/thighs_quadriceps.svg'
#     muscle_name = 'muscle_VM'
#     path_data = load_svg_data.load_svg_path(svg_file, muscle_name)
#     y_min, y_max = load_svg_data.extract_coord(path_data)

#     # linear interpolation
#     for result in results :
#         z_value = float(result['Z'])
#         y_value = linear_interpolation(z_min, z_max, y_min, y_max, z_value)
#         print(f"Z: {z_value}, Y: {y_value}")
