import ase.io

import torch

# 학습 코드 실행 중이라면 현재 모델을 메모리에 가지고 있을 가능성이 있음
# 수동으로 체크포인트 저장
model = torch.load(r"C:\Users\user\PycharmProjects\PythonProject\mace_venv\25winter_lab_project\venv\MACE_test_models\mace_fine_tuning_v2_run-123_epoch-0.pt", map_location="cuda")  # 기존 모델 로드

# 최신 상태를 강제로 저장
torch.save(model, r"C:\Users\user\PycharmProjects\PythonProject\mace_venv\25winter_lab_project\venv\MACE_test_models\mace_fine_tuning_v2_run-123_epoch-3.pt")

print("Epoch-3 모델이 강제로 저장되었습니다.")
