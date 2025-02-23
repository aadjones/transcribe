from setuptools import find_packages, setup

setup(
    name="transcribe-app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.4.0",  # Modern Qt bindings
        "openai-whisper>=20231117",  # Core transcription functionality
        "transformers>=4.36.0",  # For Hugging Face models
        "torch>=2.1.0",  # Required by transformers
        "jiwer>=3.0.0",  # For WER calculation
        "sounddevice>=0.4.6",  # Audio recording
        "datasets>=2.15.0",  # Required for some HF models
        "soundfile>=0.12.1",  # Audio file handling
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",  # For testing Qt GUI components
            "pytest-mock>=3.11.1",  # For mocking in tests
        ],
    },
    python_requires=">=3.8",  # Ensure Python compatibility
    description="A secure, local audio transcription application with multiple model support",
    author="aadjones",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
