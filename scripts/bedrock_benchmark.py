#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ripple.aws.bedrock import TrackedBedrockConverseClient
from ripple.evaluation.bedrock_benchmark import DEFAULT_MODELS, evaluate_model, load_cases, render_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Ripple's live Bedrock normalization benchmark.")
    parser.add_argument("--region", default="eu-central-1")
    parser.add_argument("--cases", default="fixtures/bedrock_normalization_cases.json")
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--output", default="docs/BEDROCK_BENCHMARK_LIVE.md")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    results = []
    for model_id in args.models:
        results.append(evaluate_model(
            model_id,
            cases,
            lambda _model_id, region=args.region: TrackedBedrockConverseClient(region_name=region),
        ))
    report = render_markdown(results)
    Path(args.output).write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
