import time
from ase.io import read
from ase.optimize import LBFGS
from mace.calculators import mace_mp

# 1. POSCAR 파일 읽기
atoms = read(r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\venv\mace_cal_data\Cu_bulk_calc\POSCAR")  # VASP의 POSCAR 파일을 ASE 원자 객체로 변환

# 2. MACE 계산기 설정
calc = mace_mp(model="small", dispersion=False, default_dtype="float64", device='cpu', verbose=True)
atoms.calc = calc  # 원자 객체에 계산기 할당

# 3. BFGS 최적화 객체 생성 (실시간 경과 시간 출력 포함)
class TimerBFGS(LBFGS):
    def __init__(self, atoms, *args, **kwargs):
        super().__init__(atoms, *args, **kwargs)
        self.start_time = time.time()  # 최적화 시작 시간

    def log_iteration(self):
        elapsed_time = time.time() - self.start_time
        print(f"Step {self.nsteps}, Elapsed Time: {elapsed_time:.2f} s, Energy: {self.atoms.get_potential_energy():.6f} eV")

# 4. 최정화 수행 및 구조 저장
opt = TimerBFGS(atoms)
opt.run(fmax=0.005)  # 힘이 0.01 eV/Å 이하가 될 때까지 최적화
atoms.write(r"C:\Users\spark\PycharmProjects\CCEL_25winter_project\venv\mace_cal_data\Cu_bulk_calc\bulk_small_CONTCAR")  # VASP 형식으로 최적화된 구조 저장 (VASP의 CONTCAR 역할)

# 5. 최적화된 에너지 출력
print("Optimized Energy:", atoms.get_potential_energy())

# 6. 최적화 완료 후 총 경과 시간 출력
total_time = time.time() - opt.start_time
print(f"Optimization completed in {total_time:.2f} seconds")

