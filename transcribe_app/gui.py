# main_window.py
import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Assume your transcription worker already exists; it takes an audio file path
from transcribe_app.transcription_worker import TranscriptionWorker
from transcribe_app.utils import calculate_wpm, get_wav_duration

from .recording_manager import RecordingManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Transcription App")
        self.resize(800, 600)

        # Left panel with controls
        self.control_panel = QWidget()
        control_layout = QVBoxLayout()
        self.record_button = QPushButton("🎤 Record")
        self.stop_button = QPushButton("⏹️ Stop")
        self.transcribe_button = QPushButton("✏️ Transcribe")
        self.delete_button = QPushButton("🗑️ Secure Delete")

        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.transcribe_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addStretch()
        self.control_panel.setLayout(control_layout)

        # Right panel for transcript display
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)

        # Main layout: split between controls and transcript
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.transcript_display, stretch=1)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect signals
        self.record_button.clicked.connect(self.handle_record)
        self.stop_button.clicked.connect(self.handle_stop)
        self.transcribe_button.clicked.connect(self.handle_transcribe)
        self.delete_button.clicked.connect(self.handle_secure_delete)

        # Initially, disable the stop button until recording starts
        self.stop_button.setEnabled(False)
        # Recording manager instance
        self.recorder = None
        # Path of the recorded file (set when recording stops)
        self.audio_file = None

    def handle_record(self):
        try:
            self.recorder = RecordingManager(self)
            self.recorder.start_recording()
        except Exception as e:
            QMessageBox.critical(self, "Recording Error", str(e))
            return
        # Update UI: disable Record, enable Stop
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar().showMessage("Recording...", 0)

    def handle_stop(self):
        if self.recorder:
            self.audio_file = self.recorder.stop_recording()
            self.statusBar().showMessage("Recording complete.", 3000)
            # Reset buttons: allow re-recording and transcription
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def handle_transcribe(self):
        if not self.audio_file:
            QMessageBox.information(self, "No Recording", "Please record audio first.")
            return
        self.statusBar().showMessage("Transcribing...", 0)
        # Create and start your transcription worker (assumed to be QThread-based)
        self.worker = TranscriptionWorker(
            self.audio_file, model_name="tiny", use_postprocessing=False
        )
        self.worker.transcription_complete.connect(self.on_transcription_complete)
        self.worker.transcription_error.connect(self.on_transcription_error)
        self.worker.start()

    def on_transcription_complete(self, transcript: str):
        self.statusBar().clearMessage()
        # Use the WAV file header to get the actual duration of the recording
        duration = get_wav_duration(self.audio_file)
        wpm = calculate_wpm(transcript, duration)
        display_text = (
            f"Transcript:\n{transcript}\n\n"
            f"Recording Duration: {duration:.2f} seconds\n"
            f"Words per minute (WPM): {wpm:.2f}"
        )
        self.transcript_display.append(display_text)

    def on_transcription_error(self, error_message: str):
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "Transcription Error", error_message)

    def handle_secure_delete(self):
        if self.audio_file:
            from transcribe_app.secure_delete import secure_delete

            secure_delete(self.audio_file)
            self.statusBar().showMessage("Temporary audio file securely deleted.", 3000)
            self.audio_file = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
