# tests/test_cli.py

import sys

from benchmarks.cli import main


def test_cli_local(monkeypatch, capsys):
    # Simulate CLI call for local benchmark.
    monkeypatch.setattr(
        sys, "argv", ["cli.py", "local", "--model-name", "tiny", "--max-files", "1"]
    )

    # Optionally, monkey-patch benchmark_local_pipeline to return a dummy result
    from benchmarks.benchmark_local import benchmark_local_pipeline

    monkeypatch.setattr(
        benchmark_local_pipeline, "__call__", lambda *args, **kwargs: []
    )

    # Run the CLI main function.
    main()

    captured = capsys.readouterr().out
    assert (
        "Running local benchmark..." in captured
    ), "CLI should indicate that the local benchmark is running."


def test_cli_medical(monkeypatch, capsys):
    # Simulate CLI call for medical benchmark.
    monkeypatch.setattr(
        sys, "argv", ["cli.py", "medical", "--model-name", "tiny", "--max-samples", "1"]
    )

    from benchmarks.benchmark_medical import benchmark_medical_pipeline

    monkeypatch.setattr(
        benchmark_medical_pipeline, "__call__", lambda *args, **kwargs: []
    )

    main()
    captured = capsys.readouterr().out
    assert (
        "Running medical benchmark..." in captured
    ), "CLI should indicate that the medical benchmark is running."
