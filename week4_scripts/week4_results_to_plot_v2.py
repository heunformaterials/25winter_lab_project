import matplotlib.pyplot as plt
import pandas as pd
import re
import os

def categorize_job_names(name):
    job_name_dictionary = {}
    subbed_name = re.sub(r"_site_", " ", name).replace(" ", "_")
    words = subbed_name.split("_")
    seen = set()
    unique_words = [word for word in words if not (word in seen or seen.add(word))]
    fined_job_name = "_".join(unique_words)
    job_name_dictionary["plane_type"] = fined_job_name.split("_")[0]
    job_name_dictionary["coverage"] = fined_job_name.split("_")[1]
    job_name_dictionary["adsorbant_name"] = fined_job_name.split("_")[3]
    job_name_dictionary["site_name"] = fined_job_name.split("_")[4]
    if 'th' in fined_job_name.split("_")[5]:
        job_name_dictionary["site_type"] = fined_job_name.split("_")[5]
        job_name_dictionary["degree"] = fined_job_name.split("_")[6]
    else:
        job_name_dictionary["degree"] = fined_job_name.split("_")[5]
    return job_name_dictionary

def get_energy_by_job_name(needed_job_dictionary, df, df_energy_column_name):
    needed_energy_list, needed_job_list = [], []
    for i, job in enumerate(df["Job Name"]):
        job_name_dictionary = categorize_job_names(job)
        is_the_needed_energy = True
        for needed_job_title, needed_job_info in needed_job_dictionary.items():
            if job_name_dictionary.get(needed_job_title) != needed_job_info:
                is_the_needed_energy = False  # False로 설정
                break  # 조건 불일치 시 반복문 종료

        if is_the_needed_energy:
            needed_energy_list.append(df.at[i, df_energy_column_name])  # 더 안전한 접근 방식
            needed_job_list.append(job)

    return needed_energy_list, needed_job_list

#task 별로 따로 만드는 게 가장 효율적인 것 같다.
def week4_results_to_plot_task1(excel_file_path, plot_directory):
    df = pd.read_excel(excel_file_path)
    #task1
    task1_needed_job_dictionary ={
        "plane_type": "100",
        "coverage": "3x3",
        "adsorbant_name": "H2",
    }
    df_energy_column_name = "Adsorption Energy [J/m^2]"
    task1_energy_list, task1_job_list = get_energy_by_job_name(task1_needed_job_dictionary, df, df_energy_column_name)
    #데이터를 1) site 별로 2) 각도 별로 분류하기
    energy_list_0, energy_list_45, energy_list_90 = [], [], []
    job_list_regardless_of_degree = []
    for i, job_name in enumerate(task1_job_list):
        job_name_dictionary = categorize_job_names(job_name)
        new_job_name = ""
        for k, name in enumerate(list(job_name_dictionary.values())[:-1]):
            #if k == 3:
                #name = name[0]
            if name not in list(task1_needed_job_dictionary.values()) and name != "8":
                new_job_name += name + '.'
        new_job_name = new_job_name.strip('.')

        if job_name_dictionary.get("degree") == "0":
            energy_list_0.append(task1_energy_list[i])
        elif job_name_dictionary.get("degree") == "45":
            energy_list_45.append(task1_energy_list[i])
        elif job_name_dictionary.get("degree") == "90":
            energy_list_90.append(task1_energy_list[i])

        if new_job_name not in job_list_regardless_of_degree:
            job_list_regardless_of_degree.append(new_job_name)

    plot_title = "(100)-plane 3x3 H2 adsorption energy"
    plt.plot(job_list_regardless_of_degree, energy_list_0, label="0˚", color="red",linestyle=":",marker="s")
    plt.plot(job_list_regardless_of_degree, energy_list_45, label="45˚", color="green",linestyle=":",marker="^")
    plt.plot(job_list_regardless_of_degree, energy_list_90, label="90˚", color="blue",linestyle=":",marker="o")
    plt.title(f"{plot_title}") #Cu (100) plane 1/4 coverage
    plt.ylabel("Adsorption Energy [J/m^2]")
    plt.legend()
    save_path = os.path.join(plot_directory, f"{plot_title}")
    plt.savefig(save_path)
    plt.show()


