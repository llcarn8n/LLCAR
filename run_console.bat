@echo off
REM LLCAR Console Launcher for Windows
REM Launches the interactive console

title LLCAR - Video Processing Pipeline
cd /d "%~dp0"

REM Check for .env
if not exist ".env" (
    if exist ".env.example" (
        echo [!] .env not found. Creating from .env.example ...
        copy ".env.example" ".env" >nul
        echo     Please edit .env and set your HuggingFace token.
        echo.
    )
)

echo ================================================================
echo   LLCAR Video Processing Pipeline - Interactive Console
echo ================================================================
echo.

REM Try EXE first, then Python
if exist "llcar.exe" (
    llcar.exe --interactive
) else (
    python main.py --interactive
)

if %errorlevel% neq 0 (
    echo.
    echo   Application exited with an error.
    pause
)
