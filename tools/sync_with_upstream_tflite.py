import os
import re
import subprocess
import shutil
import sys
from pathlib import Path

tflite_micro_url = 'https://github.com/tensorflow/tflite-micro'

def check_and_install_package(name, package):
    try:
        # Try importing the package
        __import__(name)
    except ImportError:
        # If import fails, the package is likely not installed
        print(f"{name} not found. Installing...")
        try:
            # Use subprocess to call pip install
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{name} installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {name}.")

def setup_tflite(project_root, clone_dir, source_dir):
    # Step 1: Create parent directory for clone_dir if not exist
    parent_dir = Path(clone_dir).parent
    os.makedirs(parent_dir, exist_ok=True)

    # Step 2: Clone the tflite-micro repository
    if not os.path.exists(clone_dir):
        subprocess.run(['git', 'clone', '--recurse-submodules', f'{tflite_micro_url}.git', clone_dir], check=True)
    else:
        subprocess.run(['git', 'pull'], cwd=clone_dir, check=True)

    # Step 3: Execute create_tflm_tree.py with argument -e hello_world
    if os.path.isdir(source_dir):
        shutil.rmtree(source_dir)
    script_path = os.path.join(clone_dir, 'tensorflow', 'lite', 'micro', 'tools', 'project_generation', 'create_tflm_tree.py')
    subprocess.run([sys.executable, script_path, source_dir], check=True, cwd=clone_dir)

def setup_project(project_root, clone_dir, source_dir):
    # Step 1: Remove all files and folders in project
    contents = os.listdir(source_dir)
    for path in contents:
        item_path = os.path.join(project_root, path)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

    # Step 2: Recursively copy all files and folders into project
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(project_root, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def update_readme_commit(readme_path, commit_id):
    commit_url = f'{tflite_micro_url}/commit/{commit_id}'
    # Read the old content and update the commit line
    with open(readme_path, 'r') as file:
        lines = file.readlines()

    with open(readme_path, 'w') as file:
        for line in lines:
            if line.startswith('commit:'):
                file.write(f'commit: [{commit_id}]({commit_url})\n')
            else:
                file.write(line)

def find_source_files(root_dir, subdirectories):
    """ Recursively find all C/C++ source files in specified subdirectories of the given directory. """
    cpp_extensions = {'.cpp', '.cxx', '.cc', '.c'}
    source_files = []
    for subdir in subdirectories:
        full_path = os.path.join(root_dir, subdir)
        for root, dirs, files in os.walk(full_path):
            for file in files:
                if os.path.splitext(file)[1] in cpp_extensions:
                    source_files.append(os.path.relpath(os.path.join(root, file), root_dir))
    return sorted(source_files)

def update_cmake_lists(cmake_path, source_files):
    """ Update the CMakeLists.txt file's add_library section with new source files. """
    with open(cmake_path, 'r') as file:
        lines = file.readlines()

    # Regex to find the add_library start and end
    start_pattern = re.compile(r'^add_library\(\${PROJECT_NAME}')
    end_pattern = re.compile(r'^\)')

    inside_add_library = False
    new_lines = []
    for line in lines:
        if re.match(start_pattern, line):
            inside_add_library = True
            new_lines.append(line)  # add the start line
            # Add all source files
            for src_file in source_files:
                new_lines.append(f"    {src_file}\n")
        elif re.match(end_pattern, line) and inside_add_library:
            new_lines.append(line)  # add the closing parenthesis
            inside_add_library = False
        elif not inside_add_library:
            new_lines.append(line)

    # Write modified content back to CMakeLists.txt
    with open(cmake_path, 'w') as file:
        file.writelines(new_lines)

if __name__ == '__main__':
    project_root = os.path.join(os.path.dirname(__file__), '..')

    # Check if all required packages are installed
    print('Checking if all required packages are installed...')
    check_and_install_package("numpy", "numpy")
    check_and_install_package("PIL", "pillow")

    # Generate tflite-tree
    print('Generating tflite-tree...')
    clone_dir = os.path.join(project_root, 'build', 'tflite-micro')
    source_dir = os.path.join(project_root, 'build', 'tflm-tree')
    setup_tflite(project_root, clone_dir, source_dir)

    # Setup the project
    print('Setting up the project...')
    setup_project(project_root, clone_dir, source_dir)

    # Update CMakeLists.txt
    print('Updating CMakeLists.txt...')
    cmake_path = os.path.join(project_root, 'CMakeLists.txt')
    subdirectories = os.listdir(source_dir)
    source_files = find_source_files(project_root, subdirectories)
    update_cmake_lists(cmake_path, source_files)

    # Update README.md
    print('Updating README.md...')
    commit_id = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=clone_dir, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    readme_file = os.path.join(project_root, 'README.md')
    update_readme_commit(readme_file, commit_id)
