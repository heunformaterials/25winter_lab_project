from scripts.absorbate_information import hydrogen_atom, hydrogen_gas, oxygen_atom
from scripts.site_information import Site
from week4_scripts import week4_function
import os

# Helper 함수: 디렉토리를 만들고 새로 생성된 경우에만 메시지를 출력
def create_directory(path):
    import os
    if not os.path.exists(path):  # 디렉토리가 존재하지 않을 경우
        os.makedirs(path)  # 디렉토리 생성
        print(f"Created directory: {path}")  # 생성된 디렉토리 경로 출력
    else:
        return None # 디렉토리가 존재하면 아무 일도 하지 않는다.

# Helper 함수 정의
def add_site_to_poscar(sorted_poscar_lines, site_directory, adsorbate, site): #여기서 adsobate, site는 object
    import numpy as np
    extra_height = np.array([0, 0, 1.5])

    site_coords = site.coordinates # site의 좌표
    adsorbate_coords = adsorbate.coordinates #흡착물 분자 자체의 좌표

    if len(adsorbate.atoms) == 1:

        for i, c in enumerate(site_coords): # 각 c마다 file이 1개씩 나와야함
            if len(site_coords) == 1:
                each_site_dir_path = site_directory
            elif len(site_coords) == 0:
                print("there is no site's coords")
            else:
                site_file_name = f"{i + 1}th {site.name}"
                each_site_dir_path = os.path.join(site_directory, site_file_name)
                create_directory(each_site_dir_path)

            for s in adsorbate_coords:
                angle_lines = sorted_poscar_lines[:]
                v = np.array(s) + np.array(c) + extra_height
                angle_lines.append(" ".join(map(str, v.tolist())) + "    T   T   T")

            # 불필요한 빈 줄 제거
            cleaned_data = [line.strip() + '\n' for line in angle_lines if line.strip()]

            # 각 site에 대해 POSCAR 저장
            new_file_path = os.path.join(each_site_dir_path, "POSCAR")
            with open(new_file_path, "w") as file:
                file.writelines(cleaned_data)

    else:
        angles = [0, 45, 90]
        # site에 atom 배정
        for i, c in enumerate(site_coords):
            if len(site_coords) == 1:
                each_site_dir_path = site_directory
            elif len(site_coords) == 0:
                print("there is no site's coords")
            else:
                site_file_name = f"{i + 1}th {site.name}"
                each_site_dir_path = os.path.join(site_directory, site_file_name)
                create_directory(each_site_dir_path)

            for angle in angles:
                #sorted_poscar_lines를 직접 건드는 것은 피한다.
                angle_lines = sorted_poscar_lines[:]

                tilted_coords = week4_function.molecule_angle_editor(adsorbate_coords, angle)

                # angle_type 디렉토리 이름과 구조 설정
                dir_angle_type_title = f"{angle}"
                angle_type_sub_directory = os.path.join(each_site_dir_path, dir_angle_type_title)
                create_directory(angle_type_sub_directory)

                for s in tilted_coords:
                    v = np.array(s) + np.array(c) + extra_height
                    angle_lines.append(" ".join(map(str, v.tolist())) + "    T   T   T")

                # 불필요한 빈 줄 제거
                cleaned_data = [line.strip() + '\n' for line in angle_lines if line.strip()]

                # POSCAR 저장
                new_file_path = os.path.join(angle_type_sub_directory, "POSCAR")
                with open(new_file_path, "w") as file:
                    file.writelines(cleaned_data)
    return None

#main function(adsorbate to site)
def add_adsorbate_to_site(a_info, poscar_lines, adsorbate_sub_directory, top_site, bridge_site, hollow_site):
    #adsorbate 정보 가져오기
    adsorbates = {
        "H": hydrogen_atom,
        "O": oxygen_atom,
        "H2": hydrogen_gas
    }
    # 선택된 Adsorbate 객체
    adsorbate = adsorbates[a_info]

    #adsorbate가 다원자 분자인 경우, 각 대표 원소 추출
    if len(set(adsorbate.atoms)) >= 2:
        print(f"{adsorbate.name} has at least two elements!!")

    #바뀌지 않는 변수인 reference 정의
    ref_poscar_lines = poscar_lines

    for i, line in enumerate(poscar_lines):
        if line.strip() == "Cu":
            #sites 종류에 따른 object 선언
            sites = [
                Site("top_site", top_site),
                Site("bridge_site", bridge_site),
                Site("hollow_site", hollow_site)
            ]
            for site in sites:
                new_poscar_lines = ref_poscar_lines[:] #깊은 복사를 위한 slicing
                # Cu 뒤에 adsorbate information 추가
                new_poscar_lines[i] = new_poscar_lines[i].strip() # 문장 끝의 '\n' 제거
                new_poscar_lines[i] += f" {adsorbate.atoms[0]} \n"  # 문자열로 처리

                # Cu 아래 줄에 adsorabte number 추가
                adsorbate_number = len(adsorbate.atoms)
                if i + 1 < len(new_poscar_lines):  # IndexError 방지
                    new_poscar_lines[i + 1] = new_poscar_lines[i + 1].strip() # 문장 끝의 '\n' 제거
                    new_poscar_lines[i + 1] += f" {adsorbate_number} \n"
                else:
                    print("Warning: Cannot add adsorbate_number; no line exists below Cu.")

                #site에 대한 directory 경로 형성
                site_type_sub_directory = site.generate_directory(adsorbate_sub_directory)
                add_site_to_poscar(new_poscar_lines, site_type_sub_directory, adsorbate, site)

