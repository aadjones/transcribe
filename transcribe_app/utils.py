import wave

import soundfile as sf


def get_audio_duration(filename: str) -> float:
    """Returns the duration in seconds of the audio file."""
    with sf.SoundFile(filename) as f:
        return len(f) / f.samplerate


def get_wav_duration(filename: str) -> float:
    """Return the duration (in seconds) of a WAV file based on its header."""
    with wave.open(filename, "rb") as wav_file:
        nframes = wav_file.getnframes()
        framerate = wav_file.getframerate()
        duration = nframes / float(framerate)
    return duration


def calculate_wpm(transcript: str, duration_seconds: float) -> float:
    """
    Calculate words per minute (WPM) from a transcript and a recording duration (in seconds).
    """
    word_count = len(transcript.split())
    minutes = duration_seconds / 60.0
    return word_count / minutes if minutes > 0 else 0.0
