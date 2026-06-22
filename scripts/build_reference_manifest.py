from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sheet-level reference manifest from a reference vault.")
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sheets = []
    if args.reference_dir.exists():
        for idx, path in enumerate(args.reference_dir.glob("*.pdf"), start=1):
            sheets.append({
                "project_id": args.project_id,
                "output_type": "unknown",
                "panel_id": None,
                "sheet_id": f"REF-SHEET-{idx:03d}",
                "source_pdf": str(path),
                "page": 1,
                "drawing_number": None,
                "revision": None,
                "effective": False,
                "supersedes": [],
                "superseded_by": [],
                "file_hash": sha256_file(path),
                "adjudication_status": "HUMAN_REVIEW_REQUIRED"
            })
    write_json(args.output, {
        "manifest_id": "reference-sheet-manifest",
        "project_id": args.project_id,
        "status": "EMPTY_OR_PENDING_REVIEW" if not sheets else "PENDING_REVIEW",
        "sheets": sheets
    })


if __name__ == "__main__":
    main()

