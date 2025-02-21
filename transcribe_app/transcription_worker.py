# transcribe_app/transcription_worker.py
import logging

from PySide6.QtCore import QThread, Signal


class TranscriptionWorker(QThread):
    # Signal emitted when transcription is complete; sends the transcript string
    transcription_complete = Signal(str)
    # Signal emitted on error
    transcription_error = Signal(str)
    # Signal emitted for progress updates
    progress = Signal(str)

    def __init__(
        self,
        audio_file: str,
        model_name: str = "tiny",
        use_postprocessing: bool = False,
    ):
        super().__init__()
        self.audio_file = audio_file
        self.model_name = model_name
        self.use_postprocessing = use_postprocessing
        self._is_running = True

    def run(self):
        if not self._is_running:
            return

        try:
            # Import here to avoid issues with threading
            from transcribe_app.transcription import transcribe_audio

            if not self._is_running:
                return

            self.progress.emit("Loading Whisper model...")
            transcript = transcribe_audio(
                self.audio_file,
                model_name=self.model_name,
                use_postprocessing=self.use_postprocessing,
            )

            if not transcript:
                raise RuntimeError("Transcription returned empty result")

            if not self._is_running:
                return

            self.transcription_complete.emit(transcript)

        except ImportError as e:
            error_msg = f"Could not import transcription module: {str(e)}"
            logging.error(error_msg)
            self.transcription_error.emit(error_msg)
        except RuntimeError as e:
            error_msg = f"Transcription failed: {str(e)}"
            logging.error(error_msg)
            self.transcription_error.emit(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during transcription: {str(e)}"
            logging.error(error_msg)
            self.transcription_error.emit(error_msg)

    def stop(self):
        """Stops the transcription process."""
        self._is_running = False
