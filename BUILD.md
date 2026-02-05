# LLCAR - Building Windows Installer and Executable

This document describes how to build a standalone Windows executable and installer for LLCAR.

## Quick Start

**TL;DR: To build the Windows installer:**

```cmd
# 1. Install build dependencies
pip install -r requirements-build.txt

# 2. Build the executable
python build_exe.py

# 3. Install Inno Setup from https://jrsoftware.org/isdl.php

# 4. Open installer.iss in Inno Setup and click Compile

# 5. Find your installer in installer_output/LLCAR_Setup_1.0.0.exe
```

---

## Prerequisites

### Required Software

1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/

2. **PyInstaller**
   ```bash
   pip install pyinstaller
   ```

3. **FFmpeg**
   - Download from: https://ffmpeg.org/download.html
   - Add to system PATH

4. **Inno Setup 6.0+** (for creating installer)
   - Download from: https://jrsoftware.org/isdl.php

### Required Python Packages

All dependencies from `requirements.txt` must be installed:

```bash
pip install -r requirements.txt
```

## Building the Executable

### Method 1: Using the Build Script (Recommended)

The easiest way to build the executable:

```bash
python build_exe.py
```

This script will:
1. Clean previous build artifacts
2. Check for required dependencies
3. Build the executable using PyInstaller
4. Create a portable package with all necessary files
5. Generate launcher scripts

**Output:** `dist/llcar/` directory containing the complete portable application

### Method 2: Manual Build with PyInstaller

If you prefer to build manually:

```bash
# Clean previous builds
rmdir /s /q build dist

# Build using the spec file
pyinstaller --clean llcar.spec
```

## Creating the Windows Installer

After building the executable, you can create a Windows installer using Inno Setup:

### Steps:

1. **Build the executable first** (see above)

2. **Open Inno Setup**
   - Launch "Inno Setup Compiler"

3. **Compile the installer script**
   - Open `installer.iss` in Inno Setup
   - Click "Build" → "Compile" (or press Ctrl+F9)

4. **Find the installer**
   - The installer will be created in: `installer_output/`
   - File name: `LLCAR_Setup_1.0.0.exe`

### Installer Features

The installer includes:
- ✓ Automatic installation to Program Files
- ✓ Start menu shortcuts
- ✓ Desktop icon (optional)
- ✓ FFmpeg requirement check
- ✓ HuggingFace token configuration
- ✓ Automatic .env file creation
- ✓ Clean uninstallation
- ✓ Multi-language support (English/Russian)

## Distribution Options

### Option 1: Portable Package

Distribute the `dist/llcar/` folder as a ZIP file:

**Advantages:**
- No installation required
- Can run from USB drive
- Easy to update

**Steps:**
1. Build the executable
2. Compress `dist/llcar/` to `LLCAR_Portable_v1.0.0.zip`
3. Distribute the ZIP file

**User Instructions:**
1. Extract ZIP to any location
2. Run `llcar.bat --interactive`

### Option 2: Windows Installer

Distribute the `LLCAR_Setup_1.0.0.exe` installer:

**Advantages:**
- Professional installation experience
- Start menu integration
- Automatic updates support
- Configuration wizard

**Steps:**
1. Build the executable
2. Build the installer with Inno Setup
3. Distribute the installer EXE

## Testing the Build

### Test the Executable

1. Navigate to the dist folder:
   ```bash
   cd dist\llcar
   ```

2. Test basic functionality:
   ```bash
   llcar.exe --help
   llcar.exe --interactive
   ```

3. Test video processing (requires sample file):
   ```bash
   llcar.exe --video input\test.mp4 --language en
   ```

### Test the Installer

1. Install the application:
   - Run `LLCAR_Setup_1.0.0.exe`
   - Follow installation wizard

2. Verify installation:
   - Check Start menu for "LLCAR Video Processing Pipeline"
   - Run from Start menu or desktop icon

3. Test functionality:
   - Launch interactive console
   - Process a test video/audio file

4. Verify uninstallation:
   - Use Windows "Add or Remove Programs"
   - Ensure clean removal

## Build Configuration

### PyInstaller Spec File (`llcar.spec`)

The spec file controls how PyInstaller builds the executable:

