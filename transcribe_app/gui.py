import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from transcribe_app.recording_manager import RecordingManager
from transcribe_app.transcription_worker import TranscriptionWorker
from transcribe_app.utils import calculate_wpm, get_wav_duration


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Transcription App")
        self.resize(800, 600)

        # Instance variables for external modules and state.
        self.recorder = None  # RecordingManager instance
        self.audio_file = None  # Path to the saved WAV file

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Builds the user interface."""
        # Create status bar
        self.setStatusBar(QStatusBar(self))

        # Build control panel widget
        self.control_panel = QWidget()
        control_layout = QVBoxLayout()
        self.record_button = QPushButton("🎤 Record")
        self.stop_button = QPushButton("⏹️ Stop")
        self.transcribe_button = QPushButton("✏️ Transcribe")
        self.delete_button = QPushButton("🗑️ Secure Delete")

        for btn in [
            self.record_button,
            self.stop_button,
            self.transcribe_button,
            self.delete_button,
        ]:
            control_layout.addWidget(btn)
        control_layout.addStretch()
        self.control_panel.setLayout(control_layout)

        # Build transcript display widget
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)

        # Set up main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.transcript_display, stretch=1)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Initial UI state
        self.stop_button.setEnabled(False)

    def connect_signals(self):
        """Connects UI signals to their respective slots."""
        self.record_button.clicked.connect(self.handle_record)
        self.stop_button.clicked.connect(self.handle_stop)
        self.transcribe_button.clicked.connect(self.handle_transcribe)
        self.delete_button.clicked.connect(self.handle_secure_delete)

    def update_status(self, message: str, timeout: int = 0):
        """Helper to update the status bar."""
        self.statusBar().showMessage(message, timeout)

    def handle_record(self):
        """Starts recording audio."""
        try:
            self.recorder = RecordingManager(self)
            self.recorder.start_recording()
        except Exception as e:
            QMessageBox.critical(self, "Recording Error", str(e))
            return
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.update_status("Recording...", 0)

    def handle_stop(self):
        """Stops recording and saves the WAV file."""
        if self.recorder:
            self.audio_file = self.recorder.stop_recording()
            self.update_status("Recording complete.", 3000)
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def handle_transcribe(self):
        """Starts transcription if a recording exists."""
        if not self.audio_file:
            QMessageBox.information(self, "No Recording", "Please record audio first.")
            return
        self.update_status("Transcribing...", 0)
        self.worker = TranscriptionWorker(
            self.audio_file, model_name="tiny", use_postprocessing=False
        )
        self.worker.transcription_complete.connect(self.on_transcription_complete)
        self.worker.transcription_error.connect(self.on_transcription_error)
        self.worker.start()

    def on_transcription_complete(self, transcript: str):
        """Callback for when transcription is complete."""
        self.statusBar().clearMessage()
        # Use WAV metadata to get recording duration
        duration = get_wav_duration(self.audio_file)
        wpm = calculate_wpm(transcript, duration)
        display_text = (
            f"Transcript:\n{transcript}\n\n"
            f"Recording Duration: {duration:.2f} seconds\n"
            f"Words per minute (WPM): {wpm:.2f}"
        )
        self.transcript_display.append(display_text)

    def on_transcription_error(self, error_message: str):
        """Callback for transcription errors."""
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "Transcription Error", error_message)

    def handle_secure_delete(self):
        """Securely deletes the recorded audio file."""
        if self.audio_file:
            from transcribe_app.secure_delete import secure_delete

            secure_delete(self.audio_file)
            self.update_status("Temporary audio file securely deleted.", 3000)
            self.audio_file = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
