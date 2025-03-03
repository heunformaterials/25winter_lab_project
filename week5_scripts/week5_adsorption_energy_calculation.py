from mace.calculators import mace_mp
from ase.calculators.emt import EMT
from ase.calculators.eam import EAM
from ase.optimize import LBFGS
from ase.io import read, write
from copy import deepcopy
import os
import re


def atoms_optimizer(atoms_origin, calculator, fmax=0.05, max_steps=100):
    atoms = deepcopy(atoms_origin)
    atoms.calc = calculator
    opt = LBFGS(atoms)
    opt.run(fmax=fmax, steps=max_steps)
    return atoms.get_total_energy(), atoms

def get_reference_slab_energy(layer_match, calculator_name, non_adsorbants_dir_path):
    keywords = "slab_energy"
    for root, dirs, files in os.walk(non_adsorbants_dir_path):
        for file in files:
            if layer_match and layer_match.group(0) in file and calculator_name in file:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    for line in f:
                        pattern = rf"{keywords}:\s*([-+]?\d*\.\d+|\d+)"
                        match = re.search(pattern, line)
                        if match:
                            slab_energy = float(match.group(1))  # 문자열을 실수(float)로 변환
                            return slab_energy
    return None  # 매칭된 slab_energy 값을 찾지 못하면 None 반환

def calculate_adsorption_slab_energy(non_adsorbants_dir_path, with_adsorbants_dir_path, calculator, calculator_name):
    layer_pattern = re.compile(r"(\d+)_(\d+)x(\d+)_(\d+)")
    #adsorbants의 에너지를 calculator로 계산하는 코드 추가하기
    H2_energy_calculation_file_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\adsotbants_energy_calculation\H2\POSCAR"
    O2_energy_calculation_file_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\adsotbants_energy_calculation\O2\POSCAR"
    H2_atoms = read(H2_energy_calculation_file_path)
    O2_atoms = read(O2_energy_calculation_file_path)
    H2_energy, _ = atoms_optimizer(H2_atoms, calculator)
    H_energy = H2_energy / 2
    O2_energy, _ = atoms_optimizer(O2_atoms, calculator)
    calculator_name = calculator_name + '_'

    for root, dirs, files in os.walk(with_adsorbants_dir_path):
        for file in files:
            if file.startswith("ENERGY") and file.find(calculator_name) != -1:
                file_path = os.path.join(root, file)

                with open(file_path, 'r') as f:
                    keywords = "slab_energy"
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
                ref_slab_energy = get_reference_slab_energy(layer_match, calculator_name, non_adsorbants_dir_path)
                if file.find("_H2_") != -1:
                    adsorbants_energy = H2_energy / 2
                elif file.find("_O_") != -1:
                    adsorbants_energy = O2_energy  / 2
                elif file.find("_H_") != -1:
                    adsorbants_energy = H_energy
                else:
                    print("strange adsorbants are detected.")
                adsorption_energy = total_ads_slab_energy  - ref_slab_energy - adsorbants_energy

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


def ask_question(question, options):
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    popup = tk.Toplevel(root)
    popup.title("선택")
    popup.geometry(f"300x{min(100 + len(options) * 30, 500)}")
    popup.resizable(False, False)
    label = tk.Label(popup, text=question, font=("Arial", 12))
    label.pack(pady=10)
    selected_option = tk.StringVar()

    def on_select(option):
        selected_option.set(option)
        popup.destroy()  # 창 닫기

    for option in options:
        button = tk.Button(popup, text=option, font=("Arial", 10), width=15,
                           command=lambda opt=option: on_select(opt))
        button.pack(pady=5)

    popup.wait_window()  # 사용자가 선택할 때까지 대기
    return selected_option.get()

#실행
if __name__ == "__main__":
    options = ["EMT", "mace_medium", "mace_medium-mpa-0"]
    what_is_the_calculator = ask_question("What type of calculator?", options)
    calculator_name = what_is_the_calculator
    if what_is_the_calculator == "EMT":
        calculator = EMT()
    elif what_is_the_calculator == "mace_medium":
        calculator = mace_mp(model="medium", dispersion=False, default_dtype="float64")
    elif what_is_the_calculator == "mace_medium-mpa-0":
        calculator = mace_mp(model="medium-mpa-0", dispersion=False, default_dtype="float32")
    else:
        print("잘못된 입력입니다. 프로그램을 종료합니다.")

    non_adsorbants_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\non_adsorbants"
    with_adsorbants_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\with_adsorbants"

    calculate_adsorption_slab_energy(non_adsorbants_dir_path, with_adsorbants_dir_path, calculator, calculator_name)

