#!/usr/bin/env python3
"""
Cross-platform package builder for LLCAR.

Creates distributable packages for different platforms:
- Linux/macOS: Portable tar.gz with all source files
- Windows: Can build using PyInstaller (requires Windows)

This script works on any platform and creates packages ready for distribution.

Usage:
    python build_package.py              # Build portable source package
    python build_package.py --platform linux
    python build_package.py --platform macos
    python build_package.py --platform windows  # Requires Windows + PyInstaller
    python build_package.py --all        # Build all portable packages
"""

import os
import sys
import shutil
import tarfile
import zipfile
import argparse
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"

def get_version():
    """Get version from src/__init__.py or use default."""
    try:
        import re
        version_file = Path('src/__init__.py')
        if version_file.exists():
            content = version_file.read_text()
            version_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']',
                                     content, re.MULTILINE)
            if version_match:
                return version_match.group(1)
    except:
        pass
    return VERSION


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")

    dirs_to_clean = ['dist', 'build', '__pycache__', '*.egg-info']
    for pattern in dirs_to_clean:
        if '*' in pattern:
            for path in Path('.').glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"  Removed {path}/")
        else:
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"  Removed {pattern}/")

    print("  Clean complete!\n")


def create_package_dir(version):
    """Create base package directory structure."""
    package_name = f"llcar-{version}"
    package_dir = Path('dist') / package_name

    # Clean and create dist directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)

    return package_dir


def copy_source_files(dest_dir):
    """Copy all necessary source files to package directory."""
    print("Copying source files...")

    # Core files
    files_to_copy = [
        'main.py',
        'gui.py',
        'console.py',
        'demo_console.py',
        'examples.py',
        'config.yaml',
        '.env.example',
        'requirements.txt',
        'requirements-recommended.txt',
        'requirements-build.txt',
        'setup.py',
        'LICENSE',
        'README.md',
        'QUICKSTART.md',
        'INSTALLATION_GUIDE.md',
        'TROUBLESHOOTING.md',
        'FAQ.md',
        'BUILD.md',
        'BUILD_QUICK_REF.md',
        'CONSOLE.md',
        'GUI.md',
        'MODELS.md',
        'WINDOWS.md',
        'DOWNLOAD.md',
        'RELEASE_GUIDE.md',
        'STATUS.md',
        'INSTALLER_SUMMARY.md',
        'ISS_FILE_INFO.md',
        'IMPLEMENTATION_SUMMARY.md',
        'CODE_REVIEW.md',
        'QUICK_FIX_INSTALLATION.md',
        'Makefile',
        'Dockerfile',
        'docker-compose.yml',
        'installer.iss',
        'llcar.spec',
        'build_exe.py',
    ]

    for file_name in files_to_copy:
        src = Path(file_name)
        if src.exists():
            shutil.copy2(src, dest_dir / file_name)
            print(f"  ✓ {file_name}")

    # Copy directories
    dirs_to_copy = ['src', 'input']
    for dir_name in dirs_to_copy:
        src_dir = Path(dir_name)
        if src_dir.exists():
            dest = dest_dir / dir_name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src_dir, dest)
            print(f"  ✓ {dir_name}/")

    # Create empty output directory
    (dest_dir / 'output').mkdir(exist_ok=True)
    print(f"  ✓ output/ (empty)")

    print()


