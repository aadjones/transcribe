import os

import numpy as np
import sounddevice as sd

from transcribe_app.audio_recorder import record_audio


def dummy_rec(n_frames, samplerate, channels, dtype):
    """
    Simulate recording by returning an array of zeros.

    Args:
        n_frames (int): Number of frames (samples) to generate.
        samplerate (int): The sample rate.
        channels (int): The number of channels.
        dtype: The numpy data type to use.

    Returns:
        numpy.ndarray: A zero-filled array simulating audio data.
    """
    # Create an array of zeros with the shape (n_frames, channels)
    return np.zeros((n_frames, channels), dtype=dtype)


def test_record_audio_creates_file(monkeypatch, tmp_path):
    # Monkeypatch the sd.rec function to use dummy_rec instead of actual recording.
    monkeypatch.setattr(sd, "rec", dummy_rec)

    # Create a temporary file path for the recording.
    tmp_file = tmp_path / "test_audio.wav"

    # Call the record_audio function, which should now use dummy_rec.
    record_audio(str(tmp_file), duration=1)

    # Assert that the file exists and that its size is greater than zero.
    assert tmp_file.exists(), "Audio file was not created."
    assert os.path.getsize(str(tmp_file)) > 0, "Audio file is empty."
