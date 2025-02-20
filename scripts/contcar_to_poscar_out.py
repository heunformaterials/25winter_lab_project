
# Function to process 'Direct' CONTCOR files to get 'Cartesian Coordination' as POSCAR_out.vasp
def extract_cartesian_coordinates(input_file_lines):
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

    try:
        lines = input_file_lines

        # lattice parameter 정보 불러오기 (3, 4, 5번째 줄)
        for line in lines[2:5]:
            values = np.array(list(map(float, line.strip().split())))
            lattice_parameters.append(values)

        # Atom 좌표 시작 위치 찾기
        front_lines = []
        coor_find = False
        for line in lines:
            if line.strip() == 'Direct' and coor_find == False:
                front_lines.append('Cartesian')
                coor_find = True
                continue
            elif coor_find == False:
                front_lines.append(line)

            elif coor_find == True:
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
                        front_lines.append(f"{x:.10f}  {y:.10f}  {z:.10f}\n")
                    except ValueError:
                        break  # 숫자가 아닌 값이 나오면 종료

        return front_lines

    except FileNotFoundError:
        print(f"Error: The file does not exist.")
    except IOError:
        print(f"Error: Could not read or write the file.")


# Cartesian POSCAR file을 정렬해 lines로 이뤄진 list를 반환하는 함수
def sort_poscar_lines(input_file_path):
    import os
    """
    <기능>
    1) z축 값을 기준으로 정렬한다.
    2) F F F와 T T T를 붙인다.
    """
    # 파일 읽기
    with open(input_file_path, 'r') as file:
        input_file_lines = file.readlines()

    output_lines = []  # 결과 출력용
    cartesian_lines = []  # Cartesian 데이터 저장용
    in_cartesian_section = False

    # direct를 cartesian으로 바꾼 lines
    lines = extract_cartesian_coordinates(input_file_lines)

    # Cartesian 섹션 이전의 데이터 복사
    cartesian_index = 0
    for line in lines:
        if line.strip().lower() == "cartesian":
            in_cartesian_section = True
            output_lines.append(line +'\n')
            cartesian_index += 1
            break
        elif line.strip().lower() == "direct":
            print("This file is not in Cartesian format.")
            print(f"File path: {os.path.dirname(input_file_path)}")
            break
        else:
            cartesian_index += 1
            output_lines.append(line)

    # Cartesian 이후의 데이터 처리
    if in_cartesian_section:
        for line in lines[cartesian_index:]:
            cartesian_lines.append(line)

        # Cartesian 데이터 정리
        coords = [l.split() for l in cartesian_lines]

        # str to float 변환 알고리즘
        converted_coords = []
        for line in coords:
            converted_line = [
                float(x) if x.replace('.', '', 1).isdigit() else x for x in line
            ]
            converted_coords.append(converted_line)
        coords = converted_coords

        # z축 기준으로 정렬
        sorted_coords = sorted(coords, key=lambda x: float(x[2]))

        # 중복 없이 z 값 리스트 생성
        z_coords = sorted({v[2] for v in sorted_coords})

        # 고정할 하단 레이어 개수와 최대 고정 높이
        fixed_layer_number = 2
        highest_fixed_layer = z_coords[fixed_layer_number]

        # F F F 또는 T T T 추가
        for i in range(len(sorted_coords)):
            # 3, 4, 5번째 값이 F 또는 T가 아닌 경우 처리
            if len(sorted_coords[i]) < 6 or not all(
                    letter in ["F", "T"] for letter in sorted_coords[i][3:6]
            ):
                if float(sorted_coords[i][2]) <= highest_fixed_layer:
                    sorted_coords[i].extend(["F", "F", "F"])
                else:
                    sorted_coords[i].extend(["T", "T", "T"])

        # sorted_coords를 문자열로 변환하여 output_lines에 추가
        output_lines.extend(
            [
                "  " + "     ".join(map(str, line)) + "\n"
                for line in sorted_coords
            ]
        )

        # 입력 파일 경로에서 디렉토리 추출
        input_dir = os.path.dirname(input_file_path)  # 입력 파일의 디렉토리 경로
        output_file = os.path.join(input_dir, "POSCAR_out.vasp")  # 출력 파일 경로 생성

        # 수정된 좌표로 새로운 파일 작성
        with open(output_file, 'w') as out_file:
            # Direct 키워드와 그 이전 줄까지 헤더로 복사
            for line in output_lines:
                out_file.write(line)

#실행 코드

input_file_path = "../week3_scripts/raw_results_after_DFT/111/3x3/8_layer/CONTCAR"
sort_poscar_lines(input_file_path)
