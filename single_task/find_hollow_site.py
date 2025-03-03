from scripts import find_adsorbate_site

#Cartesian POSCAR file을 정렬해 lines로 이뤄진 list를 반환하는 함수
def sort_poscar_lines(input_file):
    import os
    # 파일 읽기
    with open(input_file, 'r') as file:
        lines = file.readlines()

    output_lines = []  # 결과 출력용
    cartesian_lines = []  # Cartesian 데이터 저장용
    in_cartesian_section = False

    # Cartesian 섹션 이전의 데이터 복사
    cartesian_index = 0
    for line in lines:
        if line.strip() == "Cartesian":
            in_cartesian_section = True

            output_lines.append(line)
            cartesian_index += 1
            break
        elif line.strip() == "Direct":
            print("This file is not in Cartesian format.")
            print(f"File path: {os.path.dirname(input_file)}")
            return None
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

        # 결과 반환 output_lines: 전체 poscar text, sorted_coords: only coordination part
        return coords


#실행코드
input_file_path = r"C:\Users\spark\Desktop\winter_lab\lecture_5\POSCAR"
raw_coords = sort_poscar_lines(input_file_path)
hollow_sites = find_adsorbate_site.find_parallogram_hollow_site(raw_coords, hollow_site_number=2)
print(hollow_sites)
