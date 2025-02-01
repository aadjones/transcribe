from transcribe_app import transcription

# A dummy model that returns a predictable transcription.
class DummyModel:
    def transcribe(self, audio_file):
        return {"text": "dummy transcription"}

def dummy_load_model(model_name):
    return DummyModel()

def test_transcribe_audio(monkeypatch, tmp_path):
    # Create a dummy audio file (contents don't matter for the dummy model)
    dummy_audio = tmp_path / "dummy.wav"
    dummy_audio.write_bytes(b"dummy content")
    
    # Monkey-patch the whisper.load_model in the transcription module.
    monkeypatch.setattr(transcription, "whisper", type("DummyWhisper", (), {"load_model": dummy_load_model}))
    
    # Run the transcription function.
    text = transcription.transcribe_audio(str(dummy_audio))
    
    # Check that the dummy transcription is returned.
    assert text == "dummy transcription", "The transcription did not return the expected dummy output."
