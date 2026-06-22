from __future__ import annotations

import argparse
from pathlib import Path

from source_guard import (
    read_csv,
    read_json,
    validate_approval,
    validate_bound_inputs,
    write_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate signed source approvals against current source indexes.")
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--file-role-index", type=Path, required=True)
    parser.add_argument("--workbook-sheet-index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    approval = read_json(args.approval)
    file_rows = read_csv(args.file_role_index)
    sheet_rows = read_csv(args.workbook_sheet_index)
    result = validate_approval(approval, file_rows, sheet_rows)
    bound_errors = validate_bound_inputs(approval, args.file_role_index, args.workbook_sheet_index)
    errors = [*bound_errors, *result.errors]
    status = "FAIL" if errors else result.status
    write_json(args.output, {
        "approval_id": approval.get("approval_id", ""),
        "status": status,
        "errors": errors,
        "warnings": result.warnings,
        "allowed_file_ids": result.allowed_file_ids if status == "PASS" else [],
        "allowed_sheet_ids": result.allowed_sheet_ids if status == "PASS" else [],
    })
    if status == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

