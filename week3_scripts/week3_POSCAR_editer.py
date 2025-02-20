"""
!!!week3에 특화된 함수임!!!
주의: 반드시 Cartesian의 POSCAR를 입력받아야 한다.
아쉬운 점: Cartesian 이후의 값들을 z축을 기준으로 정렬하는 기능과 'F F F', 'T T T'를 붙이는 기능을 추가했어야 했다.
<기능>
1) z축 값을 기준으로 정렬한다.
2) F F F와 T T T를 붙인다.
"""
def process_procore_file(input_file, output_file):
    import os

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Read the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    output_lines = []
    cartesian_lines = []
    in_cartesian_section = False
    removed_lines_count = 0  # Count removed lines

    # Parse the file
    for line in lines:
        #Cartesian이 나올 때까지 한다.
        if line.strip() == "Cartesian":
            in_cartesian_section = True
            output_lines.append(line)
            continue

        #만약 Direct가 나오면 오류코드
        elif line.strip() == "Direct":
            print("This file is not Cartesian file")
            print(f"file path: {os.path.dirname(input_file)}")
            break

        #Cartesian 이후의 코드
        if in_cartesian_section:
            if line.strip():
                cartesian_lines.append(line)

            #Cartesian 이후의 좌표 줄들을 모두 list에 저장하면 실행되는 코드
            else:
                in_cartesian_section = False
                # Process Cartesian lines
                coords = [l.split() for l in cartesian_lines]

                #z축 값의 오름 차순으로 좌표들 정렬
                sorted_coords = sorted(coords, key = lambda x: float(x[2]))

                # 중복 없이 z 값 리스트 생성
                z_coords = list({v[2] for v in sorted_coords})
                z_coords.sort()

                # 고정시킬 하단 layers 개수와 최대 고정 높이
                fixed_layer_number = 2
                highest_fixed_layer = z_coords[fixed_layer_number]

                # 제거할 상단 layers 개수와 최저 제거 높이
                removed_layer_number = 1
                lowest_fixed_layer = z_coords[-removed_layer_number]

                # 주어진 layer 만큼 제거시키는 코드
                iterate_number = len(sorted_coords)
                removed_and_sorted_coords = []
                for i in range(iterate_number):
                    if sorted_coords[i][2] >= lowest_fixed_layer:
                        removed_lines_count += 1
                    else:
                        removed_and_sorted_coords.append(sorted_coords[i])

                # 주어진 fixed layers만큼 고정시키는 코드, 혹은 T 부여
                for i in range(len(removed_and_sorted_coords)):
                    # 3, 4, 5번째 값에 F나 T가 없는 경우
                    if not (removed_and_sorted_coords[i][3:6] and all(letter in ["F", "T"] for letter in removed_and_sorted_coords[i][3:6])):
                        # z값에 따라 F 또는 T 추가
                        if removed_and_sorted_coords[i][2] <= highest_fixed_layer:
                            removed_and_sorted_coords[i].extend('FFF')
                        else:
                            removed_and_sorted_coords[i].extend('TTT')

                # removed_and_sorted_coords를 문자열로 변환하며 output_lines에 추가
                output_lines.extend(['  ' + '     '.join(line) + '\n' for line in removed_and_sorted_coords])
        else:
            output_lines.append(line)

    # Adjust the value below "Cu" and above "Cu"
    for i, line in enumerate(output_lines):
        if line.strip() == "Cu":
            # Modify the value in the line below "Cu"
            below_cu_line = output_lines[i + 1]
            split_line = below_cu_line.split()

            # Ensure we are modifying a numeric value
            if split_line and split_line[0].replace('.', '', 1).isdigit():
                first_number = float(split_line[0])
                first_number -= removed_lines_count

                # Update the modified value back to the line
                split_line[0] = f"{int(first_number)}"  # 정수로 출력
                output_lines[i + 1] = " ".join(split_line) + "\n"

            # Modify the value in the line above "Cu"
            above_cu_line = output_lines[i - 1]
            split_line_above = above_cu_line.split()

            # Ensure the third value (index 2) exists and is numeric
            if len(split_line_above) >= 3 and split_line_above[2].replace('.', '', 1).isdigit():
                max_value = z_coords[-removed_layer_number - 1]
                third_value = float(max_value)
                # Example modification: Add 15 to the third value
                third_value += 15

                # Update the modified value back to the line
                split_line_above[2] = f"{third_value:.6f}"  # Keep formatting consistent
                output_lines[i - 1] = " ".join(split_line_above) + "\n"
            break

    # Write the updated lines to the output file
    with open(output_file, 'w') as file:
        file.writelines(output_lines)

# 실행
input_file = 'raw_file_before_DFT/POSCAR'  # Input file path
output_file = 'preprocessed_before_DFT/POSCAR'  # Output file path
process_procore_file(input_file, output_file)