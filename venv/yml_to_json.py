import yaml
import json

config_path = "config_test_v1.yml"  # 본인의 config 파일 경로로 변경

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

with open("config_test_v1.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4)

print("✅ config.json 파일이 생성되었습니다. 이제 JSON 파일로 실행해보세요!")
