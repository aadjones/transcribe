import os
from transcribe_app.audio_recorder import record_audio

def test_record_audio_creates_file(tmp_path):
    # Create a temporary file path
    tmp_file = tmp_path / "test_audio.wav"
    
    # Record audio for 1 second (for testing)
    record_audio(str(tmp_file), duration=1)
    
    # Check that the file exists
    assert tmp_file.exists(), "Audio file was not created."
    
    # Check that the file size is greater than zero (i.e., it's not empty)
    file_size = os.path.getsize(str(tmp_file))
    assert file_size > 0, "Audio file is empty."
