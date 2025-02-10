# benchmark_utils.py

import random
import time

from jiwer import (
    Compose,
    ReduceToListOfListOfWords,
    RemoveMultipleSpaces,
    RemovePunctuation,
    Strip,
    SubstituteRegexes,
    ToLowerCase,
)


def load_ground_truth(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def create_transformations() -> tuple:
    """
    Create and return the reference and hypothesis transformation pipelines.
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


def timing_decorator(func):
    """Optional decorator to measure execution time."""

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.3f}s")
        return result

    return wrapper


def process_sample(
    audio_file: str,
    transcript: str,
    model_fn,  # Callable: (audio_file, model_name, use_postprocessing) -> transcription
    model_name: str,
    use_postprocessing: bool,
    get_duration_fn,  # Callable to get audio duration (audio_file -> duration)
    ref_transform_fn,  # Transformation function (expects a list of strings)
    hyp_transform_fn,  # Transformation function (expects a list of strings)
):
    duration = get_duration_fn(audio_file)
    if duration <= 0:
        print(f"Audio duration for {audio_file} is non-positive.")
        return None

    import time

    start_time = time.perf_counter()
    hypothesis = model_fn(
        audio_file, model_name=model_name, use_postprocessing=use_postprocessing
    )
    end_time = time.perf_counter()
    processing_time = end_time - start_time
    rtf = processing_time / duration

    try:
        # Use the minimal transformation exactly as in your original code.
        # It takes a list of strings and returns a list-of-lists-of-words.
        ref_words = ref_transform_fn([transcript])[0]
        hyp_words = hyp_transform_fn([hypothesis])[0]
        from jiwer import wer

        error_rate = wer([ref_words], [hyp_words])
    except Exception as e:
        print(f"Error computing WER for {audio_file}: {e}")
        return None

    return hypothesis, processing_time, rtf, error_rate


def get_random_subset(dataset, max_samples):
    """
    Returns a random subset of the dataset (as a list) containing at most max_samples items.
    """
    samples = list(dataset)
    if max_samples is not None and len(samples) > max_samples:
        # Ensure variability by seeding from current time (or just let Python do it)
        random.seed(time.time())
        random.shuffle(samples)
        samples = samples[:max_samples]
    return samples


def benchmark_dataset(
    dataset,
    audio_extractor,  # Function: sample -> audio_file path (or temporary file)
    transcript_extractor,  # Function: sample -> transcript (string)
    model_name: str,
    use_postprocessing: bool,
    max_samples: int,
    model_fn,  # The transcription function (e.g., transcribe_audio)
    get_duration_fn,
    ref_transform_fn,
    hyp_transform_fn,
):
    total_wer = 0.0
    total_rtf = 0.0
    successful = 0
    results = []
    samples = get_random_subset(dataset, max_samples)
    for i, sample in enumerate(samples):
        audio_file = audio_extractor(sample)
        transcript = transcript_extractor(sample)
        if not audio_file or not transcript:
            print(f"Sample {i+1}: Missing audio or transcript, skipping.")
            continue

        print(f"\nProcessing sample {i+1}:")
        print("Reference transcript:", transcript)

        outcome = process_sample(
            audio_file,
            transcript,
            model_fn,
            model_name,
            use_postprocessing,
            get_duration_fn,
            ref_transform_fn,
            hyp_transform_fn,
        )
        if outcome is None:
            continue

        hypothesis, processing_time, rtf, error_rate = outcome
        results.append(
            (audio_file, hypothesis, transcript, error_rate, processing_time, rtf)
        )
        total_wer += error_rate
        total_rtf += rtf
        successful += 1
        print(
            f"Sample {i+1}, WER: {error_rate:.3f}, Processing Time: {processing_time:.3f}s, RTF: {rtf:.3f}"
        )

    if successful > 0:
        print(f"\nAverage WER over {successful} samples: {total_wer/successful:.3f}")
        print(f"Average RTF over {successful} samples: {total_rtf/successful:.3f}")
    else:
        print("No samples benchmarked.")

    return results
