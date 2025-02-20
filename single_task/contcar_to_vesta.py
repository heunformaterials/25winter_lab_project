import os
import subprocess

def contcar_to_vesta(contcars_directory, program_path):
    contcar_path_list = []

    # CONTCAR 파일 탐색
    for root, dirs, files in os.walk(contcars_directory):
        for file in files:
            if file == 'CONTCAR':
                raw_contcar_path = os.path.join(root, file)
                contcar_path_list.append(raw_contcar_path)

    # 상위 2개의 CONTCAR 파일만 실행
    for i, p in enumerate(contcar_path_list):
        try:
            print(f"Opening: {p} with {program_path}")
            subprocess.Popen(f'"{program_path}" "{p}"', shell=True)  # shell=True 추가
        except PermissionError as e:
            print(f"PermissionError 발생: {e}")
        except FileNotFoundError:
            print(f"파일을 찾을 수 없음: {p}")
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")

# 사용 예시 (VESTA 실행 파일 경로 정확히 지정)
program_path = r"C:\Users\spark\Desktop\winter_lab\VASP_lecture\VESTA-win64\VESTA-win64\VESTA.exe"
contcars_directory = r'C:\Users\spark\PycharmProjects\CCEL_25winter_project\week4_scripts\week4_raw_results'  # 상대 경로 사용 시 문제 발생 가능 -> 절대 경로로 변경 추천

contcar_to_vesta(contcars_directory, program_path)
