import pandas as pd
import os
import re
import matplotlib.pyplot as plt

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
    if 'H2' in fined_job_name.split("_"):
        if 'th' in fined_job_name.split("_")[5]:
            job_name_dictionary["site_type"] = fined_job_name.split("_")[5]
            job_name_dictionary["degree"] = fined_job_name.split("_")[6]
        else:
            job_name_dictionary["degree"] = fined_job_name.split("_")[5]
    else:
        if len(fined_job_name.split("_")) > 5:
            job_name_dictionary["site_type"] = fined_job_name.split("_")[5]
        None
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

def week5_results_to_plot(reference_excel_file_path, excel_by_calculator_dir_path, plot_directory):
    df_list = {}
    ref_df = pd.read_excel(reference_excel_file_path)
    df_list["DFT"] = ref_df
    raw_reference_job_name_list = ref_df['Job Name']
    fined_reference_job_name_list = []
    for job in raw_reference_job_name_list:
        subbed_name = re.sub(r"_site_", " ", job).replace(" ", "_")
        words = subbed_name.split("_")
        seen = set()
        unique_words = [word for word in words if not (word in seen or seen.add(word))]
        fined_job_name = "_".join(unique_words)
        fined_reference_job_name_list.append(fined_job_name)


    for root, dirs, files in os.walk(excel_by_calculator_dir_path):
        for file in files:
            if file.startswith("~$"):
                continue
            calculator_name = file.split("_")[2:]
            calculator_name = "_".join(calculator_name)
            calculator_name = calculator_name.replace(".xlsx", "")
            df = pd.read_excel(os.path.join(root, file))
            df_list[calculator_name] = df

    #task 분류 시작 - 1
    task1_energy_list = {}
    for calculator_name in list(df_list.keys()):
        task1_energy_list[calculator_name] = {"energy_list_0": [],"energy_list_45": [],"energy_list_90": [], "job_name_list": []}
    #계산기 이름에 따른 각도 에너지 리스트 생성 완료
    for calculator_name, df in df_list.items():
        needed_job_dictionary = {
            "plane_type": "100",
            "coverage": "3x3",
            "adsorbant_name": "H2",
        }
        df_energy_column_name = "Adsorption Energy [eV/Å^2]"
        energy_list, job_list = get_energy_by_job_name(needed_job_dictionary, df, df_energy_column_name)
        # 데이터를 1) site 별로 2) 각도 별로 분류하기
        energy_list_0, energy_list_45, energy_list_90 = [], [], []
        job_list_regardless_of_degree = []
        for i, job_name in enumerate(job_list):
            job_name_dictionary = categorize_job_names(job_name)
            new_job_name = ""
            for k, name in enumerate(list(job_name_dictionary.values())[:-1]):
                # if k == 3:
                # name = name[0]
                if name not in list(needed_job_dictionary.values()) and name != "8":
                    new_job_name += name + '.'
            new_job_name = new_job_name.strip('.')

            if job_name_dictionary.get("degree") == "0":
                energy_list_0.append(energy_list[i])
            elif job_name_dictionary.get("degree") == "45":
                energy_list_45.append(energy_list[i])
            elif job_name_dictionary.get("degree") == "90":
                energy_list_90.append(energy_list[i])

            if new_job_name not in job_list_regardless_of_degree:
                job_list_regardless_of_degree.append(new_job_name)

        task1_energy_list[calculator_name]["energy_list_0"].extend(energy_list_0)
        task1_energy_list[calculator_name]["energy_list_45"].extend(energy_list_45)
        task1_energy_list[calculator_name]["energy_list_90"].extend(energy_list_90)
        task1_energy_list[calculator_name]["job_name_list"].extend(job_list_regardless_of_degree)

    color_list = ["black", "blue","green","red","magenta","yellow","black","gray","orange","purple","pink","brown","cyan",]
    count = 0
    plt.figure(figsize=(10, 6))
    for calculator_name, property_list in task1_energy_list.items():
        if 'mace' not in calculator_name:
            continue
        angle_styles = {
            "0˚": (f"{color_list[count]}", ":", "s"),
            "45˚": (f"{color_list[count]}", ":", "^"),
            "90˚": (f"{color_list[count]}", ":", "o")
        }
        count += 1
        energy_lists = {
            "0˚": property_list["energy_list_0"],
            "45˚": property_list["energy_list_45"],
            "90˚": property_list["energy_list_90"]
        }
        for angle, (color, linestyle, marker) in angle_styles.items():
            plt.plot(property_list["job_name_list"], energy_lists[angle], label=f"{calculator_name} - {angle}",
                     color=color, linestyle=linestyle, marker=marker)

    plt.title("Calculator Comparison - Adsorption Energy")  # Cu (100) plane 1/4 coverage
    plt.grid(True, linestyle="--", alpha=0.5)  # 배경에 그리드 추가하여 가독성 향상
    plt.ylabel(df_energy_column_name)
    plt.legend()
    plt.show()

    #save_path = os.path.join(plot_directory, f"{plot_title}")
    #plt.savefig(save_path)

