@echo off
echo Setting up virtual environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Check if ffmpeg is installed
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo WARNING: ffmpeg is not installed. Please install it:
    echo Download from https://ffmpeg.org/download.html
    echo Add ffmpeg to your system PATH
)

echo.
echo Setup complete! Virtual environment is activated.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat
