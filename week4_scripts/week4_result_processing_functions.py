import re
#표면 에너지 계산 함수
def get_surface_energy(E0, layer_pattern, file_path):
    try:
        # 정규 표현식으로 레이어 정보 추출
        layer_match = layer_pattern.search(file_path)
        if not layer_match:
            raise ValueError("파일 경로에서 레이어 정보를 찾을 수 없습니다.")

        layer_info_plane = int(layer_match.group(1))
        layer_info_matrix = layer_match.group(2) + 'x' + layer_match.group(3)

        # A_coefficient 추출 (숫자로 변환 시도)
        try:
            A_coefficient = int(layer_match.group(2))
        except ValueError:
            raise ValueError(f"A_coefficient 값을 정수로 변환할 수 없습니다: {layer_match.group(2)}")

        # 레이어 정보 추출
        layer_info_number = int(layer_match.group(4))
        N_layer = int(layer_info_number)
        N_slab = A_coefficient**2 * N_layer  # 기본 N_slab 값 계산

        # layer_info_plane 값에 따른 면적 할당
        if layer_info_plane == 111:
            A = 5.705775672
        elif layer_info_plane == 110:
            A = 9.317484
        elif layer_info_plane == 100:
            A = 13.1769
            N_slab *= 2  # 100의 경우 N_slab을 두 배로 변경
        else:
            raise ValueError(f"유효하지 않은 layer_info_plane 값: {layer_info_plane}")

        # e0_bulk 선언
        e0_bulk = -3.729872

        # E0 값이 올바른지 체크
        if not isinstance(E0, (int, float)):
            raise TypeError(f"E0 값이 숫자가 아닙니다: {E0}")

        # 표면 에너지 계산
        surface_energy = (E0 - N_slab * e0_bulk) / (2 * A * A_coefficient**2)
        return surface_energy

    except Exception as e:
        print(f"Error processing file at {file_path}: {e}")
        return {
            "E0 Value": f"Could not process input: {e}",
            "Layer Plane": "Error",
            "Layer Matrix Info": "Error",
            "Layers": "Error"
        }

# Extracts the final E0 energy value from OSZICAR
def energy_from_oszicar(file_path):
    import re
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        if not lines:
            return None  # 파일이 비어 있으면 None 반환

        # 마지막 줄부터 역순으로 확인하여 "E0=" 값 찾기
        for line in reversed(lines):
            match = re.search(r"E0=\s*([-\.\dE+]+)", line)
            if match:
                return float(match.group(1))  # E0 값이 있으면 float로 변환하여 반환

        return None  # E0 값이 발견되지 않으면 None 반환

    except Exception as e:
        print(f"Error processing OSZICAR file at {file_path}: {e}")
        return None  # 예외 발생 시 None 반환

#layer_info에서 week3의 slab energy, E0 2개를 가져오는 함수
def slab_energy_from_week3(file_path, layer_pattern):
    import pandas as pd
    import re
    import os

    # 정규 표현식으로 레이어 정보 추출
    layer_match = layer_pattern.search(file_path)
    if not layer_match:
        raise ValueError("파일 경로에서 레이어 정보를 찾을 수 없습니다.")

    layer_info_plane = str(layer_match.group(1))
    layer_info_matrix = layer_match.group(2) + 'x' + layer_match.group(3)
    layer_number = str(layer_match.group(4))
    search_strings = [layer_info_plane, layer_info_matrix, layer_number]

    # 엑셀 파일 경로 설정 및 존재 여부 확인
    week3_excel_path = r'/week3_scripts/final_results_excel/week3_result.xlsx'
    if not os.path.exists(week3_excel_path):
        raise FileNotFoundError(f"엑셀 파일을 찾을 수 없습니다: {week3_excel_path}")

    # 엑셀 데이터 로드
    df = pd.read_excel(week3_excel_path, engine='openpyxl')

    # 필요한 열 확인
    columns = ['Layer Plane', 'Layer Matrix Info', 'Layers', 'Surface Energy', 'E0 Value[eV]']
    if not all(col in df.columns for col in columns):
        raise ValueError(f"엑셀 파일에 필요한 열이 없습니다. 필요 열: {columns}")

    # 데이터 필터링
    filtered_df = df[
        (df[columns[0]].astype(str) == str(layer_info_plane)) &  # 타입 변환 추가
        (df[columns[1]].astype(str).str.contains(layer_info_matrix, na=False)) &  # 기존 유지
        (df[columns[2]].astype(str) == str(layer_number))  # 타입 변환 추가
        ]

    # 필터링된 결과 반환
    if filtered_df.empty:
        return None  # 검색 결과가 없을 경우 None 반환

    return filtered_df[columns[3]].iloc[0], filtered_df[columns[4]].iloc[0]

# 흡착 에너지 게산 함수
def adsorption_energy(E_H_surf, atoms_name, E_surf):
    from ase import Atoms
    # using ase, absorbate 정의
    hydrogen_gas_energy = -0.67538668E+01  # H2 gas energy
    oxygen_gas_energy = -0.98507142E+01  # O2 gas energy
    if atoms_name == 'H':
        hydrogen_atom = Atoms('H')
        hydrogen_atom.info['energy'] = hydrogen_gas_energy / 2
        atoms = hydrogen_atom
    if atoms_name == 'H2':
        hydrogen_gas = Atoms('H2')
        hydrogen_gas.info['energy'] = hydrogen_gas_energy
        atoms = hydrogen_gas
    if atoms_name == 'O':
        oxygen_atom = Atoms('O')
        oxygen_atom.info['energy'] = oxygen_gas_energy / 2
        atoms = oxygen_atom

    adsorbate_energy = atoms.info.get('energy', None)
    E_ads = E_H_surf - adsorbate_energy - E_surf

    return E_ads