def week5_results_to_plot_v2(reference_excel_file_path, excel_by_calculator_dir_path, plot_directory):
    df_list = {}
    ref_df = pd.read_excel(reference_excel_file_path)
    df_list["DFT"] = ref_df
    raw_reference_job_name_list = ref_df['Job Name']
    fined_reference_job_name_list = []
    for job in raw_reference_job_name_list:
        subbed_name = re.sub(r"_site_", " ", job).replace(" ", "_")
        words = subbed_name.split("_")
        seen = set()
        unique_words = [word for word in words if not (word in seen or seen.add(word))]
        fined_job_name = "_".join(unique_words)
        fined_reference_job_name_list.append(fined_job_name)


    for root, dirs, files in os.walk(excel_by_calculator_dir_path):
        for file in files:
            if file.startswith("~$"):
                continue
            calculator_name = file.split("_")[2:]
            calculator_name = "_".join(calculator_name)
            calculator_name = calculator_name.replace(".xlsx", "")
            df = pd.read_excel(os.path.join(root, file))
            df_list[calculator_name] = df

    #task 분류 시작 - 1
    task1_energy_list = {}
    for calculator_name in list(df_list.keys()):
        task1_energy_list[calculator_name] = {"energy_list_0": [],"energy_list_45": [],"energy_list_90": [], "job_name_list": []}
    #계산기 이름에 따른 각도 에너지 리스트 생성 완료
    for calculator_name, df in df_list.items():
        needed_job_dictionary = {
            "plane_type": "100",
            "coverage": "3x3",
            "adsorbant_name": "H2",
        }
        df_energy_column_name = "Adsorption Energy [eV/Å^2]"
        energy_list, job_list = get_energy_by_job_name(needed_job_dictionary, df, df_energy_column_name)
        # 데이터를 1) site 별로 2) 각도 별로 분류하기
        energy_list_0, energy_list_45, energy_list_90 = [], [], []
        job_list_regardless_of_degree = []
        for i, job_name in enumerate(job_list):
            job_name_dictionary = categorize_job_names(job_name)
            new_job_name = ""
            for k, name in enumerate(list(job_name_dictionary.values())[:-1]):
                # if k == 3:
                # name = name[0]
                if name not in list(needed_job_dictionary.values()) and name != "8":
                    new_job_name += name + '.'
            new_job_name = new_job_name.strip('.')

            if job_name_dictionary.get("degree") == "0":
                energy_list_0.append(energy_list[i])
            elif job_name_dictionary.get("degree") == "45":
                energy_list_45.append(energy_list[i])
            elif job_name_dictionary.get("degree") == "90":
                energy_list_90.append(energy_list[i])

            if new_job_name not in job_list_regardless_of_degree:
                job_list_regardless_of_degree.append(new_job_name)

        task1_energy_list[calculator_name]["energy_list_0"].extend(energy_list_0)
        task1_energy_list[calculator_name]["energy_list_45"].extend(energy_list_45)
        task1_energy_list[calculator_name]["energy_list_90"].extend(energy_list_90)
        task1_energy_list[calculator_name]["job_name_list"].extend(job_list_regardless_of_degree)

    color_list = ["black", "blue", "green", "red", "magenta", "yellow", "black", "gray",
                  "orange", "purple", "pink", "brown", "cyan"]
    count = 0
    for calculator_name, property_list in task1_energy_list.items():
        plt.figure(figsize=(8, 6))  # 각 calculator마다 새로운 figure 생성
        angle_styles = {
            "0˚": (f"{color_list[count]}", ":", "s"),
            "45˚": (f"{color_list[count]}", ":", "^"),
            "90˚": (f"{color_list[count]}", ":", "o")
        }
        count += 1  # 색상 인덱스 증가

        energy_lists = {
            "0˚": property_list["energy_list_0"],
            "45˚": property_list["energy_list_45"],
            "90˚": property_list["energy_list_90"]
        }

        for angle, (color, linestyle, marker) in angle_styles.items():
            plt.plot(property_list["job_name_list"], energy_lists[angle],
                     label=f"{angle}", color=color, linestyle=linestyle, marker=marker)
        plt.title(f"{calculator_name} - H2 Adsorption Energy")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.ylabel(df_energy_column_name)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        save_path = os.path.join(plot_directory, f"{calculator_name} - H2 Adsorption Energy")
        plt.savefig(save_path)
        plt.show()  # 각 계산기별 그래프 출력



#실행 코드
if __name__ == "__main__":
    reference_excel_file_path = r'C:\Users\spark\PycharmProjects\CCEL_25winter_project\week4_scripts\week4_processed_results\week4_processed_results.xlsx'
    excel_by_calculator_dir_path = r'C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\week5_results'
    plot_directory = r'C:\Users\spark\Desktop\winter_lab\lecture_5'
    #week5_results_to_plot(reference_excel_file_path, excel_by_calculator_dir_path, plot_directory)
    week5_results_to_plot_v2(reference_excel_file_path, excel_by_calculator_dir_path, plot_directory)


    """
     plt.plot(property_list["job_name_list"], property_list["energy_list_0"], label="0˚", color="red", linestyle=":", marker="s")
            plt.plot(property_list["job_name_list"], property_list["energy_list_45"], label="45˚", color="green", linestyle=":", marker="^")
            plt.plot(property_list["job_name_list"], property_list["energy_list_90"], label="90˚", color="blue", linestyle=":", marker="o")
    """