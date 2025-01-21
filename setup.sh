#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: ffmpeg is not installed. Please install it:"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Linux: sudo apt-get install ffmpeg (Ubuntu/Debian)"
    echo "          sudo yum install ffmpeg (CentOS/RHEL)"
fi

echo "Setup complete! Virtual environment is activated."
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
