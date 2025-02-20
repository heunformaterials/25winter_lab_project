import os
import re
import pandas as pd
from scripts import vasp_process

"""
주의: POSCAR_out가 생성된 계산의 경우, 결과 파일(result.xlsx)에 포함되려면
      해당 코드를 한 번 더 실행해야 합니다.

코드 설명:
- CCEL 25_winter week3
- Slab의 에너지와 layer 간의 거리 변화 분석.

기능:
1. POSCAR 파일에서 원본 좌표(original coordination)를 추출합니다.
2. POSCAR_out 값을 POSCAR 값과 비교하여 차이를 계산합니다.
3. 단, POSCAR_out 파일이 없는 경우 CONTCAR 파일로부터 POSCAR_out을 생성합니다.
4. OSZICAR 파일에서 E0값을 추출하고, surface energy를 계산합니다.

주요 파일:
- POSCAR: 원본 좌표를 포함한 파일.
- POSCAR_out: 계산 결과 파일.
- CONTCAR: POSCAR_out을 생성할 수 있는 파일.
"""

# Main function to process files and save results to Excel
def collect_e0_and_layer_info_from_vasp(data_directory, output_excel_path):
    results = []
    layer_pattern = re.compile(r"(\d+)[\\/](\d+)x(\d+)[\\/](\d+)_layer")
    for root, dirs, files in os.walk(data_directory):
        # POSCAR_out.vasp와 CONTCAR의 존재 여부 확인
        is_here_poscar_out = any(file == 'POSCAR_out.vasp' for file in files)
        is_here_contcar_out = any(file == 'CONTCAR' for file in files)

        # POSCAR_out.vasp가 없는 경우 CONTCAR를 처리
        if not is_here_poscar_out and is_here_contcar_out:
            contcar_out_path = os.path.join(root, 'CONTCAR')
            try:
                vasp_process.extract_cartesian_coordinates(contcar_out_path)
            except Exception as e:
                print(f"Error processing file {contcar_out_path}: {e}")

        #각 함수 호출
        OG_list, RS_list, OSZICAR_list = [], [], []
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file == 'POSCAR':
                    OG_list.append(vasp_process.read_original_layer_distance(file_path))
                elif file == 'POSCAR_out.vasp':
                    RS_list.append(vasp_process.read_result_layer_distance(file_path))
                elif file == "OSZICAR":
                    OSZICAR_list.append(vasp_process.extract_energy_from_oszicar(file_path, layer_pattern))
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        min_length = min(len(OG_list), len(RS_list), len(OSZICAR_list))

        # 필요한 모든 데이터가 있는지 확인
        if len(OG_list) > 0 and len(RS_list) > 0 and len(OSZICAR_list) > 0:
            min_length = min(len(OG_list), len(RS_list), len(OSZICAR_list))

            # 계산 수행
            for i in range(min_length):
                try:
                    distance = []
                    OG_d = []
                    for j in range(3):
                        d = (RS_list[i][j] - RS_list[i][j + 1]) - (OG_list[i][j] - OG_list[i][j + 1])
                        OG_d.append(OG_list[i][j] - OG_list[i][j + 1])
                        distance.append(d)

                    # 결과 저장
                    results.append({
                        "δd_12[%]": distance[0] / OG_d[0] * 100 if OG_d[0] != 0 else None,
                        "δd_23[%]": distance[1] / OG_d[1] * 100 if OG_d[1] != 0 else None,
                        "δd_34[%]": distance[2] / OG_d[2] * 100 if OG_d[2] != 0 else None,
                        **OSZICAR_list[i]
                    })
                except IndexError as e:
                    print(f"IndexError in calculation for index {i}: {e}")
                except ZeroDivisionError as e:
                    print(f"ZeroDivisionError in calculation for index {i}: {e}")

    #전체 결과 저장
    df = pd.DataFrame(results)
    try:
        os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
        df.to_excel(output_excel_path, index=False)
        print(f"Results saved to {output_excel_path}")
    except Exception as e:
        print(f"Could not save results to Excel: {e}")

# Example usage
data_directory = "week3_scripts/raw_results_after_DFT"
output_excel_path = "final_results_excel/week3_result.xlsx"
collect_e0_and_layer_info_from_vasp(data_directory, output_excel_path)
