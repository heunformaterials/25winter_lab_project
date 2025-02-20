import os
import re
import week4_function
from scripts import add_adsrobate_to_poscar, vasp_process, find_adsorbate_site


# Helper function: 디렉토리 생성
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

# Helper function: layer information 정리
def layer_info_from_path(layer_pattern, file_path):
    dir_path = os.path.normpath(os.path.dirname(file_path)).replace(os.sep, "/")

    # raw_data_directory 제거 후 상대 경로만 추출
    relative_path = os.path.relpath(dir_path, raw_data_directory).replace(os.sep, "/")

    # 정규식 매칭
    layer_match = layer_pattern.match(relative_path)
    if not layer_match:
        raise ValueError(f"File path '{dir_path}' does not match the expected pattern.")

    sorted_poscar_lines, sorted_coords = week4_function.sort_poscar_lines(file_path)
    top_site, bridge_site, hollow_site = find_adsorbate_site.find_adsorbate_site(layer_match.group(1), sorted_coords)

    return {
        "plane_type": layer_match.group(1),
        "slab_matrix": layer_match.group(2) + 'x' + layer_match.group(3),
        "layer_number": layer_match.group(4),
        "sorted_poscar_lines": sorted_poscar_lines,
        "top_site": top_site,
        "bridge_site": bridge_site,
        "hollow_site": hollow_site
    }

# POSCAR_out.vasp와 CONTCAR 확인 및 처리
def is_here_poscar_out(root, files):
    if 'POSCAR_out.vasp' not in files and 'CONTCAR' in files:
        contcar_path = os.path.join(root, 'CONTCAR')
        try:
            vasp_process.extract_cartesian_coordinates(contcar_path)
            print(f"Created POSCAR_out.vasp in {root}")
        except Exception as e:
            print(f"Error processing CONTCAR in {root}: {e}")

# 디렉토리 구조 생성
def make_directory_structure(output_poscar_path, plane_type, slab_matrix, layer_number):
    dir_structure = [output_poscar_path, plane_type, slab_matrix, layer_number]
    full_path = os.path.join(*dir_structure)
    create_directory(full_path)
    return full_path

#main function
def week4_preprocessing(raw_data_directory, output_poscar_path):
    import os
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_poscar_path), exist_ok=True)

    layer_pattern = re.compile(r"(\d+)[\\/](\d+)x(\d+)[\\/](\d+)_layer")
    for root, dirs, files in os.walk(raw_data_directory):
        # POSCAR_out.vasp와 CONTCAR의 존재 여부 확인 & POSCAR_out.vasp가 없는 경우 CONTCAR를 처리
        is_here_poscar_out(root, files)

        for file in files:
            # 3x3 slab만 만들도록 코드 제한
            if file == 'POSCAR_out.vasp':
                file_path = os.path.join(root, file)
                try:
                    # 3x3 slab만 만들도록 코드 제한
                    dir_path = os.path.normpath(os.path.dirname(file_path)).replace(os.sep, "/")
                    relative_path = os.path.relpath(dir_path, raw_data_directory).replace(os.sep, "/")
                    layer_match = layer_pattern.match(relative_path)
                    slab_matrix = int(layer_match.group(2))
                    if slab_matrix <= 2:
                        continue

                    layer_info = layer_info_from_path(layer_pattern, file_path)
                    adsorbates = ['H', 'H2', 'O']

                    for a_info in adsorbates:
                        # layer info에 대한 디렉토리 생성
                        dir_path = make_directory_structure(
                            output_poscar_path,
                            layer_info["plane_type"],
                            layer_info["slab_matrix"],
                            layer_info["layer_number"],
                        )
                        #adsorbate에 대한 디렉토리 생성
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
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


# 실행
raw_data_directory = 'data/week4_raw_POSCAR'
output_file_path = '../data/week4_processed_POSCAR'
week4_preprocessing(raw_data_directory, output_file_path)


