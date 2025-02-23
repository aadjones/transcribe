# Model Picker Implementation Plan

## Feature Overview
Add a segmented model picker to the GUI that allows users to select between Whisper Tiny, Whisper Small, and the Hugging Face medical fine-tuned model for transcription.

## Implementation Steps

### Frontend Changes
- [x] Add segmented control widget to control panel layout
- [x] Define model options (Whisper Tiny, Small, Medical)
- [x] Set default selection to Whisper Tiny
- [x] Add get_selected_model method
- [x] Update handle_transcribe to use selected model

### Model Configuration Updates (`transcribe_app/transcription.py`)
- [x] Define model mapping constants
- [x] Add error handling for model loading failures
- [x] Add validation for model availability
- [x] Update docstrings to reflect model selection options

### TranscriptionWorker Updates (`transcribe_app/transcription_worker.py`)
- [x] Update worker to handle different model types
- [x] Add progress indicators for model loading
- [x] Enhance error handling for model-specific issues
- [x] Add logging for model selection and loading

### Dependencies Update (`setup.py`)
- [x] Add transformers package as dependency
- [x] Update requirements.txt
- [x] Specify version constraints for new dependencies
- [x] Document new dependencies in README.md

### Documentation Updates
- [x] Update architecture documentation with model selection feature
- [x] Add user documentation about available models
- [x] Document model characteristics and use cases
- [x] Update CHANGELOG.md with new feature

### Testing (`tests/test_gui.py`)
- [x] Create new test file for GUI components
- [x] Test model picker presence and visibility
- [x] Test default selection
- [x] Test model selection persistence
- [x] Test model selection is correctly passed to TranscriptionWorker
- [x] Mock transcription process for testing

## Notes
- Keep tests qualitative and not too rigid
- Maintain backward compatibility
- Consider future model additions
- Follow project's Python type annotation requirements
- Preserve existing comments and documentation

# Dropdown Menu Implementation Plan

## Feature Overview
Replace the current segmented model picker with Qt's built-in QComboBox component for a cleaner and more scalable model selection interface.

## Implementation Steps

### Frontend Changes
1. Component Updates
   - [x] Import QComboBox from PySide6.QtWidgets
   - [x] Replace existing QButtonGroup with QComboBox in the control panel
   - [x] Add model options to QComboBox (Whisper Tiny, Small, Medical)
   - [x] Set default selection to Whisper Tiny
   - [x] Add informative tooltips for each model option

2. State Management
   - [x] Update get_selected_model method to work with QComboBox
   - [x] Connect QComboBox's currentIndexChanged signal to handle selection changes
   - [x] Preserve model selection state during transcription

### Integration
1. Replace Existing Control
   - [x] Remove QButtonGroup and related buttons
   - [x] Insert QComboBox into the existing control_layout
   - [x] Update layout spacing and alignment for visual consistency
   - [x] Preserve all existing model selection logic

2. Style Updates
   - [x] Use Qt's native styling (clean and consistent with system)
   - [x] Leverage built-in hover and focus states
   - [x] Maintain visual hierarchy in control panel
   - [x] Match application's design system using native widgets

### Testing Updates
1. Component Testing
   - [x] Update test_model_picker_exists for QComboBox
   - [x] Test dropdown functionality using Qt's testing tools
   - [x] Verify model selection using QComboBox methods
   - [x] Test tooltips and accessibility features

2. Integration Testing
   - [x] Verify model selection still works end-to-end
   - [x] Test state persistence with QComboBox
   - [x] Verify no regression in existing functionality
   - [x] Test QComboBox signals and slots

2. Update CHANGELOG
   - [x] Document UI improvement
   - [x] Note the switch to QComboBox
   - [x] Update version number

## Notes
- [x] Leverage Qt's built-in accessibility features
- [x] Use Qt's native dropdown animations
- [x] Maintain consistent styling with other Qt widgets
- [x] Plan for future model additions using QComboBox's dynamic item management
- [x] Rely on Qt's built-in keyboard navigation and focus handling 