"""
Custom PyInstaller hook for MediaPipe.
This hook ensures that all necessary MediaPipe resources are included in the build.
"""

import os
import glob
import shutil
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

def hook(hook_api):
    """
    PyInstaller hook for MediaPipe.
    This function is called by PyInstaller during the build process.
    """
    # Get MediaPipe package path
    try:
        import mediapipe as mp
        mp_path = os.path.dirname(mp.__file__)
        print(f"MediaPipe path: {mp_path}")
    except ImportError:
        print("MediaPipe not found. Please install it with 'pip install mediapipe'.")
        return
    
    # Collect all MediaPipe modules
    hidden_imports = collect_submodules('mediapipe')
    for imp in hidden_imports:
        hook_api.add_imports(imp)
    
    # Collect all MediaPipe data files
    datas = collect_data_files('mediapipe')
    for src, dest in datas:
        hook_api.add_datas([(src, dest)])
    
    # Ensure binary files are included
    modules_dir = os.path.join(mp_path, 'modules')
    if os.path.exists(modules_dir):
        for root, dirs, files in os.walk(modules_dir):
            for file in files:
                if file.endswith('.binarypb') or file.endswith('.tflite'):
                    src = os.path.join(root, file)
                    # Determine the destination path relative to mediapipe
                    rel_path = os.path.relpath(src, mp_path)
                    dest = os.path.join('mediapipe', os.path.dirname(rel_path))
                    hook_api.add_datas([(src, dest)])
    
    # Include other important directories
    for dir_name in ['calculators', 'modules', 'python', 'tasks']:
        dir_path = os.path.join(mp_path, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith('.py') and not file.endswith('.pyc'):
                        src = os.path.join(root, file)
                        rel_path = os.path.relpath(src, mp_path)
                        dest = os.path.join('mediapipe', os.path.dirname(rel_path))
                        hook_api.add_datas([(src, dest)])
