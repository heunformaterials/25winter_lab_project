import os
from pathlib import Path
import shutil

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

#실행
if __name__ == "__main__":
    poscar_dir_path_week3 = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week3_scripts\raw_results_after_DFT"
    poscar_dir_path_week4 = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week4_scripts\week4_raw_results"
    output_dir_path = r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\week5_scripts\calculators_comparision"

    harvest_poscars(poscar_dir_path_week3, output_dir_path)
    harvest_poscars(poscar_dir_path_week4, output_dir_path)

