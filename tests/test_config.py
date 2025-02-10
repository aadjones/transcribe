# tests/test_config.py


def test_hf_api_token_loading(monkeypatch):
    # Ensure that when we set HF_API_TOKEN, the configuration picks it up.
    monkeypatch.setenv("HF_API_TOKEN", "dummy_token")
    # Import the config module after setting the env var.
    from transcribe_app import config

    assert (
        config.HF_API_TOKEN == "dummy_token"
    ), "Config should load HF_API_TOKEN from the environment."
