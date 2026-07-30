import os
import shutil

def copy_workflow_file(src_dir, filename: str):
    # Define source and destination directories
    dst_dir = ".github/workflows"

    # Construct full file paths
    src_path = os.path.join(src_dir, filename)
    dst_path = os.path.join(dst_dir, filename)

    try:
        # Create destination directory (and parent folders) if missing
        os.makedirs(dst_dir, exist_ok=True)

        # Copy the file (overwrites if it already exists)
        shutil.copy(src_path, dst_path)
        print(f"Successfully copied {filename} to {dst_dir}/")

    except FileNotFoundError:
        print(f"Error: Source file '{src_path}' not found.")
    except PermissionError:
        print(f"Error: Missing permissions to write to '{dst_dir}'.")
