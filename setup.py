from setuptools import find_packages, setup

setup(
    name="transcribe-app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "whisper",
        "jiwer",
        "sounddevice",
        "datasets",
        "soundfile",
    ],
)
