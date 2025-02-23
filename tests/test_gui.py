"""Tests for the GUI components, particularly the model picker functionality."""

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import Qt

from transcribe_app.gui import MainWindow
from transcribe_app.transcription import AVAILABLE_MODELS

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def main_window(qtbot):
    """Create a MainWindow instance for testing."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window


def test_model_picker_exists(main_window: MainWindow):
    """Test that the model picker widget exists and is visible."""
    assert main_window.model_picker is not None, "Model picker should exist"
    assert (
        main_window.model_picker.parent() is not None
    ), "Model picker should have a parent"

    # Check that we have the correct number of buttons
    assert (
        len(main_window.model_picker.buttons()) == 3
    ), "Should have exactly 3 model options"


def test_model_picker_default(main_window: MainWindow):
    """Test that the model picker defaults to Whisper Tiny."""
    selected_model = main_window.get_selected_model()
    assert selected_model == "tiny", "Default model should be 'tiny'"

    # Verify the correct button is checked
    buttons = main_window.model_picker.buttons()
    assert any(
        b.isChecked() and "Tiny" in b.text() for b in buttons
    ), "Tiny model button should be checked"


def test_model_picker_selection(main_window: MainWindow, qtbot):
    """Test that model selection works and persists."""
    # Get all buttons
    buttons = main_window.model_picker.buttons()

    # Find and click the medical model button
    medical_button = next(b for b in buttons if "Medical" in b.text())
    qtbot.mouseClick(medical_button, Qt.LeftButton)

    # Verify selection
    selected_model = main_window.get_selected_model()
    assert selected_model == "bqtsio/whisper-large-rad", "Should select medical model"
    assert medical_button.isChecked(), "Medical model button should be checked"


def test_model_selection_exclusive(main_window: MainWindow, qtbot):
    """Test that only one model can be selected at a time."""
    buttons = main_window.model_picker.buttons()

    # Click each button and verify only it is checked
    for button in buttons:
        qtbot.mouseClick(button, Qt.LeftButton)
        assert button.isChecked(), f"{button.text()} should be checked"
        assert (
            sum(b.isChecked() for b in buttons) == 1
        ), "Only one button should be checked"


def test_transcription_uses_selected_model(
    main_window: MainWindow, mocker: "MockerFixture"
):
    """Test that transcription uses the selected model."""
    # Mock the TranscriptionWorker
    mock_worker = mocker.patch("transcribe_app.gui.TranscriptionWorker")

    # Select the medical model
    buttons = main_window.model_picker.buttons()
    medical_button = next(b for b in buttons if "Medical" in b.text())
    medical_button.setChecked(True)

    # Create a new worker with the selected model
    main_window.worker = mock_worker(
        audio_file="dummy.wav", model_name=main_window.get_selected_model()
    )

    # Verify the worker was created with the correct model
    mock_worker.assert_called_once()
    assert mock_worker.call_args[1]["model_name"] == "bqtsio/whisper-large-rad"


def test_model_names_match_registry(main_window: MainWindow):
    """Test that the available model selections match our model registry."""
    buttons = main_window.model_picker.buttons()
    button_models = {
        "Tiny": "tiny",
        "Small": "small",
        "Medical": "bqtsio/whisper-large-rad",
    }

    # Verify each button corresponds to a registered model
    for button in buttons:
        model_key = next(k for k in button_models if k in button.text())
        expected_model = button_models[model_key]
        assert (
            expected_model in AVAILABLE_MODELS
        ), f"Model {expected_model} should be in registry"
