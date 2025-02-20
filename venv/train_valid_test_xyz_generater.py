import os
import random
from ase.io import read, write

def classify_contcars(contcar_list, contcar_dir):
    """
    CONTCAR 파일을 흡착물 유무에 따라 분류.
    - 'H2', 'H', 'O' 원자가 포함되면 with_adsorbate_contcar_list
    - 포함되지 않으면 non_adsorbate_contcar_list
    """
    non_adsorbate_contcar_list = []
    with_adsorbate_contcar_list = []

    for contcar in contcar_list:
        contcar_path = os.path.join(contcar_dir, contcar)
        atoms = read(contcar_path, format="xyz")
        elements = set(atoms.get_chemical_symbols())
        print(elements)

        if "H" in elements: # or "O" in elements
            with_adsorbate_contcar_list.append(contcar)
        else:
            non_adsorbate_contcar_list.append(contcar)

    return non_adsorbate_contcar_list, with_adsorbate_contcar_list

def xyz_merge(contcar_list, contcar_dir, xyz_dir_path, filename):
    """
    여러 CONTCAR 파일을 하나의 .xyz 파일로 변환하여 저장.
    """
    output_path = os.path.join(xyz_dir_path, filename)

    with open(output_path, "w") as outfile:
        for contcar in contcar_list:
            contcar_path = os.path.join(contcar_dir, contcar)
            atoms = read(contcar_path, format="xyz")
            write(outfile, atoms, format="xyz")

    print(f"✅ {filename} 파일이 {xyz_dir_path}에 저장되었습니다.")


def main():
    # train, valid, test size 지정
    '''
    H2_train_size = int(input('enter the H2 train size(even number!): '))  # typically 26
    non_train_size = int(input('enter the pure train size(even number!): '))  # typically 26
    H2_valid_size = int(input('enter the H2 valid size(even number!): '))  # typically 6
    non_valid_size = int(input('enter the valid size(even number!): '))  # typically 6
    H2_test_size = int(input('enter the H2 test size(even number!): '))  # typically 6
    non_test_size = int(input('enter the test size(even number!): '))  # typically 6
    '''

    H2_train_size = 36
    non_train_size = 18
    H2_valid_size = 8
    non_valid_size = 5
    H2_test_size = 8
    non_test_size = 5

    # CONTCAR 파일이 있는 디렉토리 & XYZ 파일 저장 디렉토리
    contcar_dir = "./xyz_files_for_fine_tuning"
    merged_xyz_dir_path = f"./mace_fine_tuning_data_set/test_size_v1"
    os.makedirs(merged_xyz_dir_path, exist_ok=True)

    total_contcar_list = [f for f in os.listdir(contcar_dir) if f.startswith("CONTCAR")]
    non_adsorbate_contcar_list, with_adsorbate_contcar_list = classify_contcars(total_contcar_list, contcar_dir)

    # 랜덤 샘플링 (각 그룹에서 train: 26, valid: 6, test: 6)
    train_non_ads = random.sample(non_adsorbate_contcar_list, non_train_size)
    valid_non_ads = random.sample([x for x in non_adsorbate_contcar_list if x not in train_non_ads], non_valid_size)
    test_non_ads = random.sample([x for x in non_adsorbate_contcar_list if x not in train_non_ads + valid_non_ads], non_test_size)

    train_with_ads = random.sample(with_adsorbate_contcar_list, H2_train_size)
    valid_with_ads = random.sample([x for x in with_adsorbate_contcar_list if x not in train_with_ads], H2_valid_size)
    test_with_ads = random.sample([x for x in with_adsorbate_contcar_list if x not in train_with_ads + valid_with_ads], H2_test_size)

    # 최종 train, valid, test 리스트 합치기
    train_list = train_non_ads + train_with_ads
    valid_list = valid_non_ads + valid_with_ads
    test_list = test_non_ads + test_with_ads

    # xyz_merge 함수 실행 및 파일 저장
    xyz_merge(train_list, contcar_dir, merged_xyz_dir_path, f"Cu_slab_train_H2_{H2_train_size}_non_{non_train_size}.xyz")
    xyz_merge(valid_list, contcar_dir, merged_xyz_dir_path, f"Cu_slab_valid_H2_{H2_valid_size}_non_{non_valid_size}.xyz")
    xyz_merge(test_list, contcar_dir, merged_xyz_dir_path, f"Cu_slab_test_H2_{H2_test_size}_non_{non_test_size}.xyz")


if __name__ == "__main__":
    main()
