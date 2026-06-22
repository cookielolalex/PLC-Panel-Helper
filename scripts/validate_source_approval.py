from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from harness_lib import sha256_file, sha256_json, write_json
from source_guard import SAFE_HUMAN_DECISIONS, csv_rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate human source approvals against source-guard decisions.")
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--human-decisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--approval-csv", type=Path)
    parser.add_argument("--policy-version", default="source_guard_policy_v1")
    args = parser.parse_args()

    decisions = {row["decision_id"]: row for row in csv_rows(args.decisions)}
    human_rows = csv_rows(args.human_decisions)
    errors: list[str] = []
    accepted: list[dict[str, Any]] = []
    reviewed: list[dict[str, Any]] = []

    if not human_rows:
        errors.append("NO_HUMAN_DECISION_ROWS")

    for index, row in enumerate(human_rows, start=2):
        decision_id = row.get("decision_id", "")
        human_decision = (row.get("human_decision", "") or "").strip()
        reviewer = (row.get("reviewer", "") or "").strip()
        source = decisions.get(decision_id)
        if not source:
            errors.append(f"ROW_{index}_UNKNOWN_DECISION_ID")
            continue
        if human_decision not in SAFE_HUMAN_DECISIONS:
            errors.append(f"ROW_{index}_INVALID_OR_BLANK_HUMAN_DECISION")
        if not reviewer:
            errors.append(f"ROW_{index}_MISSING_REVIEWER")
        if row.get("file_sha256", "").upper() != source.get("file_sha256", "").upper():
            errors.append(f"ROW_{index}_FILE_HASH_MISMATCH")
        if row.get("worksheet_fingerprint", "") != source.get("worksheet_fingerprint", ""):
            errors.append(f"ROW_{index}_WORKSHEET_FINGERPRINT_MISMATCH")
        if human_decision == "HUMAN_APPROVED":
            if not source.get("worksheet_fingerprint"):
                errors.append(f"ROW_{index}_APPROVED_WITHOUT_FINGERPRINT")
            if source.get("proposed_decision") in {"AUTO_DENIED", "QUARANTINED", "PARSER_REQUIRED", "SUPERSEDED"}:
                errors.append(f"ROW_{index}_APPROVED_UNAPPROVABLE_STATE_{source.get('proposed_decision')}")
            accepted.append({
                "decision_id": decision_id,
                "human_decision": human_decision,
                "reviewer": reviewer,
                "file_sha256": row.get("file_sha256", ""),
                "worksheet_fingerprint": row.get("worksheet_fingerprint", ""),
                "notes": row.get("notes", ""),
            })
        if human_decision in SAFE_HUMAN_DECISIONS:
            reviewed.append({
                "decision_id": decision_id,
                "human_decision": human_decision,
                "reviewer": reviewer,
                "file_sha256": row.get("file_sha256", ""),
                "worksheet_fingerprint": row.get("worksheet_fingerprint", ""),
                "notes": row.get("notes", ""),
            })

    approval_manifest = {
        "approval_manifest_id": args.output.stem,
        "policy_version": args.policy_version,
        "status": "FAIL" if errors else "PASS",
        "decisions": reviewed,
        "approved_count": len(accepted),
        "errors": errors,
    }
    approval_manifest["approval_manifest_hash"] = sha256_json(approval_manifest)
    write_json(args.output, approval_manifest)
    if args.approval_csv:
        write_csv(args.approval_csv, reviewed, ["decision_id", "human_decision", "reviewer", "file_sha256", "worksheet_fingerprint", "notes"])
    print(approval_manifest["status"])
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

