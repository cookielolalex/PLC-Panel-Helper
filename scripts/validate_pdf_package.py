from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import TARGET_OUTPUT_TYPES, sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate required PDF package readability.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--run-id", default="RUN")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    from pypdf import PdfReader

    checks = []
    failures = []
    for output_type, pattern in TARGET_OUTPUT_TYPES.items():
        path = args.pdf_dir / pattern.format(project_id=args.project_id)
        row = {"output_type": output_type, "path": str(path), "exists": path.exists(), "pages": 0, "sha256": None}
        if not path.exists():
            failures.append("MISSING_REQUIRED_PDF")
        else:
            try:
                reader = PdfReader(str(path))
                row["pages"] = len(reader.pages)
                row["sha256"] = sha256_file(path)
                if row["pages"] < 1:
                    failures.append("BLANK_CORRUPT_OR_WRONG_PROJECT_PDF")
            except Exception as exc:
                row["error"] = str(exc)
                failures.append("BLANK_CORRUPT_OR_WRONG_PROJECT_PDF")
        checks.append(row)
    write_json(args.output, {
        "run_id": args.run_id,
        "validity": "FAIL" if failures else "PASS",
        "checks": checks,
        "hard_gate_failures": sorted(set(failures)),
        "limitations": []
    })


if __name__ == "__main__":
    main()

