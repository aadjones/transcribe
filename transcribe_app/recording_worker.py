# transcribe_app/recording_worker.py
from PySide6.QtCore import QThread, Signal

from transcribe_app.audio_recorder import record_audio


class RecordingWorker(QThread):
    # Signal emitted when recording is complete.
    recording_complete = Signal(str)  # Sends the filename or a status message
    recording_error = Signal(str)

    def __init__(self, audio_file: str, duration: int = 10, parent=None):
        super().__init__(parent)
        self.audio_file = audio_file
        self.duration = duration
        self._running = True

    def run(self):
        while self._running:
            try:
                record_audio(self.audio_file, duration=self.duration)
                self.recording_complete.emit(self.audio_file)
            except Exception as e:
                self.recording_error.emit(str(e))

    def stop(self):
        self._running = False
