# transcribe_app/transcription_worker.py
from PySide6.QtCore import QThread, Signal


class TranscriptionWorker(QThread):
    # Signal emitted when transcription is complete; sends the transcript string.
    transcription_complete = Signal(str)
    # Signal emitted on error.
    transcription_error = Signal(str)

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

    def run(self):
        try:
            # Import the transcription function (do this inside run to avoid issues with threading)
            from transcribe_app.transcription import transcribe_audio

            transcript = transcribe_audio(
                self.audio_file,
                model_name=self.model_name,
                use_postprocessing=self.use_postprocessing,
            )
            self.transcription_complete.emit(transcript)
        except Exception as e:
            self.transcription_error.emit(str(e))
