from __future__ import annotations

import argparse
from pathlib import Path

from source_guard import (
    build_sanitized_bundle_manifest,
    read_csv,
    read_json,
    validate_approval,
    validate_bound_inputs,
    verify_bundle_manifest,
    write_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a sanitized generator bundle from validated source approvals.")
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--file-role-index", type=Path, required=True)
    parser.add_argument("--workbook-sheet-index", type=Path, required=True)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--run-id", default="RUN")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--copy-files", action="store_true")
    args = parser.parse_args()

    approval = read_json(args.approval)
    file_rows = read_csv(args.file_role_index)
    sheet_rows = read_csv(args.workbook_sheet_index)
    guard_result = validate_approval(approval, file_rows, sheet_rows)
    bound_errors = validate_bound_inputs(approval, args.file_role_index, args.workbook_sheet_index)
    if bound_errors or guard_result.status != "PASS":
        write_json(args.output_manifest, {
            "manifest_id": f"sanitized-generator-input-{args.run_id}",
            "project_id": args.project_id,
            "run_id": args.run_id,
            "status": "FAIL" if bound_errors or guard_result.errors else "HUMAN_REVIEW_REQUIRED",
            "source_approval_id": approval.get("approval_id", ""),
            "bundle_root": str(args.bundle_dir),
            "allowed_files": [],
            "allowed_sheets": [],
            "excluded": [],
            "verification": {"status": "FAIL", "errors": [*bound_errors, *guard_result.errors]},
        })
        raise SystemExit(1)

    manifest = build_sanitized_bundle_manifest(
        approval=approval,
        guard_result=guard_result,
        file_rows=file_rows,
        sheet_rows=sheet_rows,
        bundle_root=args.bundle_dir,
        run_id=args.run_id,
        project_id=args.project_id,
        copy_files=args.copy_files,
    )
    if args.copy_files:
        verification_errors = verify_bundle_manifest(manifest, args.bundle_dir)
        manifest["verification"] = {
            "status": "FAIL" if verification_errors else "PASS",
            "errors": verification_errors,
        }
    write_json(args.output_manifest, manifest)
    if manifest["status"] != "PASS" or manifest["verification"]["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

