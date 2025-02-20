import os
import re
from pathlib import Path

# Define the root directory where the script is run.
# This script will search for run_slurm.sh files in all subdirectories.
script_dir = os.getcwd()
root_dir = script_dir
root_project_name = '5_cu'
print('This is your root project name: ', root_project_name)
print('In terms of the depth from the root (remind Tree DB!)')
depth_from_my_element = int(input('type the depth of the script from the element: '))

# Walk through the directory tree starting from root_dir
for current_dir, dirs, files in os.walk(root_dir):
    if "run_slurm.sh" in files:
        sh_file_path = os.path.join(current_dir, "run_slurm.sh")
        # Get the relative path of the sh file from the script directory
        absolute_path = os.path.abspath(sh_file_path)
        file_path_list = Path(absolute_path).parts
        project_index = next((i for i, part in enumerate(file_path_list) if root_project_name in part), None)
        # Set the new job name as 'Cu' concatenated with the relative path
        my_new_job_name = 'Cu'
        for a in list(file_path_list[project_index + depth_from_my_element:-1]):
            if len(a) >= 4:
                a = a[:3]
            my_new_job_name += '' + a
        # Read the content of run_slurm.sh
        with open(sh_file_path, 'r') as file:
            lines = file.readlines()

        # Open the file for writing and modify the job name line
        with open(sh_file_path, 'w') as file:
            for line in lines:
                # Check if the line contains the job name specification
                if line.strip().startswith("#SBATCH") and "--job-name=" in line:
                    # Use regex to replace the existing job name with the new one
                    new_line = re.sub(r'(--job-name=)\S+', r'\1' + my_new_job_name, line)
                    file.write(new_line)
                else:
                    file.write(line)

        print(f"Updated job name to '{my_new_job_name}' with the length of {len(my_new_job_name)}")
