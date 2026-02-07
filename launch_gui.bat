@echo off
REM LLCAR GUI Launcher for Windows
REM Launches the graphical user interface

cd /d "%~dp0"

REM Try the unified entry point first (works with both Python and EXE)
if exist "llcar.exe" (
    start "" llcar.exe --gui
) else (
    python main.py --gui
)
