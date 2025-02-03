import argparse
import glob
import os
import random
import time
from typing import List, Optional, Tuple

from jiwer import (
    Compose,
    ReduceToListOfListOfWords,
    RemoveMultipleSpaces,
    RemovePunctuation,
    Strip,
    SubstituteRegexes,
    ToLowerCase,
    wer,
)

from transcribe_app.utils import get_audio_duration


def run_pipeline(
    audio_file: str, model_name: str = "tiny", use_postprocessing: bool = False
) -> str:
    import whisper

    print(f"Loading Whisper model '{model_name}' for file: {audio_file}...")
    model = whisper.load_model(model_name)
    print("Transcribing audio...")
    result = model.transcribe(audio_file)
    transcription_text = result.get("text", "")
    if use_postprocessing:
        # Placeholder for postprocessing.
        pass
    print("Transcription complete.")
    return transcription_text


def load_ground_truth(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def create_transformations() -> Tuple[Compose, Compose]:
    """
    Create and return the reference and hypothesis transformation pipelines.
    The hypothesis transformation replaces hyphens with spaces first.
    """
    hyphen_to_space = SubstituteRegexes({r"[-–—]": " "})

    hypothesis_transform = Compose(
        [
            ToLowerCase(),
            hyphen_to_space,
            RemovePunctuation(),
            RemoveMultipleSpaces(),
            Strip(),
            ReduceToListOfListOfWords(),
        ]
    )

    reference_transform = Compose(
        [
            ToLowerCase(),
            RemovePunctuation(),
            RemoveMultipleSpaces(),
            Strip(),
            ReduceToListOfListOfWords(),
        ]
    )

    return reference_transform, hypothesis_transform


def process_file(
    audio_path: str,
    transcript_path: str,
    model_name: str,
    use_postprocessing: bool,
    ref_transform: Compose,
    hyp_transform: Compose,
) -> Optional[Tuple[str, str, str, float, float, float]]:
    """
    Process a single file: compute transcription, processing time, RTF, and WER.
    Returns a tuple: (base, hypothesis, reference, wer, processing_time, rtf).
    If any error occurs, returns None.
    """
    base = os.path.splitext(os.path.basename(audio_path))[0]
    # Get audio duration
    duration = get_audio_duration(audio_path)
    if duration <= 0:
        print(f"Warning: Audio duration for {audio_path} is non-positive.")
        return None

    start_time = time.perf_counter()
    hypothesis = run_pipeline(
        audio_path, model_name=model_name, use_postprocessing=use_postprocessing
    )
    end_time = time.perf_counter()
    processing_time = end_time - start_time

    rtf = processing_time / duration

    reference = load_ground_truth(transcript_path)

    # Debug prints:
    print(f"File: {base}")
    print("Reference before transformation:", reference)
    print("Hypothesis before transformation:", hypothesis)
    print("Normalized reference:", ref_transform([reference]))
    print("Normalized hypothesis:", hyp_transform([hypothesis]))

    try:
        error_rate = wer(
            [reference],
            [hypothesis],
            truth_transform=ref_transform,
            hypothesis_transform=hyp_transform,
        )
    except ValueError as e:
        print(f"Error processing file {base}: {e}")
        return None

    return (base, hypothesis, reference, error_rate, processing_time, rtf)


def benchmark_pipeline(
    model_name: str = "tiny",
    use_postprocessing: bool = False,
    max_files: Optional[int] = None,
) -> List[Tuple[str, str, str, float, float, float]]:
    AUDIO_DIR = "benchmark_data/audio"
    TRANSCRIPTS_DIR = "benchmark_data/transcripts"

    audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
    if max_files is not None:
        random.shuffle(audio_files)
        audio_files = audio_files[:max_files]

    total_wer = 0.0
    total_rtf = 0.0
    count = 0
    results = []

    ref_transform, hyp_transform = create_transformations()

    for audio_path in audio_files:
        base = os.path.splitext(os.path.basename(audio_path))[0]
        transcript_path = os.path.join(TRANSCRIPTS_DIR, base + ".txt")
        if not os.path.exists(transcript_path):
            print(f"Warning: No transcript found for {audio_path}")
            continue

        processed = process_file(
            audio_path,
            transcript_path,
            model_name,
            use_postprocessing,
            ref_transform,
            hyp_transform,
        )
        if processed is None:
            continue

        base, hypothesis, reference, error_rate, processing_time, rtf = processed
        results.append(processed)
        total_wer += error_rate
        total_rtf += rtf
        count += 1
        print(
            f"File: {base}, WER: {error_rate:.3f}, Processing Time: {processing_time:.3f}s, RTF: {rtf:.3f}"
        )

    if count > 0:
        avg_wer = total_wer / count
        avg_rtf = total_rtf / count
        print("\nBenchmark Summary:")
        print("===================")
        print(f"Total Files Processed: {count}")
        print(f"Average WER (Word Error Rate): {avg_wer:.3f}")
        print(
            "  -> WER measures the fraction of words that are substituted, inserted, or deleted compared to the reference."
        )
        print(f"Average RTF (Real-Time Factor): {avg_rtf:.3f}")
        print(
            "  -> RTF is the ratio of the transcription processing time to the audio duration."
        )
        print(
            "     RTF < 1 indicates faster-than-real-time processing, while RTF > 1 indicates slower processing."
        )
    else:
        print("No files benchmarked.")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark Whisper transcription models."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        help="The Whisper model to use (e.g., tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--postprocessing",
        action="store_true",
        help="Enable domain-specific postprocessing corrections",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Limit the number of files processed (randomly selected)",
    )
    args = parser.parse_args()

    benchmark_pipeline(
        model_name=args.model,
        use_postprocessing=args.postprocessing,
        max_files=args.max_files,
    )
