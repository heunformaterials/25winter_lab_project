import os
from ase import Atoms
import re

def calculate_adsorption_energy(non_adsorbants_dir_path, with_adsorbant_file, calculator):
    layer_pattern = re.compile(r"(\d+)_(\d+)x(\d+)_(\d+)")
    layer_match = layer_pattern.search(non_adsorbants_dir_path)
    calculator_name = "EMT"
    adsorbant_name = with_adsorbant_file.split("_")[4]

    if layer_match:
        for root, dirs, files in os.walk(non_adsorbants_dir_path):
            for file in files:
                if file.find(calculator_name):
                    with open(file, "r") as file:
                        lines = file.readlines()
                        index = lines.find("surface_energy") #해당 단어가 들어있는 줄의 index 서칭
                        original_surface_energy = lines[index].split()[1]
                        adsorbate_energy = adsorbant_name



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
        E_ads = total_ads_E_surf - adsorbate_energy - E_surf
        return E_ads