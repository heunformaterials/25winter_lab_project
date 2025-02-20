import math
import numpy as np
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
    if isinstance(coords[0], (int, float)):
        coords = [tuple(coords)]  # (x, y, z) 형태의 튜플로 변환

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
#find parallogram hollow site, output: list의 list

def find_parallogram_hollow_site(raw_coords, hollow_site_number):
    if len(raw_coords) < 2:
        raise ValueError("At least two coordinates are required to find a bridge site.")

    # Step 0: 가장 위쪽의 layer만 고려한다.
    coords = []
    raw_coords.sort(key=lambda x: x[2])
    height = raw_coords[-1][2]
    for i, c in enumerate(raw_coords):
        if c[2] == height:
            coords.append([c[0], c[1], c[2]])
        else:
            None

    # Step 1: Calculate the geometric center
    num_points = len(coords)
    # find_top_site() 호출 전 강제 변환
    coords = [[float(value) for value in row] for row in coords]

    center = [
        sum(coord[i] for coord in coords) / num_points for i in range(3)
    ]
    # Step 2: Calculate distances from the center and sort by distance
    distances = [(math.sqrt(sum((c - center[i]) ** 2 for i, c in enumerate(coord))), coord) for coord in coords]
    distances.sort(key=lambda x: x[0])

    # Step 3: find the closest point to the geometric center
    most_center_point = distances[0][1]

    # Step 4: find the first closest point to most center point
    distances_from_c_atom = [(math.sqrt(sum((c - most_center_point[i]) ** 2 for i, c in enumerate(coord))), coord) for
                             coord in coords]
    distances_from_c_atom.sort(key=lambda x: x[0])

    # 짧은 변을 정의
    first_bridge_point = np.array(distances_from_c_atom[1][1])
    z_axis = [0, 0, 1]
    vector = (first_bridge_point - most_center_point).tolist()
    second_ref_vector = rotate_coords_to_be_tuned(vector, z_axis, 90)
    second_ref_vector = list(second_ref_vector[0])  # 튜플 → 리스트 변환

    # Step 4: 짧은변과 90도를 이루는 point를 찾기
    distances_from_c_and_first = [(math.sqrt(sum((c - second_ref_vector[i] - most_center_point[i]) ** 2 for i, c in enumerate(coord))),
                                   coord) for coord in coords]
    distances_from_c_and_first.sort(key=lambda x: x[0])
    second_bridge_point = np.array(distances_from_c_and_first[0][1])

    # Step 6: find the hollow site according to the site number
    hollow_site = []
    c0 = most_center_point
    c1 = first_bridge_point
    c2 = second_bridge_point
    p1 = (c1 + c2) / 2
    if hollow_site_number == 1:
        hollow_site.append(p1)
    elif hollow_site_number == 2:
        dis_c1 = c0 - c1
        rev_c1 = c0 + dis_c1
        p2 = (rev_c1 + c2) / 2
        hollow_site.append(p1)
        hollow_site.append(p2)
    else:
        print('hollow_site_number is bigger than 3!')

    hollow_site = [vector.tolist() for vector in hollow_site]
    return hollow_site

