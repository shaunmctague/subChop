import os
import re
import sys
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog,
    QMessageBox, QPlainTextEdit, QProgressBar
)

class Worker(QThread):
    """
    Worker thread that:
      1. Checks ffmpeg availability.
      2. Parses SRT.
      3. Spawns parallel tasks, each calling ffmpeg to slice & encode audio.
      4. Supports a stop request.

    We rely on QThread's built-in 'finished' signal (emitted automatically
    when run() returns). No custom 'finished' signal is used, so there's
    only one "Done" pop-up at the end.
    """
    log_emitted = Signal(str)
    error_emitted = Signal(str)
    progress_emitted = Signal(int, int)  # (current, total)

    def __init__(self, video_path, subtitle_path, output_folder, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.subtitle_path = subtitle_path
        self.output_folder = output_folder
        self._stop_requested = False

        # Adjust concurrency to your machine. 
        # E.g. on an 8-core system, you might set self.max_workers = 6 or 8.
        self.max_workers = 6  

    def run(self):
        try:
            # 1) Check ffmpeg
            self._log("Checking ffmpeg availability...")
            if not self._is_ffmpeg_available():
                raise RuntimeError("ffmpeg not found or not available on PATH.")

            # 2) Parse SRT
            self._log("Parsing SRT file...")
            subs = self._parse_srt_file(self.subtitle_path)
            total_subs = len(subs)
            self._log(f"Found {total_subs} subtitle segments.")

            if total_subs == 0:
                self._log("No subtitles found. Finishing.")
                return  # QThread 'finished' signal will auto-fire

            # 3) Create a ThreadPoolExecutor to slice/encode in parallel
            tasks = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for idx, segment in enumerate(subs, start=1):
                    if self._stop_requested:
                        self._log("Stop requested. Exiting early...")
                        return

                    start_time = segment['start_ms']
                    end_time = segment['end_ms']
                    text = segment['text']

                    tasks.append(
                        executor.submit(
                            self._slice_and_encode_ffmpeg,
                            start_time, end_time, text, idx
                        )
                    )

                # Track completion to update progress bar
                for i, future in enumerate(as_completed(tasks), start=1):
                    if self._stop_requested:
                        self._log("Stop requested. Exiting early...")
                        return

                    exc = future.exception()
                    if exc:
                        # Will bubble up to except clause below
                        raise exc

                    self.progress_emitted.emit(i, total_subs)

            self._log("All segments processed successfully.")
            # No need to emit a custom finished signal; QThread finished is auto.

        except Exception as e:
            self._log(f"Error: {e}")
            self.error_emitted.emit(str(e))
        # When run() ends, QThread automatically emits "finished".

    def stop(self):
        self._stop_requested = True

    # --------------------------
    #       HELPER METHODS
    # --------------------------

    def _log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.log_emitted.emit(f"{timestamp} - {message}")

    def _is_ffmpeg_available(self) -> bool:
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except Exception:
            return False

    def _parse_srt_file(self, srt_path: str):
        """
        Return a list of dicts: [{'start_ms', 'end_ms', 'text'}, ...]
        We'll convert times to milliseconds to simplify slicing.
        """
        subtitles = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            lines = [line.strip('\ufeff').strip() for line in f]

        idx = 0
        while idx < len(lines):
            line = lines[idx].strip()
            # If the line is just a number, it typically indicates a new subtitle block
            if line.isdigit():
                idx += 1
                if idx < len(lines):
                    time_line = lines[idx]
                    idx += 1
                    times = time_line.split('-->')
                    if len(times) == 2:
                        start_ms = self._time_str_to_ms(times[0].strip())
                        end_ms = self._time_str_to_ms(times[1].strip())

                        text_lines = []
                        while idx < len(lines) and lines[idx]:
                            text_lines.append(lines[idx])
                            idx += 1

                        subtitle_text = " ".join(text_lines)
                        subtitles.append({
                            'start_ms': start_ms,
                            'end_ms': end_ms,
                            'text': subtitle_text
                        })
            idx += 1
        return subtitles

    def _time_str_to_ms(self, time_str: str) -> int:
        """
        Convert 'HH:MM:SS,mmm' or 'HH:MM:SS.mmm' to milliseconds.
        """
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        hours = float(parts[0])
        minutes = float(parts[1])
        sec_parts = parts[2].split('.')
        seconds = float(sec_parts[0])
        frac = float("0." + sec_parts[1]) if len(sec_parts) == 2 else 0

        total_s = hours * 3600 + minutes * 60 + seconds + frac
        return int(round(total_s * 1000))

    def _slice_and_encode_ffmpeg(self, start_ms: int, end_ms: int, text: str, idx: int):
        """
        Use ffmpeg to slice audio from video without loading entire track into memory.
        Also embed the correct Title metadata so macOS sees the correct title.
        """
        if self._stop_requested:
            return

        safe_name = self._sanitize_filename(text)

        # Ensure it's not empty or too long
        if len(safe_name) > 50:
            safe_name = safe_name[:50].strip()
        if not safe_name:
            safe_name = f"subtitle_segment_{idx}"

        # Prefix the filename with zero-padded index
        safe_name = f"{idx:03d}_{safe_name}"

        mp3_file = safe_name + ".mp3"
        output_path = os.path.join(self.output_folder, mp3_file)

        start_seconds = start_ms / 1000.0
        end_seconds = end_ms / 1000.0
        duration = end_seconds - start_seconds

        self._log(f"Segment #{idx}: \"{text}\" -> {mp3_file}")

        # Build ffmpeg command, setting Title metadata to match safe_name
        command = [
            "ffmpeg", "-y",
            "-ss", str(start_seconds),
            "-i", self.video_path,
            "-t", str(duration),
            "-vn",                  # no video
            "-acodec", "libmp3lame",
            "-b:a", "192k",         # or use "-q:a 0" for variable bitrate
            "-metadata", f"title={safe_name}",  # embed the Title so mac sees correct name
            output_path
        ]

        # Run ffmpeg
        process = subprocess.run(command, capture_output=True)
        if process.returncode != 0:
            err_msg = process.stderr.decode("utf-8")
            raise RuntimeError(f"ffmpeg failed for segment #{idx}:\n{err_msg}")

        self._log(f"Saved MP3: {output_path}")

    def _sanitize_filename(self, text: str) -> str:
        """
        1) Remove HTML tags
        2) Remove all punctuation
        3) Replace whitespace with underscores
        4) Remove invalid Windows filename chars
        5) Strip leading/trailing underscores
        """
        # Remove HTML tags (e.g. <i>...</i>)
        text = re.sub(r'<[^>]*>', '', text)

        # Remove punctuation (anything not letter, digit, underscore, space)
        text = re.sub(r'[^\w\s]', '', text)

        # Replace all whitespace with underscores
        text = re.sub(r'\s+', '_', text)

        # Remove invalid Windows filename characters (on Mac it's not required,
        # but good practice for cross-platform).
        text = re.sub(r'[\\/:*?"<>|]', '', text)

        # Strip leading/trailing underscores
        text = text.strip('_')

        return text


class SubtitleAudioChopper(QMainWindow):
    """
    Main Window that sets up the UI and spawns a Worker thread to do the heavy tasks.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Subtitle Audio Chopper (FFmpeg per slice)")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.is_processing = False
        self.worker = None

        self._build_ui()

    def _build_ui(self):
        heading_label = QLabel("Extract MP3 audio clips from your video using ffmpeg (per-slice).")
        heading_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(heading_label)

        desc_label = QLabel(
            "1. Select a video file\n"
            "2. Select the .srt subtitle file\n"
            "3. Choose an output folder\n"
            "4. Click 'Start Processing' (then 'Stop' if needed)\n"
            "This method avoids loading the entire audio into memory."
        )
        self.main_layout.addWidget(desc_label)

        # Form
        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Video File:"), 0, 0, Qt.AlignRight)
        self.video_edit = QLineEdit()
        form_layout.addWidget(self.video_edit, 0, 1)
        browse_video_btn = QPushButton("Browse...")
        browse_video_btn.clicked.connect(self._browse_video)
        form_layout.addWidget(browse_video_btn, 0, 2)

        form_layout.addWidget(QLabel("Subtitle File (.srt):"), 1, 0, Qt.AlignRight)
        self.subtitle_edit = QLineEdit()
        form_layout.addWidget(self.subtitle_edit, 1, 1)
        browse_subtitle_btn = QPushButton("Browse...")
        browse_subtitle_btn.clicked.connect(self._browse_subtitle)
        form_layout.addWidget(browse_subtitle_btn, 1, 2)

        form_layout.addWidget(QLabel("Output Folder:"), 2, 0, Qt.AlignRight)
        self.output_edit = QLineEdit()
        form_layout.addWidget(self.output_edit, 2, 1)
        browse_output_btn = QPushButton("Browse...")
        browse_output_btn.clicked.connect(self._browse_output_folder)
        form_layout.addWidget(browse_output_btn, 2, 2)

        self.main_layout.addLayout(form_layout)

        # Start/Stop Button
        self.start_stop_button = QPushButton("Start Processing")
        self.start_stop_button.clicked.connect(self._toggle_processing)
        self.main_layout.addWidget(self.start_stop_button, alignment=Qt.AlignHCenter)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.main_layout.addWidget(self.progress_bar)

        # Log
        log_label = QLabel("Log / Status:")
        self.main_layout.addWidget(log_label)

        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.main_layout.addWidget(self.log_area, stretch=1)

        self.resize(700, 500)

    # ---------------------
    #      UI Handlers
    # ---------------------
    def _browse_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.mov *.avi *.mkv *.flv *.wmv *.m4v);;All Files (*)"
        )
        if path:
            self.video_edit.setText(path)

    def _browse_subtitle(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Subtitle File",
            "",
            "Subtitle Files (*.srt);;All Files (*)"
        )
        if path:
            self.subtitle_edit.setText(path)

    def _browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_edit.setText(folder)

    def _toggle_processing(self):
        if not self.is_processing:
            self._start_processing()
        else:
            self._stop_processing()

    def _start_processing(self):
        video_path = self.video_edit.text().strip()
        subtitle_path = self.subtitle_edit.text().strip()
        output_folder = self.output_edit.text().strip()

        # Validate paths
        if not os.path.isfile(video_path):
            QMessageBox.critical(self, "Error", "Invalid video file path.")
            return
        if not os.path.isfile(subtitle_path):
            QMessageBox.critical(self, "Error", "Invalid subtitle file path.")
            return
        if not os.path.isdir(output_folder):
            QMessageBox.critical(self, "Error", "Invalid output folder.")
            return

        self.is_processing = True
        self.start_stop_button.setText("Stop Processing")
        self.log_area.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(1)  # Will adjust once we know total segments

        self.worker = Worker(video_path, subtitle_path, output_folder)
        self.worker.log_emitted.connect(self._append_log)
        self.worker.error_emitted.connect(self._on_worker_error)
        
        # QThread's built-in finished signal
        self.worker.finished.connect(self._on_worker_finished)
        
        self.worker.progress_emitted.connect(self._on_worker_progress)
        self.worker.start()

    def _stop_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._append_log("Stop requested. Please wait...")

    # ---------------------
    # Worker-Signal Slots
    # ---------------------
    def _append_log(self, text: str):
        self.log_area.appendPlainText(text)

    def _on_worker_error(self, error_message: str):
        QMessageBox.critical(self, "Error", error_message)
        self._cleanup_after_finish()

    def _on_worker_finished(self):
        QMessageBox.information(self, "Done", "Processing completed (or stopped).")
        self._cleanup_after_finish()

    def _on_worker_progress(self, current: int, total: int):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def _cleanup_after_finish(self):
        self.is_processing = False
        self.start_stop_button.setText("Start Processing")
        self.worker = None


def main():
    app = QApplication(sys.argv)
    window = SubtitleAudioChopper()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()