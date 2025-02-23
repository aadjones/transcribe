# transcribe_app/transcription_worker.py
import logging
from typing import Optional

from PySide6.QtCore import QThread, Signal

from transcribe_app.transcription import (
    AVAILABLE_MODELS,
    validate_model,
)


class TranscriptionWorker(QThread):
    # Signal emitted when transcription is complete; sends the transcript string
    transcription_complete = Signal(str)
    # Signal emitted on error
    transcription_error = Signal(str)
    # Signal emitted for progress updates
    progress = Signal(str)
    # Signal for model loading progress (0-100)
    model_progress = Signal(int)

    def __init__(
        self,
        audio_file: str,
        model_name: str = "tiny",
        use_postprocessing: bool = False,
    ):
        """
        Initialize the transcription worker.

        Args:
            audio_file (str): Path to the audio file to transcribe
            model_name (str): Name of the model to use (default: "tiny")
            use_postprocessing (bool): Whether to apply post-processing (default: False)
        """
        super().__init__()
        self.audio_file = audio_file
        self.model_name = model_name
        self.use_postprocessing = use_postprocessing
        self._is_running = True

    def _get_model_info(self) -> Optional[dict]:
        """Get information about the selected model."""
        try:
            validate_model(self.model_name)
            return AVAILABLE_MODELS.get(self.model_name)
        except ValueError as e:
            self.transcription_error.emit(str(e))
            return None

    def _emit_model_loading_progress(self, model_info: dict):
        """Emit appropriate progress messages based on model type and size."""
        model_name = model_info["name"]
        model_size = model_info["size_mb"]

        self.progress.emit(f"Loading {model_name} model ({model_size}MB)...")
        if "/" in self.model_name:  # Hugging Face model
            self.progress.emit(
                "Downloading model from Hugging Face (this may take a while)..."
            )
        else:  # Whisper model
            self.progress.emit("Initializing Whisper model...")

        # Simulate progress for model loading
        # In a future enhancement, we could hook into actual model loading progress
        self.model_progress.emit(0)
        self.model_progress.emit(50)

    def run(self):
        """Run the transcription process."""
        if not self._is_running:
            return

        try:
            # Get model information
            model_info = self._get_model_info()
            if not model_info:
                return

            # Import here to avoid issues with threading
            from transcribe_app.transcription import transcribe_audio

            if not self._is_running:
                return

            # Show model loading progress
            self._emit_model_loading_progress(model_info)

            # Perform transcription
            self.progress.emit("Transcribing audio...")
            transcript = transcribe_audio(
                self.audio_file,
                model_name=self.model_name,
                use_postprocessing=self.use_postprocessing,
            )

            if not transcript:
                raise RuntimeError("Transcription returned empty result")

            if not self._is_running:
                return

            # Complete progress and emit result
            self.model_progress.emit(100)
            self.progress.emit("Transcription complete!")
            self.transcription_complete.emit(transcript)

        except ImportError as e:
            error_msg = f"Could not import required module: {str(e)}"
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
        finally:
            # Ensure progress is reset if there was an error
            if not self._is_running:
                self.model_progress.emit(0)

    def stop(self):
        """Stops the transcription process."""
        self._is_running = False
        self.progress.emit("Transcription cancelled.")
