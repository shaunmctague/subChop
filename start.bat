@echo off

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup.bat first:
    echo   setup.bat
    exit /b 1
)

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Virtual environment not activated. Activating now...
    call venv\Scripts\activate.bat
)

REM Check if requirements are installed
pip freeze | findstr "PySide6" >nul
if errorlevel 1 (
    echo Dependencies not installed. Please run setup.bat first:
    echo   setup.bat
    exit /b 1
)

REM Check if ffmpeg is installed
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo FFmpeg not found. Please install it first:
    echo Download from https://ffmpeg.org/download.html
    echo Add ffmpeg to your system PATH
    exit /b 1
)

echo Environment checks passed. Starting application...
REM Run the application
python main.py
