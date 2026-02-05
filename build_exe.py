#!/usr/bin/env python3
"""
Build script for creating LLCAR Windows executable

This script automates the process of building a standalone executable
using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

    print("  Clean complete!\n")


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking build dependencies...")

    try:
        import PyInstaller
        print(f"  ✓ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  ✗ PyInstaller not found")
        print("\nPlease install PyInstaller:")
        print("  pip install pyinstaller")
        return False

    # Check for FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ FFmpeg installed")
    except FileNotFoundError:
        print("  ⚠ FFmpeg not found in PATH")
        print("    Note: FFmpeg is required for the application to work")

    print()
    return True


def check_required_files():
    """Check if all required files for building exist."""
    print("Checking required files...")

    required_files = [
        'main.py',
        'llcar.spec',
        'config.yaml',
        '.env.example',
        'README.md',
        'LICENSE',
    ]

    all_exist = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} NOT FOUND")
            all_exist = False

    print()

    if not all_exist:
        print("ERROR: Some required files are missing!")
        print("Please ensure you are running this script from the LLCAR root directory")
        print("and that all necessary files exist.")
        return False

    return True


def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    print("This may take several minutes...\n")

    # Run PyInstaller
    cmd = ['pyinstaller', '--clean', 'llcar.spec']

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error:\n{e.stderr}")
        return False


def create_portable_package():
    """Create a portable package with necessary files."""
    print("Creating portable package...")

    dist_dir = Path('dist/llcar')
    if not dist_dir.exists():
        print("  ✗ Build directory not found")
        return False

    # Copy additional files
    files_to_copy = [
        'README.md',
        'LICENSE',
        'config.yaml',
        '.env.example',
        'QUICKSTART.md',
        'CONSOLE.md',
    ]

    for file_name in files_to_copy:
        src = Path(file_name)
        if src.exists():
            dst = dist_dir / file_name
            shutil.copy2(src, dst)
            print(f"  Copied {file_name}")

    # Create directories
    (dist_dir / 'input').mkdir(exist_ok=True)
    (dist_dir / 'output').mkdir(exist_ok=True)
    print("  Created input/ and output/ directories")

    # Create batch file for easy launching
    batch_content = """@echo off
REM LLCAR Video Processing Pipeline Launcher
REM
REM Usage:
REM   llcar.bat --help              - Show help
REM   llcar.bat --interactive       - Launch interactive console
REM   llcar.bat --video input\\video.mp4  - Process video

llcar.exe %*
"""

    batch_file = dist_dir / 'llcar.bat'
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    print("  Created llcar.bat launcher")

    # Create README for the package
    readme_content = """# LLCAR - Portable Windows Package

This is a portable version of LLCAR Video Processing Pipeline.

## Quick Start

1. Get your HuggingFace token from https://huggingface.co/settings/tokens
2. Rename `.env.example` to `.env` and add your token
3. Place your video/audio files in the `input/` folder
4. Run `llcar.bat --interactive` to launch the interactive console

## Usage

### Interactive Console (Recommended)
```
llcar.bat --interactive
```

### Command Line
```
llcar.bat --video input\\video.mp4 --language en
llcar.bat --audio input\\audio.wav --language ru
```

### Help
```
llcar.bat --help
```

## Requirements

- FFmpeg must be installed and in your system PATH
- Minimum 8GB RAM (16GB recommended)
- GPU with CUDA support (optional, for faster processing)

## Documentation

See the included documentation files:
- README.md - Full documentation
- QUICKSTART.md - Quick start guide
- CONSOLE.md - Interactive console guide

## Support

GitHub: https://github.com/llcarn8n/LLCAR
"""

    readme_file = dist_dir / 'README_PORTABLE.txt'
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print("  Created README_PORTABLE.txt")

    print("\n✓ Portable package created successfully!")
    print(f"\nPackage location: {dist_dir.absolute()}")
    return True


def main():
    """Main build process."""
    print("=" * 70)
    print("LLCAR Windows Executable Builder")
    print("=" * 70)
    print()

    # Check we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: Please run this script from the LLCAR root directory")
        return 1

    # Check required files exist
    if not check_required_files():
        return 1

    # Clean previous builds
    clean_build_artifacts()

    # Check dependencies
    if not check_dependencies():
        return 1

    # Build executable
    if not build_executable():
        print("\n✗ Build failed!")
        return 1

    # Create portable package
    if not create_portable_package():
        print("\n✗ Failed to create portable package!")
        return 1

    print("\n" + "=" * 70)
    print("✓ BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nYour executable is ready in: dist/llcar/")
    print("\nNext steps:")
    print("  1. Test the executable: cd dist/llcar && llcar.bat --help")
    print("  2. Create installer: Use Inno Setup with installer.iss")
    print("  3. Distribute the dist/llcar/ folder or the installer")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
