import soundfile as sf


def get_audio_duration(filename: str) -> float:
    """Returns the duration in seconds of the audio file."""
    with sf.SoundFile(filename) as f:
        return len(f) / f.samplerate
