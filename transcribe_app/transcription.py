# transcribe_app/transcription.py


def transcribe_audio(audio_file: str) -> str:
    # Defer the import of whisper until the function is called
    import whisper

    print("Loading Whisper model...")
    model = whisper.load_model("tiny")
    print("Transcribing audio...")
    result = model.transcribe(audio_file)
    transcription_text = result.get("text", "")
    print("Transcription complete.")
    return transcription_text
