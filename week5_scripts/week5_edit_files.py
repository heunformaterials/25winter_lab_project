import re

# 원본 데이터 리스트
data = [
    "111_1x1_8_H2_hollow_site_1th hollow_site_0",
    "111_1x1_8_H2_hollow_site_1th hollow_site_45",
    "111_1x1_8_H2_hollow_site_1th hollow_site_90"
]

# 정규식을 사용하여 변환
processed_data = [re.sub(r"_site_", " ", item).replace(" ", "_") for item in data]

# 출력 결과 확인
for item in processed_data:
    print(item)
