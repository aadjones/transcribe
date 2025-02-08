import argparse
import glob
import os
import random
import time
from typing import List, Optional, Tuple
from itertools import islice

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


def benchmark_medical_pipeline(model_name: str = "tiny", use_postprocessing: bool = False, max_samples: Optional[int] = 10):
    """
    Benchmark the transcription performance using the pauleyc/radiology_audio_3_iphone_laptop_666_samples 
    dataset from Hugging Face. This dataset contains both audio and corresponding reference transcripts.
    
    For debugging purposes, this version loads only max_samples (default 10) entries.
    """
    import os
    from datasets import load_dataset
    from jiwer import Compose, RemoveMultipleSpaces, Strip, wer
    from transcribe_app.transcription import transcribe_audio
    import tempfile, soundfile as sf

    # Load the entire dataset and convert it to a list
    print("Loading dataset...")
    dataset = load_dataset("pauleyc/radiology_audio_3_iphone_laptop_666_samples", split="train")
    dataset = list(dataset)
    print(f"Dataset originally contains {len(dataset)} samples.")

    # Slice the dataset to only keep the first max_samples entries
    if max_samples is not None:
        dataset = dataset[:max_samples]
        print(f"Limiting to {max_samples} samples for debugging.")
    else:
        print("max_samples is None; processing the entire dataset.")

    print(f"Processing {len(dataset)} samples.\n")

    total_wer = 0.0
    successful_samples = 0
    results = []

    # Minimal transformation: collapse spaces, strip whitespace, then split into words.
    minimal_transform = Compose([
        RemoveMultipleSpaces(),
        Strip(),
        lambda x: x.split() if isinstance(x, str) else x,  # Only split if x is a string
    ])

    # Process each sample
    for i, sample in enumerate(dataset):
        audio_info = sample.get("audio")
        if not audio_info:
            print(f"Sample {i + 1}: No audio information found, skipping.")
            continue

        # Prefer using the file if its path exists; otherwise, create a temporary WAV file
        if "path" in audio_info and audio_info["path"] and os.path.exists(audio_info["path"]):
            audio_file = audio_info["path"]
        else:
            tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(tmp_file.name, audio_info["array"], audio_info["sampling_rate"])
            audio_file = tmp_file.name

        transcript = sample.get("transcription")
        if not transcript:
            print(f"Sample {i + 1}: No reference transcript found, skipping.")
            continue

        print(f"\nProcessing sample {i + 1} of {len(dataset)}:")
        print("Reference transcript:", transcript)

        # Transcribe using your function (which now accepts model_name and use_postprocessing)
        hypothesis = transcribe_audio(audio_file, model_name=model_name, use_postprocessing=use_postprocessing)
        print("Generated transcript:", hypothesis)

        try:
            # Use the transformation so that both texts become lists of words.
            ref_words = minimal_transform([transcript])[0]
            hyp_words = minimal_transform([hypothesis])[0]

            if not ref_words or not hyp_words:
                print(f"Error: Empty word list after transformation for sample {i + 1}")
                continue

            error_rate = wer([ref_words], [hyp_words])
        except Exception as e:
            print(f"Error computing WER for sample {i + 1}: {str(e)}")
            continue

        results.append((audio_file, hypothesis, transcript, error_rate))
        total_wer += error_rate
        successful_samples += 1
        print(f"Sample {i + 1}, WER: {error_rate:.3f}")

    if successful_samples > 0:
        avg_wer = total_wer / successful_samples
        print(f"\nAverage WER over {successful_samples} samples: {avg_wer:.3f}")
    else:
        print("No samples benchmarked.")

    return results


