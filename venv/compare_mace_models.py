import os
from ase.io import read, write
from ase.optimize import BFGS
from mace.calculators import MACECalculator
import numpy as np


def load_mace_model(model_path, device="cuda"):
    """
    MACE 모델을 로드하는 함수.

    :param model_path: 학습된 MACE 모델의 경로 (.pth 파일)
    :param device: "cuda" 또는 "cpu"
    :return: ASE MACE 계산기
    """
    return MACECalculator(model_path=model_path, device=device)


def optimize_structure(poscar_path, calculator):
    """
    주어진 POSCAR 파일을 최적화하는 함수.

    :param poscar_path: 구조 최적화를 수행할 POSCAR 파일 경로
    :param calculator: MACE 계산기 객체
    :return: 최적화된 ASE 원자 객체, 최종 에너지
    """
    atoms = read(poscar_path, format="vasp")
    atoms.calc = calculator

    optimizer = BFGS(atoms)
    optimizer.run(fmax=0.01)  # 힘이 0.01 eV/Å 이하가 될 때까지 최적화

    final_energy = atoms.get_potential_energy()

    return atoms, final_energy


def compare_models(poscar_path, trained_model_path, original_model_path, device="cuda"):
    """
    학습된 MACE 모델과 원본 MACE 모델의 구조 최적화 및 에너지를 비교.

    :param poscar_path: 입력 POSCAR 파일 경로
    :param trained_model_path: 학습된 MACE 모델 경로 (.pth)
    :param original_model_path: 원본 MACE 모델 경로 (.pth)
    :param device: "cuda" 또는 "cpu"
    """
    # 모델 로드
    trained_mace = load_mace_model(trained_model_path, device)
    original_mace = load_mace_model(original_model_path, device)

    # 구조 최적화 및 에너지 계산
    optimized_atoms_trained, energy_trained = optimize_structure(poscar_path, trained_mace)
    optimized_atoms_original, energy_original = optimize_structure(poscar_path, original_mace)

    # 최적화된 구조 저장
    trained_output_path = poscar_path.replace("POSCAR", "optimized_trained.vasp")
    original_output_path = poscar_path.replace("POSCAR", "optimized_original.vasp")

    write(trained_output_path, optimized_atoms_trained, format="vasp")
    write(original_output_path, optimized_atoms_original, format="vasp")

    # 결과 출력
    print("=== MACE Model Performance Comparison ===")
    print(f"Input POSCAR: {poscar_path}")
    print(f"Trained Model Optimized Energy: {energy_trained:.6f} eV")
    print(f"Original Model Optimized Energy: {energy_original:.6f} eV")
    print(f"Energy Difference (Trained - Original): {energy_trained - energy_original:.6f} eV")
    print(f"Optimized Structures Saved:")
    print(f"  - Trained Model: {trained_output_path}")
    print(f"  - Original Model: {original_output_path}")


# 실행 예제
poscar_path = "path/to/POSCAR"
trained_model_path = "path/to/trained_mace.pth"
original_model_path = "path/to/original_mace.pth"
compare_models(poscar_path, trained_model_path, original_model_path, device="cuda")
