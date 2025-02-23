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