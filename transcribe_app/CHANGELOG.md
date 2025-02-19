# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive debug logging system with millisecond precision timestamps
- Audio data analysis with silence detection and sample verification
- Detailed device enumeration and format compatibility logging
- Buffer size optimization for audio recording
- Retry logic for file operations to handle Windows file locks
- WAV file integrity checks and verification
- Post-processing support for transcription text correction
- Test utilities for generating valid WAV files with configurable parameters
- Helper function `create_dummy_wav()` for testing with proper RIFF headers

### Changed
- Switched to explicit 16-bit PCM format for WAV files
- Improved error handling for audio device detection
- Enhanced temporary file management using QTemporaryFile
- Updated secure deletion with multiple retry attempts
- Refined resource cleanup and handle release procedures
- Improved WAV header handling and verification
- Modified test setup to bypass WAV validation in transcription tests

### Fixed
- [WinError 32] file locking issues on Windows
- Audio format compatibility issues with Qt 6
- Silent recording detection and reporting
- Resource cleanup during error conditions
- WAV file corruption issues during save operations
- Test failures related to invalid WAV headers by using monkeypatch

### Testing
- Added `create_dummy_wav()` utility function with configurable:
  - Duration
  - Sample rate
  - Channel count
  - Bit depth
- Improved test reliability with proper WAV file validation
- Enhanced dummy model testing with valid audio files
- Added validation checks for WAV file integrity in tests

### Removed
- References to deprecated Qt audio APIs
- Unused compression type checks for WAV files
- Legacy audio format configurations

## [0.1.0] - 2025-02-18

### Added
- Initial implementation of secure transcription application
- Basic audio recording functionality
- Whisper integration for transcription
- Simple GUI with record/stop/transcribe buttons
- Basic file encryption and secure deletion
- Preliminary error handling and logging

### Technical Details

#### Audio Recording Improvements
- Implemented proper 16-bit PCM format setting
- Added device format compatibility checks
- Enhanced error detection and reporting
- Improved buffer management and state monitoring

#### File Operations
- Added robust file locking detection
- Implemented multiple deletion attempts for Windows compatibility
- Enhanced WAV header validation and verification
- Improved temporary file cleanup

#### Logging System
- Added comprehensive debug logging
- Implemented audio data analysis
- Added file operation tracking
- Enhanced error message detail and context

#### Post-Processing Support
- Added framework for transcription text correction
- Implemented medical terminology corrections
- Added support for custom correction dictionaries
- Enhanced error detection in transcribed text

### Developer Notes

When making significant changes to the codebase, please:

1. Add a new entry under the [Unreleased] section
2. Include the date of the change
3. Categorize the change as Added, Changed, Fixed, or Removed
4. Provide a brief but clear description of the change
5. Include any relevant technical details or impact on existing functionality
6. Document any breaking changes prominently

For changes that affect the audio processing pipeline:
- Document format changes
- Note any performance impacts
- List compatibility considerations
- Include any new dependencies

For security-related changes:
- Document the security impact
- Note any changes to encryption or secure deletion
- List any new security considerations

Remember to move [Unreleased] changes to a new version section when creating a release. 