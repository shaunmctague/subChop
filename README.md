# SubChop

A Python GUI application for extracting audio clips from video files using subtitle timing information. SubChop creates individual MP3 files for each dialogue segment, making it perfect for language learning, dialogue study, or content creation.

## Features

- Extract audio clips based on subtitle timing
- Support for multiple video formats (mp4, mov, avi, mkv, flv, wmv, m4v)
- SRT subtitle file support
- Parallel processing for improved performance
- Real-time progress tracking
- Memory-efficient processing
- Cross-platform compatibility

## Requirements

- Python 3.x
- FFmpeg installed and accessible in PATH
  - macOS: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - Linux: Use package manager (e.g., `apt install ffmpeg` or `yum install ffmpeg`)

## Setup

### Unix/macOS
```bash
# Clone the repository
git clone <repository-url>
cd sub_chop

# Run setup script
./setup.sh
```

### Windows
```batch
# Clone the repository
git clone <repository-url>
cd sub_chop

# Run setup script
setup.bat
```

The setup scripts will:
- Create a Python virtual environment
- Install all required dependencies
- Check for FFmpeg installation
- Provide helpful error messages if anything is missing

## Running the Application

### Unix/macOS
```bash
./start.sh
```

### Windows
```batch
start.bat
```

The start scripts will:
- Verify the environment is properly set up
- Activate the virtual environment if needed
- Launch the application

## Usage

1. Launch the application using the start script
2. Select your video file
3. Select the corresponding SRT subtitle file
4. Choose an output directory
5. Click Start to begin processing
6. Monitor progress in the application window
7. Find your extracted audio clips in the output directory

## Output

- Individual MP3 files for each dialogue segment
- Files named with index prefix and dialogue text
- 192k bitrate audio quality
- Metadata embedded for proper title display

## Development

For development setup and technical details, please refer to the documentation in the `cline_docs` directory:
- `productContext.md`: Project overview and goals
- `techContext.md`: Technical implementation details
- `systemPatterns.md`: Architecture and design patterns
- `progress.md`: Development progress and roadmap
