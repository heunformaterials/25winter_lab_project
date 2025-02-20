"""
3 주차 surface energy와 layer distance 변화를 계산하기 위한 함수 모음

"""
import os
import re

# Function to process POSCAR files to get original layer_interval
def read_original_layer_distance(file_path):
    OG_height = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for _ in range(4):
                if lines:
                    line_index = -1
                    while True:
                        if abs(line_index) > len(lines):
                            print("No more lines to check.")
                            print(file_path)
                            break
                        line = lines[line_index].strip()
                        values = line.split()
                        if len(values) >= 3:
                            new_value = float(values[2])
                            if len(OG_height) == 0 or OG_height[-1] > new_value:
                                OG_height.append(new_value)
                                break
                            else:
                                line_index -= 1
                        else:
                            line_index -= 1
                else:
                    print("The file is empty or no lines were read.")
    except Exception as e:
        print(f"Error processing POSCAR file at {file_path}: {e}")
    return OG_height

# Function to process POSCAR_out.vasp files to get result layer_interval
def read_result_layer_distance(file_path):
    RS_height = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for _ in range(4):
                if lines:
                    line_index = -1
                    while True:
                        if abs(line_index) > len(lines):
                            print("No more lines to check.")
                            break
                        line = lines[line_index].strip()
                        values = line.split()
                        if len(values) >= 3:
                            new_value = float(values[2])
                            if len(RS_height) == 0 or RS_height[-1] > new_value:
                                RS_height.append(new_value)
                                break
                            else:
                                line_index -= 1
                        else:
                            line_index -= 1
                else:
                    print("The file is empty or no lines were read.")
    except Exception as e:
        print(f"Error processing POSCAR_out.vasp file at {file_path}: {e}")
    return RS_height

# Function to process OSZICAR files to get layer_info and surface energy
def extract_energy_from_oszicar(file_path, layer_pattern):

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            e0_value = None

            # 파일이 비어 있는 경우 처리
            if not lines:
                e0_value = "File is empty"
            else:
                while lines:
                    last_line = lines.pop().strip()  # 마지막 줄을 제거하면서 읽음
                    match = re.search(r"E0=\s*([-\.\dE+]+)", last_line)
                    if match:
                        e0_value = float(match.group(1))
                        break
                else:
                    e0_value = "Not Found"

            layer_info_plane = "Not Found"
            layer_info_matrix = "Not Found"
            layer_info_number = "Not Found"
            layer_match = layer_pattern.search(file_path)

            #파일 경로에서 layer 정보 할당 및 표면 에너지 계산
            if layer_match:
                layer_info_plane = int(layer_match.group(1))
                layer_info_matrix = layer_match.group(2) + 'x' + layer_match.group(3)
                A_coefficient = int(layer_match.group(2))

                layer_info_number = int(layer_match.group(4))
                N_layer = int(layer_info_number)
                # N_slab 값 할당
                N_slab = A_coefficient**2 * N_layer

                #layer_info_plane 값에 따른 면적 할당
                if layer_info_plane == 111:
                    A = 5.705775672
                elif layer_info_plane == 110:
                    A = 9.317484
                elif layer_info_plane == 100:
                    A = 13.1769
                    N_slab = N_slab * 2
                else:
                    A = 0 # 유효하지 않은 plane 처리

                #e0_bulk 선언
                e0_bulk = -3.729872

                if isinstance(e0_value, (int, float)):
                    surface_energy = 1 / (2 * A * A_coefficient**2) * (e0_value - N_slab * e0_bulk)
                else:
                    surface_energy = "Calculation Error"

            return {
                "E0 Value[eV]": e0_value,
                "Layer Plane": layer_info_plane,
                "Layer Matrix Info": layer_info_matrix,
                "Layers": layer_info_number,
                "Surface Energy": surface_energy,
                "N_slab": N_slab
            }
    except Exception as e:
        print(f"Error processing OSZICAR file at {file_path}: {e}")
        return {
            "E0 Value": f"Could not read file: {e}",
            "Layer Plane": "Error",
            "Layer Matrix Info": "Error",
            "Layers": "Error"
        }

# Function to process 'Direct' CONTCOR files to get 'Cartesian Coordination' as POSCAR_out.vasp
def extract_cartesian_coordinates(file_path):
    import os
    import numpy as np
    """
    POSCAR 파일에서 lattice parameters와 Direct 좌표를 읽고 Cartesian 좌표로 변환하여
    입력 파일이 있는 경로에 새로운 파일로 저장합니다.

    Parameters:
    file_path (str): POSCAR 파일 경로

    Returns:
    None
    """
    lattice_parameters = []
    atom_coordinates = []

    try:
        with open(file_path, 'r') as file:
            # 모든 줄을 읽어 리스트로 저장
            lines = file.readlines()

        # lattice parameter 정보 불러오기 (3, 4, 5번째 줄)
        for line in lines[2:5]:
            values = np.array(list(map(float, line.strip().split())))
            lattice_parameters.append(values)

        # Atom 좌표 시작 위치 찾기
        coor_find = False
        for line in lines:
            if line.strip() == 'Direct':
                coor_find = True
                continue

            if coor_find:
                # 공백줄이면 종료
                if line.strip() == '':
                    break

                # 좌표 값 추출 및 Cartesian 변환
                values = line.strip().split()
                if len(values) >= 3:
                    try:
                        atom_vector = np.array([0.0, 0.0, 0.0], dtype=float)
                        for i in range(3):
                            atom_vector += lattice_parameters[i] * float(values[i])
                        x = float(atom_vector[0])
                        y = float(atom_vector[1])
                        z = float(atom_vector[2])
                        atom_coordinates.append([x, y, z])
                    except ValueError:
                        break  # 숫자가 아닌 값이 나오면 종료

        # 입력 파일 경로에서 디렉토리 추출
        input_dir = os.path.dirname(file_path)  # 입력 파일의 디렉토리 경로
        output_file = os.path.join(input_dir, "POSCAR_out.vasp")  # 출력 파일 경로 생성

        # 수정된 좌표로 새로운 파일 작성
        with open(output_file, 'w') as out_file:
            # Direct 키워드와 그 이전 줄까지 헤더로 복사
            for line in lines:
                if line.strip().lower() == 'direct':   # 'Direct' 키워드 발견 시 종료
                    break
                out_file.write(line)

            # 수정된 Cartesian 좌표 기록
            out_file.write("Cartesian\n")
            for coords in atom_coordinates:
                out_file.write(" ".join(map(str, coords)) + '\n')

        print(f"Cartesian coordinates written to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except IOError:
        print(f"Error: Could not read or write the file.")

# extract_cartesian_coordinates 실행 코드

