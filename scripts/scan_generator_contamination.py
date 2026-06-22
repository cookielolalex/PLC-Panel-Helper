from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import FORBIDDEN_TERMS, detect_forbidden_text, read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan a generator bundle for forbidden labels and sentinel content.")
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    hits = []
    manifest_text = args.manifest.read_text(encoding="utf-8")
    for term in detect_forbidden_text(manifest_text):
        hits.append({"path": str(args.manifest), "term": term, "location": "manifest"})
    if args.bundle_dir.exists():
        for path in args.bundle_dir.rglob("*"):
            rel = str(path.relative_to(args.bundle_dir))
            for term in detect_forbidden_text(rel):
                hits.append({"path": rel, "term": term, "location": "path"})
            if path.is_file() and path.stat().st_size < 1024 * 1024:
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                for term in detect_forbidden_text(text):
                    hits.append({"path": rel, "term": term, "location": "content"})
    write_json(args.output, {
        "scan_id": "generator-contamination-scan",
        "status": "FAIL" if hits else "PASS",
        "forbidden_terms": FORBIDDEN_TERMS,
        "hits": hits
    })


if __name__ == "__main__":
    main()