def week4_results_to_plot_task2(excel_file_path, plot_directory):
    df = pd.read_excel(excel_file_path)
    #task1
    task2_needed_job_dictionary_100 ={
        "plane_type": "100",
        "coverage": "2x2",
        "adsorbant_name": "H2",
    }
    task2_needed_job_dictionary_110 = {
        "plane_type": "110",
        "coverage": "2x2",
        "adsorbant_name": "H2",
    }
    task2_needed_job_dictionary_111 = {
        "plane_type": "111",
        "coverage": "2x2",
        "adsorbant_name": "H2",
    }
    df_energy_column_name = "Adsorption Energy [J/m^2]"
    task2_energy_list, task2_job_list = [], []
    E_100, J_100 = get_energy_by_job_name(task2_needed_job_dictionary_100, df, df_energy_column_name)
    E_110, J_110 = get_energy_by_job_name(task2_needed_job_dictionary_110, df, df_energy_column_name)
    E_111, J_111 = get_energy_by_job_name(task2_needed_job_dictionary_111, df, df_energy_column_name)
    task2_energy_list.extend(E_100)
    task2_energy_list.extend(E_110)
    task2_energy_list.extend(E_111)
    task2_job_list.extend(J_100)
    task2_job_list.extend(J_110)
    task2_job_list.extend(J_111)
    #데이터를 1) site 별로 2) 각도 별로 분류하기
    energy_list_0, energy_list_45, energy_list_90 = [], [], []
    job_list_regardless_of_degree = []
    for i, job_name in enumerate(task2_job_list):
        job_name_dictionary = categorize_job_names(job_name)

        new_job_name = ""
        for k, name in enumerate(list(job_name_dictionary.values())[:-1]):
            if k == 3:
                name = name[0]
            if name != "2x2" and name != "8" and name != "H2":
                new_job_name += name + '.'
        new_job_name = new_job_name.strip('.')

        if job_name_dictionary.get("degree") == "0":
            energy_list_0.append(task2_energy_list[i])
        elif job_name_dictionary.get("degree") == "45":
            energy_list_45.append(task2_energy_list[i])
        elif job_name_dictionary.get("degree") == "90":
            energy_list_90.append(task2_energy_list[i])
        if new_job_name not in job_list_regardless_of_degree:
            job_list_regardless_of_degree.append(new_job_name)

    plot_title = "(100), (110), (111) 2x2 H2 adsorption energy comparision"
    plt.plot(job_list_regardless_of_degree, energy_list_0, label="0˚", color="red",linestyle=":",marker="s")
    plt.plot(job_list_regardless_of_degree, energy_list_45, label="45˚", color="green",linestyle=":",marker="^")
    plt.plot(job_list_regardless_of_degree, energy_list_90, label="90˚", color="blue",linestyle=":",marker="o")
    plt.title(f"{plot_title}") #Cu (100) plane 1/4 coverage
    plt.xticks(rotation=45)
    plt.ylabel("Adsorption Energy [J/m^2]")
    plt.tight_layout()  # 자동으로 여백 조정
    plt.legend()
    save_path = os.path.join(plot_directory, f"{plot_title}")
    plt.savefig(save_path)
    plt.show()


#실행
excel_file_path = r'C:\Users\spark\PycharmProjects\CCEL_25winter_project\week4_scripts\week4_processed_results\week4_processed_results.xlsx'
plot_directory = r'C:\Users\spark\Desktop\winter_lab\lecture_4'
week4_results_to_plot_task1(excel_file_path, plot_directory)
week4_results_to_plot_task2(excel_file_path, plot_directory)




