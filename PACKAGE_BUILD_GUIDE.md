# LLCAR - Package Build Guide

**Обновлено:** 2026-02-07

This guide explains how to build distributable packages for LLCAR across different platforms.

## Overview

LLCAR provides two different build systems:

1. **Cross-Platform Package Builder** (`build_package.py`) - Works on Linux/macOS/Windows
   - Creates portable source packages
   - No compilation required
   - Users run from Python source

2. **Windows Executable Builder** (`build_exe.py`) - Windows only
   - Creates standalone .exe files
   - Requires PyInstaller and Windows
   - See [BUILD.md](BUILD.md) for details

## Quick Start

### Build Portable Package (Any Platform)

```bash
# Build for current platform
python build_package.py

# Or use Make
make package
```

### Build All Platforms at Once

```bash
# Build Linux, macOS, and Windows portable packages
python build_package.py --all

# Or use Make
make package-all
```

## Package Builder (`build_package.py`)

### Features

- ✅ Works on any platform (Linux, macOS, Windows)
- ✅ Creates ready-to-distribute packages
- ✅ Includes installation scripts
- ✅ Generates launcher scripts
- ✅ No compilation needed
- ✅ Small package size (~100KB compressed)

### Usage

```bash
# Build for specific platform
python build_package.py --platform linux
python build_package.py --platform macos
python build_package.py --platform windows

# Build all platforms
python build_package.py --all

# Clean build artifacts
python build_package.py --clean

# Override version
python build_package.py --version 1.2.0
```

### Output Files

After building, you'll find in the `dist/` directory:

**Linux:**
- `llcar-1.0.0-linux.tar.gz` - Compressed package for Linux

**macOS:**
- `llcar-1.0.0-macos.tar.gz` - Compressed package for macOS

**Windows:**
- `LLCAR-1.0.0-windows-portable.zip` - Compressed package for Windows

### What's Included in Packages

Each package contains:

```
llcar-1.0.0/
├── src/                    # Source code
├── main.py                 # CLI entry point
├── gui.py                  # GUI application
├── console.py              # Console launcher
├── config.yaml             # Configuration
├── .env.example            # Environment template
├── requirements*.txt       # Dependencies
├── INSTALL.txt            # Installation instructions
├── README.md              # Documentation
├── LICENSE                # License file
├── llcar-console.sh       # Console launcher (Linux/macOS)
├── llcar-gui.sh          # GUI launcher (Linux/macOS)
├── llcar-console.bat      # Console launcher (Windows)
├── llcar-gui.bat         # GUI launcher (Windows)
├── install.sh            # Install script (Linux/macOS)
├── install.bat           # Install script (Windows)
├── input/                # Sample input directory
└── output/               # Output directory
```

## Distribution Instructions

### For End Users

#### Linux/macOS

1. Extract the tarball:
   ```bash
   tar -xzf llcar-1.0.0-linux.tar.gz
   cd llcar-1.0.0
   ```

2. Run installation:
   ```bash
   ./install.sh
   ```

3. Launch LLCAR:
   ```bash
   ./llcar-console.sh    # Interactive console
   ./llcar-gui.sh        # Graphical interface
   ```

#### Windows

1. Extract the ZIP file to any location

2. Run installation:
   ```cmd
   install.bat
   ```

3. Launch LLCAR:
   ```cmd
   llcar-console.bat    REM Interactive console
   llcar-gui.bat        REM Graphical interface
   ```

## Using Make

The Makefile provides convenient shortcuts:

```bash
# Build package for current platform
make package

# Build packages for all platforms
make package-all

# Clean build artifacts
make clean
```

## Automating Releases

### GitHub Actions

You can use GitHub Actions to automatically build packages:

```yaml
name: Build Packages

on:
  release:
    types: [created]

jobs:
  build-packages:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Build all packages
        run: python build_package.py --all

      - name: Upload packages
        uses: actions/upload-artifact@v4
        with:
          name: packages
          path: dist/*
```

### Manual Release Process

1. **Update version:**
   ```bash
   # Edit src/__init__.py
   __version__ = "1.1.0"
   ```

