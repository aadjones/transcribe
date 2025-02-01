# transcribe_app/transcription.py

import whisper


def transcribe_audio(audio_file: str) -> str:
    """
    Transcribes the audio file using the Whisper model.

    :param audio_file: The path to the audio file to transcribe.
    :return: The transcription as a string.
    """
    print("Loading Whisper model...")
    model = whisper.load_model(
        "tiny"
    )  # You can change to "small" or another model as needed
    print("Transcribing audio...")
    result = model.transcribe(audio_file)
    transcription_text = result.get("text", "")
    print("Transcription complete.")
    return transcription_text
