# tests/test_benchmark_pipeline.py


def test_benchmark_local_pipeline_returns_list(monkeypatch, tmp_path):
    # Monkey-patch transcribe_audio in benchmarks.benchmark_local to return a fixed string.
    from transcribe_app import transcription

    monkeypatch.setattr(
        transcription,
        "transcribe_audio",
        lambda audio_file, model_name, use_postprocessing=False: "dummy transcription",
    )

    from benchmarks.benchmark_local import benchmark_local_pipeline

    results = benchmark_local_pipeline(
        model_name="tiny", use_postprocessing=False, max_files=2
    )
    # Check that results is a list and that each result tuple has the expected number of elements.
    assert isinstance(results, list), "Benchmark pipeline should return a list."
    if results:
        # For example, each result tuple might have 6 elements.
        for item in results:
            assert (
                len(item) == 6
            ), "Each benchmark result should be a tuple of 6 elements (audio_file, hypothesis, transcript, WER, time, RTF)."