def create_launcher_scripts(package_dir, platform='linux'):
    """Create platform-specific launcher scripts."""
    print(f"Creating launcher scripts for {platform}...")

    if platform in ['linux', 'macos']:
        # Bash launcher for console
        console_launcher = package_dir / 'llcar-console.sh'
        console_launcher.write_text(
            '#!/bin/bash\n'
            '# LLCAR Interactive Console Launcher\n'
            '\n'
            'cd "$(dirname "$0")"\n'
            '\n'
            '# Check for .env file\n'
            'if [ ! -f ".env" ] && [ -f ".env.example" ]; then\n'
            '    echo "[!] .env not found. Creating from .env.example ..."\n'
            '    cp .env.example .env\n'
            '    echo "    Please edit .env and set your HuggingFace token."\n'
            '    echo ""\n'
            'fi\n'
            '\n'
            'echo "================================================================"\n'
            'echo "  LLCAR Video Processing Pipeline - Interactive Console"\n'
            'echo "================================================================"\n'
            'echo ""\n'
            '\n'
            'python3 main.py --interactive\n'
        )
        console_launcher.chmod(0o755)
        print(f"  ✓ llcar-console.sh")

        # Bash launcher for GUI
        gui_launcher = package_dir / 'llcar-gui.sh'
        gui_launcher.write_text(
            '#!/bin/bash\n'
            '# LLCAR GUI Launcher\n'
            '\n'
            'cd "$(dirname "$0")"\n'
            'python3 gui.py\n'
        )
        gui_launcher.chmod(0o755)
        print(f"  ✓ llcar-gui.sh")

        # Install script
        install_script = package_dir / 'install.sh'
        if not install_script.exists():
            install_script.write_text(
                '#!/bin/bash\n'
                '# LLCAR Installation Script\n'
                '\n'
                'set -e\n'
                '\n'
                'echo "Installing LLCAR dependencies..."\n'
                'echo ""\n'
                '\n'
                '# Create virtual environment\n'
                'if [ ! -d "venv" ]; then\n'
                '    python3 -m venv venv\n'
                '    echo "✓ Created virtual environment"\n'
                'fi\n'
                '\n'
                '# Activate virtual environment\n'
                'source venv/bin/activate\n'
                '\n'
                '# Upgrade pip\n'
                'pip install --upgrade pip\n'
                '\n'
                '# Install dependencies\n'
                'echo ""\n'
                'echo "Installing Python packages..."\n'
                'pip install -r requirements.txt\n'
                '\n'
                'echo ""\n'
                'echo "✓ Installation complete!"\n'
                'echo ""\n'
                'echo "To run LLCAR:"\n'
                'echo "  source venv/bin/activate"\n'
                'echo "  ./llcar-console.sh"\n'
                'echo "  or"\n'
                'echo "  ./llcar-gui.sh"\n'
            )
            install_script.chmod(0o755)
        else:
            shutil.copy2(install_script, package_dir / 'install.sh')
        print(f"  ✓ install.sh")

    elif platform == 'windows':
        # Batch launcher for console
        console_launcher = package_dir / 'llcar-console.bat'
        console_launcher.write_text(
            '@echo off\r\n'
            'rem LLCAR Interactive Console Launcher\r\n'
            '\r\n'
            'cd /d "%~dp0"\r\n'
            '\r\n'
            'rem Check for .env file\r\n'
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
            'python main.py --interactive\r\n'
            'if %errorlevel% neq 0 pause\r\n',
            encoding='utf-8'
        )
        print(f"  ✓ llcar-console.bat")

        # Batch launcher for GUI
        gui_launcher = package_dir / 'llcar-gui.bat'
        gui_launcher.write_text(
            '@echo off\r\n'
            'cd /d "%~dp0"\r\n'
            'start "" python gui.py\r\n',
            encoding='utf-8'
        )
        print(f"  ✓ llcar-gui.bat")

        # Install script
        install_script = package_dir / 'install.bat'
        install_script.write_text(
            '@echo off\r\n'
            'rem LLCAR Installation Script\r\n'
            '\r\n'
            'echo Installing LLCAR dependencies...\r\n'
            'echo.\r\n'
            '\r\n'
            'rem Create virtual environment\r\n'
            'if not exist "venv" (\r\n'
            '    python -m venv venv\r\n'
            '    echo [OK] Created virtual environment\r\n'
            ')\r\n'
            '\r\n'
            'rem Activate virtual environment\r\n'
            'call venv\\Scripts\\activate.bat\r\n'
            '\r\n'
            'rem Upgrade pip\r\n'
            'python -m pip install --upgrade pip\r\n'
            '\r\n'
            'rem Install dependencies\r\n'
            'echo.\r\n'
            'echo Installing Python packages...\r\n'
            'pip install -r requirements.txt\r\n'
            '\r\n'
            'echo.\r\n'
            'echo [OK] Installation complete!\r\n'
            'echo.\r\n'
            'echo To run LLCAR:\r\n'
            'echo   llcar-console.bat\r\n'
            'echo   or\r\n'
            'echo   llcar-gui.bat\r\n'
            '\r\n'
            'pause\r\n',
            encoding='utf-8'
        )
        print(f"  ✓ install.bat")

    print()


