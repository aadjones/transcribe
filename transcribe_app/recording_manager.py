# recording_manager.py
import logging
import os
import wave

from PySide6.QtCore import QIODevice, QTemporaryFile
from PySide6.QtMultimedia import QAudioFormat, QAudioSource, QMediaDevices


class RecordingManager:
    """
    A robust recording manager that uses QAudioSource and QTemporaryFile.
    It records audio until stop_recording() is called.
    """

    def __init__(self, parent=None):
        self.parent = parent
        # Create a temporary file with .wav extension
        self.temp_file = QTemporaryFile(os.path.join(os.getcwd(), "XXXXXX.wav"), parent)
        self.temp_file.setAutoRemove(False)
        if not self.temp_file.open(QIODevice.ReadWrite):
            raise RuntimeError("Cannot open temporary file for recording")

        logging.info(f"Created temporary file: {self.temp_file.fileName()}")

        # Initialize WAV file header
        with wave.open(self.temp_file.fileName(), "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes for Int16
            wav_file.setframerate(44100)

        self.audio_source = None

    def start_recording(self):
        fmt = QAudioFormat()
        fmt.setSampleRate(44100)
        fmt.setChannelCount(1)
        fmt.setSampleFormat(QAudioFormat.Int16)

        devices = QMediaDevices()
        default_input = devices.defaultAudioInput()
        if not default_input.isFormatSupported(fmt):
            fmt = default_input.preferredFormat()

        self.audio_source = QAudioSource(default_input, fmt, self.parent)
        self.temp_file.seek(44)  # Skip WAV header
        self.audio_source.start(self.temp_file)

    def stop_recording(self):
        if self.audio_source is not None:
            self.audio_source.stop()

        # Update WAV header with correct size
        file_size = self.temp_file.size()
        logging.info(f"Recording size: {file_size} bytes")

        self.temp_file.seek(0)
        temp_filename = self.temp_file.fileName()

        # Read all audio data before closing
        self.temp_file.seek(44)  # Skip original header
        audio_data = self.temp_file.readAll()

        # Close the temp file
        self.temp_file.close()

        # Write to a new WAV file
        with wave.open(temp_filename, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            wav_file.writeframes(audio_data.data())

        logging.info(f"Saved WAV file: {temp_filename}")
        if os.path.exists(temp_filename):
            logging.info(f"File exists with size: {os.path.getsize(temp_filename)}")
        else:
            logging.error("File does not exist after saving!")

        return temp_filename

    # def delete_recording(self):
    #     # Secure deletion would need to overwrite the file contents before removal,
    #     # which you would implement as needed.
    #     filename = self.temp_file.fileName()
    #     if os.path.exists(filename):
    #         os.remove(filename)
