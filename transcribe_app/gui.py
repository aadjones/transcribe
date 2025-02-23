import logging
import os
import sys
import time
import wave

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
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

        # Create model picker dropdown
        model_layout = QHBoxLayout()
        self.model_picker = QComboBox(self)

        # Add model options with tooltips
        models = [
            (
                "Whisper Tiny",
                "tiny",
                "Fastest model - optimized for speed but may be less accurate",
            ),
            (
                "Whisper Small",
                "small",
                "Balanced model - good trade-off between speed and accuracy",
            ),
            (
                "Medical Model",
                "bqtsio/whisper-large-rad",
                "Medical-specific model - fine-tuned for medical speech, highest accuracy but slower",
            ),
        ]

        for label, model_id, tooltip in models:
            self.model_picker.addItem(label, userData=model_id)
            self.model_picker.setItemData(
                self.model_picker.count() - 1, tooltip, Qt.ToolTipRole
            )

        # Set Whisper Tiny as default
        self.model_picker.setCurrentIndex(0)

        model_layout.addWidget(self.model_picker)
        control_layout.addLayout(model_layout)
        control_layout.addSpacing(
            10
        )  # Add some space between model picker and other buttons

        # Add existing buttons
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
        self.model_picker.currentIndexChanged.connect(self.handle_model_changed)

    def update_status(self, message: str, timeout: int = 0):
        self.statusBar().showMessage(message, timeout)

    def handle_record(self):
        """Starts a new recording session."""
        try:
            # Clean up any existing recorder
            if self.recorder:
                try:
                    self.recorder.stop_recording()
                except Exception:
                    pass
                self.recorder = None

            self.recorder = RecordingManager(self)
            self.recorder.start_recording()
            self.record_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.update_status("Recording...", 0)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Recording Error",
                f"Could not start recording: {str(e)}\n"
                "Please check your microphone settings.",
            )
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.recorder = None

    def handle_stop(self):
        """Stops the recording and encrypts the resulting WAV file."""
        if not self.recorder:
            self.update_status("No active recording.", 3000)
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return

        try:
            # Stop recording; recorder returns the plain WAV file path
            plain_wav = self.recorder.stop_recording()
            if not plain_wav:
                raise RuntimeError("Recording failed to save properly")

            # Verify the WAV file before encryption
            try:
                with wave.open(plain_wav, "rb") as wav_file:
                    frames = wav_file.getnframes()
                    channels = wav_file.getnchannels()
                    rate = wav_file.getframerate()
                    logging.info(
                        f"Pre-encryption WAV verification:\n"
                        f"  Frames: {frames}\n"
                        f"  Channels: {channels}\n"
                        f"  Sample Rate: {rate} Hz\n"
                        f"  Duration: {frames/rate:.2f} seconds"
                    )
                    if frames == 0:
                        raise RuntimeError("WAV file contains no audio data")
            except Exception as e:
                logging.error(f"Error verifying WAV file: {e}")
                raise

            self.update_status("Recording complete. Encrypting...", 0)
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)

            # Generate a new encryption key and store it
            self.encryption_key = generate_key()
            # Define an encrypted filename; e.g. replace .wav with .enc.wav
            encrypted_file = plain_wav.replace(".wav", ".enc.wav")

            try:
                encrypt_file(plain_wav, encrypted_file, self.encryption_key)
                # Only remove the plain WAV if encryption succeeded
                if os.path.exists(encrypted_file):
                    # Try to delete with retries
                    for attempt in range(3):
                        try:
                            os.remove(plain_wav)
                            logging.info(
                                f"Successfully deleted plain WAV file on attempt {attempt + 1}"
                            )
                            break
                        except PermissionError as e:
                            logging.warning(f"Delete attempt {attempt + 1} failed: {e}")
                            if attempt < 2:  # Don't sleep on last attempt
                                time.sleep(0.5)
                        except Exception as e:
                            logging.warning(f"Could not remove plain WAV file: {e}")
                            break

                self.audio_file = encrypted_file
                self.update_status("Recording encrypted and saved.", 3000)
                logging.info(f"Encrypted file saved as: {self.audio_file}")
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Encryption Warning",
                    "Could not encrypt the recording. Using unencrypted file instead.\n"
                    f"Error: {str(e)}",
                )
                self.audio_file = (
                    plain_wav  # Fallback to plain file if encryption fails
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Recording Error", f"Error while stopping recording: {str(e)}"
            )
            self.audio_file = None
            self.encryption_key = None
        finally:
            self.recorder = None  # Clean up the recorder instance

    def get_selected_model(self) -> str:
        """Returns the ID of the currently selected model."""
        return self.model_picker.currentData()

    def handle_transcribe(self):
        """Decrypts the recording and launches transcription."""
        if not self.audio_file or not self.encryption_key:
            QMessageBox.information(self, "No Recording", "Please record audio first.")
            return

        # Define a temporary filename for the decrypted file
        decrypted_file = self.audio_file.replace(".enc.wav", ".dec.wav")

        # Clean up any existing decrypted file
        if os.path.exists(decrypted_file):
            try:
                os.remove(decrypted_file)
            except Exception as e:
                logging.warning(f"Could not remove existing decrypted file: {e}")

        self.update_status("Decrypting for transcription...", 0)
        try:
            decrypt_file(self.audio_file, decrypted_file, self.encryption_key)
            if not os.path.exists(decrypted_file):
                raise RuntimeError("Decryption failed to create output file")
        except Exception as e:
            QMessageBox.critical(
                self, "Decryption Error", f"Could not decrypt the recording: {str(e)}"
            )
            return

        self.update_status("Transcribing...", 0)
        try:
            # Use the selected model for transcription
            model_name = self.get_selected_model()
            self.worker = TranscriptionWorker(
                decrypted_file, model_name=model_name, use_postprocessing=False
            )
            self.worker.transcription_complete.connect(self.on_transcription_complete)
            self.worker.transcription_error.connect(self.on_transcription_error)
            self.worker.finished.connect(
                lambda: self.cleanup_decrypted_file(decrypted_file)
            )
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(
                self, "Transcription Error", f"Could not start transcription: {str(e)}"
            )
            try:
                os.remove(decrypted_file)
            except Exception:
                pass

    def cleanup_decrypted_file(self, decrypted_file: str):
        """Clean up the decrypted file after transcription."""
        if os.path.exists(decrypted_file):
            for attempt in range(3):
                try:
                    os.remove(decrypted_file)
                    logging.info(
                        f"Cleaned up decrypted file on attempt {attempt + 1}: {decrypted_file}"
                    )
                    break
                except PermissionError as e:
                    logging.warning(f"Delete attempt {attempt + 1} failed: {e}")
                    if attempt < 2:  # Don't sleep on last attempt
                        time.sleep(0.5)
                except Exception as e:
                    logging.warning(f"Could not remove decrypted file: {e}")
                    break

    def on_transcription_complete(self, transcript: str):
        """Handles transcription completion by calculating WPM and updating display."""
        self.statusBar().clearMessage()
        try:
            # Get the decrypted file path
            decrypted_file = self.audio_file.replace(".enc.wav", ".dec.wav")
            duration = get_wav_duration(decrypted_file)
            wpm = calculate_wpm(transcript, duration)

            display_text = (
                f"Transcript:\n{transcript}\n\n"
                f"Recording Duration: {duration:.2f} seconds\n"
                f"Words per minute (WPM): {wpm:.2f}"
            )
            self.transcript_display.append(display_text)
        except Exception as e:
            logging.error(f"Error calculating duration/WPM: {e}")
            # Still display the transcript even if we can't calculate duration/WPM
            self.transcript_display.append(f"Transcript:\n{transcript}")

    def on_transcription_error(self, error_message: str):
        """Handles transcription errors."""
        self.statusBar().clearMessage()
        QMessageBox.critical(
            self, "Transcription Error", f"Transcription failed: {error_message}"
        )

    def handle_secure_delete(self):
        """Securely deletes both the encrypted and decrypted audio files and discards the key."""
        if self.audio_file:
            from transcribe_app.secure_delete import secure_delete

            files_to_delete = [
                self.audio_file,  # Encrypted file
                self.audio_file.replace(".enc.wav", ".dec.wav"),  # Decrypted file
            ]

            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    # Try to verify the file before deletion
                    try:
                        with wave.open(file_path, "rb") as wav_file:
                            logging.info(
                                f"Pre-deletion WAV verification for {os.path.basename(file_path)}:\n"
                                f"  Frames: {wav_file.getnframes()}\n"
                                f"  Duration: {wav_file.getnframes()/wav_file.getframerate():.2f} seconds"
                            )
                    except Exception as e:
                        logging.warning(
                            f"Could not verify WAV file before deletion: {e}"
                        )

                    # Attempt secure deletion
                    for attempt in range(3):
                        try:
                            secure_delete(file_path)
                            logging.info(
                                f"Securely deleted {file_path} on attempt {attempt + 1}"
                            )
                            break
                        except PermissionError as e:
                            logging.warning(
                                f"Secure delete attempt {attempt + 1} failed: {e}"
                            )
                            if attempt < 2:
                                time.sleep(0.5)
                        except Exception as e:
                            logging.error(f"Error securely deleting {file_path}: {e}")
                            QMessageBox.warning(
                                self,
                                "Deletion Warning",
                                f"Could not securely delete {os.path.basename(file_path)}.\n"
                                f"Error: {str(e)}",
                            )
                            break

            self.update_status("Temporary audio files securely deleted.", 3000)
            self.audio_file = None
            # Destroy the encryption key
            self.encryption_key = None

    def handle_model_changed(self, index: int):
        """Handles when the user selects a different model.

        Args:
            index: The index of the newly selected model (automatically provided by Qt)
        """
        model_name = self.model_picker.currentText()
        model_id = self.model_picker.currentData()
        self.update_status(f"Selected model: {model_name}", 3000)
        logging.info(f"Model changed to: {model_name} (ID: {model_id})")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
