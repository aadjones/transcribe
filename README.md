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

## Hugging Face API Key Setup

Some datasets used by this project (e.g. [United-Syn-Med](https://huggingface.co/datasets/united-we-care/United-Syn-Med)) are gated and require authentication via a Hugging Face API key. To set this up, follow these steps:

1. **Create or Log In to Your Hugging Face Account:**
   - Visit [Hugging Face](https://huggingface.co) and either log in or create a new account.

2. **Generate Your API Token:**
   - Click on your profile picture at the top-right, then go to **Settings**.
   - Navigate to the **Access Tokens** section.
   - Click **New token**, give it a name (for example, `transcribe-app`), select the appropriate scope (usually "read"), and generate the token.
   - **Copy the token** — you will need this in the next step.

3. **Accept Dataset Terms (If Needed):**
   - For gated datasets (such as United-Syn-Med), visit their page and accept any usage terms if prompted.

4. **Configure Your Local Environment:**
   - In your project's root directory, create a file named `.env`.
   - Add the following line to the `.env` file, replacing `your_huggingface_api_token_here` with the token you copied:
     ```
     HF_API_TOKEN=your_huggingface_api_token_here
     ```
   - **Tip:** Make sure that your `.env` file is listed in your `.gitignore` to avoid committing sensitive information to version control.

5. **Install the Required Dependency:**
   - This project uses the `python-dotenv` package to load environment variables from the `.env` file. If you haven't installed it yet, run:
     ```bash
     pip install python-dotenv
     ```

6. **Using the API Key in the Project:**
   - The project includes a configuration module (`transcribe_app/config.py`) that automatically loads the API key from the `.env` file:
     ```python
     import os
     from dotenv import load_dotenv

     # Load variables from the .env file if it exists
     load_dotenv()

     # Retrieve the Hugging Face API token from the environment
     HF_API_TOKEN = os.environ.get("HF_API_TOKEN")

     if HF_API_TOKEN is None:
         print("Warning: HF_API_TOKEN not set. Please add it to your .env file.")
     ```
   - The key is then used when loading datasets. For example, in the benchmarking script:
     ```python
     dataset = load_dataset("united-we-care/United-Syn-Med", split="train", use_auth_token=HF_API_TOKEN)
     ```

7. **For Collaborators:**
   - Each developer should generate their own API token and add it to their local `.env` file following the above instructions.
