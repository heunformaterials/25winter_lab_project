import os
import shutil
from pathlib import Path
def harvest_my_contcars(scattered_contcars_directory, harvested_contcars_directory):
    if not os.path.exists(harvested_contcars_directory):
        os.makedirs(harvested_contcars_directory)

    data_tree_root_name = Path(scattered_contcars_directory).parts[-1]

    for root, dirs, files in os.walk(scattered_contcars_directory):
        for file in files:
            if file == "CONTCAR":
                contcar_info = []
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
                new_filename = 'CONTCAR'
                for name in contcar_info:
                    new_filename += '_' + name.split("_")[0]
                #copy the file to the directory
                new_file_path = os.path.join(harvested_contcars_directory, new_filename)
                try:
                    shutil.copy2(file_path, new_file_path)  # 파일 복사
                    print(f"파일 복사 및 이름 변경 완료: {new_file_path}")
                except Exception as e:
                    print(f"파일 이동 중 오류 발생: {e}")

#실행 코드
scattered_contcars_directory1 = '../week3_scripts/raw_results_after_DFT'
scattered_contcars_directory2 = '../week4_scripts/week4_raw_results'
harvested_contcars_directory = './contcars_for_fine_tuning'
harvest_my_contcars(scattered_contcars_directory1, harvested_contcars_directory)
harvest_my_contcars(scattered_contcars_directory2, harvested_contcars_directory)