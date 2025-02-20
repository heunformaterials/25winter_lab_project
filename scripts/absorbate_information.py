"""
앞으로 metal surface에 붙일 absorbate의 기본 정보를 제공하는 나만의 mini data base. week4_function.py의 함수와 연계할 때 편리함 up
"""
import math
import numpy as np
class Absorbate:
    def __init__(self, name, atoms, coordinates, energy):
        """
                분자 정보를 초기화하는 클래스
                Args:
                    name (str): 분자의 이름
                    atoms (list of str): 원자들의 리스트 (예: ["H", "H", "O"])
                    coordinates (list of tuple): 각 원자의 3D 좌표 리스트 (예: [(0, 0, 0), (1, 1, 1), (2, 2, 2)])
                """
        self.name = name
        self.atoms = atoms
        self.coordinates = np.array(coordinates)
        self.energy = energy

#adsorbate계산 결과(좌표, 에너지) 넣기
hydrogen_gas_energy = -0.67538668E+01 #H2 gas energy
hydrogen_atom = Absorbate("H", ["H"], [[0.0, 0.0, 0.0]], hydrogen_gas_energy / 2)
hydrogen_gas = Absorbate("H", ["H", "H"], [[0.0, 0.0, 0.0], [0.0000, 0.0000, 0.7460]], hydrogen_gas_energy)
oxygen_gas_energy = -0.98507142E+01 #O2 gas energy
oxygen_atom = Absorbate("O", ["O"], [[0.0, 0.0, 0.0]], oxygen_gas_energy / 2)
oxygen_gas = Absorbate("O", ["O", "O"], [[0.0, 0.0, 0.0], [0.0000, 0.0000, 1.2347]], oxygen_gas_energy)
