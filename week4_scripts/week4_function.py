#molecule_atoms: 분자의 원소들이 담긴 list
#molecule_original_locations: 분자 내 원자들의 기본 위치(Cartesian)
#이때 위 두 lists의 순서는 정렬돼있다.
#molecule_angle: surface에 대한 법선 벡터와 이루는 각도, degree

import numpy as np
import math

#functions for main function1
def find_farthest_points(coords):
    """
    n개의 좌표에서 가장 먼 두 점을 찾는 함수
    Args:
        coords (list of tuple): 3D 좌표 리스트 [(x1, y1, z1), (x2, y2, z2), ...]
    Returns:
        tuple: (좌표1, 좌표2, 거리)
    """
    max_distance = 0
    point1 = None
    point2 = None

    n = len(coords)
    for i in range(n):
        for j in range(i + 1, n):
            x1, y1, z1 = coords[i]
            x2, y2, z2 = coords[j]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            if distance > max_distance:
                max_distance = distance
                point1, point2 = coords[i], coords[j]
                point1, point2 = sorted([point1, point2], key=lambda x: np.sum(x))

    return point1, point2, max_distance
def find_tilted_angle(vector):
    """
    3D 벡터와 z축 사이의 각도를 계산하는 함수
    Args:
        vector (tuple): 3D 벡터 (x, y, z)
    Returns:
        float: z축과의 각도 (라디안)
        float: z축과의 각도 (도)
    """
    x, y, z = vector
    magnitude = math.sqrt(x ** 2 + y ** 2 + z ** 2)  # 벡터 크기
    if magnitude == 0:
        raise ValueError("영벡터는 방향이 정의되지 않습니다.")

    cos_theta = z / magnitude  # 코사인 값
    theta_radians = math.acos(cos_theta)  # 라디안 단위의 각도
    theta_degrees = math.degrees(theta_radians)  # 도 단위로 변환

    return theta_radians, theta_degrees
def find_tilted_axis(v1, v2): #v2 = z축
    """
    두 벡터에 수직이고 길이가 1인 벡터를 계산하는 함수
    Args:
        v1 (tuple): 첫 번째 벡터 (x1, y1, z1)
        v2 (tuple): 두 번째 벡터 (x2, y2, z2)
    Returns:
        tuple: 두 벡터에 수직이고 길이가 1인 단위 벡터
    """
    # 외적 계산
    cross_x = v1[1] * v2[2] - v1[2] * v2[1]
    cross_y = v1[2] * v2[0] - v1[0] * v2[2]
    cross_z = v1[0] * v2[1] - v1[1] * v2[0]

    # 벡터 크기 계산
    magnitude = math.sqrt(cross_x ** 2 + cross_y ** 2 + cross_z ** 2)

    if math.sqrt(v1[0] ** 2 + v1[1] ** 2 + v1[2] ** 2) == 0:
        raise ValueError("주어진 벡터가 영벡터입니다. 수직 벡터를 정의할 수 없습니다.")
    elif magnitude == 0:
        return [1, 0 ,0] #그냥 x축 반환

    # 단위 벡터 계산
    tilted_axis = (cross_x / magnitude, cross_y / magnitude, cross_z / magnitude)

    return tilted_axis
def rotate_coords_to_be_tuned(coords, axis, angle):
    """
    임의의 축에 대해 여러 좌표들를 회전시키는 함수
    Args:
        coords (list of tuple): 회전시킬 좌표들의 리스트 [(x1, y1, z1), (x2, y2, z2), ...]
        axis (tuple): 회전 축 벡터 (vx, vy, vz) (단위 벡터가 아님)
        angle (float): 회전 각도 (라디안)
    Returns:
        list of tuple: 회전된 좌표들의 리스트 [(x1', y1', z1'), (x2', y2', z2'), ...]
    """
    vx, vy, vz = axis

    # 회전 축을 단위 벡터로 정규화
    axis_magnitude = math.sqrt(vx ** 2 + vy ** 2 + vz ** 2)
    if axis_magnitude == 0:
        raise ValueError("회전 축 벡터가 영벡터입니다.")
    kx, ky, kz = vx / axis_magnitude, vy / axis_magnitude, vz / axis_magnitude

    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    rotated_coords = []
    for x, y, z in coords:
        # 내적과 외적 계산
        dot_product = kx * x + ky * y + kz * z  # k ⋅ p
        cross_product = (
            ky * z - kz * y,  # kx
            kz * x - kx * z,  # ky
            kx * y - ky * x  # kz
        )

        # Rodrigues' Rotation Formula 적용
        x_new = (x * cos_theta +
                 cross_product[0] * sin_theta +
                 kx * dot_product * (1 - cos_theta))
        y_new = (y * cos_theta +
                 cross_product[1] * sin_theta +
                 ky * dot_product * (1 - cos_theta))
        z_new = (z * cos_theta +
                 cross_product[2] * sin_theta +
                 kz * dot_product * (1 - cos_theta))

        rotated_coords.append((x_new, y_new, z_new))

    return rotated_coords
