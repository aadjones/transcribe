# Architecture Overview

This document provides a high-level overview of the Transcribe App, its core components, and how they interact. The application is designed to run locally, transcribe audio using the Whisper model, and securely delete sensitive files. It is built using Python, with a PySide6-based GUI, and follows a modular design.

---

## High-Level Components

### 1. **Application Package (`transcribe_app`)**

The main package is organized into several modules, each responsible for a specific aspect of the application's functionality:

- **`main.py`**
  - **Purpose:**  
    Serves as the entry point for the application. It initializes the GUI and starts the event loop.
  - **Responsibilities:**  
    - Create and configure the QApplication instance.
    - Instantiate and display the main window.

- **`gui.py`**
  - **Purpose:**  
    Contains the code for the graphical user interface.
  - **Key Components:**  
    - `MainWindow` class that sets up the window, layout, and widgets (buttons for recording, transcribing, secure deletion, and a text area for displaying transcriptions).
  - **Interaction:**  
    - Connects user interactions (button clicks) to backend functions (e.g., record audio, run transcription).

- **`audio_recorder.py`**
  - **Purpose:**  
    Manages audio recording functionality using libraries such as `sounddevice` and `soundfile`.
  - **Key Function:**  
    - `record_audio(filename, duration, fs)`: Records audio for a specified duration at a given sample rate, saving the recording as a WAV file.

- **`transcription.py`**
  - **Purpose:**  
    Handles the transcription of audio files using the OpenAI Whisper model.
  - **Key Function:**  
    - `transcribe_audio(audio_file)`: Loads the Whisper model (e.g., the "tiny" model) and returns a transcription of the given audio file.
  - **Note:**  
    - The module can be configured to use different devices (CPU, MPS for Apple Silicon) as needed.

- **`secure_delete.py`**
  - **Purpose:**  
    Implements secure deletion of files, ensuring that sensitive data is properly overwritten and removed.
  - **Key Function:**  
    - `secure_delete(file_path, passes)`: Overwrites a file multiple times with random data before deleting it.

- **`config.py`**
  - **Purpose:**  
    Centralizes configuration settings for the application.
  - **Usage:**  
    - Stores constants such as default file paths, sample rates, model parameters, etc.

- **`utils.py`**
  - **Purpose:**  
    Contains helper functions that are used across multiple modules.
  - **Usage:**  
    - Common utility functions such as file management or logging configuration.

---

## Supporting Components
### 2. **Tests (`tests/` Directory)**
- **Purpose:**  
  Contains unit and integration tests to verify the functionality of the core modules.
- **Organization:**  
  - `test_audio_recorder.py`: Tests for verifying that the audio recorder creates a valid, non-empty WAV file.
  - `test_transcription.py`: Uses monkeypatching to simulate the Whisper model, ensuring that the transcription logic returns expected results.
  - `test_secure_delete.py`: Confirms that files are securely overwritten and deleted.
- **Testing Framework:**  
  - Uses pytest, with tests run from the project root to ensure proper module resolution.

### 3. **Documentation (`docs/` Directory)**
- **Purpose:**  
  Contains supporting documentation such as architecture diagrams, design decisions, and user guides.
- **Files:**  
  - `architecture.md`: This document.
  - `architecture.png`: An image of the high-level data flowchart below.
  - `overview.md`: A higher-level overview of the purpose of the app.
---

## High-Level Data Flow

```mermaid
flowchart TD
    A[User] --> B[GUI (PySide6)]
    B --> C[Audio Recording Module]
    C --> D[Temporary Audio File (WAV)]
    D --> E[Transcription Module (Whisper)]
    E --> F[Transcript Display]
    B --> G[Secure Deletion Module]
    G --> D[Overwrites & Deletes File]
```

**User Interaction:**
- The user interacts with the GUI, triggering actions such as recording audio and requesting a transcription.
**Audio Recording:**
- The audio_recorder.py module captures audio and stores it temporarily.
**Transcription:**
- The temporary audio file is passed to the transcription.py module, which returns a text transcription that is displayed in the GUI.
**Secure Deletion:**
- Once the user extracts the necessary information, the secure_delete.py module securely removes the temporary file.

## Device and Performance Considerations
**CPU vs. GPU (MPS on Apple Silicon):**
- By default, the application uses CPU for transcription.
- On Macs with M1/M2 chips, experimental MPS support in PyTorch may be configured for better performance.

**Precision:**
- The app may fall back to FP32 precision if FP16 is not supported by the hardware.

## Future Enhancements
**Enhanced Model Support:**
- Integrate WhisperX for improved timestamping and alignment.

**GUI Testing:**
- Add automated GUI tests using pytest-qt if needed.

**Performance Optimization:**
- Explore further device configuration to fully leverage MPS on Apple Silicon.

**Additional Features:**
Consider adding features like speaker diarization or real-time transcription, if requirements evolve.
