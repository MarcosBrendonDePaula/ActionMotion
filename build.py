"""
Build script for ActionMotion application.
This script creates an executable version of the application using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import platform

def install_dependencies():
    """Install required dependencies from requirements.txt."""
    if not os.path.exists('requirements.txt'):
        print("requirements.txt not found. Creating a basic one...")
        with open('requirements.txt', 'w') as f:
            f.write("""# Core dependencies
opencv-python>=4.5.0
mediapipe>=0.8.9
numpy>=1.19.0
pillow>=8.0.0

# Build dependencies
pyinstaller>=5.0.0

# Optional dependencies
pynput>=1.7.0  # For keyboard and mouse control
""")
    
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install some dependencies. Please install them manually with 'pip install -r requirements.txt'.")
        return False

def check_pyinstaller():
    """Check if PyInstaller is installed, and install it if not."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
        return True
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller. Please install it manually with 'pip install pyinstaller'.")
            return False

def create_spec_file():
    """Create a PyInstaller spec file for the application."""
    # Check if vosk model directory exists
    vosk_data = ""
    if os.path.exists('vosk-model-small-pt-0.3'):
        vosk_data = "        ('vosk-model-small-pt-0.3', 'vosk-model-small-pt-0.3'),"
        print("Including Vosk model in the build.")
    
    # Create hooks directory if it doesn't exist
    if not os.path.exists('hooks'):
        os.makedirs('hooks', exist_ok=True)
    
    # Copy mediapipe_hook.py to hooks directory
    if os.path.exists('mediapipe_hook.py'):
        shutil.copy('mediapipe_hook.py', os.path.join('hooks', 'hook-mediapipe.py'))
        print("Copied MediaPipe hook to hooks directory")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gestos', 'gestos'),
        ('config', 'config'),
""" + vosk_data + """
    ],
    hiddenimports=[
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.hands',
        'mediapipe.python.solutions.pose',
        'mediapipe.python.solutions.drawing_utils',
        'mediapipe.python.solutions.drawing_styles',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ActionMotion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ActionMotion',
)
"""
    
    with open('ActionMotion.spec', 'w') as f:
        f.write(spec_content)
    
    print("Spec file created: ActionMotion.spec")
    return True

def create_icon():
    """Create a simple icon for the application if one doesn't exist."""
    if os.path.exists('icon.ico'):
        print("Icon already exists: icon.ico")
        return True
    
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        img = Image.new('RGB', (256, 256), color=(53, 53, 53))
        d = ImageDraw.Draw(img)
        
        # Draw a hand shape
        d.rectangle((50, 50, 206, 206), fill=(0, 120, 212))
        d.ellipse((70, 70, 130, 130), fill=(255, 255, 255))
        d.rectangle((90, 130, 110, 190), fill=(255, 255, 255))
        d.rectangle((120, 110, 140, 190), fill=(255, 255, 255))
        d.rectangle((150, 90, 170, 190), fill=(255, 255, 255))
        d.rectangle((180, 110, 200, 190), fill=(255, 255, 255))
        
        # Save as ICO
        img.save('icon.ico')
        print("Created icon: icon.ico")
        return True
    except ImportError:
        print("PIL (Pillow) is not installed. Using a default icon.")
        # Create an empty file as a placeholder
        with open('icon.ico', 'wb') as f:
            f.write(b'')
        return True

def find_mediapipe_path():
    """Find the MediaPipe installation path."""
    try:
        import mediapipe as mp
        mp_path = os.path.dirname(mp.__file__)
        print(f"MediaPipe path: {mp_path}")
        return mp_path
    except ImportError:
        print("MediaPipe not found. Please install it with 'pip install mediapipe'.")
        return None

def build_application():
    """Build the application using PyInstaller."""
    try:
        # Create directories if they don't exist
        os.makedirs('gestos', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        
        # Create a default gestures file if it doesn't exist
        if not os.path.exists(os.path.join('gestos', 'gestos.json')):
            with open(os.path.join('gestos', 'gestos.json'), 'w') as f:
                f.write('{}')
        
        # Create a default config file if it doesn't exist
        if not os.path.exists(os.path.join('config', 'settings.json')):
            with open(os.path.join('config', 'settings.json'), 'w') as f:
                f.write('{}')
        
        # Find MediaPipe path
        mp_path = find_mediapipe_path()
        if mp_path:
            # Copy MediaPipe binary files to a local directory
            mp_modules_dir = os.path.join(mp_path, 'modules')
            if os.path.exists(mp_modules_dir):
                local_mp_dir = 'mediapipe_data'
                os.makedirs(local_mp_dir, exist_ok=True)
                
                # Copy modules directory
                local_modules_dir = os.path.join(local_mp_dir, 'modules')
                if os.path.exists(local_modules_dir):
                    shutil.rmtree(local_modules_dir)
                shutil.copytree(mp_modules_dir, local_modules_dir)
                
                print(f"Copied MediaPipe modules to {local_modules_dir}")
                
                # Update spec file to include MediaPipe data
                with open('ActionMotion.spec', 'r') as f:
                    spec_content = f.read()
                
                # Add MediaPipe data to datas list
                spec_content = spec_content.replace(
                    "datas=[",
                    "datas=[\n        ('mediapipe_data', 'mediapipe'),")
                
                with open('ActionMotion.spec', 'w') as f:
                    f.write(spec_content)
                
                print("Updated spec file to include MediaPipe data")
        
        # Run PyInstaller
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "ActionMotion.spec"])
        
        # Determine the output directory based on the platform
        if platform.system() == "Windows":
            output_dir = "dist\\ActionMotion"
        else:
            output_dir = "dist/ActionMotion"
        
        # Run the copy_mediapipe_resources.py script as a post-build step
        if os.path.exists('copy_mediapipe_resources.py'):
            mediapipe_dest_dir = os.path.join(output_dir, 'mediapipe')
            print(f"Copying MediaPipe resources to {mediapipe_dest_dir}...")
            try:
                subprocess.check_call([sys.executable, 'copy_mediapipe_resources.py', mediapipe_dest_dir])
                print("MediaPipe resources copied successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to copy MediaPipe resources: {e}")
                print("The application may still work if the PyInstaller hook included all necessary files.")
        
        print("Build completed successfully!")
        
        print(f"The executable is located in: {os.path.abspath(output_dir)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def main():
    """Main function to build the application."""
    print("=== ActionMotion Build Script ===")
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        return
    
    # Create spec file
    if not create_spec_file():
        return
    
    # Create icon
    if not create_icon():
        return
    
    # Build the application
    if not build_application():
        return
    
    print("=== Build Process Completed ===")

if __name__ == "__main__":
    main()