#find triangle hollow site, output: list의 list
def find_triangle_hollow_site(raw_coords, hollow_site_number):
    if len(raw_coords) < 2:
        raise ValueError("At least two coordinates are required to find a bridge site.")

    # Step 0: 가장 위쪽의 layer만 고려한다.
    coords = []
    raw_coords.sort(key=lambda x: x[2])
    height = raw_coords[-1][2]
    for i, c in enumerate(raw_coords):
        if c[2] == height:
            coords.append([c[0], c[1], c[2]])
        else:
            None

    # Step 1: Calculate the geometric center
    num_points = len(coords)
    # find_top_site() 호출 전 강제 변환
    coords = [[float(value) for value in row] for row in coords]

    center = [
        sum(coord[i] for coord in coords) / num_points for i in range(3)
    ]
    center = np.array(center)

    # Step 2: Calculate distances from the center and sort by distance
    distances = [(math.sqrt(sum((c - center[i]) ** 2 for i, c in enumerate(coord))), coord) for coord in coords]
    distances.sort(key=lambda x: x[0])

    #가장 가까운 점들 중 임의의 하나를 고른다.
    center = np.array(distances[0][1]) #c0
    one_nearest_point = np.array(distances[1][1]) #c1

    #중심과 앞서 고른 점과 가장 가까운 점들 중 한 개를 고른다.
    distances2 = [
        (math.sqrt(sum((c - center[i]) ** 2 for i, c in enumerate(coord))) +
         math.sqrt(sum((c - one_nearest_point[i]) ** 2 for i, c in enumerate(coord))),
                   coord) for coord in coords
    ]
    distances2.sort(key=lambda x: x[0])

    #가장 가까운 점들 중 임의의 하나를 고른다.
    two_nearest_point = np.array(distances2[2][1]) #c2

    # Step 6: find the hollow site according to the site number
    hollow_site = []
    p1 = (center + one_nearest_point + two_nearest_point) / 3
    if hollow_site_number == 1:
        hollow_site.append(p1)
    elif hollow_site_number == 2: #FCC와 같이 ABCABC인 상황
        dis_c1 = center - one_nearest_point
        rev_c1 = np.array(center + dis_c1)
        dis_c2 = center - two_nearest_point
        rev_c2 = np.array(center + dis_c2)
        p2 = (center + rev_c1 + rev_c2) / 3
        hollow_site.append(p1)
        hollow_site.append(p2)
    else:
        print('hollow_site_number is bigger than 3!')

    hollow_site = [vector.tolist() for vector in hollow_site]
    return hollow_site

#find top site, output: list
def find_top_site(raw_coords):
    if len(raw_coords) < 2:
        raise ValueError("At least two coordinates are required to find a bridge site.")

    # Step 0: 가장 위쪽의 layer만 고려한다.
    coords = []
    raw_coords.sort(key=lambda x: x[2])
    height = raw_coords[-1][2]
    for i, c in enumerate(raw_coords):
        if c[2] == height:
            coords.append([c[0], c[1], c[2]])
        else:
            None

    # Step 1: Calculate the geometric center
    num_points = len(coords)
    coords = [[float(value) for value in row] for row in coords]

    center = [
        sum(float(coord[i]) for coord in coords) / num_points for i in range(3)
    ]

    # Step 2: Calculate distances from the center and sort by distance
    distances = [(math.sqrt(sum((c - center[i]) ** 2 for i, c in enumerate(coord))), coord) for coord in coords]
    distances.sort(key=lambda x: x[0])

    # Step 3: find the closest point to the geometric center
    most_center_point = distances[0][1]

    # list 형식으로 변환
    top_site = []
    top_site.append(most_center_point)

    return top_site

