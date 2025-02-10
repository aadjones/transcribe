# Transcribe

A cross-platform desktop application for secure, local audio transcription. This app records audio, transcribes it using OpenAI's Whisper, and securely deletes temporary files, making it ideal for environments with HIPAA concerns.

## Features

- **Local Audio Recording:** Capture audio using a simple GUI.
- **Transcription:** Use the Whisper model (via `openai-whisper`) to transcribe recordings.
- **Secure Deletion:** Overwrite and delete temporary files to prevent unauthorized data recovery.
- **Cross-Platform:** Built with PySide6 for a native look on Windows and macOS.
- **Extensible & Modular:** Easily update or expand individual modules (recording, transcription, deletion).


## Getting Started

### Prerequisites
- Python: Recommended version: 3.11
- Dependencies: Listed in requirements.txt

### Installation
1. Clone the Repository:
```
git clone https://github.com/aadjones/transcribe.git
cd transcribe
```

2. Create and Activate a Virtual Environment:
```
python3.11 -m venv env
# On macOS/Linux:
source env/bin/activate
# On Windows:
.\env\Scripts\activate
```

3. Install Dependencies:
```
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

4. Install the Package in Development Mode:
```
pip install -e .
```

### Running the Application
To launch the app, you can use either:
```
# Option 1: Run as a module (recommended)
python -m transcribe_app.main

# Option 2: Run the file directly
python transcribe_app/main.py
```

A GUI window should open with options to Record, Transcribe, and Secure Delete.

### Testing
We use pytest for testing. From the root directory, run
```
pytest
```
to run all tests.

## For Developers
For more detailed setup instructions, please see our [Developer Guide](docs/DEVELOPER.md).

## Acknowledgements
- OpenAI Whisper for the transcription engine
- PySide6 for the cross-platform GUI framework