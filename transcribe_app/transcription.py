# transcribe_app/transcription.py


def transcribe_audio(audio_file: str, model_name: str = "tiny", use_postprocessing: bool = False) -> str:
    """
    Transcribe audio from a file using the given model.
    
    If the model name contains a slash ("/"), load the model using the Hugging Face 
    Transformers pipeline. Otherwise, use the OpenAI Whisper package.
    
    Parameters:
      audio_file (str): Path to the audio file.
      model_name (str): Name of the model. For a Hugging Face model, this will be the repository name,
                        e.g., "bqtsio/whisper-large-rad". Defaults to "tiny".
      use_postprocessing (bool): Option to enable additional postprocessing (if implemented).
    
    Returns:
      str: The transcribed text.
    """
    if "/" in model_name:
        # Load model from Hugging Face using the automatic speech recognition pipeline.
        from transformers import pipeline
        pipe = pipeline("automatic-speech-recognition", model=model_name)
        result = pipe(audio_file)
        transcription = result["text"]
    else:
        # Load using OpenAI's Whisper package with supported model names.
        import whisper
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_file)
        transcription = result["text"]
    
    # Apply any additional postprocessing if needed (not implemented here).
    if use_postprocessing:
        # For example, you could call a function: transcription = my_postprocessing(transcription)
        pass

    return transcription
