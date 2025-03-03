import re
import os
import pandas as pd


def week5_results_to_excel(with_adsorbants_dir_path, processed_excel_file_path, calculator_name):
    energies_by_calculator_name, job_names_by_calculator_name, excel_results = [], [], []
    for root, dirs, files in os.walk(with_adsorbants_dir_path):
        for file in files:
            if file.startswith("ENERGY") and file.find(calculator_name + '_') != -1:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    keywords = "adsorption_energy"
                    match = None
                    for line in f:
                        pattern = rf"{keywords}:\s*([-+]?\d*\.\d+|\d+)"
                        match = re.search(pattern, line)
                        if match:
                            break  # 첫 번째 매칭된 값만 사용
                    if match:
                        # 정규식을 사용하여 'EMT'와 뒤의 숫자 포함 부분 추출
                        pattern = f"_POSCAR_(.+)"
                        job_names = re.search(pattern, file).groups()
                        job_name = "_".join(job_names)
                        job_names_by_calculator_name.append(f"{job_name}")
                        adsorption_energy = float(match.group(1))
                        energies_by_calculator_name.append(adsorption_energy)
                    else:
                        print(f"파일 {file_path}에서 {keywords}값을 찾을 수 없음.")
                        continue  # 매칭되지 않으면 다음 파일로
    if len(job_names_by_calculator_name) != len(energies_by_calculator_name): #간단한 디버깅
        print("the lengths of the job name lists and the energy lists are different.")
    for i in range(len(job_names_by_calculator_name)):
        excel_results.append({
            "Adsorption Energy [eV/Å^2]": energies_by_calculator_name[i],
            "Adsorption Energy [J/m^2]": energies_by_calculator_name[i] * 16.0217,
            "Job Name": job_names_by_calculator_name[i]
        })
    # 엑셀 예쁘게 만들어서 저장하기
    df = pd.DataFrame(excel_results)
    try:
        final_excel_file_path = processed_excel_file_path + "_" + calculator_name.strip('_') + ".xlsx"
        os.makedirs(os.path.dirname(final_excel_file_path), exist_ok=True)
        with pd.ExcelWriter(final_excel_file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="week5_results", index=False)
            workbook = writer.book
            worksheet = writer.sheets["week5_results"]
            # 특정 열 너비 설정 (예: B열을 넓게 설정)
            column_widths = {"Adsorption Energy [eV/Å^2]": 25,
                             "Adsorption Energy [J/m^2]": 25,
                             "Job Name": 50
                             }  # 필요한 열 너비 지정
            for idx, col_name in enumerate(df.columns):
                if col_name in column_widths:
                    col_letter = chr(65 + idx)
                    worksheet.column_dimensions[col_letter].width = column_widths[col_name]
            workbook.save(final_excel_file_path)

        print(f"Results saved to {final_excel_file_path}")
    except Exception as e:
        print(f"Could not save results to Excel: {e}")

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
    with_adsorbants_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision\with_adsorbants"
    processed_excel_file_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\week5_results\week5_results"
    options = ["EMT", "mace_medium", "mace_medium-mpa-0", "mace_small"]
    what_is_the_calculator = ask_question("What type of calculator?", options)
    calculator_name = what_is_the_calculator

    week5_results_to_excel(with_adsorbants_dir_path, processed_excel_file_path, calculator_name)