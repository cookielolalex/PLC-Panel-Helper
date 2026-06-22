from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import classify_path, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify files by bootstrap source-role rules.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for raw in args.paths:
        info = classify_path(raw)
        info["path"] = raw
        rows.append(info)
    data = {"classifier": "bootstrap_path_classifier_v0", "files": rows}
    if args.output:
        write_json(args.output, data)
    else:
        print(data)


if __name__ == "__main__":
    main()

