# LLCAR - Release Guide

**Обновлено:** 2026-02-07

This guide explains how to create a proper release with installer files for LLCAR.

## ⚠️ Important Note

GitHub releases automatically include source code archives (`.zip` and `.tar.gz`), but these are **not** the installer files that users need. You must build and upload the actual installer files separately.

## Two Ways to Create a Release

### Option 1: Automated Release (Recommended)

We have a GitHub Actions workflow that automatically builds and uploads installers when you create a release.

**Steps:**

1. **Create a new tag and release on GitHub:**
   ```bash
   # Locally create and push a tag
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Create the release on GitHub:**
   - Go to https://github.com/llcarn8n/LLCAR/releases/new
   - Select the tag you just created (v1.0.0)
   - Fill in the release title and description
   - Click "Publish release"

3. **Wait for the workflow:**
   - The GitHub Actions workflow will automatically start
   - Go to https://github.com/llcarn8n/LLCAR/actions to monitor progress
   - After ~10-15 minutes, the installer files will be uploaded to the release

4. **Verify the release:**
   - Go to https://github.com/llcarn8n/LLCAR/releases
   - Your release should now have these files:
     - ✅ `LLCAR_Setup_v1.0.0.exe` - Windows installer
     - ✅ `LLCAR_Portable_v1.0.0.zip` - Portable version
     - ✅ Source code (zip) - Auto-generated
     - ✅ Source code (tar.gz) - Auto-generated

### Option 2: Manual Release

If the automated workflow fails or you need to build manually:

**Prerequisites:**
- Windows machine (or Windows VM)
- Python 3.8+
- Git

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/llcarn8n/LLCAR.git
   cd LLCAR
   ```

2. **Install build dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-build.txt
   ```

3. **Build the executable:**
   ```bash
   python build_exe.py
   ```
   This creates `dist/llcar/` with the portable application.

4. **Create portable ZIP:**
   ```bash
   cd dist
   # On Windows PowerShell:
   Compress-Archive -Path llcar -DestinationPath LLCAR_Portable_v1.0.0.zip

   # On Windows with 7-Zip:
   7z a LLCAR_Portable_v1.0.0.zip llcar
   ```

5. **Build the installer (optional but recommended):**
   - Install Inno Setup from https://jrsoftware.org/isdl.php
   - Open `installer.iss` in Inno Setup Compiler
   - Click "Build" → "Compile"
   - The installer will be in `installer_output/LLCAR_Setup_1.0.0.exe`

6. **Create GitHub release:**
   - Go to https://github.com/llcarn8n/LLCAR/releases/new
   - Create a tag (e.g., v1.0.0)
   - Fill in title and description
   - **Upload the files:**
     - Drag and drop `LLCAR_Setup_1.0.0.exe` (rename to include version)
     - Drag and drop `LLCAR_Portable_v1.0.0.zip`
   - Click "Publish release"

## Release Checklist

Before creating a release, ensure:

- [ ] All tests pass: `pytest`
- [ ] Version updated in:
  - [ ] `setup.py`
  - [ ] `installer.iss` (MyAppVersion)
  - [ ] Documentation files
- [ ] CHANGELOG.md updated with new changes
- [ ] Documentation is up to date
- [ ] Build script tested: `python build_exe.py`
- [ ] Installer tested on clean Windows machine

## Updating an Existing Release

If you already created a release but forgot to upload the installer files:

1. **Build the files** (follow steps in "Manual Release" above)

2. **Edit the existing release:**
   - Go to https://github.com/llcarn8n/LLCAR/releases
   - Find your release and click "Edit"
   - Drag and drop the installer files
   - Click "Update release"

## Troubleshooting

### "The release only has source code archives"

This means you created the release but didn't upload the actual installer files. Follow the "Updating an Existing Release" section above.

### "GitHub Actions workflow failed"

1. Go to https://github.com/llcarn8n/LLCAR/actions
2. Click on the failed workflow
3. Check the error logs
4. Common issues:
   - Missing dependencies: Update requirements.txt
   - Build errors: Test `build_exe.py` locally
   - Inno Setup errors: Check `installer.iss` syntax

### "Users can't find the installer"

Make sure the release has:
- Clear release notes explaining which files to download
- Both `LLCAR_Setup_vX.X.X.exe` and `LLCAR_Portable_vX.X.X.zip`
- Instructions in the release description

## File Naming Convention

- Installer: `LLCAR_Setup_v1.0.0.exe`
- Portable: `LLCAR_Portable_v1.0.0.zip`
- Always include the version number in filenames

## Release Notes Template

```markdown
# LLCAR v1.0.0

## 📥 Download

**For Windows users:**
- **Recommended:** Download `LLCAR_Setup_v1.0.0.exe` and run the installer
- **Portable:** Download `LLCAR_Portable_v1.0.0.zip`, extract, and run `llcar.bat`

**For Linux/macOS users:**
- Clone the repository or download source code and follow [QUICKSTART.md](QUICKSTART.md)

## What's New

- Feature 1
- Feature 2
- Bug fix 1

## Requirements

- Windows 10/11 (64-bit)
- 8GB RAM minimum (16GB recommended)
- FFmpeg (must be installed separately)
- HuggingFace token (for speaker diarization)

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Windows Installation Guide](WINDOWS.md)
- [Build Instructions](BUILD.md)

## Support

- Report issues: https://github.com/llcarn8n/LLCAR/issues
- Documentation: https://github.com/llcarn8n/LLCAR
```

## Automated Workflow Details

The `.github/workflows/build-release.yml` workflow:
- Triggers automatically when a release is created
- Builds on Windows runner
- Installs all dependencies
- Builds executable with PyInstaller
- Creates portable ZIP
- Builds installer with Inno Setup
- Uploads both files to the release

**Manual trigger:**
You can also run the workflow manually:
1. Go to Actions tab
2. Select "Build and Release Windows Installer"
3. Click "Run workflow"
4. Enter the tag name
5. The files will be available as artifacts

---

**Last updated:** 2026-02-05
**LLCAR Team**
