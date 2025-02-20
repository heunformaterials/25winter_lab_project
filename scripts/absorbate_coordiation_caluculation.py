from week4_scripts import week4_function

atoms = ["H", "H"]
angles = 0
original_coords = [(0.50000,   0.50000,   0.5), (0.5 + 1.23465, 0.5, 0.5)]
_, result_coords = week4_function.molecule_angle_editor(atoms, original_coords, angles)
for point in result_coords:
    formatted_point = [f"{i:.4f}" for i in point]
    for v in formatted_point:
        print(v, end = ", ")
    print("")



