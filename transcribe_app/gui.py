# transcribe_app/gui.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Transcription App")
        self.resize(800, 600)

        # --- Left Panel: Control Panel ---
        self.control_panel = QWidget()
        control_layout = QVBoxLayout()

        # Create custom buttons (later, you might add icons)
        self.record_button = QPushButton("Record")
        self.transcribe_button = QPushButton("Transcribe")
        self.delete_button = QPushButton("Secure Delete")

        # A status label for messages
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)

        # A loading indicator label (for "Transcribing...") - could later be an animated GIF.
        self.loading_label = QLabel("Transcribing...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)

        # Add the buttons and labels to the control layout
        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.transcribe_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.loading_label)
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()
        self.control_panel.setLayout(control_layout)

        # --- Right Panel: Transcript Display ---
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)
        self.transcript_display.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        # --- Main Layout: Split Layout ---
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        # Left panel gets a fixed width, right panel expands.
        main_layout.addWidget(self.control_panel, stretch=0)
        main_layout.addWidget(self.transcript_display, stretch=1)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        # --- Connect signals ---
        self.record_button.clicked.connect(self.handle_record)
        self.transcribe_button.clicked.connect(self.handle_transcribe)
        self.delete_button.clicked.connect(self.handle_secure_delete)

        # Temporary audio file name
        self.audio_file = "temp_audio.wav"

    def handle_record(self):
        from transcribe_app.audio_recorder import record_audio

        self.status_label.setText("Recording...")
        record_audio(self.audio_file, duration=10)  # Duration can be adjusted.
        self.status_label.setText("Recording complete.")

    def handle_transcribe(self):
        from transcribe_app.transcription import transcribe_audio

        self.status_label.setText("Transcribing...")
        self.loading_label.setVisible(True)

        # Ideally, run transcription in a background thread to keep the UI responsive.
        # For now, we run it synchronously.
        transcript = transcribe_audio(self.audio_file)
        self.transcript_display.append("Transcript:\n" + transcript)

        self.loading_label.setVisible(False)
        self.status_label.setText("Transcription complete.")

    def handle_secure_delete(self):
        from transcribe_app.secure_delete import secure_delete

        secure_delete(self.audio_file)
        self.status_label.setText("Temporary file securely deleted.")
