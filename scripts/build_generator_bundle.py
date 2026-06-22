from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import copy_allowed_file, detect_forbidden_text, read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a positive generator bundle from approved manifest rows.")
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--sheet-adjudication", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--run-id", default="RUN")
    parser.add_argument("--project-id", default="PROJECT")
    args = parser.parse_args()

    source_manifest = read_json(args.source_manifest)
    sheet_adjudication = read_json(args.sheet_adjudication)
    allowed_files = []
    excluded = []
    copied = []
    for file_row in source_manifest.get("files", []):
        text = " ".join(str(file_row.get(k, "")) for k in ("relative_path", "file_name", "primary_role"))
        if file_row.get("generator_eligibility") == "ALLOWED" and not detect_forbidden_text(text):
            allowed_files.append(file_row["file_id"])
            original_path = file_row.get("absolute_path")
            if original_path and Path(original_path).exists():
                copied.append(copy_allowed_file(Path(original_path), args.bundle_dir / "evidence"))
        else:
            excluded.append({"id": file_row.get("file_id"), "reason": "not_positive_allowed_or_forbidden_label"})

    allowed_sheets = [
        row["sheet_id"]
        for row in sheet_adjudication.get("worksheets", [])
        if row.get("generator_eligibility") == "ALLOWED" and row.get("stale_template_status") not in {"STALE_TEMPLATE_SHEET"}
    ]
    for row in sheet_adjudication.get("worksheets", []):
        if row.get("sheet_id") not in allowed_sheets:
            excluded.append({"id": row.get("sheet_id"), "reason": "worksheet_not_approved_or_stale"})

    manifest = {
        "manifest_id": f"generator-input-{args.run_id}",
        "project_id": args.project_id,
        "run_id": args.run_id,
        "allowed_files": allowed_files,
        "allowed_sheets": allowed_sheets,
        "excluded": excluded,
        "copied_files": copied,
        "contamination_scan": {"status": "NOT_RUN"},
        "symlink_junction_scan": {"status": "NOT_IMPLEMENTED_PHASE0"},
        "environment_variable_allowlist": [],
        "generator_eligibility": "ALLOWED" if allowed_files or allowed_sheets else "HUMAN_REVIEW_REQUIRED"
    }
    write_json(args.output_manifest, manifest)


if __name__ == "__main__":
    main()

