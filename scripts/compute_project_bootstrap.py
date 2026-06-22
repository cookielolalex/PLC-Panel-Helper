from __future__ import annotations

import argparse
import random
from pathlib import Path

from harness_lib import write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute a simple bootstrap CI for project score deltas.")
    parser.add_argument("--scores", nargs="+", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=1000)
    args = parser.parse_args()
    means = []
    for _ in range(args.samples):
        sample = [random.choice(args.scores) for _ in args.scores]
        means.append(sum(sample) / len(sample))
    means.sort()
    lo = means[int(0.025 * len(means))]
    hi = means[int(0.975 * len(means)) - 1]
    write_json(args.output, {"mean": sum(args.scores) / len(args.scores), "ci95": [lo, hi], "samples": args.samples})


if __name__ == "__main__":
    main()

