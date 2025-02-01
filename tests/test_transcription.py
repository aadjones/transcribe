import sys
import types

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

    # Create a dummy module for 'whisper' with the dummy load_model function.
    dummy_whisper = types.ModuleType("whisper")
    dummy_whisper.load_model = dummy_load_model

    # Insert the dummy whisper module into sys.modules
    monkeypatch.setitem(sys.modules, "whisper", dummy_whisper)

    # Now, when transcription.transcribe_audio is called, it will do:
    #    import whisper
    # and get our dummy_whisper module.
    text = transcription.transcribe_audio(str(dummy_audio))

    # Check that the dummy transcription is returned.
    assert (
        text == "dummy transcription"
    ), "The transcription did not return the expected dummy output."
