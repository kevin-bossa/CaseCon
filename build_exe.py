#!/usr/bin/env python3
"""
Build script for CaseCon application
Creates a standalone executable using PyInstaller
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    print("Cleaning previous build artifacts...")
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}")
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"Removed {spec_file}")

def install_requirements():
    """Install required packages for building"""
    requirements = [
        'pyinstaller',
        'tkinter',  # Usually built-in but just in case
        'keyboard',
        'pystray',
        'Pillow',
        'pyperclip'
    ]
    
    print("Installing/checking build requirements...")
    for req in requirements:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], 
                          check=True, capture_output=True)
            print(f"✓ {req}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {req}")

def create_icon():
    """Create a basic icon if none exists"""
    icon_path = "icon.ico"
    if not os.path.exists(icon_path):
        print("Creating default icon...")
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a blue square with white "CC" text
            draw.rectangle([32, 32, 224, 224], fill='#0066CC', outline='#004499', width=4)
            
            # Draw "CC" text
            try:
                # Try to use a better font if available
                from PIL import ImageFont
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Get text size and center it
            bbox = draw.textbbox((0, 0), "CC", font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (256 - text_width) // 2
            text_y = (256 - text_height) // 2
            
            draw.text((text_x, text_y), "CC", fill='white', font=font)
            
            # Save as ICO
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"Created icon: {icon_path}")
            
        except ImportError:
            print("Pillow not available for icon creation, using default")
        except Exception as e:
            print(f"Could not create icon: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable file
        '--windowed',                   # No console window
        '--name=CaseCon',              # Executable name
        '--icon=icon.ico',             # Icon file (if exists)
        '--add-data=icon.ico;.',       # Include icon in bundle
        '--hidden-import=pystray._win32',  # Required for pystray
        '--hidden-import=PIL._tkinter_finder',  # Required for PIL with tkinter
        '--distpath=installer_files',   # Output to installer_files directory
        'GUI.py'                       # Main script
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Executable built successfully!")
        print("Output location: installer_files/CaseCon.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def create_installer_directory():
    """Create directory structure for Inno Setup"""
    installer_dir = Path("installer_files")
    installer_dir.mkdir(exist_ok=True)
    
    # Copy additional files if they exist
    files_to_copy = ["icon.ico", "README.md", "LICENSE.txt"]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, installer_dir / file_name)
            print(f"Copied {file_name} to installer directory")

def main():
    """Main build process"""
    print("=" * 50)
    print("Building CaseCon Application")
    print("=" * 50)
    
    # Step 1: Clean previous builds
    clean_build()
    
    # Step 2: Install requirements
    install_requirements()
    
    # Step 3: Create icon if needed
    create_icon()
    
    # Step 4: Create installer directory
    create_installer_directory()
    
    # Step 5: Build executable
    if build_executable():
        print("\n" + "=" * 50)
        print("Build completed successfully!")
        print("Files ready for Inno Setup:")
        print("- installer_files/CaseCon.exe")
        print("- installer_files/icon.ico")
        print("- CaseCon_Setup.iss (Inno Setup script)")
        print("\nNext steps:")
        print("1. Install Inno Setup Compiler")
        print("2. Open CaseCon_Setup.iss in Inno Setup")
        print("3. Click 'Compile' to create the installer")
        print("=" * 50)
    else:
        print("\n✗ Build failed. Check error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()