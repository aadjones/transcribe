"""Tests for the GUI components, particularly the model picker functionality."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox

from transcribe_app.gui import MainWindow
from transcribe_app.transcription import AVAILABLE_MODELS


@pytest.fixture
def main_window(qtbot):
    """Create a MainWindow instance for testing."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window


def test_model_picker_exists(main_window: MainWindow):
    """Test that the model picker widget exists and is visible."""
    assert main_window.model_picker is not None, "Model picker should exist"
    assert isinstance(
        main_window.model_picker, QComboBox
    ), "Model picker should be a QComboBox"
    assert main_window.model_picker.count() == 3, "Should have exactly 3 model options"


def test_model_picker_default(main_window: MainWindow):
    """Test that the model picker defaults to Whisper Tiny."""
    selected_model = main_window.get_selected_model()
    assert selected_model == "tiny", "Default model should be 'tiny'"
    assert main_window.model_picker.currentText().startswith(
        "Whisper Tiny"
    ), "Tiny model should be selected"


def test_model_picker_selection(main_window: MainWindow, qtbot):
    """Test that model selection works and persists."""
    # Select the medical model
    main_window.model_picker.setCurrentText("Medical Model")

    # Verify selection
    selected_model = main_window.get_selected_model()
    assert selected_model == "bqtsio/whisper-large-rad", "Should select medical model"
    assert (
        main_window.model_picker.currentText() == "Medical Model"
    ), "Medical model should be selected"


def test_model_picker_tooltips(main_window: MainWindow):
    """Test that tooltips are properly set for each model."""
    expected_tooltips = {
        "Whisper Tiny": "Fastest model - optimized for speed but may be less accurate",
        "Whisper Small": "Balanced model - good trade-off between speed and accuracy",
        "Medical Model": "Medical-specific model - fine-tuned for medical speech, highest accuracy but slower",
    }

    for i in range(main_window.model_picker.count()):
        item_text = main_window.model_picker.itemText(i)
        tooltip = main_window.model_picker.itemData(i, Qt.ToolTipRole)
        assert (
            tooltip == expected_tooltips[item_text]
        ), f"Tooltip mismatch for {item_text}"


def test_model_selection_signal(main_window: MainWindow, qtbot):
    """Test that model selection emits proper signals and updates status."""
    # Create a signal spy to track status bar updates
    status_messages: list[str] = []
    main_window.statusBar().messageChanged.connect(status_messages.append)

    # Change model selection
    main_window.model_picker.setCurrentText("Medical Model")

    # Verify status bar was updated
    assert any(
        "Selected model: Medical Model" in msg for msg in status_messages
    ), "Status bar should show model selection message"


def test_model_selection_persistence(main_window: MainWindow, qtbot):
    """Test that model selection persists through transcription process."""
    # Select medical model
    main_window.model_picker.setCurrentText("Medical Model")

    # Verify initial selection
    model_id = main_window.get_selected_model()
    assert model_id == "bqtsio/whisper-large-rad", "Model selection should persist"

    # Change selection and verify it updates
    main_window.model_picker.setCurrentText("Whisper Small")
    assert main_window.get_selected_model() == "small", "Model selection should update"


def test_model_names_match_registry(main_window: MainWindow):
    """Test that the available model selections match our model registry."""
    model_map = {
        "Whisper Tiny": "tiny",
        "Whisper Small": "small",
        "Medical Model": "bqtsio/whisper-large-rad",
    }

    # Verify each item in the combo box corresponds to a registered model
    for i in range(main_window.model_picker.count()):
        label = main_window.model_picker.itemText(i)
        model_id = main_window.model_picker.itemData(i)
        assert model_id == model_map[label], f"Model ID mismatch for {label}"
        assert model_id in AVAILABLE_MODELS, f"Model {model_id} should be in registry"
