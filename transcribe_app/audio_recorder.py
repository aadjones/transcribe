# transcribe_app/audio_recorder.py

import sounddevice as sd
import soundfile as sf


def record_audio(filename: str, duration: int = 10, fs: int = 16000):
    """
    Records audio for a given duration and saves it to a file.

    :param filename: The file path to save the recorded audio.
    :param duration: Duration of the recording in seconds.
    :param fs: Sampling rate (defaults to 16000 Hz).
    """
    print("Starting recording...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    sf.write(filename, audio_data, fs)
    print(f"Recording saved to {filename}")
