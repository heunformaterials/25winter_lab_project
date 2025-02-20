import os
import time
import subprocess
import shutil
from pathlib import Path

def contcar_to_vesta(contcars_directory, program_path, contcars_output_path):
    contcar_path_list, new_contcar_path_list = [], []
    # CONTCAR 파일 탐색
    for root, dirs, files in os.walk(contcars_directory):
        for file in files:
            if file == 'CONTCAR':
                raw_contcar_path = os.path.join(root, file)
                contcar_path_list.append(raw_contcar_path)

                #CONTCAR 복사본 형성
                file_path_list = Path(raw_contcar_path).parts
                project_index = next((i for i, path in enumerate(file_path_list) if "week4_raw_results" in path), None)
                job_name = 'CONTCAR'
                for a in list(file_path_list[project_index + 1:-1]):
                    job_name += ' ' + a
                new_contcar_path = os.path.join(contcars_output_path, job_name)
                new_contcar_path_list.append(new_contcar_path)
                shutil.copy(raw_contcar_path, new_contcar_path)

    #VESTA로 new CONTCARs 실행
    count = 0
    for p in new_contcar_path_list:
        try:
            print(f"Opening: {p} with VESTA")
            subprocess.Popen(f'"{program_path}" "{p}"', shell=True)  # shell=True 추가
            time.sleep(0.5)  # 1초 지연
            count += 1
        except PermissionError as e:
            print(f"PermissionError 발생: {e}")
        except FileNotFoundError:
            print(f"파일을 찾을 수 없음: {p}")
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")

    return print(f"total opened contcars: {count}")

# 사용 예시 (VESTA 실행 파일 경로 정확히 지정)
program_path = r"C:\Users\spark\Desktop\winter_lab\VASP_lecture\VESTA-win64\VESTA-win64\VESTA.exe"
contcars_directory = r'C:\Users\spark\PycharmProjects\CCEL_25winter_project\week4_scripts\week4_raw_results'
contcars_output_path = r'C:\Users\spark\PycharmProjects\CCEL_25winter_project\week4_scripts\week4_processed_contcars'
os.makedirs(contcars_output_path, exist_ok=True)

contcar_to_vesta(contcars_directory, program_path, contcars_output_path)