def compare_medical_pipeline(
    baseline_model: str = "tiny",
    fine_tuned_model: str = "bqtsio/whisper-large-rad",
    use_postprocessing: bool = False,
    max_samples: int = 10
):
    """
    Compare transcription performance of two models on the radiology audio dataset.

    This function runs:
      - A baseline transcription using a standard Whisper model (e.g., "tiny", "large")
      - A second transcription using a fine-tuned version (e.g., "bqtsio/whisper-large-rad")
    
    The same audio sample from the dataset is passed to both models, and their outputs are compared
    against the reference transcript using Word Error Rate (WER).

    Parameters:
      baseline_model (str): The baseline Whisper model to use (e.g., "tiny", "large").
      fine_tuned_model (str): The fine-tuned Whisper model to use (default: "bqtsio/whisper-large-rad").
      use_postprocessing (bool): Enable domain-specific postprocessing corrections.
      max_samples (int): Limit the number of samples processed (for debugging; default: 10).

    Returns:
      A list of tuples for each processed sample:
         (audio_file, baseline_transcript, fine_tuned_transcript, reference, baseline_wer, fine_tuned_wer)
    
    How it works:
      1. Loads the radiology audio dataset from the Hugging Face Hub.
      2. Converts the dataset to a list and slices it to only the first 'max_samples' items.
      3. For each sample:
         - Checks for the "audio" key and loads the corresponding audio file.
         - Retrieves the reference transcript.
         - Transcribes the audio using both the baseline and the fine-tuned models.
         - Applies minimal text normalization (collapsing spaces, stripping whitespace, and splitting into words).
         - Computes the WER for both transcriptions.
         - Prints the results.
    """
    import os
    import tempfile, soundfile as sf
    from datasets import load_dataset
    from jiwer import Compose, RemoveMultipleSpaces, Strip, wer
    from transcribe_app.transcription import transcribe_audio

    # Load radiology audio dataset and limit samples for debugging.
    print("Loading dataset...")
    dataset = load_dataset("pauleyc/radiology_audio_3_iphone_laptop_666_samples", split="train")
    dataset = list(dataset)[:max_samples]  # Only keep the first max_samples samples.
    print(f"Processing {len(dataset)} samples.\n")

    # Define a minimal text normalization transformation:
    # - Remove extra spaces, strip whitespace, then split into words.
    minimal_transform = Compose([
        RemoveMultipleSpaces(),
        Strip(),
        lambda x: x.split() if isinstance(x, str) else x,
    ])

    results = []

    # Iterate over the dataset samples.
    for i, sample in enumerate(dataset):
        # Retrieve the audio data.
        audio_info = sample.get("audio")
        if not audio_info:
            print(f"Sample {i+1}: No audio information available. Skipping.")
            continue

        # Use the provided file path if available; otherwise, create a temporary file.
        if "path" in audio_info and audio_info["path"] and os.path.exists(audio_info["path"]):
            audio_file = audio_info["path"]
        else:
            tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(tmp_file.name, audio_info["array"], audio_info["sampling_rate"])
            audio_file = tmp_file.name

        # Retrieve the reference transcript.
        transcript = sample.get("transcription")
        if not transcript:
            print(f"Sample {i+1}: No reference transcript found. Skipping.")
            continue

        print(f"\nProcessing sample {i+1}:")
        print("Reference transcript:", transcript)

        # Generate transcriptions using both models.
        baseline_transcript = transcribe_audio(
            audio_file,
            model_name=baseline_model,
            use_postprocessing=use_postprocessing
        )
        print("Baseline transcript:", baseline_transcript)

        fine_tuned_transcript = transcribe_audio(
            audio_file,
            model_name=fine_tuned_model,
            use_postprocessing=use_postprocessing
        )
        print("Fine-tuned transcript:", fine_tuned_transcript)

        try:
            # Apply text normalization to both the transcripts.
            ref_words = minimal_transform([transcript])[0]
            baseline_words = minimal_transform([baseline_transcript])[0]
            fine_tuned_words = minimal_transform([fine_tuned_transcript])[0]

            # Calculate the Word Error Rate (WER).
            baseline_wer = wer([ref_words], [baseline_words])
            fine_tuned_wer = wer([ref_words], [fine_tuned_words])
        except Exception as e:
            print(f"Error computing WER for sample {i+1}: {e}")
            continue

        print(f"Sample {i+1} - Baseline WER: {baseline_wer:.3f}, Fine-tuned WER: {fine_tuned_wer:.3f}")
        results.append((audio_file, baseline_transcript, fine_tuned_transcript, transcript, baseline_wer, fine_tuned_wer))

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare transcription performance on medical audio using baseline and fine-tuned Whisper models."
    )
    parser.add_argument(
        "--baseline-model",
        type=str,
        default="tiny",
        help="The baseline Whisper model to use (e.g., tiny, small, large)."
    )
    parser.add_argument(
        "--fine-tuned-model",
        type=str,
        default="bqtsio/whisper-large-rad",
        help="The fine-tuned Whisper model to use (e.g., bqtsio/whisper-large-rad)."
    )
    parser.add_argument(
        "--postprocessing",
        action="store_true",
        help="Enable domain-specific postprocessing corrections."
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=10,
        help="Limit number of samples processed (for debugging)."
    )

    args = parser.parse_args()

    # Run the comparison benchmark.
    compare_medical_pipeline(
        baseline_model=args.baseline_model,
        fine_tuned_model=args.fine_tuned_model,
        use_postprocessing=args.postprocessing,
        max_files=args.max_files,
    )


def get_transformations():
    """
    Returns the reference and hypothesis transformations used for WER computation.
    The hypothesis transformation replaces hyphens with spaces before removing punctuation,
    whereas the reference transformation does not apply the hyphen replacement.
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
