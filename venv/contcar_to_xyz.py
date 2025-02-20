import os
from ase.io import read, write
def transform_contcars_into_xyz(harvested_contcars_directory, xyz_files_directory):
    if not os.path.exists(xyz_files_directory):
        os.makedirs(xyz_files_directory)

    input_dir_path = harvested_contcars_directory
    output_dir_path = xyz_files_directory
    contcar_files = [f for f in os.listdir(input_dir_path) if f.startswith("CONTCAR")]

    if len(contcar_files) != len(set(contcar_files)):
        print("주의: 중복된 파일 이름이 존재함")

    # 변환 실행
    for contcar in contcar_files:
        try:
            # 파일 읽고, xyz 변환 후 저장
            atoms = read(os.path.join(input_dir_path, contcar), format="vasp")
            xyz_filename = contcar + ".xyz"
            write(os.path.join(output_dir_path, xyz_filename), atoms, format="xyz")
            print(f"변환 완료: {contcar} → {xyz_filename}")

        except Exception as e:
            print(f"오류 발생: {contcar} 변환 실패 - {e}")

    xyz_file_number = len(contcar_files)
    print("모든 변환이 완료되었습니다.")
    print(f"변환된 총 .xyz 파일 개수: {xyz_file_number}")

harvested_contcars_directory = './contcars_for_fine_tuning'
xyz_files_directory = './xyz_files_for_fine_tuning'
transform_contcars_into_xyz(harvested_contcars_directory, xyz_files_directory)