2. **Build packages:**
   ```bash
   python build_package.py --all
   ```

3. **Create GitHub release:**
   - Go to https://github.com/llcarn8n/LLCAR/releases/new
   - Create tag: `v1.1.0`
   - Upload files from `dist/`:
     - `llcar-1.1.0-linux.tar.gz`
     - `llcar-1.1.0-macos.tar.gz`
     - `LLCAR-1.1.0-windows-portable.zip`

## Comparison: Portable vs. Executable

| Feature | Portable Package | Windows Executable |
|---------|-----------------|-------------------|
| **Build Platform** | Any | Windows only |
| **Size** | ~100KB | ~500MB+ |
| **Requires Python** | Yes | No |
| **Startup Time** | Fast | Slower (first run) |
| **Update Method** | Git pull | Re-download |
| **Flexibility** | Full source access | Limited |
| **Best For** | Developers, Linux/macOS | End users, Windows |

## Best Practices

### For Developers

1. **Always test packages before distribution:**
   ```bash
   # Build package
   python build_package.py

   # Extract and test
   cd dist
   tar -xzf llcar-1.0.0-linux.tar.gz
   cd llcar-1.0.0
   ./install.sh
   ./llcar-console.sh --help
   ```

2. **Keep version numbers consistent:**
   - Update `src/__init__.py`
   - Tag releases properly
   - Document changes in CHANGELOG

3. **Include platform-specific instructions:**
   - Update INSTALL.txt as needed
   - Test on target platforms
   - Document known issues

### For Users

1. **Always download from official sources:**
   - GitHub Releases page
   - Official website only

2. **Verify package integrity:**
   ```bash
   # Check file size and contents
   tar -tzf llcar-1.0.0-linux.tar.gz | head
   ```

3. **Read INSTALL.txt first:**
   - Contains platform-specific instructions
   - Lists all requirements
   - Provides troubleshooting tips

## Troubleshooting

### "build_package.py not found"

Run from the LLCAR root directory:
```bash
cd /path/to/LLCAR
python build_package.py
```

### "Permission denied" on Linux/macOS

Make scripts executable:
```bash
chmod +x build_package.py
chmod +x llcar-console.sh llcar-gui.sh install.sh
```

### "Version shows as 1.0.0 instead of my version"

Update the version in `src/__init__.py`:
```python
__version__ = "1.2.0"
```

### Package size is too large

The portable package should be ~100KB. If it's much larger:
- Check for `.pyc` files: `python build_package.py --clean`
- Ensure `dist/` is cleaned before building
- Don't include `venv/` or `__pycache__/`

## Advanced Usage

### Custom Package Contents

Edit `build_package.py` and modify the `files_to_copy` list:

```python
files_to_copy = [
    'main.py',
    'gui.py',
    # Add your custom files here
    'custom_config.yaml',
    'custom_script.py',
]
```

### Platform-Specific Customization

Add custom logic in `create_launcher_scripts()`:

```python
if platform == 'linux':
    # Add Linux-specific files
    pass
elif platform == 'macos':
    # Add macOS-specific files
    pass
elif platform == 'windows':
    # Add Windows-specific files
    pass
```

### Compression Options

For better compression, modify `create_tarball()`:

```python
# For maximum compression (slower)
with tarfile.open(tar_path, 'w:xz') as tar:
    tar.add(package_dir, arcname=package_name)
```

## Support

For build-related issues:
- Check this documentation
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- For Windows .exe builds: [BUILD.md](BUILD.md)
- Open GitHub issue: https://github.com/llcarn8n/LLCAR/issues

## Additional Resources

- **Windows Executable Build:** [BUILD.md](BUILD.md)
- **Release Process:** [RELEASE_GUIDE.md](RELEASE_GUIDE.md)
- **Quick Reference:** [BUILD_QUICK_REF.md](BUILD_QUICK_REF.md)
- **Installation Guide:** [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

---

**Version:** 1.0.0
**Last Updated:** 2026-02-07
**LLCAR Team**
