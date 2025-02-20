import week4_result_processing_functions
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
class SlabCalculation:
    def __init__(self):
        self.plane_size_list = ['1x1', '2x2', '3x3']
        self.plane_type_list = ['100', '110', '111']
        self.adsorbate = ['H', 'H2', 'O']

    def __repr__(self):
        return (f"SlabCalculation(plane_size_list={self.plane_size_list}, "
                f"plane_type_list={self.plane_type_list}, adsorbate={self.adsorbate})")
def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            # 재귀 호출로 내부 리스트를 풀어서 flat_list에 추가합니다.
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list
# Main function to process files and save results to Excel
def week4_result_preocessing(data_directory, processed_excel_path):
    layer_pattern = re.compile(r"(\d+)[\\/](\d+)x(\d+)[\\/](\d+)")
    results = [] #최종 결과 list

    for root, dirs, files in os.walk(data_directory):
        job_name_list, energy_ads_list, week4_E0_list, week3_E0_list, jule_energy_ads_list = [], [], [], [], []
        for file in files:
            file_path = os.path.join(root, file)
            file_dir = os.path.dirname(file_path)

            # 첫 번째로 "week4_raw_results"가 포함된 인덱스 찾기
            file_path_list = Path(file_path).parts
            project_index = next((i for i, path in enumerate(file_path_list) if "week4_raw_results" in path), None)
            atoms_name = file_path_list[project_index + 4] # 주의!!

            try:
                if file == "OSZICAR":
                    E0_week4 = week4_result_processing_functions.energy_from_oszicar(file_path)
                    E_H_surface = week4_result_processing_functions.get_surface_energy(E0_week4, layer_pattern, file_path)
                    E_surface, E0_week3 = week4_result_processing_functions.slab_energy_from_week3(file_path, layer_pattern)
                    E_ads = week4_result_processing_functions.adsorption_energy(E0_week4, atoms_name, E0_week3)
                    week4_E0_list.append(E0_week4)
                    week3_E0_list.append(E0_week3)
                    job_name = ''
                    for a in list(file_path_list[project_index + 1:-1]):
                        job_name += a + ' '
                    job_name_list.append(job_name)
                    energy_ads_list.append(E_ads)
                    jule_energy_ads_list.append(16.0217 * E_ads)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        # 계산한 결과 저장
        for i in range(len(energy_ads_list)):
            try:
                results.append({
                    "Adsorption Energy [eV/Å^2]":energy_ads_list[i],
                    "Adsorption Energy [J/m^2]": jule_energy_ads_list[i],
                    "week4 E0 [eV/Å^2]": week4_E0_list[i],
                    "week3 E0 [eV/Å^2]": week3_E0_list[i],
                    "Job Name": job_name_list[i]
                })
            except IndexError as e:
                print(f"IndexError in calculation for index {i}: {e}")
            except ZeroDivisionError as e:
                print(f"ZeroDivisionError in calculation for index {i}: {e}")
    #엑셀 예쁘게 만들어서 저장하기
    df = pd.DataFrame(results)
    try:
        os.makedirs(os.path.dirname(processed_excel_path), exist_ok=True)
        with pd.ExcelWriter(processed_excel_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Results", index=False)
            workbook = writer.book
            worksheet = writer.sheets["Results"]
            # 특정 열 너비 설정 (예: B열을 넓게 설정)
            column_widths = {"Adsorption Energy [eV/Å^2]": 25,
                             "Adsorption Energy [J/m^2]": 25,
                             "week4 E0 [eV/Å^2]": 18,
                             "week3 E0 [eV/Å^2]": 18,
                             "Job Name": 50
                             }  # 필요한 열 너비 지정
            for idx, col_name in enumerate(df.columns):
                if col_name in column_widths:
                    col_letter = chr(65 + idx)
                    worksheet.column_dimensions[col_letter].width = column_widths[col_name]
            workbook.save(processed_excel_path)

        print(f"Results saved to {processed_excel_path}")
    except Exception as e:
        print(f"Could not save results to Excel: {e}")

#plot에 넣을 데이터를 선정하는 함수
def edit_plot_data(df, plane_size, plane_type, adsorbate): # plane_type and plane_type are str
    column_names = df.columns.tolist()
    jule_ads_energy_list = df[column_names[1]].tolist()
    plot_data = []
    for i, job_name in enumerate(df[column_names[4]]):
        if plane_size in job_name and plane_type in job_name and adsorbate in job_name:
            job_name_splited = job_name.split()
            name = ''
            for j in job_name_splited:
                name += j + " "
            plot_data.append([name, jule_ads_energy_list[i]])
    plot_data_job_names = []
    plot_data_values = []
    for t in plot_data:
        plot_data_job_names.append(t[0])
        plot_data_values.append(t[1])
    return plot_data_job_names, plot_data_values

#plot을 그리는 함수
def draw_plot(job_names,  values, column_names, plot_directory, plot_name):
    plt.figure(figsize=(20, 12))
    plt.bar(job_names, values, color='royalblue')
    plt.xlabel('Job names', fontsize=22)
    plt.ylabel(column_names[1], fontsize=22)
    plt.ylim(sorted(values)[2] - 1, sorted(values)[-1] + 1)
    plt.title(f'{plot_name}', fontsize=30)
    if len(job_names) >= 50:
        plt.xticks(rotation=90, fontsize=16)
    else:
        plt.xticks(rotation=75, fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_directory, f'week4_{plot_name}_plot.png'))

