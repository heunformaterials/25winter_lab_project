import warnings
warnings.filterwarnings("ignore")

import os
import sys
import json
import logging
from mace.cli.run_train import main as mace_run_train_main

# Windows에서 UTF-8 강제 적용
os.environ["PYTHONUTF8"] = "1"

def train_mace(config_file_path):
    # JSON 파일도 지원할 수 있도록 수정
    if config_file_path.endswith(".json"):
        with open(config_file_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)  # JSON 파일 로드

        # JSON 데이터를 임시 YAML 파일로 변환 (MACE는 YAML을 기본으로 사용 가능성 높음)
        temp_yaml_path = config_file_path.replace(".json", ".yml")
        with open(temp_yaml_path, "w", encoding="utf-8") as f:
            import yaml
            yaml.dump(config_data, f, default_flow_style=False)

        config_file_path = temp_yaml_path  # 변환된 YAML 사용

    # stdout으로 실시간 출력
    sys.argv = ["program", "--config", config_file_path]
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")

    mace_run_train_main()
    sys.stdout.flush()  # 강제 출력

# 실행 코드 (JSON 파일 사용 가능)
config_file_path = "./config_test_v2.json"  # JSON 파일 사용 가능
train_mace(config_file_path)
