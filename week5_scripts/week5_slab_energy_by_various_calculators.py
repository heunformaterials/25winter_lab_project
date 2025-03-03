
from mace.calculators import mace_mp
from ase.calculators.emt import EMT
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

def compare_calculators(new_poscar_dir_path, calculator, calculator_name):
    e0_bulk_calculation_file_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\Bulk_energy_calculation\POSCAR"
    for root, dirs, files in os.walk(new_poscar_dir_path):
        for file in files:
            if file.startswith("POSCAR"):
                try:
                    dir_path = os.path.join(root)
                    file_path = os.path.join(root, file)
                    atoms = read(file_path)
                    e0_bulk_atoms = read(e0_bulk_calculation_file_path)
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

    output_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision"
    #test_new_poscar_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\POSCAR_100_1x1_6"

    compare_calculators(output_dir_path, calculator, calculator_name)