#각 task를 실행하는 함수
def do_task(df, plane_size, plane_type, adsorbate, plot_name, plot_directory):
    column_names = df.columns.tolist()
    # task1
    task_job_names, task_values = [], []
    for ad in adsorbate:
        for ps in plane_size:
            for pt in plane_type:
                job_names, values = edit_plot_data(df, ps, pt, ad)
                task_job_names.append(job_names)
                task_values.append(values)
    task_job_names = flatten_list(task_job_names)
    task_values = flatten_list(task_values)
    draw_plot(task_job_names, task_values, column_names, plot_directory, plot_name)

#각 task를 실행하는 함수
def extract_key(s):
    tokens = s.split()
    # tokens의 길이에 따라 다르게 처리합니다.
    if len(tokens) >= 8:
        # 예: ['111', '1x1', '8', 'H2', 'hollow_site', '2th', 'hollow_site', '0']
        # 키로 ('hollow_site', '2th', 'hollow_site', '0') 사용
        return (tokens[4], tokens[5], tokens[6], tokens[7])
    elif len(tokens) >= 6:
        # 예: ['111', '1x1', '8', 'H2', 'bridge_site', '0']
        # 키로 ('bridge_site', '0') 사용
        return (tokens[4], tokens[5])
    else:
        return s  # 기본적으로 전체 문자열을 키로 사용
def do_task_2(df, plane_size, plane_type, adsorbate, plot_name, plot_directory):
    column_names = df.columns.tolist()
    # task1
    task_job_names, task_values = [], []
    for ad in adsorbate:
        for ps in plane_size:
            for pt in plane_type:
                job_names, values = edit_plot_data(df, ps, pt, ad)
                task_job_names.append(job_names)
                task_values.append(values)
    task_job_names = flatten_list(task_job_names)
    task_values = flatten_list(task_values)
    combined = list(zip(task_job_names, task_values))
    # 정렬: extract_key()를 기준으로 정렬합니다.
    sorted_combined = sorted(combined, key=lambda pair: extract_key(pair[0]))
    # 정렬된 결과를 다시 분리합니다.
    sorted_task_job_names, sorted_task_values = zip(*sorted_combined)
    draw_plot(sorted_task_job_names, sorted_task_values, column_names, plot_directory, plot_name)

# Main function 2 to plot the results
def week4_result_plotting_task(processed_excel_path, plot_directory):
    # 컬럼 제목 추출
    df = pd.read_excel(processed_excel_path)
    #task1
    plane_size = ['3x3']
    plane_type = ['100']
    adsorbate = SlabCalculation().adsorbate
    plot_name = 'Adsorption energy of 100 3x3 size'
    do_task(df, plane_size, plane_type, adsorbate, plot_name, plot_directory)

    #task2
    task_job_names, task_values = [], []
    plane_size = ['3x3']
    plane_type = SlabCalculation().plane_type_list
    adsorbate = SlabCalculation().adsorbate
    plot_name = 'Adsorption energy of 3x3 size for 100 110 111'
    do_task(df, plane_size, plane_type, adsorbate, plot_name, plot_directory)

    # task3
    task_job_names, task_values = [], []
    plane_size = SlabCalculation().plane_size_list
    plane_type = SlabCalculation().plane_type_list
    adsorbate = ['H2']
    plot_name = 'Adsorption energy of H2 for 100 110 111'
    do_task(df, plane_size, plane_type, adsorbate, plot_name, plot_directory)

    #task_coverage
    #task_coverage_100
    plane_size = SlabCalculation().plane_size_list
    plane_type = ['100']
    adsorbate = ['H2']
    plot_name = 'Coverage Comparsion 100 H2'
    do_task_2(df, plane_size, plane_type, adsorbate, plot_name, plot_directory)
    # task_coverage_110
    plane_size = SlabCalculation().plane_size_list
    plane_type = ['110']
    adsorbate = ['H2']
    plot_name = 'Coverage Comparsion 110 H2'
    do_task_2(df, plane_size, plane_type, adsorbate, plot_name, plot_directory)
    #task_coverage_111
    plane_size = SlabCalculation().plane_size_list
    plane_type = ['111']
    adsorbate = ['H2']
    plot_name = 'Coverage Comparsion 111 H2'
    do_task_2(df, plane_size, plane_type, adsorbate, plot_name, plot_directory)




#decide the task
def ask_question(question):
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨기기
    return messagebox.askyesno("확인", question)  # Yes -> True, No -> False

# 팝업창에서 Yes/No 버튼으로 선택
is_process = ask_question("Do you want to process the raw data?")
is_plot = ask_question("Do you want to plot the processed data?")

#path
data_directory = 'week4_raw_results/'
processed_excel_path = 'week4_processed_results/week4_processed_results.xlsx'
plot_directory = 'week4_processed_results/'

if is_process:
    week4_result_preocessing(data_directory, processed_excel_path)
if is_plot:
    week4_result_plotting_task(processed_excel_path, plot_directory)