import argparse
import glob
import os

from jiwer import wer


# Placeholder for any domain-specific postprocessing
def apply__corrections(transcription: str) -> str:
    # TODO: Add custom postprocessing rules for jargon.
    return transcription


def run_pipeline(
    audio_file: str, model_name: str = "tiny", use_postprocessing: bool = False
) -> str:
    """
    Runs the speech-to-text pipeline on the given audio file
    using a specified Whisper model.

    Parameters:
        audio_file (str): Path to the input audio file.
        model_name (str): Name of the Whisper model to load
        (e.g., "tiny", "base", "small", "medium", "large").
        use_postprocessing (bool): Whether to apply domain-specific postprocessing.

    Returns:
        str: The transcribed text.
    """
    # Defer importing whisper until this function is called.
    import whisper

    print(f"Loading Whisper model '{model_name}' for file: {audio_file}...")
    model = whisper.load_model(model_name)
    print("Transcribing audio...")
    result = model.transcribe(audio_file)
    transcription_text = result.get("text", "")

    if use_postprocessing:
        transcription_text = apply__corrections(transcription_text)

    print("Transcription complete.")
    return transcription_text


def load_ground_truth(filename: str) -> str:
    """
    Loads the ground truth transcription from a text file.

    Parameters:
        filename (str): Path to the transcript file.

    Returns:
        str: The ground truth transcription.
    """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def benchmark_pipeline(model_name: str = "tiny", use_postprocessing: bool = False):
    """
    Runs the transcription pipeline on all benchmark audio files and computes WER.

    Parameters:
        model_name (str): Name of the Whisper model to use.
        use_postprocessing (bool): Whether to enable postprocessing.

    Returns:
        list: A list of results for each file (base name, hypothesis, reference, WER).
    """
    AUDIO_DIR = "benchmark_data/audio"
    TRANSCRIPTS_DIR = "benchmark_data/transcripts"

    audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
    total_wer = 0.0
    count = 0
    results = []

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
        error_rate = wer(reference, hypothesis)
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
        help="Enable radiology-specific postprocessing corrections",
    )
    args = parser.parse_args()

    benchmark_pipeline(model_name=args.model, use_postprocessing=args.postprocessing)