def rotate_polar_to_z(coords,tilted_angle):
    """
    3D 좌표를 z축 기준으로 45도 회전 변환
    Args:
        coords (list of tuple): [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3)]
    Returns:
        list of tuple: 회전된 좌표
    """
    phi = tilted_angle  #목표 회전 각도 저장
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)

    rotated_coords = []

    for x, y, z in coords:
        x_new = x * cos_phi - y * sin_phi
        y_new = x * sin_phi + y * cos_phi
        z_new = z  # z는 변하지 않음
        rotated_coords.append((x_new, y_new, z_new))

    return rotated_coords
def shift_coords_to_origin(coords):
    """
        가장 작은 z값을 가지는 좌표를 원점(0, 0, 0)으로 평행 이동하고,
        그 이동을 다른 모든 좌표들에도 적용하는 함수.

        Args:
            coords (list of tuple): 3D 좌표 리스트 [(x1, y1, z1), (x2, y2, z2), ...]
        Returns:
            list of tuple: 평행 이동된 좌표 리스트
        """
    if not coords:
        raise ValueError("좌표 리스트가 비어 있습니다.")

    # 가장 작은 z값을 가지는 좌표 찾기
    min_z_coord = min(coords, key=lambda coord: coord[2])  # z축 기준 최소값 좌표
    dx, dy, dz = min_z_coord  # 이동할 값 (min_z_coord의 역방향 이동)

    # 모든 좌표를 dx, dy, dz만큼 이동
    translated_coords = [(x - dx, y - dy, z - dz) for x, y, z in coords]

    return translated_coords
def correct_molecule_coordinates(coords, tolerance=1e-16):
    """
    3차원 좌표 리스트에서 오차 범위 이하의 값을 0으로 설정
    Args:
        coords (list of tuple): 3D 좌표 리스트 [(x1, y1, z1), (x2, y2, z2), ...]
        tolerance (float): 오차 범위 (기본값: 1e-16)
    Returns:
        list of tuple: 보정된 3D 좌표 리스트
    """
    corrected_coords = []
    for coord in coords:
        corrected_coord = tuple(0 if abs(value) < tolerance else value for value in coord)
        corrected_coords.append(corrected_coord)
    return corrected_coords

#main function1
def molecule_angle_editor(molecule_original_locations, molecule_angle_degree):
    if len(molecule_original_locations) == 0:
        raise ValueError("입력된 좌표 리스트가 비어 있습니다.")

    #주어진 degree를 radian으로 변환
    molecule_angle_radian = math.radians(molecule_angle_degree)
    atom_point1, atom_point2, distance = find_farthest_points(molecule_original_locations)

    # 두 좌표를 numpy 배열로 변환
    point1 = np.array(atom_point1)
    point2 = np.array(atom_point2)

    #계산에 필요한 두 axis 찾기
    z_axis = (0, 0, 1)
    # 벡터 차 계산
    tilted_molecule_vector = point2 - point1
    tilted_axis = find_tilted_axis(tilted_molecule_vector, z_axis)
    tilted_angle_radians = find_tilted_angle(tilted_molecule_vector)[0]

    #목표 각도와 현재 각도의 차이만큼 회전
    angle_difference = tilted_angle_radians - molecule_angle_radian
    molecule_tuned_locations = rotate_coords_to_be_tuned(molecule_original_locations, tilted_axis, angle_difference)
    #절대 좌표들을 원점에 대한 상대 좌표로 변환
    molecule_tuned_locations = shift_coords_to_origin(molecule_tuned_locations)
    #원점 부근에서 부동 소수점 보정
    molecule_tuned_locations = correct_molecule_coordinates(molecule_tuned_locations, tolerance=1e-16)

    return molecule_tuned_locations #원자 정보와 회전된 좌표들을 각각 반환한다.

#side function1
def what_is_this_absortbate(molecule_name):
    return None

# Cartesian POSCAR file을 정렬해 lines로 이뤄진 list를 반환하는 함수
def sort_poscar_lines(input_file):
    import os
    """
    <기능>
    1) z축 값을 기준으로 정렬한다.
    2) F F F와 T T T를 붙인다.
    <주의사항>
    반드시 Cartesian 형식을 받아야 한다. Direct면 오류 발생.
    """

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
            return None, None
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

        # 결과 반환 output_lines: 전체 poscar text, sorted_coords: only coordination part
        return output_lines, sorted_coords


    '''
    week4_function이라 개조했다.
    
    

    # Write the updated lines to the output file
    with open(output_file, 'w') as file:
        file.writelines(output_lines)
    '''

#실행
#input_file = 'data/week4_raw_POSCAR/100/1x1/5_layer/POSCAR_out.vasp'
#print(sort_poscar_lines(input_file))