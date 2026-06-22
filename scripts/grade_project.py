from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute deterministic grading shell from validation and profile.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--profile", type=Path, default=Path("evals/grading_profiles/plc_layout_v1.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    validation = read_json(args.validation)
    profile = read_json(args.profile)
    weights = profile["weights"]
    failures = validation.get("hard_gate_failures", [])
    validity = "FAIL" if failures or validation.get("validity") == "FAIL" else "PASS"
    if validity == "FAIL":
        dimension_scores = {k: 0 for k in weights}
        quality = 0.0
        coverage = 0.0
        confidence = "LOW"
    else:
        dimension_scores = {k: float(v) for k, v in weights.items()}
        quality = float(sum(dimension_scores.values()))
        coverage = 100.0
        confidence = "HIGH"
    write_json(args.output, {
        "run_id": args.run_id,
        "validity": validity,
        "quality_score": quality,
        "scorable_coverage": coverage,
        "confidence": confidence,
        "critical_findings": len(failures),
        "high_findings": 0,
        "dimension_scores": dimension_scores,
        "hard_gate_failures": failures
    })


if __name__ == "__main__":
    main()

