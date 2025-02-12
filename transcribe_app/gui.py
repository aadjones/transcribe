import os
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

# Import our encryption functions from security.py
from transcribe_app.security import decrypt_file, encrypt_file, generate_key
from transcribe_app.transcription_worker import TranscriptionWorker
from transcribe_app.utils import calculate_wpm, get_wav_duration


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Transcription App")
        self.resize(800, 600)

        self.init_ui()
        self.connect_signals()

        # Instance variables for recording and encryption
        self.recorder = None  # RecordingManager instance
        self.audio_file = None  # Path to the encrypted WAV file
        self.encryption_key = None  # The key used for encryption

    def init_ui(self):
        """Constructs the UI components."""
        # Create status bar
        self.setStatusBar(QStatusBar(self))

        # Build control panel
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

        # Build transcript display
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)

        # Create main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.transcript_display, stretch=1)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Initial UI state
        self.stop_button.setEnabled(False)

    def connect_signals(self):
        """Connect UI signals to their corresponding handlers."""
        self.record_button.clicked.connect(self.handle_record)
        self.stop_button.clicked.connect(self.handle_stop)
        self.transcribe_button.clicked.connect(self.handle_transcribe)
        self.delete_button.clicked.connect(self.handle_secure_delete)

    def update_status(self, message: str, timeout: int = 0):
        self.statusBar().showMessage(message, timeout)

    def handle_record(self):
        """Starts a new recording session."""
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
        """Stops the recording and encrypts the resulting WAV file."""
        if self.recorder:
            # Stop recording; recorder returns the plain WAV file path.
            plain_wav = self.recorder.stop_recording()
            self.update_status("Recording complete.", 3000)
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            # Generate a new encryption key and store it
            self.encryption_key = generate_key()
            # Define an encrypted filename; e.g. replace .wav with .enc.wav
            encrypted_file = plain_wav.replace(".wav", ".enc.wav")
            try:
                encrypt_file(plain_wav, encrypted_file, self.encryption_key)
                # Optionally, delete the plain WAV file
                os.remove(plain_wav)
                self.audio_file = encrypted_file
                print(f"Encrypted file saved as: {self.audio_file}")
            except Exception as e:
                QMessageBox.critical(self, "Encryption Error", str(e))
                self.audio_file = (
                    plain_wav  # Fallback to plain file if encryption fails
                )

    def handle_transcribe(self):
        """Decrypts the recording and launches transcription."""
        if not self.audio_file or not self.encryption_key:
            QMessageBox.information(self, "No Recording", "Please record audio first.")
            return
        self.update_status("Decrypting for transcription...", 0)
        # Define a temporary filename for the decrypted file.
        # For simplicity, remove the '.enc' substring.
        decrypted_file = self.audio_file.replace(".enc.wav", ".dec.wav")
        try:
            decrypt_file(self.audio_file, decrypted_file, self.encryption_key)
        except Exception as e:
            QMessageBox.critical(self, "Decryption Error", str(e))
            return
        self.update_status("Transcribing...", 0)
        self.worker = TranscriptionWorker(
            decrypted_file, model_name="tiny", use_postprocessing=False
        )
        self.worker.transcription_complete.connect(self.on_transcription_complete)
        self.worker.transcription_error.connect(self.on_transcription_error)
        self.worker.start()

    def on_transcription_complete(self, transcript: str):
        """Handles transcription completion by calculating WPM and updating display."""
        self.statusBar().clearMessage()
        duration = get_wav_duration(self.audio_file.replace(".enc.wav", ".dec.wav"))
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
        """Securely deletes both the encrypted and decrypted audio files and discards the key."""
        if self.audio_file:
            from transcribe_app.secure_delete import secure_delete

            # Delete the encrypted file.
            secure_delete(self.audio_file)
            # Also delete the decrypted file, if it exists.
            dec_file = self.audio_file.replace(".enc.wav", ".dec.wav")
            if os.path.exists(dec_file):
                secure_delete(dec_file)
            self.update_status("Temporary audio files securely deleted.", 3000)
            self.audio_file = None
            # Destroy the encryption key.
            self.encryption_key = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
