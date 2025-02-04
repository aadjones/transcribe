import argparse
import glob
import os
import random
from typing import Optional

from datasets import load_dataset
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
from transcribe_app.config import HF_API_TOKEN

from transcribe_app.transcription import transcribe_audio


def run_pipeline(
    audio_file: str, model_name: str = "tiny", use_postprocessing: bool = False
) -> str:
    """
    Runs the speech-to-text pipeline on the given audio file
    using a specified Whisper model.
    """
    import whisper

    print(f"Loading Whisper model '{model_name}' for file: {audio_file}...")
    model = whisper.load_model(model_name)
    print("Transcribing audio...")
    # Access the result directly since we only need the text
    transcription_text = model.transcribe(audio_file)["text"]

    if use_postprocessing:
        # Placeholder for any domain-specific postprocessing.
        pass

    print("Transcription complete.")
    return transcription_text


def load_ground_truth(filename: str) -> str:
    """
    Loads the ground truth transcription from a text file.
    """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def benchmark_pipeline(
    model_name: str = "tiny",
    use_postprocessing: bool = False,
    max_files: Optional[int] = None,
):
    AUDIO_DIR = "benchmark_data/audio"
    TRANSCRIPTS_DIR = "benchmark_data/transcripts"

    audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
    if max_files is not None:
        random.shuffle(audio_files)
        audio_files = audio_files[:max_files]

    total_wer = 0.0
    count = 0
    results = []

    # Create a transformation that first replaces hyphens
    # and other dash‐like characters with spaces.
    # The regex pattern "[-–—]" matches a hyphen (-), en dash (–), and em dash (—).
    hyphen_to_space = SubstituteRegexes({r"[-–—]": " "})

    # Now build a custom transformation chain that:
    # Converts text to lowercase.
    # Replaces hyphens/dashes with spaces.
    # Removes punctuation (all punctuation will be removed, including apostrophes).
    # Collapses multiple spaces.
    # Strips whitespace.
    # Finally reduces each sentence to a list of words.
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

    # The reference starts in all-caps with only apostrophes and no other punctuation.
    # we still apply a similar transformation as to the hypothesis.
    reference_transform = Compose(
        [
            ToLowerCase(),
            RemovePunctuation(),
            RemoveMultipleSpaces(),
            Strip(),
            ReduceToListOfListOfWords(),
        ]
    )

    for audio_path in audio_files:
        base = os.path.splitext(os.path.basename(audio_path))[0]
        transcript_path = os.path.join(TRANSCRIPTS_DIR, base + ".txt")
        if not os.path.exists(transcript_path):
            print(f"Warning: No transcript found for {audio_path}")
            continue

        hypothesis = run_pipeline(
            audio_path, model_name=model_name, use_postprocessing=use_postprocessing
        )
        reference = load_ground_truth(transcript_path)

        # Debug prints
        print(f"File: {base}")
        print("Reference before transformation:", reference)
        print("Hypothesis before transformation:", hypothesis)
        print("Normalized reference:", reference_transform([reference]))
        print("Normalized hypothesis:", hypothesis_transform([hypothesis]))

        try:
            # Wrap each string in a list so that Jiwer processes each as one sentence.
            error_rate = wer(
                [reference],
                [hypothesis],
                truth_transform=reference_transform,
                hypothesis_transform=hypothesis_transform,
            )
        except ValueError as e:
            print(f"Error processing file {base}: {e}")
            continue

        results.append((base, hypothesis, reference, error_rate))
        total_wer += error_rate
        count += 1
        print(f"File: {base}, WER: {error_rate:.3f}")

    if count > 0:
        avg_wer = total_wer / count
        print(f"\nAverage WER over {count} files: {avg_wer:.3f}")
    else:
        print("No files benchmarked.")

    return results


def benchmark_medical_pipeline(model_name: str = "tiny", use_postprocessing: bool = False, max_samples: Optional[int] = 10):
    """
    Benchmark the transcription performance using the pauleyc/radiology_audio_3_iphone_laptop_666_samples 
    dataset from Hugging Face. This dataset contains both audio and corresponding reference transcripts.

    The model_name parameter specifies which Whisper model to use (e.g., "tiny", "small", "large").
    The use_postprocessing flag enables any domain-specific postprocessing.
    
    Note: This version applies minimal text normalization—collapsing multiple spaces, stripping extra whitespace, 
    and tokenizing the text—while preserving case, punctuation, and hyphens. It processes up to 10 samples by default.
    """
    import os
    from datasets import load_dataset

    # Load the dataset using its correct identifier.
    dataset = load_dataset("pauleyc/radiology_audio_3_iphone_laptop_666_samples", split="train")

    # Limit the number of samples for debugging by explicitly converting the range to a list.
    if max_samples is not None:
        dataset = dataset.shuffle(seed=42).select(list(range(max_samples)))
        print(f"Dataset length after limiting: {len(dataset)}")

    total_wer = 0.0
    successful_samples = 0
    results = []

    # Import jiwer and define a minimal transformation.
    from jiwer import Compose, RemoveMultipleSpaces, Strip, wer
    minimal_transform = Compose([
        RemoveMultipleSpaces(),
        Strip(),
        lambda x: x.split() if isinstance(x, str) else x,
    ])

    # Process each sample using enumeration to display sample numbers.
    for i, sample in enumerate(dataset):
        # Retrieve audio information from the "audio" key.
        audio_info = sample.get("audio")
        if not audio_info:
            print(f"Sample {i + 1}: No audio information found, skipping.")
            continue

        # Use the file from the 'path' if it exists on disk; otherwise, create a temporary WAV file.
        if "path" in audio_info and audio_info["path"] and os.path.exists(audio_info["path"]):
            audio_file = audio_info["path"]
        else:
            import tempfile, soundfile as sf
            tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(tmp_file.name, audio_info["array"], audio_info["sampling_rate"])
            audio_file = tmp_file.name

        # Retrieve the reference transcript.
        transcript = sample.get("transcription")
        if not transcript:
            print(f"Sample {i + 1}: No reference transcript found, skipping.")
            continue

        print(f"Processing sample {i + 1}:")
        print("Reference transcript:", transcript)

        # Transcribe the audio using the specified Whisper model.
        from transcribe_app.transcription import transcribe_audio
        hypothesis = transcribe_audio(audio_file, model_name=model_name, use_postprocessing=use_postprocessing)

        try:
            error_rate = wer(
                [transcript],
                [hypothesis],
                truth_transform=minimal_transform,
                hypothesis_transform=minimal_transform,
            )
        except ValueError as e:
            print(f"Error computing WER for sample {i + 1}: {e}")
            continue

        results.append((audio_file, hypothesis, transcript, error_rate))
        total_wer += error_rate
        successful_samples += 1
        print(f"Sample {i + 1}, WER: {error_rate:.3f}\n")

    if successful_samples > 0:
        avg_wer = total_wer / successful_samples
        print(f"\nAverage WER over {successful_samples} samples: {avg_wer:.3f}")
    else:
        print("No samples benchmarked.")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark Whisper transcription models on the United-Syn-Med dataset."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        help="The Whisper model to use (e.g., tiny, base, small, medium, large)"
    )
    parser.add_argument(
        "--postprocessing",
        action="store_true",
        help="Enable domain-specific postprocessing corrections"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit number of samples processed (randomly selected)"
    )
    
    args = parser.parse_args()
    
    benchmark_medical_pipeline(
        model_name=args.model,
        use_postprocessing=args.postprocessing,
        max_samples=args.max_samples
    )
