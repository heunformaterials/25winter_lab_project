import time
from week5_harvest_poscars import *
from week5_slab_energy_by_various_calculators import *
from week5_adsorption_energy_calculation import *
from week5_results_to_excel import *

def week5_run_whole_processes(calculator, calculator_name):
    output_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision"
    compare_calculators(output_dir_path, calculator, calculator_name)
    time.sleep(3)
    print("stop for 3 seconds")
    non_adsorbants_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\non_adsorbants"
    with_adsorbants_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\with_adsorbants"
    calculate_adsorption_slab_energy(non_adsorbants_dir_path, with_adsorbants_dir_path, calculator, calculator_name)
    time.sleep(3)
    print("stop for 3 seconds")
    processed_excel_file_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\week5_results\week5_results"
    week5_results_to_excel(with_adsorbants_dir_path, processed_excel_file_path, calculator_name)


#실행
if __name__ == "__main__":
    options = ["EMT", "EAM", "mace_medium", "mace_medium-mpa-0", "mace_small"]
    what_is_the_calculator = ask_question("What type of calculator?", options)
    calculator_name = what_is_the_calculator
    if what_is_the_calculator == "EMT":
        calculator = EMT()
    elif what_is_the_calculator == "EAM":
        calc = EAM(potential=r'C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\ema_potential_reference\Cu_lammps.eam')
    elif what_is_the_calculator == "mace_medium_":
        calculator = mace_mp(model="medium", dispersion=False, default_dtype="float64")
    elif what_is_the_calculator == "mace_medium-mpa-0":
        calculator = mace_mp(model="medium-mpa-0", dispersion=False, default_dtype="float32")
    elif what_is_the_calculator == "mace_small":
        calculator = mace_mp(model="small", dispersion=False, default_dtype="float32")
    else:
        print("잘못된 입력입니다. 프로그램을 종료합니다.")

    week5_run_whole_processes(calculator, calculator_name)