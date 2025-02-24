import os
from ase import Atoms
from ase.io import read, write
import re
from copy import deepcopy
from ase.optimize import LBFGS
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

def get_reference_surface_energy(layer_match, calculator_name, non_adsorbants_dir_path):
    keywords = "surface_energy"
    for root, dirs, files in os.walk(non_adsorbants_dir_path):
        for file in files:
            if layer_match and layer_match.group(0) in file and calculator_name in file:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    for line in f:
                        pattern = rf"{keywords}:\s*([-+]?\d*\.\d+|\d+)"
                        match = re.search(pattern, line)
                        if match:
                            surface_energy = float(match.group(1))  # 문자열을 실수(float)로 변환
                            return surface_energy
    return None  # 매칭된 surface_energy 값을 찾지 못하면 None 반환

def calculate_adsorption_energy(non_adsorbants_dir_path, with_adsorbants_dir_path, calculator):
    layer_pattern = re.compile(r"(\d+)_(\d+)x(\d+)_(\d+)")
    calculator_name = "EMT"
    #adsorbants의 에너지를 calculator로 계산하는 코드 추가하기
    H2_energy_calculation_file_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\adsotbants_energy_calculation\H2\POSCAR"
    O2_energy_calculation_file_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\adsotbants_energy_calculation\O2\POSCAR"
    H2_atoms = read(H2_energy_calculation_file_path)
    O2_atoms = read(O2_energy_calculation_file_path)
    H2_energy, _ = atoms_optimizer(H2_atoms, calculator)
    H_energy = H2_energy / 2
    O2_energy, _ = atoms_optimizer(O2_atoms, calculator)

    for root, dirs, files in os.walk(with_adsorbants_dir_path):
        for file in files:
            if file.startswith("ENERGY") and file.find(calculator_name) != -1:
                file_path = os.path.join(root, file)

                with open(file_path, 'r') as f:
                    keywords = "surface_energy"
                    match = None
                    for line in f:
                        pattern = rf"{keywords}: \s*([-+]?\d*\.\d+|\d+)"
                        match = re.search(pattern, line)
                        if match:
                            break  # 첫 번째 매칭된 값만 사용
                if match:
                    total_ads_slab_energy = float(match.group(1))
                else:
                    print(f"파일 {file_path}에서 surface_energy 값을 찾을 수 없음.")
                    continue  # 매칭되지 않으면 다음 파일로

                layer_match = layer_pattern.search(file_path)
                surface_energy = get_reference_surface_energy(layer_match, calculator_name, non_adsorbants_dir_path)
                if file.find("_H2_") != -1:
                    adsorbants_energy = H2_energy
                elif file.find("_O_") != -1:
                    adsorbants_energy = O2_energy
                elif file.find("_H_") != -1:
                    adsorbants_energy = H_energy
                else:
                    print("strange adsorbants are detected.")
                adsorption_energy = total_ads_slab_energy - adsorbants_energy - surface_energy

                with open(file_path, 'r') as f:
                    lines = f.readlines()

                pattern = r"^adsorption_energy:\s*([-+]?\d*\.\d+|\d+)"
                updated = False
                for i, line in enumerate(lines):
                    if re.search(pattern, line):
                        lines[i] = f"adsorption_energy: {adsorption_energy:.6f}\n"
                        updated = True
                        break

                if not updated:
                    lines.append(f"\nadsorption_energy: {adsorption_energy:.6f}\n")
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                print(f"파일 {file_path}의 adsorption_energy 값이 업데이트되었습니다.")



calc_EMT = EMT()
#calc_MACE = mace_mp(model="medium", dispersion=False, default_dtype="float64")
#실행 코드
non_adsorbants_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\non_adsorbants"
with_adsorbants_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\with_adsorbants"

calculator = calc_EMT
#calculator = calc_MACE

calculate_adsorption_energy(non_adsorbants_dir_path, with_adsorbants_dir_path, calculator)

