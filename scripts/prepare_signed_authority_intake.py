from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from harness_lib import read_json, write_json
from validate_signed_authority_decision import validate_decision


def prepare_intake(decision: dict[str, Any], *, decision_path: Path) -> dict[str, Any]:
    validation = validate_decision(decision, decision_path=decision_path)
    status = validation["status"]

    if status != "PASS":
        next_action = "WAIT_FOR_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION"
        required_follow_up = [
            "provide_schema_valid_signed_authority_decision",
            "rerun_scripts_validate_signed_authority_decision_py",
        ]
    elif validation["reject_all_authority_lanes"]:
        next_action = "ENTER_TERMINAL_CANDIDATE_REVIEW"
        required_follow_up = [
            "record_signed_reject_all_decision_in_decision_ledger",
            "prepare_terminal_candidate_review_for_structural_source_insufficiency_or_fabrication_domain_decision_required",
        ]
    else:
        next_action = "ADD_REGRESSION_TESTS_BEFORE_ACCEPTED_AUTHORITY_LANE_FIX"
        required_follow_up = [
            "record_signed_authority_decision_in_decision_ledger",
            "write_regression_tests_before_any_accepted_lane_fix",
            "bound_implementation_scope_to_selected_authority_lanes",
            "rerun_full_tests_and_relevant_scoped_freezes",
            "run_independent_audit_before_model_promotion",
        ]

    return {
        "schema_version": "sheetmetal-v1.signed_authority_decision_intake.v1",
        "status": status,
        "decision_path": validation["decision_path"],
        "decision_sha256_canonical": validation["decision_sha256_canonical"],
        "validation_status": validation["status"],
        "selected_choice_ids": validation["selected_choice_ids"],
        "selected_authority_lanes": validation["selected_authority_lanes"],
        "reject_all_authority_lanes": validation["reject_all_authority_lanes"],
        "implementation_authorized": False,
        "implementation_can_start": False,
        "customer_pdf_dxf_dwg_generation_authorized": False,
        "production_approval_declared": False,
        "next_action": next_action,
        "required_follow_up": required_follow_up,
        "validation_errors": validation["errors"],
        "hash_checks": validation["hash_checks"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a neutral intake packet from a signed SMV1 source/rule authority decision.")
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    decision = read_json(args.decision)
    result = prepare_intake(decision, decision_path=args.decision)
    write_json(args.output, result)
    print(json.dumps({"status": result["status"], "next_action": result["next_action"], "validation_errors": result["validation_errors"]}, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
