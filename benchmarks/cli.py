#!/usr/bin/env python
import argparse

# Import the benchmark functions from the respective modules.
from .benchmark_local import benchmark_local_pipeline
from .benchmark_medical import benchmark_medical_pipeline, compare_medical_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Benchmarking tool for speech-to-text models."
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Subcommand to run", required=True
    )

    # Subcommand for running a local (general text) benchmark.
    parser_local = subparsers.add_parser(
        "local", help="Run benchmark on local audio files (general text)"
    )
    parser_local.add_argument(
        "--model-name",
        type=str,
        default="tiny",
        help="Model name to use for local benchmark",
    )
    parser_local.add_argument(
        "--max-files", type=int, default=10, help="Maximum number of files to process"
    )
    parser_local.add_argument(
        "--postprocessing", action="store_true", help="Enable postprocessing"
    )

    # Subcommand for running a single-model benchmark on the medical dataset.
    parser_medical = subparsers.add_parser(
        "medical", help="Run benchmark on the medical audio dataset"
    )
    parser_medical.add_argument(
        "--model-name",
        type=str,
        default="tiny",
        help="Model name to use for medical benchmark",
    )
    parser_medical.add_argument(
        "--max-samples",
        type=int,
        default=10,
        help="Maximum number of samples to process",
    )
    parser_medical.add_argument(
        "--postprocessing", action="store_true", help="Enable postprocessing"
    )

    # Subcommand for comparing two models on the medical dataset.
    parser_compare = subparsers.add_parser(
        "compare", help="Compare two models on the medical audio dataset"
    )
    parser_compare.add_argument(
        "--baseline-model", type=str, default="tiny", help="Baseline model name"
    )
    parser_compare.add_argument(
        "--fine-tuned-model",
        type=str,
        default="bqtsio/whisper-large-rad",
        help="Fine-tuned model name",
    )
    parser_compare.add_argument(
        "--max-samples",
        type=int,
        default=10,
        help="Maximum number of samples to process",
    )
    parser_compare.add_argument(
        "--postprocessing", action="store_true", help="Enable postprocessing"
    )

    args = parser.parse_args()

    if args.command == "local":
        print("Running local benchmark...")
        benchmark_local_pipeline(
            model_name=args.model_name,
            use_postprocessing=args.postprocessing,
            max_files=args.max_files,
        )
    elif args.command == "medical":
        print("Running medical benchmark...")
        benchmark_medical_pipeline(
            model_name=args.model_name,
            use_postprocessing=args.postprocessing,
            max_samples=args.max_samples,
        )
    elif args.command == "compare":
        print("Running model vs. model comparison on medical dataset...")
        compare_medical_pipeline(
            baseline_model=args.baseline_model,
            fine_tuned_model=args.fine_tuned_model,
            use_postprocessing=args.postprocessing,
            max_samples=args.max_samples,
        )
    else:
        parser.print_help()
        return

    # Optionally, you can print or process the results here.
    # For example:
    print("Benchmark complete.")


if __name__ == "__main__":
    main()
