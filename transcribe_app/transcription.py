# transcribe_app/transcription.py

import logging
import os
import wave
from typing import Dict, Union

# Model configuration constants
WHISPER_MODELS: Dict[str, Dict[str, Union[str, int]]] = {
    "tiny": {
        "name": "tiny",
        "description": "Fastest, suitable for quick transcriptions",
        "size_mb": 150,
    },
    "small": {
        "name": "small",
        "description": "Good balance of speed and accuracy",
        "size_mb": 500,
    },
}

HUGGINGFACE_MODELS: Dict[str, Dict[str, Union[str, int]]] = {
    "bqtsio/whisper-large-rad": {
        "name": "Medical Model",
        "description": "Specialized for medical transcription",
        "size_mb": 3000,
    }
}

# Combined model registry
AVAILABLE_MODELS: Dict[str, Dict[str, Union[str, int]]] = {
    **WHISPER_MODELS,
    **HUGGINGFACE_MODELS,
}


def validate_model(model_name: str) -> bool:
    """
    Validate that the requested model is available and supported.

    Args:
        model_name (str): Name of the model to validate.

    Returns:
        bool: True if the model is valid.

    Raises:
        ValueError: If the model is not supported or invalid.
    """
    if "/" in model_name:  # Huggingface model
        if model_name not in HUGGINGFACE_MODELS:
            raise ValueError(
                f"Unsupported Hugging Face model: {model_name}. "
                f"Available models: {list(HUGGINGFACE_MODELS.keys())}"
            )
    else:  # Whisper model
        if model_name not in WHISPER_MODELS:
            raise ValueError(
                f"Unsupported Whisper model: {model_name}. "
                f"Available models: {list(WHISPER_MODELS.keys())}"
            )
    return True


def validate_audio_file(audio_file: str) -> bool:
    """
    Validate that the audio file exists and is a valid WAV file.

    Args:
        audio_file (str): Path to the audio file to validate.

    Returns:
        bool: True if the file is valid, False otherwise.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        RuntimeError: If the file is not a valid WAV file.
    """
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    if not os.path.isfile(audio_file):
        raise RuntimeError(f"Path exists but is not a file: {audio_file}")

    try:
        with wave.open(audio_file, "rb") as wav_file:
            if wav_file.getnframes() == 0:
                raise RuntimeError("WAV file contains no frames")
            if wav_file.getsampwidth() not in [2, 4]:  # 16-bit or 32-bit
                raise RuntimeError(
                    f"Unsupported sample width: {wav_file.getsampwidth() * 8}-bit"
                )
            if wav_file.getframerate() < 8000:  # Basic sanity check
                raise RuntimeError(f"Sample rate too low: {wav_file.getframerate()} Hz")
    except wave.Error as e:
        raise RuntimeError(f"Invalid WAV file: {str(e)}")

    return True


def transcribe_audio(
    audio_file: str, model_name: str = "tiny", use_postprocessing: bool = False
) -> str:
    """
    Transcribe audio from a file using the given model.

    The function supports two types of models:
    1. OpenAI Whisper models ("tiny", "small") - Faster, general-purpose transcription
    2. Hugging Face models (e.g., "bqtsio/whisper-large-rad") - Specialized models

    Args:
        audio_file (str): Path to the audio file to transcribe.
        model_name (str): Name of the model to use. Defaults to "tiny".
            - For Whisper models: "tiny" or "small"
            - For Hugging Face models: Full model path (e.g., "bqtsio/whisper-large-rad")
        use_postprocessing (bool): Whether to apply additional text processing. Defaults to False.

    Returns:
        str: The transcribed text.

    Raises:
        FileNotFoundError: If the audio file doesn't exist.
        ValueError: If the model name is not supported.
        RuntimeError: If there are issues with the audio file or transcription process.
        ImportError: If required packages cannot be imported.
    """
    logging.info(
        f"Attempting to transcribe file: {audio_file} with model: {model_name}"
    )

    # Validate inputs
    validate_audio_file(audio_file)
    validate_model(model_name)

    transcription = None
    try:
        if "/" in model_name:
            # Load model from Hugging Face using the automatic speech recognition pipeline
            try:
                from transformers import pipeline
            except ImportError as e:
                raise ImportError(
                    "Could not import transformers. Please install with: pip install transformers"
                ) from e

            try:
                pipe = pipeline("automatic-speech-recognition", model=model_name)
                result = pipe(audio_file)
                transcription = result["text"]
            except Exception as e:
                raise RuntimeError(
                    f"Error loading or using Hugging Face model: {str(e)}"
                )

        else:
            # Load using OpenAI's Whisper package with supported model names
            try:
                import whisper
            except ImportError as e:
                raise ImportError(
                    "Could not import whisper. Please install with: pip install openai-whisper"
                ) from e

            try:
                model = whisper.load_model(model_name)
                result = model.transcribe(audio_file)
                transcription = result["text"]
            except Exception as e:
                raise RuntimeError(f"Error during Whisper transcription: {str(e)}")

        if not transcription or not isinstance(transcription, str):
            raise RuntimeError("Transcription returned invalid or empty result")

        # Apply any additional postprocessing if needed
        if use_postprocessing:
            # For example, you could call a function: transcription = my_postprocessing(transcription)
            pass

        logging.info(f"Successfully transcribed {audio_file}")
        return transcription.strip()

    except Exception as e:
        logging.error(f"Error transcribing {audio_file}: {str(e)}")
        raise
