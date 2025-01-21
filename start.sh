#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first:"
    echo "  ./setup.sh"
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Virtual environment not activated. Activating now..."
    source venv/bin/activate
fi

# Check if requirements are installed
if ! pip freeze | grep -q "PySide6"; then
    echo "Dependencies not installed. Please run setup.sh first:"
    echo "  ./setup.sh"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found. Please install it first:"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Linux: sudo apt-get install ffmpeg (Ubuntu/Debian)"
    echo "          sudo yum install ffmpeg (CentOS/RHEL)"
    exit 1
fi

echo "Environment checks passed. Starting application..."
# Run the application
python main.py
