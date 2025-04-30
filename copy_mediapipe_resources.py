"""
Script to copy MediaPipe resources to the build directory.
This is a fallback method in case the PyInstaller hook doesn't work.
"""

import os
import sys
import shutil

def copy_mediapipe_resources(dest_dir):
    """
    Copy MediaPipe resources to the build directory.
    
    Parameters:
    - dest_dir: Destination directory
    """
    try:
        import mediapipe as mp
        mp_path = os.path.dirname(mp.__file__)
        print(f"MediaPipe path: {mp_path}")
    except ImportError:
        print("MediaPipe not found. Please install it with 'pip install mediapipe'.")
        return False
    
    # Create destination directory
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy modules directory
    modules_dir = os.path.join(mp_path, 'modules')
    if os.path.exists(modules_dir):
        dest_modules_dir = os.path.join(dest_dir, 'modules')
        if os.path.exists(dest_modules_dir):
            shutil.rmtree(dest_modules_dir)
        shutil.copytree(modules_dir, dest_modules_dir)
        print(f"Copied modules directory to {dest_modules_dir}")
    
    # Copy other important directories
    for dir_name in ['calculators', 'python', 'tasks']:
        dir_path = os.path.join(mp_path, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            dest_dir_path = os.path.join(dest_dir, dir_name)
            if os.path.exists(dest_dir_path):
                shutil.rmtree(dest_dir_path)
            shutil.copytree(dir_path, dest_dir_path)
            print(f"Copied {dir_name} directory to {dest_dir_path}")
    
    # Copy individual files
    for file_name in os.listdir(mp_path):
        file_path = os.path.join(mp_path, file_name)
        if os.path.isfile(file_path) and not file_name.endswith('.py') and not file_name.endswith('.pyc'):
            dest_file_path = os.path.join(dest_dir, file_name)
            shutil.copy2(file_path, dest_file_path)
            print(f"Copied {file_name} to {dest_file_path}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python copy_mediapipe_resources.py <destination_directory>")
        sys.exit(1)
    
    dest_dir = sys.argv[1]
    if copy_mediapipe_resources(dest_dir):
        print("MediaPipe resources copied successfully.")
    else:
        print("Failed to copy MediaPipe resources.")
        sys.exit(1)
