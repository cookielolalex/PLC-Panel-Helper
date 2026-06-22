from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = read_json(args.baseline)
    cand = read_json(args.candidate)
    delta = cand["quality_score"] - base["quality_score"]
    write_json(args.output, {
        "comparison_id": "candidate-comparison",
        "project_id": "UNKNOWN",
        "metrics": {
            "candidate_minus_baseline": delta,
            "baseline_validity": base["validity"],
            "candidate_validity": cand["validity"]
        },
        "limitations": ["Phase 0 single-result comparison shell."]
    })


if __name__ == "__main__":
    main()

