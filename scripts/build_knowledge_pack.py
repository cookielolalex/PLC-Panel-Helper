from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Knowledge upload manifest from sanitized production Knowledge files.")
    parser.add_argument("--knowledge-dir", type=Path, default=Path("knowledge/production"))
    parser.add_argument("--output", type=Path, default=Path("gpt-config/KNOWLEDGE_UPLOAD_MANIFEST.md"))
    args = parser.parse_args()
    rows = []
    if args.knowledge_dir.exists():
        for path in sorted(args.knowledge_dir.glob("*")):
            if path.is_file():
                rows.append((path.name, sha256_file(path)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Knowledge Upload Manifest\n\n")
        f.write("Status: BOOTSTRAP_DRAFT\n\n")
        for name, digest in rows:
            f.write(f"- `{name}` `{digest}`\n")


if __name__ == "__main__":
    main()