def create_readme_install(package_dir, platform='linux'):
    """Create installation README."""
    print("Creating INSTALL.txt...")

    if platform in ['linux', 'macos']:
        install_text = f"""LLCAR Video Processing Pipeline - Installation Guide

Version: {get_version()}
Platform: {platform.upper()}

═══════════════════════════════════════════════════════════════════

QUICK START
═══════════════════════════════════════════════════════════════════

1. Run the installation script:

   ./install.sh

2. Activate the virtual environment:

   source venv/bin/activate

3. Set up your HuggingFace token:

   cp .env.example .env
   # Edit .env and add your token

4. Launch LLCAR:

   ./llcar-console.sh    # Interactive console
   ./llcar-gui.sh        # Graphical interface

═══════════════════════════════════════════════════════════════════

REQUIREMENTS
═══════════════════════════════════════════════════════════════════

- Python 3.8 or later
- FFmpeg (must be installed separately)
- HuggingFace account and token (free)
- 8GB RAM minimum (16GB recommended for GPU processing)

═══════════════════════════════════════════════════════════════════

MANUAL INSTALLATION
═══════════════════════════════════════════════════════════════════

If the install.sh script doesn't work, install manually:

1. Install FFmpeg:

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS
   brew install ffmpeg

2. Create a virtual environment:

   python3 -m venv venv
   source venv/bin/activate

3. Install Python dependencies:

   pip install --upgrade pip
   pip install -r requirements.txt

4. Set up .env file:

   cp .env.example .env
   # Edit .env and set HF_TOKEN=your_token_here

═══════════════════════════════════════════════════════════════════

GETTING A HUGGINGFACE TOKEN
═══════════════════════════════════════════════════════════════════

1. Sign up at https://huggingface.co/
2. Go to Settings → Access Tokens
3. Create a new token with 'read' permissions
4. Copy the token to your .env file

═══════════════════════════════════════════════════════════════════

USAGE
═══════════════════════════════════════════════════════════════════

Interactive Console:
   ./llcar-console.sh

Graphical Interface:
   ./llcar-gui.sh

Command Line:
   python main.py --video /path/to/video.mp4 --language ru

For more information, see:
- README.md - Full documentation
- QUICKSTART.md - Quick start guide
- TROUBLESHOOTING.md - Common issues

═══════════════════════════════════════════════════════════════════

SUPPORT
═══════════════════════════════════════════════════════════════════

Documentation: https://github.com/llcarn8n/LLCAR
Issues: https://github.com/llcarn8n/LLCAR/issues

"""
    else:  # Windows
        install_text = f"""LLCAR Video Processing Pipeline - Installation Guide

Version: {get_version()}
Platform: WINDOWS

═══════════════════════════════════════════════════════════════════

QUICK START
═══════════════════════════════════════════════════════════════════

1. Run the installation script:

   install.bat

2. Set up your HuggingFace token:

   copy .env.example .env
   REM Edit .env and add your token

3. Launch LLCAR:

   llcar-console.bat    REM Interactive console
   llcar-gui.bat        REM Graphical interface

═══════════════════════════════════════════════════════════════════

REQUIREMENTS
═══════════════════════════════════════════════════════════════════

- Windows 10/11 (64-bit)
- Python 3.8 or later
- FFmpeg (must be installed separately)
- HuggingFace account and token (free)
- 8GB RAM minimum (16GB recommended for GPU processing)

═══════════════════════════════════════════════════════════════════

MANUAL INSTALLATION
═══════════════════════════════════════════════════════════════════

If the install.bat script doesn't work, install manually:

1. Install FFmpeg:

   Download from: https://ffmpeg.org/download.html
   Add to system PATH

2. Create a virtual environment:

   python -m venv venv
   venv\\Scripts\\activate.bat

3. Install Python dependencies:

   python -m pip install --upgrade pip
   pip install -r requirements.txt

4. Set up .env file:

   copy .env.example .env
   REM Edit .env and set HF_TOKEN=your_token_here

═══════════════════════════════════════════════════════════════════

GETTING A HUGGINGFACE TOKEN
═══════════════════════════════════════════════════════════════════

1. Sign up at https://huggingface.co/
2. Go to Settings → Access Tokens
3. Create a new token with 'read' permissions
4. Copy the token to your .env file

═══════════════════════════════════════════════════════════════════

USAGE
═══════════════════════════════════════════════════════════════════

Interactive Console:
   llcar-console.bat

Graphical Interface:
   llcar-gui.bat

Command Line:
   python main.py --video C:\\path\\to\\video.mp4 --language ru

For more information, see:
- README.md - Full documentation
- QUICKSTART.md - Quick start guide
- TROUBLESHOOTING.md - Common issues

═══════════════════════════════════════════════════════════════════

SUPPORT
═══════════════════════════════════════════════════════════════════

Documentation: https://github.com/llcarn8n/LLCAR
Issues: https://github.com/llcarn8n/LLCAR/issues

"""

    (package_dir / 'INSTALL.txt').write_text(install_text)
    print(f"  ✓ INSTALL.txt")
    print()


