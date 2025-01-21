# System Patterns

## Architecture Overview
The application follows a multi-threaded architecture with clear separation of concerns:

1. GUI Layer (SubtitleAudioChopper)
   - Main window implementation
   - User interface components
   - Event handling
   - Worker thread management

2. Processing Layer (Worker)
   - Background processing thread
   - FFmpeg integration
   - Subtitle parsing
   - File operations
   - Progress reporting

## Design Patterns

1. Worker Thread Pattern
   - Separate QThread for heavy processing
   - Non-blocking UI during processing
   - Progress updates via signals
   - Cancellation support

2. Observer Pattern (Qt Signals/Slots)
   - log_emitted signal for status updates
   - error_emitted signal for error handling
   - progress_emitted signal for progress tracking
   - finished signal for completion handling

3. Factory-like Methods
   - _parse_srt_file for subtitle parsing
   - _slice_and_encode_ffmpeg for audio extraction
   - Standardized output generation

## Technical Decisions

1. Threading Model
   - QThread for main worker process
   - ThreadPoolExecutor for parallel segment processing
   - Configurable number of worker threads
   - Clean thread termination support

2. File Processing
   - Stream-based processing using ffmpeg
   - Memory-efficient segment extraction
   - Parallel processing of segments
   - Robust error handling

3. User Interface
   - Qt-based GUI for cross-platform support
   - Real-time progress tracking
   - Detailed logging interface
   - Intuitive file selection dialogs

4. Error Handling
   - Comprehensive error checking
   - User-friendly error messages
   - Graceful failure handling
   - Process cancellation support

## Code Organization

1. Main Components
   ```
   SubtitleAudioChopper (QMainWindow)
   ├── UI Components
   │   ├── File selection inputs
   │   ├── Progress bar
   │   └── Log area
   │
   Worker (QThread)
   ├── FFmpeg integration
   ├── Subtitle parsing
   ├── File operations
   └── Progress reporting
   ```

2. Signal Flow
   ```
   Worker Thread ─────────┐
   │                     │
   ├── log_emitted ──────┤
   ├── error_emitted ────┼──> Main Window
   ├── progress_emitted ─┤
   └── finished ─────────┘
   ```

## Best Practices

1. Resource Management
   - Proper thread cleanup
   - File handle management
   - Process termination handling
   - Memory-efficient processing

2. Cross-Platform Compatibility
   - Platform-agnostic file paths
   - Unicode support
   - Filename sanitization
   - Portable file operations

3. User Experience
   - Real-time feedback
   - Progress indication
   - Error reporting
   - Operation cancellation
