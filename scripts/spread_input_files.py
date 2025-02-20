import os
import shutil

def confirm_file_action(file_name):
    """
    사용자에게 특정 파일을 처리할 것인지 확인하는 함수.

    """
    while True:
        try:
            user_input = input(f"Shall we spread '{file_name}'? (y/n): ").strip().lower()
            if user_input == 'y':
                return True
            elif user_input == 'n':
                return False
            else:
                print("Please enter 'y' or 'n'.")
        except KeyboardInterrupt:
            print("\nUser interrupted input. Exiting...")
            return False  # 강제 종료 시 False 반환

def spread_input_files(root_dir_path, input_dir_path):
    """
    input_dir_path에서 입력 파일을 찾고, root_dir_path 내의 POSCAR이 있는 폴더로 복사.

    Parameters:
        root_dir_path (str): POSCAR을 찾을 루트 디렉토리.
        input_dir_path (str): 복사할 원본 파일이 위치한 디렉토리.

    Returns:
        None
    """
    # 사용자가 복사할 파일 선택
    will_spread = {
        'INCAR': confirm_file_action('INCAR'),
        'KPOINTS': confirm_file_action('KPOINTS'),
        'run_slurm.sh': confirm_file_action('run_slurm.sh'),
        'POTCAR': confirm_file_action('POTCAR'),
        'POSCAR': confirm_file_action('POSCAR')
    }

    # input_dir_path에서 존재하는 파일만 확인하여 복사할 목록 생성
    source_files = {file for file in will_spread if
                    will_spread[file] and os.path.exists(os.path.join(input_dir_path, file))}

    if not source_files:
        print("No selected input files exist in the specified input directory.")
        return

    print(f"Selected files to copy from: {input_dir_path}")
    print(f"Files: {', '.join(source_files)}")

    # root_dir_path에서 POSCAR이 있는 디렉토리 찾기
    for root, dirs, files in os.walk(root_dir_path):
        if 'POSCAR' in files:  # POSCAR이 있는 디렉토리
            print(f"POSCAR found in: {root}")
            for file in source_files:
                src = os.path.join(input_dir_path, file)  # 원본 파일 경로
                dst = os.path.join(root, file)  # 대상 디렉토리의 파일 경로
                try:
                    shutil.copy(src, dst)
                    print(f"Copied {file} to {root}")
                except Exception as e:
                    print(f"Failed to copy {file} to {root}: {e}")

    print("File spreading complete.")

#실행 코드
root_dir_path = '../week4_scripts/week4_mini_preprocessing/preprocessed/111/1x1/8/H2'
input_dir_path = '../week4_scripts/week4_mini_preprocessing/input_files/POTCAR_Cu+H'
spread_input_files(root_dir_path, input_dir_path)
