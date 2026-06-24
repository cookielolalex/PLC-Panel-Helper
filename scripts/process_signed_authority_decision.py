from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from harness_lib import read_json, sha256_file, write_json
from prepare_signed_authority_intake import prepare_intake
from validate_signed_authority_decision import validate_decision


def submission_status(intake: dict[str, Any]) -> str:
    if intake["status"] != "PASS":
        return "SIGNED_AUTHORITY_DECISION_INVALID_FAIL_CLOSED"
    if intake["reject_all_authority_lanes"]:
        return "SIGNED_AUTHORITY_REJECT_ALL_INTAKE_READY"
    return "SIGNED_AUTHORITY_DECISION_VALIDATED_INTAKE_READY"


def process_decision(*, decision_path: Path, output_dir: Path) -> dict[str, Any]:
    decision = read_json(decision_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    validation = validate_decision(decision, decision_path=decision_path)
    validation_path = output_dir / "validation.json"
    write_json(validation_path, validation)

    intake = prepare_intake(decision, decision_path=decision_path)
    intake_path = output_dir / "intake.json"
    write_json(intake_path, intake)

    summary = {
        "schema_version": "sheetmetal-v1.signed_authority_decision_submission.v1",
        "status": submission_status(intake),
        "decision_path": str(decision_path),
        "decision_sha256_canonical": validation["decision_sha256_canonical"],
        "validation_path": str(validation_path),
        "validation_sha256": sha256_file(validation_path),
        "intake_path": str(intake_path),
        "intake_sha256": sha256_file(intake_path),
        "validation_status": validation["status"],
        "intake_status": intake["status"],
        "selected_choice_ids": intake["selected_choice_ids"],
        "selected_authority_lanes": intake["selected_authority_lanes"],
        "reject_all_authority_lanes": intake["reject_all_authority_lanes"],
        "implementation_authorized": False,
        "implementation_can_start": False,
        "customer_pdf_dxf_dwg_generation_authorized": False,
        "production_approval_declared": False,
        "next_action": intake["next_action"],
        "required_follow_up": intake["required_follow_up"],
        "validation_errors": validation["errors"],
        "hash_checks": validation["hash_checks"],
    }
    write_json(output_dir / "submission_summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Process a signed SMV1 source/rule authority decision into validation, intake, and summary artifacts.")
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    summary = process_decision(decision_path=args.decision, output_dir=args.output_dir)
    print(json.dumps({"status": summary["status"], "next_action": summary["next_action"], "validation_errors": summary["validation_errors"]}, ensure_ascii=False))
    if summary["validation_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