**Key configurations:**
- `datas`: Additional files to include
- `hiddenimports`: Python modules not automatically detected
- `console=True`: Command-line application
- `upx=True`: Compress executable

**Customization:**
- Add icon: Set `icon='path/to/icon.ico'`
- Change name: Modify `name='llcar'`
- Add more data files: Append to `datas` list

### Inno Setup Script (`installer.iss`)

The Inno Setup script controls the installer creation:

**Key sections:**
- `[Setup]`: Basic installer configuration
- `[Files]`: Files to include in installation
- `[Icons]`: Start menu and desktop shortcuts
- `[Code]`: Custom installation logic

**Customization:**
- Change app name/version in `#define` section
- Modify installation directory
- Add/remove custom pages
- Change installer appearance

## Troubleshooting

### Build Issues

**Problem:** "PyInstaller not found"
```bash
pip install pyinstaller
```

**Problem:** "Module not found" errors during build
- Add missing module to `hiddenimports` in `llcar.spec`

**Problem:** Executable is too large (>500MB)
- This is normal due to PyTorch and AI models
- Consider using `--onefile` flag (slower startup)

**Problem:** Missing DLL errors when running EXE
- Ensure all dependencies are in `requirements.txt`
- Check `hiddenimports` in spec file

### Runtime Issues

**Problem:** "FFmpeg not found"
- Install FFmpeg and add to PATH
- Or include FFmpeg binaries in the package

**Problem:** Slow startup time
- First run loads AI models (normal)
- Subsequent runs are faster

**Problem:** CUDA/GPU errors
- Install CUDA toolkit and compatible PyTorch
- Or use `--device cpu` flag

### Installer Issues

**Problem:** Inno Setup compilation errors
- Verify all source files exist
- Check file paths in `installer.iss`

**Problem:** "File not found" in installer
- Ensure `dist/llcar/` exists and is complete
- Rebuild executable if needed

## Advanced Options

### Creating a Smaller Executable

Use PyInstaller's `--exclude-module` option:

```bash
pyinstaller llcar.spec --exclude-module matplotlib --exclude-module scipy
```

### Including GPU Support

Ensure CUDA-enabled PyTorch is installed:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Custom Branding

1. Create application icon (`icon.ico`)
2. Update `llcar.spec`: `icon='icon.ico'`
3. Update `installer.iss`: `SetupIconFile=icon.ico`
4. Rebuild

## Automated Build Pipeline

### Using GitHub Actions

We have a GitHub Actions workflow that automatically builds and uploads installers to releases.

The workflow is located at `.github/workflows/build-release.yml` and:
- Triggers automatically when a release is created
- Builds the Windows executable
- Creates the portable ZIP package
- Builds the installer with Inno Setup
- Uploads both files to the GitHub release

**To use it:**
1. Create a tag and push it: `git tag v1.0.0 && git push origin v1.0.0`
2. Create a release on GitHub using that tag
3. The workflow will automatically build and upload the installers

**For detailed instructions, see:** [RELEASE_GUIDE.md](RELEASE_GUIDE.md)

## Release Checklist

**⚠️ Important:** See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for the complete release process.

Quick checklist before releasing:

- [ ] Update version in `setup.py`
- [ ] Update version in `installer.iss`
- [ ] Update CHANGELOG.md
- [ ] Test on clean Windows installation
- [ ] Build and test executable locally
- [ ] Create release with proper installer files
- [ ] Verify release has both `.exe` and `.zip` files (not just source code)

## Support

For build issues:
- Check this documentation
- Review PyInstaller documentation: https://pyinstaller.org/
- Review Inno Setup documentation: https://jrsoftware.org/ishelp/
- Open GitHub issue: https://github.com/llcarn8n/LLCAR/issues

## Additional Resources

- **PyInstaller Manual:** https://pyinstaller.org/en/stable/
- **Inno Setup Help:** https://jrsoftware.org/ishelp/
- **Python Packaging Guide:** https://packaging.python.org/
- **Windows Installer Best Practices:** https://docs.microsoft.com/windows/win32/msi/

---

**Version:** 1.0.0
**Last Updated:** 2026-02-05
**LLCAR Team**