#find bridge site, output: list의 list
def find_center_bridge_site(raw_coords, bridge_site_number):
    """
    Find a bridge site defined by the two atoms closest to the geometric center.

    Args:
        coords (list): A list of 3D coordinates, where each element is [x, y, z].

    Returns:
        list: The coordinate of the bridge site between the two closest atoms to the center.
    """
    if len(raw_coords) < 2:
        raise ValueError("At least two coordinates are required to find a bridge site.")

    # Step 0: 가장 위쪽의 layer만 고려한다.
    coords = []
    raw_coords.sort(key=lambda x: x[2])
    height = raw_coords[-1][2]
    for i, c in enumerate(raw_coords):
        if c[2] == height:
            coords.append([c[0], c[1], c[2]])

    # Step 1: Calculate the geometric center
    num_points = len(coords)
    # find_top_site() 호출 전 강제 변환
    coords = [[float(value) for value in row] for row in coords]

    center = [
        sum(coord[i] for coord in coords) / num_points for i in range(3)
    ]

    # Step 2: Calculate distances from the center and sort by distance
    distances = [(math.sqrt(sum((c - center[i]) ** 2 for i, c in enumerate(coord))), coord) for coord in coords]
    distances.sort(key=lambda x: x[0])

    # Step 3: find the closest point to the geometric center
    most_center_point = np.array(distances[0][1])

    # Step 4: find the 2nd closest point to most center point
    distances_from_c_atom = [(math.sqrt(sum((c - most_center_point[i]) ** 2 for i, c in enumerate(coord))), coord) for coord in coords]
    distances_from_c_atom.sort(key=lambda x: x[0])

    #짧은 변과 긴 변을 정의
    first_bridge_point = np.array(distances_from_c_atom[1][1])
    second_bridge_point = np.array(distances_from_c_atom[3][1])

    # bridge site 정의
    bridge_site = []
    if bridge_site_number == 1:
        bridge_site.append((most_center_point + first_bridge_point) / 2)
    elif bridge_site_number == 2:
        bridge_site.append((most_center_point + first_bridge_point) / 2)
        bridge_site.append((most_center_point + second_bridge_point) / 2)
    else:
        print("bridge site number is bigger than 3!!")

    # np.array에서 list로 변환
    bridge_site = [vector.tolist() for vector in bridge_site]

    return bridge_site

#Main function for finding the adsorbate site according to the plane type
def find_adsorbate_site(plane_info, atoms_coords):
    if type(plane_info) == int:
        plane_name = str(plane_info)
    elif type(plane_info) == str:
        plane_name = plane_info
        None
    else:
        print('???Type of plane_info is strange???')

    if plane_name == '100':
        bridge_site_number = 1
        hollow_site_number = 1
        top_site = find_top_site(atoms_coords)

        bridge_site = find_center_bridge_site(atoms_coords, bridge_site_number)

        parallogram_hollow_site = find_parallogram_hollow_site(atoms_coords, hollow_site_number)
        return top_site, bridge_site, parallogram_hollow_site

    elif plane_name == '110':
        bridge_site_number = 2
        hollow_site_number = 1
        bridge_site = find_center_bridge_site(atoms_coords, bridge_site_number)
        top_site = find_top_site(atoms_coords)
        parallogram_hollow_site = find_parallogram_hollow_site(atoms_coords, hollow_site_number)
        return top_site, bridge_site, parallogram_hollow_site

    elif plane_name == '111':
        bridge_site_number = 1
        hollow_site_number = 2
        bridge_site = find_center_bridge_site(atoms_coords, bridge_site_number)
        top_site = find_top_site(atoms_coords)
        triangle_hollow_site = find_triangle_hollow_site(atoms_coords, hollow_site_number)
        return top_site, bridge_site, triangle_hollow_site

    else:
        print("Warning: plane_type is not 100, 110, or 111.\n"
            "Please check the input or revise the function for correctness.")
        return None


'''
# Example usage
coords = [
    [0, 0, 2], [1, 0, 2], [2, 0, 2],
    [0, 1, 2], [1, 1, 2], [2, 1, 2],
    [0, 2, 2], [1, 2, 2], [2, 2, 2]
]
bridge_site_number = 2
hollow_site_number = 1
plane_info = 110


bridge_site = find_center_bridge_site(coords, bridge_site_number)
top_site = find_top_site(coords)
parallogram_hollow_site = find_parallogram_hollow_site(coords, hollow_site_number)
triangle_hollow_site = find_triangle_hollow_site(coords, hollow_site_number)


top_site, bridge_site, hollow_site = find_adsorbate_site(plane_info, coords)

#print("Coordinates:", coords)
#print("Center-defined bridge site:", bridge_site)
#print("Top site:", top_site)
#print("Hollow site:", hollow_site)



print("Parallogram hollow site:", parallogram_hollow_site)
print("Triangle hollow site:", triangle_hollow_site)
'''
