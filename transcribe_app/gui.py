# transcribe_app/gui.py
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from transcribe_app.recording_worker import RecordingWorker
from transcribe_app.transcription_worker import TranscriptionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speak Easy")
        self.resize(800, 600)

        # Create and set the status bar so that it’s explicitly in the window.
        self.setStatusBar(QStatusBar(self))

        # --- Left Panel: Control Panel ---
        self.control_panel = QWidget()
        control_layout = QVBoxLayout()

        self.record_button = QPushButton("🎤 Record (10 seconds)")
        self.transcribe_button = QPushButton("✏️ Transcribe")
        self.delete_button = QPushButton("🗑️ Secure Delete")

        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.transcribe_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addStretch()
        self.control_panel.setLayout(control_layout)

        # --- Right Panel: Transcript Display ---
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)

        # --- Main Layout: Split Layout ---
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.control_panel, stretch=0)
        main_layout.addWidget(self.transcript_display, stretch=1)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect signals
        self.record_button.clicked.connect(self.handle_record)
        self.transcribe_button.clicked.connect(self.handle_transcribe)
        self.delete_button.clicked.connect(self.handle_secure_delete)

        self.audio_file = "temp_audio.wav"

    def handle_record(self):
        # Use the status bar to show recording progress.
        self.statusBar().showMessage("Recording...", 0)

        # Start the recording worker thread.
        self.record_worker = RecordingWorker(self.audio_file, duration=10)
        self.record_worker.recording_complete.connect(self.on_recording_complete)
        self.record_worker.recording_error.connect(self.on_recording_error)
        self.record_worker.start()

    def on_recording_complete(self, audio_file: str):
        # Show completion message in the status bar.
        self.statusBar().showMessage("Recording complete.", 3000)

    def on_recording_error(self, error_message: str):
        # Clear any status message and alert the user.
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "Recording Error", error_message)

    def handle_transcribe(self):
        # Show transcribing message in the status bar.
        self.statusBar().showMessage("Transcribing Audio...", 0)

        # Start the transcription worker thread.
        self.worker = TranscriptionWorker(
            self.audio_file, model_name="tiny", use_postprocessing=False
        )
        self.worker.transcription_complete.connect(self.on_transcription_complete)
        self.worker.transcription_error.connect(self.on_transcription_error)
        self.worker.start()

    def on_transcription_complete(self, transcript: str):
        # Clear the status bar and display the transcript.
        self.statusBar().clearMessage()
        self.transcript_display.append("Transcript:\n" + transcript)

    def on_transcription_error(self, error_message: str):
        # Clear the status bar and alert the user.
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "Transcription Error", error_message)

    def handle_secure_delete(self):
        from transcribe_app.secure_delete import secure_delete

        secure_delete(self.audio_file)
        # Use the status bar to notify the user.
        self.statusBar().showMessage("Temporary audio file securely deleted.", 3000)
