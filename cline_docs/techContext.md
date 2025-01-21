# Technical Context

## Core Technologies

1. Python
   - Main implementation language
   - Requires Python 3.x (specific version TBD)

2. PySide6
   - Qt-based GUI framework
   - Provides cross-platform interface components
   - Handles threading and signals/slots

3. FFmpeg
   - External dependency for audio processing
   - Must be available in system PATH
   - Used for video-to-audio extraction
   - Handles various video format support

## Dependencies

1. Required Python Packages:
   ```
   PySide6          # GUI framework
   concurrent.futures # Built-in for parallel processing
   ```

2. System Requirements:
   - FFmpeg installed and accessible in PATH
   - Sufficient disk space for audio extraction
   - CPU capable of parallel processing
   - Adequate RAM for video processing

## Project Structure
```
sub_chop/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── cline_docs/         # Documentation
    ├── productContext.md
    ├── activeContext.md
    ├── systemPatterns.md
    └── techContext.md
```

## Development Setup

1. Git Setup:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd sub_chop

   # Create new branch for features
   git checkout -b feature/your-feature-name
   ```

2. Environment Setup:
   ```bash
   # Unix/macOS
   ./setup.sh

   # Windows
   setup.bat
   ```

   The setup scripts will:
   - Create a Python virtual environment
   - Activate the environment
   - Install all required dependencies
   - Check for FFmpeg installation
   
   To manually activate the virtual environment later:
   ```bash
   # Unix/macOS
   source venv/bin/activate

   # Windows
   venv\Scripts\activate.bat
   ```

3. Running the Application:
   ```bash
   # Unix/macOS
   ./start.sh

   # Windows
   start.bat
   ```

   The start scripts will:
   - Activate the virtual environment if not already active
   - Run the application

2. FFmpeg Installation:
   - macOS: `brew install ffmpeg`
   - Windows: Download from ffmpeg.org
   - Linux: Use package manager (apt, yum, etc.)

## Technical Constraints

1. Video Processing
   - Supported formats: mp4, mov, avi, mkv, flv, wmv, m4v
   - Processing time depends on video size
   - Memory usage scales with parallel processing

2. Subtitle Processing
   - Currently supports SRT format only
   - UTF-8 encoding expected
   - Handles various timestamp formats

3. Output Limitations
   - MP3 format only
   - 192k bitrate (configurable in code)
   - Filename length limited to 50 characters
   - Index-prefixed naming scheme

4. System Requirements
   - FFmpeg dependency
   - Qt dependencies (via PySide6)
   - Disk space for output files
   - Multi-core CPU recommended

## Version Control

1. Git Workflow
   - Main branch: stable releases
   - Development branch: integration
   - Feature branches: new features
   - Hotfix branches: urgent fixes

2. Git Practices
   - Commit messages follow conventional commits
   - Pull requests for code review
   - Branch protection rules
   - Regular rebasing

3. Ignored Files (via .gitignore)
   - Python artifacts (__pycache__, *.pyc)
   - Virtual environments
   - IDE settings
   - Media files (mp3, mp4, etc.)
   - Logs and databases

## Performance Considerations

1. Parallel Processing
   - Default 6 worker threads
   - Configurable via max_workers
   - CPU and memory impact

2. Memory Management
   - Stream-based processing
   - No full video loading
   - Efficient subtitle parsing

3. File I/O
   - Asynchronous processing
   - Progress tracking
   - Cancellation support
