import os
import re

# 데이터 파일이 있는 디렉토리 설정
data_dir = "../data/STD"

# 정규 표현식 패턴: 'E0='가 포함된 줄 찾기
line_pattern = r".*E0=.*"

# 파일 ID 추출 정규식
file_id_pattern = r"\d+(?=\.out$)"

# 값 추출 함수: E0= 포함된 줄 전체를 출력
def extract_lines_with_ids(directory, line_pattern, file_id_pattern):
    extracted_lines = []
    for filename in os.listdir(directory):
        if filename.endswith(".out"):
            filepath = os.path.join(directory, filename)

            # 파일 읽기
            with open(filepath, "r") as file:
                lines = file.readlines()

                # 각 줄에서 'E0=' 패턴 찾기
                for line in lines:
                    if re.search(line_pattern, line):
                        # 파일 이름에서 ID 추출
                        file_id_match = re.search(file_id_pattern, filename)
                        file_id = file_id_match.group() if file_id_match else "Unknown"

                        # 파일 ID와 줄 텍스트 저장
                        extracted_lines.append((file_id, line.strip()))

    return extracted_lines

# 실행
if __name__ == "__main__":
    extracted_lines = extract_lines_with_ids(data_dir, line_pattern, file_id_pattern)

    # 결과 출력
    if extracted_lines:
        print(f"Extracted {len(extracted_lines)} lines:")
        for file_id, line in extracted_lines:
            # E0 값 추출
            e0_value = None
            match = re.search(r"E0=\s*([-\.\dE+]+)", line)
            if match:
                e0_value = float(match.group(1))  # E0 값을 실수로 변환

            if e0_value is not None:
                # 일반 형식으로 변환하여 출력
                print(f"File ID: {file_id}, E0= {e0_value:.6f}")
            else:
                print(f"File ID: {file_id}, E0= Not Found")
    else:
        print("No lines found containing 'E0='.")
