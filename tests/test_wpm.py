import pytest

from transcribe_app.utils import calculate_wpm


def test_wpm_normal():
    # "Hello world" has 2 words; if recorded for 60 seconds, it should be 2 WPM.
    transcript = "Hello world"
    duration_seconds = 60.0
    wpm = calculate_wpm(transcript, duration_seconds)
    assert wpm == pytest.approx(2.0)


def test_wpm_another():
    # "This is a test" has 4 words; if recorded for 30 seconds, it should be 8 WPM.
    transcript = "This is a test"
    duration_seconds = 30.0
    wpm = calculate_wpm(transcript, duration_seconds)
    assert wpm == pytest.approx(8.0)


def test_wpm_zero_duration():
    # If the duration is zero, we expect the function to return 0.0.
    transcript = "Some transcript"
    duration_seconds = 0.0
    wpm = calculate_wpm(transcript, duration_seconds)
    assert wpm == 0.0
