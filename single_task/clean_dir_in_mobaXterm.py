import os

# Set of file names to keep (e.g., the script itself and files to preserve)
FILES_TO_KEEP = {"INCAR", "KPOINTS", "POSCAR", "POTCAR", "run_slurm.sh"}
# Get the directory path where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Iterate over all items in the directory
for item in os.listdir(script_dir):
    # Skip items that are in the keep list
    if item in FILES_TO_KEEP:
        continue

    # Create the full path for the item to be deleted
    full_path = os.path.join(script_dir, item)

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"File removed: {full_path}")
        elif os.path.isdir(full_path):
            # Skip directories
            continue
    except Exception as e:
        print(f"Failed to remove ({full_path}): {e}")
