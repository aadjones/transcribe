# benchmark_local.py

import glob
import os

from transcribe_app.transcription import transcribe_audio
from transcribe_app.utils import get_audio_duration

from .benchmark_utils import (  # This returns (ref_transform, hyp_transform)
    benchmark_dataset,
    create_transformations,
)


def local_audio_extractor(file_path):
    # In local benchmark, the dataset is just file paths.
    return file_path


def local_transcript_extractor(file_path):
    base = os.path.splitext(os.path.basename(file_path))[0]
    transcript_path = os.path.join("benchmark_data/transcripts", base + ".txt")
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def benchmark_local_pipeline(model_name="tiny", use_postprocessing=False, max_files=10):
    AUDIO_DIR = "benchmark_data/audio"
    # Do not slice here; pass the full list to the generic function.
    audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))

    # Get the full transformation pipelines for local benchmark.
    ref_transform, hyp_transform = create_transformations()

    dataset = audio_files  # Each sample is a file path.

    return benchmark_dataset(
        dataset=dataset,
        audio_extractor=local_audio_extractor,
        transcript_extractor=local_transcript_extractor,
        model_name=model_name,
        use_postprocessing=use_postprocessing,
        max_samples=max_files,  # Let benchmark_dataset handle shuffling and slicing.
        model_fn=transcribe_audio,
        get_duration_fn=get_audio_duration,
        ref_transform_fn=ref_transform,
        hyp_transform_fn=hyp_transform,
    )
