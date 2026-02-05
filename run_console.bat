@echo off
REM LLCAR Video Processing Pipeline - Windows Launcher
REM This script helps launch LLCAR in interactive mode

echo.
echo ================================================================
echo   LLCAR Video Processing Pipeline
echo   Interactive Console Launcher for Windows
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org
    echo.
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please run this script from the LLCAR directory
    echo.
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found
    echo.
    echo Please create .env file with your HuggingFace token:
    echo   1. Copy .env.example to .env
    echo   2. Add your HuggingFace token from https://huggingface.co/settings/tokens
    echo.
    echo The application may not work without a valid token.
    echo.
    pause
)

echo Starting LLCAR Interactive Console...
echo.

REM Launch in interactive mode
python main.py --interactive

if %errorlevel% neq 0 (
    echo.
    echo ================================================================
    echo   Application exited with an error
    echo ================================================================
    echo.
    pause
)
