# transcribe_app/transcription.py


def transcribe_audio(audio_file, model_name="tiny", use_postprocessing=False):
    """
    Transcribe the given audio file using a Whisper model.

    :param audio_file: Path to the audio file.
    :param model_name: The size/model version to use (e.g., "tiny", "small", "large").
    :param use_postprocessing: Flag to enable domain-specific postprocessing (if any).
    :return: The transcription text.
    """
    import whisper

    print(f"Loading Whisper model '{model_name}' for file: {audio_file}...")
    model = whisper.load_model(model_name)
    print("Transcribing audio...")
    
    result = model.transcribe(audio_file)
    transcription_text = result["text"]

    if use_postprocessing:
        # Add any domain-specific postprocessing here
        pass

    print("Transcription complete.")
    return transcription_text
