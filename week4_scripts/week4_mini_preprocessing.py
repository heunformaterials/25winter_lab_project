import os
import week4_function
from scripts import add_adsrobate_to_poscar, find_adsorbate_site


# Helper function: 디렉토리 생성
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

# 디렉토리 구조 생성
def make_directory_structure(output_poscar_path, plane_type, slab_matrix, layer_number):
    dir_structure = [output_poscar_path, plane_type, slab_matrix, layer_number]
    full_path = os.path.join(*dir_structure)
    create_directory(full_path)
    return full_path

#main function
def week4_mini_preprocessing(raw_data_directory, output_poscar_path):
    import os
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_poscar_path), exist_ok=True)

    #file_path 정의
    for root, dirs, files in os.walk(raw_data_directory):
        for file in files:
            if file == 'POSCAR_out.vasp':
                raw_data_file_path = os.path.join(root, file)

    #3x3 file을 갖고 오자..
    ref_data_file_path = 'week4_mini_preprocessing/ref/POSCAR_out.vasp'

    #기초 변수
    sorted_poscar_lines, sorted_coords = week4_function.sort_poscar_lines(raw_data_file_path)
    ref_sorted_poscar_lines, ref_sorted_coords = week4_function.sort_poscar_lines(ref_data_file_path)

    adsorbates = ['H', 'H2', 'O']
    plane_type = input('enter the plane_type (ex. 211): ')
    #ref로부터 adsorbate site 추출
    top_site, bridge_site, hollow_site = find_adsorbate_site.find_adsorbate_site(plane_type, ref_sorted_coords)

    layer_info = {
        "plane_type": plane_type,
        "slab_matrix": input('enter the slab_matrix (ex. 2x2): '),
        "layer_number": input('enter the layer_number (ex. 6): '),
        "sorted_poscar_lines": sorted_poscar_lines,
        "top_site": top_site,
        "bridge_site": bridge_site,
        "hollow_site": hollow_site

    }

    # layer info에 대한 디렉토리 생성
    dir_path = make_directory_structure(
        output_poscar_path,
        layer_info["plane_type"],
        layer_info["slab_matrix"],
        layer_info["layer_number"],
    )

    for a_info in adsorbates:
        # layer_info에 추가로 adsorbate에 대한 디렉토리 생성
        adsorbate_dir = os.path.join(dir_path, a_info)
        create_directory(adsorbate_dir)

        # POSCAR 업데이트
        add_adsrobate_to_poscar.add_adsorbate_to_site(
            a_info,
            layer_info["sorted_poscar_lines"],
            adsorbate_dir,
            layer_info["top_site"],
            layer_info["bridge_site"],
            layer_info["hollow_site"],
        )


# 실행
raw_data_directory = 'week4_mini_preprocessing/raw'
output_file_path = 'week4_mini_preprocessing/preprocessed'
week4_mini_preprocessing(raw_data_directory, output_file_path)
