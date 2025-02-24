'''
mase, XTB를 활용해서 지금까지 했던 POSCAR 파일들을 다시 계산해보자!
'''

from mace.calculators import mace_mp
from ase.calculators.emt import EMT
from ase.optimize import LBFGS
from ase.io import read, write
from copy import deepcopy
from pathlib import Path
import shutil
import os
import re

def atoms_optimizer(atoms_origin, calculator, fmax=0.05, max_steps=100):
      atoms = deepcopy(atoms_origin)
      atoms.calc = calculator
      opt = LBFGS(atoms)
      opt.run(fmax=fmax, steps=max_steps)
      return atoms.get_total_energy(), atoms

def harvest_poscars(poscar_dir_path, output_dir_path): #dir_root is 'str'
    output_non_ads_dir_path = os.path.join(output_dir_path, 'non_adsorbants')
    output_with_ads_dir_path = os.path.join(output_dir_path, 'with_adsorbants')
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
        os.makedirs(output_non_ads_dir_path)
        os.makedirs(output_with_ads_dir_path)
    data_tree_root_name = Path(poscar_dir_path).parts[-1]
    for root, dirs, files in os.walk(poscar_dir_path):
        for file in files:
            if file == "POSCAR":
                file_path = os.path.join(root, file)
                # 파일 크기 확인
                if os.path.getsize(file_path) == 0:
                    print(f"파일이 비어 있습니다: {file_path}")
                    continue

                file_dir = os.path.dirname(file_path)
                # "data tree의 root"에 대한 인덱스 찾기
                file_path_list = Path(file_path).parts
                project_index = next((i for i, path in enumerate(file_path_list) if data_tree_root_name in path), None)
                contcar_info = file_path_list[project_index + 1: -1]
                new_filename = "POSCAR"
                for name in contcar_info:
                    new_filename += '_' + name.split("_")[0]
                new_dir_name = new_filename
                if 'H' in file_path_list or 'O' in file_path_list or 'H2' in file_path_list:
                    os.makedirs(os.path.join(output_with_ads_dir_path, new_dir_name), exist_ok=True)
                    new_dir_path = os.path.join(output_with_ads_dir_path, new_dir_name)
                    new_file_path = os.path.join(new_dir_path, new_filename)
                else:
                    os.makedirs(os.path.join(output_non_ads_dir_path, new_dir_name), exist_ok=True)
                    new_dir_path = os.path.join(output_non_ads_dir_path, new_dir_name)
                    new_file_path = os.path.join(new_dir_path, new_filename)

                try:
                    shutil.copy2(file_path, new_file_path)  # 파일 복사
                    print(f"파일 복사 및 이름 변경 완료: {new_file_path}")
                except Exception as e:
                    print(f"파일 이동 중 오류 발생: {e}")

# Function to process OSZICAR files to get layer_info and surface energy
def calculate_surface_energy(file_path, slab_energy, e0_bulk):
    # 파일 경로에서 layer 정보 할당 및 표면 에너지 계산
    layer_pattern = re.compile(r"(\d+)_(\d+)x(\d+)_(\d+)")
    layer_match = layer_pattern.search(file_path)
    if layer_match:
        layer_info_plane = int(layer_match.group(1))
        layer_info_matrix = layer_match.group(2) + 'x' + layer_match.group(3)
        A_coefficient = int(layer_match.group(2))
        layer_info_number = int(layer_match.group(4))
        N_layer = int(layer_info_number)
        N_slab = A_coefficient ** 2 * N_layer
        # layer_info_plane 값에 따른 면적 할당
        if layer_info_plane == 111:
            A = 5.705775672
        elif layer_info_plane == 110:
            A = 9.317484
        elif layer_info_plane == 100:
            A = 13.1769
            N_slab = N_slab * 2
        else:
            A = 0  # 유효하지 않은 plane 처리

        if isinstance(slab_energy, (int, float)):
            surface_energy = 1 / (2 * A * A_coefficient ** 2) * (slab_energy - N_slab * e0_bulk)
        else:
            surface_energy = "Calculation Error"
        return surface_energy

def compare_calculators(new_poscar_dir_path, calculator):
    calculator_name = input('what is calculator name and model?: ')
    e0_bulk_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\Bulk_energy_calculation\POSCAR"
    for root, dirs, files in os.walk(new_poscar_dir_path):
        for file in files:
            if file.startswith("POSCAR"):
                # POSCAR 파일을 Atoms 객체로 변환
                try:
                    dir_path = os.path.join(root)
                    file_path = os.path.join(root, file)
                    atoms = read(file_path)
                    e0_bulk_atoms = read(e0_bulk_path)
                except Exception as e:
                    print(f"파일 읽기 오류: {file}, 오류 메시지: {e}")
                    continue
                energy_dic = {"slab_energy" : 0, "surface_energy" : 0}
                #계산 파트
                energy_dic["slab_energy"], CONTCAR_slab = atoms_optimizer(atoms, calculator)
                e0_bulk, _ = atoms_optimizer(e0_bulk_atoms, calculator)

                energy_dic["surface_energy"] = calculate_surface_energy(file_path, energy_dic["slab_energy"], e0_bulk)

                # H_ads_energy_EMT = energy_adslab - energy_slab - energy_H2 / 2
                new_energy_filename = f"ENERGY_calculated_by_{calculator_name}_" + file
                new_poscar_filename = f"CONTCAR_calculated_by_{calculator_name}_" + file
                new_energy_file = os.path.join(dir_path, new_energy_filename)
                new_poscar_file = os.path.join(dir_path, new_poscar_filename)

                with open(new_energy_file, 'w') as file:
                    lines = ""
                    for i in energy_dic:
                        lines += f"{i}: {energy_dic[i]}\n"
                    file.write(lines)

                with open(new_poscar_file, 'w') as file:
                    write(new_poscar_file, CONTCAR_slab)

#계산기 선언
#calc_EMT = EMT()
calc_MACE = mace_mp(model="medium", dispersion=False, default_dtype="float64")
#실행 코드
poscar_dir_path_1 = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week3_scripts\raw_results_after_DFT"
poscar_dir_path_2 = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week4_scripts\week4_raw_results"
output_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision"

#harvest_poscars(poscar_dir_path_1, output_dir_path)
#harvest_poscars(poscar_dir_path_2, output_dir_path)
test_new_poscar_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\POSCAR_100_1x1_6"
#calculator = calc_EMT
calculator = calc_MACE

compare_calculators(output_dir_path, calculator)

