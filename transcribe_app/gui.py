# transcribe_app/gui.py
from PySide6.QtWidgets import QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget

from transcribe_app.audio_recorder import record_audio
from transcribe_app.secure_delete import secure_delete
from transcribe_app.transcription import transcribe_audio


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Transcription App")

        self.record_button = QPushButton("Record")
        self.transcribe_button = QPushButton("Transcribe")
        self.delete_button = QPushButton("Secure Delete")
        self.transcript_display = QTextEdit()

        # Connect buttons to functions
        self.record_button.clicked.connect(self.handle_record)
        self.transcribe_button.clicked.connect(self.handle_transcribe)
        self.delete_button.clicked.connect(self.handle_secure_delete)

        layout = QVBoxLayout()
        layout.addWidget(self.record_button)
        layout.addWidget(self.transcribe_button)
        layout.addWidget(self.transcript_display)
        layout.addWidget(self.delete_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.audio_file = "temp_audio.wav"

    def handle_record(self):
        # Record for a fixed duration (e.g., 10 seconds for testing)
        record_audio(self.audio_file, duration=10)
        self.transcript_display.append("Recording complete.")

    def handle_transcribe(self):
        transcript = transcribe_audio(self.audio_file)
        self.transcript_display.append("Transcript:\n" + transcript)

    def handle_secure_delete(self):
        secure_delete(self.audio_file)
        self.transcript_display.append("Temporary file securely deleted.")
