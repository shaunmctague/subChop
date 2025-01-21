# Product Context

## Purpose
subChop is a Python GUI application designed to extract audio clips from video files using subtitle timing information. The application creates individual MP3 files for each dialogue segment, making it useful for:
- Creating audio clips from video dialogue
- Extracting specific dialogue segments for analysis or study
- Batch processing of video content into audio segments
- Language learning and dialogue study

## Problems Solved
1. Manual audio extraction is time-consuming and error-prone
2. Precise timing of dialogue segments requires careful attention
3. Processing multiple dialogue segments manually would be tedious
4. Memory efficiency when dealing with large video files
5. Cross-platform compatibility for audio extraction

## How It Works
1. User Interface:
   - Simple GUI interface for file selection
   - Progress tracking with status updates
   - Start/Stop functionality
   - Detailed logging of operations

2. Input Processing:
   - Accepts video files (mp4, mov, avi, mkv, flv, wmv, m4v)
   - Processes SRT subtitle files
   - Validates file paths and availability

3. Processing:
   - Uses ffmpeg for efficient audio extraction
   - Processes segments in parallel (configurable worker count)
   - Avoids loading entire audio into memory
   - Sanitizes filenames for cross-platform compatibility

4. Output:
   - Creates MP3 files for each dialogue segment
   - Names files with index prefix and sanitized dialogue text
   - Embeds metadata for proper title display
   - Organizes output in user-selected directory

## Key Features
- Parallel processing for improved performance
- Memory-efficient processing using ffmpeg
- Real-time progress tracking
- Detailed operation logging
- Error handling and user feedback
- Clean filename generation from dialogue text
- Stop/Cancel capability during processing
