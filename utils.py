from pathlib import Path
import shutil

def copy_workflow_file(src_dir, filename: str):
    # 1. Get the absolute path of the script itself
    script_path = Path(__file__).resolve()

    # 2. Get the repository root directory (assumes script is in the root folder)
    # If your script is inside a subfolder, add another .parent (e.g., script_path.parent.parent)
    repo_root = script_path.parent

    # 3. Create absolute paths
    src_path = repo_root / src_dir / filename
    dst_dir = repo_root / ".github" / "workflows"
    dst_path = dst_dir / filename

    try:
        # Create destination directory if missing
        dst_dir.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy(src_path, dst_path)
        print(f"Successfully copied {filename} to {dst_dir}/")

    except FileNotFoundError:
        print(f"Error: Source file '{src_path}' not found.")
        print(f"Looked inside: {src_path.parent}")
