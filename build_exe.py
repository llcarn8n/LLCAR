#!/usr/bin/env python3
"""
Build script for creating LLCAR Windows executable.

Builds a standalone .exe using PyInstaller, creates a portable ZIP package,
and optionally builds an InnoSetup installer.

Usage:
    python build_exe.py              # Build exe + portable package
    python build_exe.py --installer  # Also build InnoSetup installer
    python build_exe.py --clean      # Only clean build artifacts
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

    print("  Clean complete!\n")


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking build dependencies...")
    ok = True

    try:
        import PyInstaller
        print(f"  [OK] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  [!!] PyInstaller not found — pip install pyinstaller")
        ok = False

    try:
        result = subprocess.run(['ffmpeg', '-version'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else 'unknown'
            print(f"  [OK] FFmpeg ({version_line.strip()})")
    except FileNotFoundError:
        print("  [!!] FFmpeg not found in PATH (required at runtime)")

    print()
    return ok


def check_required_files():
    """Check if all required files for building exist."""
    print("Checking required files...")

    required_files = [
        'main.py',
        'gui.py',
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
            print(f"  [OK] {file_name}")
        else:
            print(f"  [!!] {file_name} NOT FOUND")
            all_exist = False

    print()

    if not all_exist:
        print("ERROR: Some required files are missing!")
        print("Please ensure you are running this script from the LLCAR root directory.")
        return False

    return True


def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    print("This may take several minutes...\n")

    cmd = ['pyinstaller', '--clean', 'llcar.spec']

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines[-10:]:
                print(f"  {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error:\n{e.stderr}")
        return False


def create_portable_package():
    """Create a portable package with all necessary files."""
    print("\nCreating portable package...")

    dist_dir = Path('dist/llcar')
    if not dist_dir.exists():
        print("  [!!] Build directory not found")
        return False

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
            shutil.copy2(src, dist_dir / file_name)
            print(f"  Copied {file_name}")

    (dist_dir / 'input').mkdir(exist_ok=True)
    (dist_dir / 'output').mkdir(exist_ok=True)
    print("  Created input/ and output/ directories")

    # ── Console launcher ─────────────────────────────────────────────
    (dist_dir / 'LLCAR Console.bat').write_text(
        '@echo off\r\n'
        'title LLCAR - Video Processing Pipeline\r\n'
        'cd /d "%~dp0"\r\n'
        '\r\n'
        'if not exist ".env" (\r\n'
        '    if exist ".env.example" (\r\n'
        '        echo [!] .env not found. Creating from .env.example ...\r\n'
        '        copy ".env.example" ".env" >nul\r\n'
        '        echo     Please edit .env and set your HuggingFace token.\r\n'
        '        echo.\r\n'
        '    )\r\n'
        ')\r\n'
        '\r\n'
        'echo ================================================================\r\n'
        'echo   LLCAR Video Processing Pipeline - Interactive Console\r\n'
        'echo ================================================================\r\n'
        'echo.\r\n'
        '\r\n'
        'llcar.exe --interactive\r\n'
        'if %errorlevel% neq 0 pause\r\n',
        encoding='utf-8'
    )
    print("  Created 'LLCAR Console.bat'")

    # ── GUI launcher ─────────────────────────────────────────────────
    (dist_dir / 'LLCAR GUI.bat').write_text(
        '@echo off\r\n'
        'cd /d "%~dp0"\r\n'
        'start "" llcar.exe --gui\r\n',
        encoding='utf-8'
    )
    print("  Created 'LLCAR GUI.bat'")

    # ── CLI helper ───────────────────────────────────────────────────
    (dist_dir / 'llcar.bat').write_text(
        '@echo off\r\n'
        'cd /d "%~dp0"\r\n'
        'llcar.exe %*\r\n',
        encoding='utf-8'
    )
    print("  Created llcar.bat")

    print(f"\n  [OK] Portable package created: {dist_dir.absolute()}")
    return True


def build_installer():
    """Build InnoSetup installer if available."""
    print("\nBuilding InnoSetup installer...")

    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    iscc = None
    for p in iscc_paths:
        if os.path.exists(p):
            iscc = p
            break

    if not iscc:
        try:
            subprocess.run(['ISCC', '/?'], capture_output=True)
            iscc = 'ISCC'
        except FileNotFoundError:
            print("  [!!] Inno Setup not found. Skipping installer build.")
            print("       Install from: https://jrsoftware.org/isdl.php")
            return False

    try:
        subprocess.run([iscc, 'installer.iss'],
                       check=True, capture_output=True, text=True)
        print("  [OK] Installer built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [!!] Installer build failed: {e.stderr}")
        return False


def main():
    """Main build process."""
    parser = argparse.ArgumentParser(description="LLCAR Windows Executable Builder")
    parser.add_argument('--installer', action='store_true',
                        help='Also build InnoSetup installer')
    parser.add_argument('--clean', action='store_true',
                        help='Only clean build artifacts and exit')
    args = parser.parse_args()

    print("=" * 70)
    print("  LLCAR Windows Executable Builder")
    print("=" * 70)
    print()

    if not os.path.exists('main.py'):
        print("Error: Please run this script from the LLCAR root directory")
        return 1

    if args.clean:
        clean_build_artifacts()
        print("[OK] Cleaned.")
        return 0

    if not check_required_files():
        return 1

    clean_build_artifacts()

    if not check_dependencies():
        return 1

    if not build_executable():
        print("\n[!!] Build failed!")
        return 1

    if not create_portable_package():
        print("\n[!!] Failed to create portable package!")
        return 1

    if args.installer:
        build_installer()

    print("\n" + "=" * 70)
    print("  BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("  Your executable is ready in: dist/llcar/")
    print()
    print("  Quick launch:")
    print('    "dist\\llcar\\LLCAR Console.bat"  — Interactive console')
    print('    "dist\\llcar\\LLCAR GUI.bat"      — Graphical interface')
    print('    "dist\\llcar\\llcar.bat" --help    — Command-line help')
    print()
    if not args.installer:
        print("  To also build an installer:")
        print("    python build_exe.py --installer")
        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
