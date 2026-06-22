from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash files in a candidate release directory.")
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    files = []
    for path in sorted(args.release_dir.rglob("*")):
        if path.is_file():
            files.append({"path": str(path.relative_to(args.release_dir)), "sha256": sha256_file(path)})
    write_json(args.output, {"release_dir": str(args.release_dir), "files": files, "status": "PASS"})


if __name__ == "__main__":
    main()

