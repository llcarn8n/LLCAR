# LLCAR - Quick Build Reference

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] Inno Setup 6.0+ installed (for installer)
- [ ] FFmpeg installed
- [ ] All dependencies from `requirements.txt` installed
- [ ] HuggingFace account and token

## Quick Build Commands

### Build Executable Only
```bash
python build_exe.py
```

**Output:** `dist/llcar/llcar.exe`

### Build with PyInstaller Manually
```bash
pyinstaller --clean llcar.spec
```

### Build Installer (after building EXE)
1. Open Inno Setup Compiler
2. Open `installer.iss`
3. Click Build → Compile (or Ctrl+F9)

**Output:** `installer_output/LLCAR_Setup_1.0.0.exe`

## Testing

### Test EXE
```cmd
cd dist\llcar
llcar.exe --help
llcar.exe --interactive
```

### Test Installer
1. Run `LLCAR_Setup_1.0.0.exe`
2. Follow installation wizard
3. Launch from Start Menu
4. Test processing a file

## Distribution Files

### Upload to GitHub Releases:
- `LLCAR_Setup_1.0.0.exe` (~300 MB compressed)
- `LLCAR_Portable_v1.0.0.zip` (~600 MB)
- Release notes

## File Locations

| File | Purpose | Location |
|------|---------|----------|
| llcar.spec | PyInstaller config | Root |
| build_exe.py | Build script | Root |
| installer.iss | Inno Setup config | Root |
| llcar.exe | Executable | dist/llcar/ |
| LLCAR_Setup.exe | Installer | installer_output/ |

## Common Issues

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Module not found" in EXE
Add to `hiddenimports` in `llcar.spec`

### Installer compilation fails
Check that `dist/llcar/` exists and is complete

### EXE too large
Normal for AI applications (~600 MB due to PyTorch)

## Version Update Checklist

When releasing new version:
- [ ] Update version in `setup.py`
- [ ] Update version in `installer.iss` (#define MyAppVersion)
- [ ] Update version in `WINDOWS.md` examples
- [ ] Update README.md release links
- [ ] Create git tag
- [ ] Build and test
- [ ] Create GitHub release
- [ ] Upload installers

## Documentation References

- Full build guide: `BUILD.md`
- Windows user guide: `WINDOWS.md`
- Implementation details: `INSTALLER_SUMMARY.md`

---

**Quick Help:** See BUILD.md for detailed instructions