def create_tarball(package_dir, version, platform='linux'):
    """Create compressed tarball."""
    print(f"Creating {platform} package archive...")

    dist_dir = Path('dist')
    package_name = f"llcar-{version}"

    if platform == 'windows':
        # Create ZIP for Windows
        zip_name = f"LLCAR-{version}-windows-portable.zip"
        zip_path = dist_dir / zip_name

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(dist_dir)
                    zipf.write(file_path, arcname)

        print(f"  ✓ {zip_name}")
        print(f"  Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        # Create tar.gz for Linux/macOS
        tar_name = f"llcar-{version}-{platform}.tar.gz"
        tar_path = dist_dir / tar_name

        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(package_dir, arcname=package_name)

        print(f"  ✓ {tar_name}")
        print(f"  Size: {tar_path.stat().st_size / 1024 / 1024:.2f} MB")

    print()
    return True


def build_package(platform='linux', version=None):
    """Build a distributable package for the specified platform."""
    if version is None:
        version = get_version()

    print("=" * 70)
    print(f"  LLCAR Package Builder - {platform.upper()}")
    print("=" * 70)
    print()
    print(f"Version: {version}")
    print(f"Platform: {platform}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Create package directory
    package_dir = create_package_dir(version)

    # Copy source files
    copy_source_files(package_dir)

    # Create launcher scripts
    create_launcher_scripts(package_dir, platform)

    # Create installation guide
    create_readme_install(package_dir, platform)

    # Create archive
    create_tarball(package_dir, version, platform)

    print("=" * 70)
    print(f"  BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print(f"  Package created: dist/")
    print()
    print(f"  Distribution files:")
    if platform == 'windows':
        print(f"    - LLCAR-{version}-windows-portable.zip")
    else:
        print(f"    - llcar-{version}-{platform}.tar.gz")
    print()

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LLCAR Cross-Platform Package Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_package.py                    # Build for current platform
  python build_package.py --platform linux   # Build Linux package
  python build_package.py --platform macos   # Build macOS package
  python build_package.py --platform windows # Build Windows portable package
  python build_package.py --all              # Build all platforms
  python build_package.py --clean            # Clean build artifacts only
        """
    )

    parser.add_argument(
        '--platform',
        choices=['linux', 'macos', 'windows'],
        default=sys.platform.replace('darwin', 'macos').replace('win32', 'windows').split('linux')[0] + ('linux' if 'linux' in sys.platform else ''),
        help='Target platform (default: current platform)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Build packages for all platforms'
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts and exit'
    )

    parser.add_argument(
        '--version',
        help='Override version number'
    )

    args = parser.parse_args()

    # Check we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: Please run this script from the LLCAR root directory")
        return 1

    # Clean if requested
    if args.clean:
        clean_build_artifacts()
        print("[OK] Cleaned.")
        return 0

    # Clean before building
    clean_build_artifacts()

    # Build for requested platforms
    if args.all:
        platforms = ['linux', 'macos', 'windows']
        for platform in platforms:
            if not build_package(platform, args.version):
                return 1
            print()
    else:
        # Auto-detect platform if not specified
        if not hasattr(args, 'platform') or args.platform is None:
            if sys.platform.startswith('linux'):
                args.platform = 'linux'
            elif sys.platform == 'darwin':
                args.platform = 'macos'
            elif sys.platform.startswith('win'):
                args.platform = 'windows'
            else:
                args.platform = 'linux'  # default

        if not build_package(args.platform, args.version):
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
