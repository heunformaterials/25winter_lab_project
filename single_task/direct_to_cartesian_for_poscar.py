from ase.cell import Cell
import numpy as np
def direct2cartesian(contcar_lines):
    lines = [line.strip() + '\n' for line in contcar_lines]

    # lattice parameter 정보 불러오기 (3, 4, 5번째 줄)
    lattice_parameters = []
    for line in lines[2:5]:
        values = np.array(list(map(float, line.strip().split())))
        lattice_parameters.append(values)

    cell = Cell(lattice_parameters)

    # direct_coords & cartesian_coords 정의 구문
    cartesian_coords = []
    coor_find = False
    for line in lines:
        if line.strip() == 'Direct':
            coor_find = True
            continue
        elif line.strip() == 'Cartesian':
            print("the context is already Cartesian!")
            return None

        if coor_find:
            # 공백줄이면 종료
            if line.strip() == '':
                break

            # 좌표 값 추출 및 Cartesian 변환
            direct_vector = line.strip().split()
            direct_vector = np.array(direct_vector[:3], dtype=float)
            if len(direct_vector) >= 3:
                try:
                    cartesian_coords.append(cell.cartesian_positions(direct_vector))
                except ValueError:
                    break  # 숫자가 아닌 값이 나오면 종료

    #검사 코드
    a_num = 0
    for n in lines[6].split():
        a_num += int(n)

    fined_line = ""
    for l in lines[5].split():
        fined_line += l + " "
    lines[5] = fined_line + "\n"

    fined_line = ""
    for l in lines[6].split():
        fined_line += l + " "
    lines[6] = fined_line + "\n"

    c_num = len(cartesian_coords)
    if a_num != c_num:
        mismatch_num = a_num - c_num
        print(f"Mismatch of atom numbers and coordination numbers: {mismatch_num}")
        return None

    # Direct 키워드와 그 이전 줄까지 헤더로 복사
    new_lines = [] #최종 출력 변수
    for line in lines:
        if line.strip().lower() == 'direct':  # 'Direct' 키워드 발견 시 종료
            # 수정된 Cartesian 좌표 기록
            new_lines.append("Cartesian\n")
            break
        else:
            new_lines.append(line)

    # z축 기준으로 cartesian_coords을 정렬
    sorted_cartesian_coords = sorted(cartesian_coords, key=lambda x: float(x[2]))
    # 중복 없이 z 값 리스트 생성
    z_coords = sorted({v[2] for v in sorted_cartesian_coords})
    # 고정할 하단 레이어 개수와 최대 고정 높이
    fixed_layer_number = 2
    highest_fixed_layer = z_coords[fixed_layer_number - 1]

    for coords in sorted_cartesian_coords:
        # ndarray를 리스트로 변환하여 포맷팅
        formatted_coords = [f"{v:16.12f}" for v in coords[:3].tolist()]

        # "F", "T" 값이 없거나 부족한 경우 처리
        if len(coords) < 6 or not all(letter in ["F", "T"] for letter in coords[3:6]):
            if float(coords[2]) <= highest_fixed_layer:
                formatted_coords.extend([" F", " F", " F"])
            else:
                formatted_coords.extend([" T", " T", " T"])
        else:
            formatted_coords.extend(list(coords[3:6]))  # 기존 "F", "T" 값 유지

        new_lines.append("".join(formatted_coords) + '\n')  # 정렬된 좌표 추가

    return new_lines

#윈도우 directory 환경에서 바로 돌린다
contcar_file_path = r"C:\Users\spark\Desktop\winter_lab\lecture_5\CONTCAR" # Input file path
output_file = r"C:\Users\spark\Desktop\winter_lab\lecture_5\POSCAR"  # Output file path

with open(contcar_file_path, 'r') as file:
    contcar_lines = file.readlines()
    output_lines = direct2cartesian(contcar_lines)
# Write the updated lines to the output file
with open(output_file, 'w') as file:
    file.writelines(output_lines)

