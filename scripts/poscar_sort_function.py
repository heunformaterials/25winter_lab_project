"""
<기능>
1) z축 값을 기준으로 정렬한다.
2) F F F와 T T T를 붙인다.
<주의사항>
반드시 Cartesian 형식을 받아야 한다. Direct면 오류 발생
"""
def sort_poscar_lines(input_file, output_file):
    import os
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Read the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    output_lines = [] #output_file에 넣을 문장들
    cartesian_lines = [] #Cartesain line 이후의 raw lines
    in_cartesian_section = False

    #copy the file until Cartesian
    cartesian_index = 0 # 'Cartesian'의 위치
    for line in lines:
        if line.strip() == "Cartesian": # Cartesian이 나올 때까지 한다.
            in_cartesian_section = True
            output_lines.append(line)
            cartesian_index += 1
            break
        elif line.strip() == "Direct": # 만약 Direct가 나오면 오류코드
            print("This file is not Cartesian file")
            print(f"file path: {os.path.dirname(input_file)}")
            break
        else:
            cartesian_index += 1
            output_lines.append(line)

    # Cartesian 이후의 코드
    if in_cartesian_section:
        for line in lines[cartesian_index:]: #cartesian_line에 좌표들 추가
            cartesian_lines.append(line)

        # cartesian_line의 각 줄에서 주요값 추출
        coords = [l.split() for l in cartesian_lines]

        # z축 값의 오름 차순으로 좌표들 정렬
        sorted_coords = sorted(coords, key=lambda x: float(x[2]))

        # 중복 없이 z 값 리스트 생성
        z_coords = list({v[2] for v in sorted_coords})
        z_coords.sort()

        # 고정시킬 하단 layers 개수와 최대 고정 높이
        fixed_layer_number = 2
        highest_fixed_layer = z_coords[fixed_layer_number]

        # 주어진 fixed layers만큼 고정시키는 코드, 혹은 T 부여
        for i in range(len(sorted_coords)):
            # 3, 4, 5번째 값에 F나 T가 없는 경우
            if not(sorted_coords[i][3:6] and all(letter in ["F", "T"] for letter in sorted_coords[i][3:6])):
                # z값에 따라 F 또는 T 추가
                if sorted_coords[i][2] <= highest_fixed_layer:
                    sorted_coords[i].extend('FFF')
                else:
                    sorted_coords[i].extend('TTT')

        # sorted_coords를 문자열로 변환하며 output_lines에 추가
        output_lines.extend(['  ' + '     '.join(line) + '\n' for line in sorted_coords])

        # Write the updated lines to the output file
        with open(output_file, 'w') as file:
            file.writelines(output_lines)

# function test
input_file = r"C:\Users\spark\Desktop\winter_lab\MLP교육\POSCAR_out.vasp" # Input file path
output_file = r"C:\Users\spark\Desktop\winter_lab\MLP교육\POSCAR"  # Output file path
sort_poscar_lines(input_file, output_file)