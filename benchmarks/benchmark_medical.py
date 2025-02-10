# benchmark_medical.py

import os
import tempfile

import soundfile as sf
from datasets import load_dataset

from transcribe_app.transcription import transcribe_audio
from transcribe_app.utils import get_audio_duration

from .benchmark_utils import (
    benchmark_dataset,
    get_random_subset,
    minimal_transform,
    process_sample,
)


def medical_audio_extractor(sample):
    audio_info = sample.get("audio")
    if (
        audio_info
        and "path" in audio_info
        and audio_info["path"]
        and os.path.exists(audio_info["path"])
    ):
        return audio_info["path"]
    elif audio_info and "array" in audio_info:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(tmp_file.name, audio_info["array"], audio_info["sampling_rate"])
        return tmp_file.name
    return None


def medical_transcript_extractor(sample):
    return sample.get("transcription")


def benchmark_medical_pipeline(
    model_name="tiny", use_postprocessing=False, max_samples=10
):
    dataset = load_dataset(
        "pauleyc/radiology_audio_3_iphone_laptop_666_samples", split="train"
    )
    # For medical benchmark, use the minimal transform for both reference and hypothesis.
    return benchmark_dataset(
        dataset=dataset,
        audio_extractor=medical_audio_extractor,
        transcript_extractor=medical_transcript_extractor,
        model_name=model_name,
        use_postprocessing=use_postprocessing,
        max_samples=max_samples,
        model_fn=transcribe_audio,
        get_duration_fn=get_audio_duration,
        ref_transform_fn=minimal_transform,
        hyp_transform_fn=minimal_transform,
    )


def compare_medical_pipeline(
    baseline_model: str = "tiny",
    fine_tuned_model: str = "bqtsio/whisper-large-rad",
    use_postprocessing: bool = False,
    max_samples: int = 10,
):
    from datasets import load_dataset

    # Load the full dataset.
    dataset = load_dataset(
        "pauleyc/radiology_audio_3_iphone_laptop_666_samples", split="train"
    )
    samples = get_random_subset(dataset, max_samples)

    results = []
    total_baseline_wer = total_ft_wer = 0.0
    total_baseline_time = total_ft_time = 0.0
    total_baseline_rtf = total_ft_rtf = 0.0
    count = 0

    for i, sample in enumerate(samples, 1):
        comp = compare_sample(
            sample, baseline_model, fine_tuned_model, use_postprocessing
        )
        if comp is None:
            continue
        (
            audio_file,
            transcript,
            (baseline_transcript, baseline_time, baseline_rtf, baseline_wer),
            (ft_transcript, ft_time, ft_rtf, ft_wer),
        ) = comp

        print(f"\nProcessing sample {i}:")
        print("Reference transcript:", transcript)
        print(
            f"Baseline - WER: {baseline_wer:.3f}, Time: {baseline_time:.3f}s, RTF: {baseline_rtf:.3f}"
        )
        print(
            f"Fine-tuned - WER: {ft_wer:.3f}, Time: {ft_time:.3f}s, RTF: {ft_rtf:.3f}"
        )

        results.append(
            (
                audio_file,
                baseline_transcript,
                ft_transcript,
                transcript,
                baseline_wer,
                ft_wer,
                baseline_time,
                baseline_rtf,
                ft_time,
                ft_rtf,
            )
        )
        total_baseline_wer += baseline_wer
        total_ft_wer += ft_wer
        total_baseline_time += baseline_time
        total_ft_time += ft_time
        total_baseline_rtf += baseline_rtf
        total_ft_rtf += ft_rtf
        count += 1

    if count > 0:
        print("\n--- Aggregated Results ---")
        print(f"Processed {count} samples.")
        print(f"Average Baseline WER: {total_baseline_wer / count:.3f}")
        print(f"Average Fine-tuned WER: {total_ft_wer / count:.3f}")
        print(
            f"Average Baseline Time: {total_baseline_time / count:.3f}s, Average Baseline RTF: {total_baseline_rtf / count:.3f}"
        )
        print(
            f"Average Fine-tuned Time: {total_ft_time / count:.3f}s, Average Fine-tuned RTF: {total_ft_rtf / count:.3f}"
        )
    else:
        print("No samples processed successfully.")

    return results


def compare_sample(sample, baseline_model, fine_tuned_model, use_postprocessing):
    """
    Process one sample with two models and return a tuple containing:
      - audio_file, transcript,
      - a tuple for the baseline model: (baseline_transcript, baseline_time, baseline_rtf, baseline_wer)
      - a tuple for the fine-tuned model: (ft_transcript, ft_time, ft_rtf, ft_wer)

    Returns None if the sample is missing audio/transcript or if processing fails.
    """
    # Use your already defined extractors.
    audio_file = medical_audio_extractor(sample)
    transcript = medical_transcript_extractor(sample)
    if not audio_file or not transcript:
        print("Sample missing audio or transcript; skipping.")
        return None

    baseline_result = process_sample(
        audio_file,
        transcript,
        transcribe_audio,
        baseline_model,
        use_postprocessing,
        get_audio_duration,
        minimal_transform,
        minimal_transform,
    )
    ft_result = process_sample(
        audio_file,
        transcript,
        transcribe_audio,
        fine_tuned_model,
        use_postprocessing,
        get_audio_duration,
        minimal_transform,
        minimal_transform,
    )
    if baseline_result is None or ft_result is None:
        return None

    return (audio_file, transcript, baseline_result, ft_result)
