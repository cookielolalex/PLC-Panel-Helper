from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from harness_lib import read_json, repo_root, sha256_file, sha256_json, validate, write_json


ROOT = repo_root()
SCHEMA_PATH = ROOT / "schemas" / "signed_authority_decision.schema.json"

CHOICE_LABELS = {
    "A": "AUTHORIZE_PANEL_ALLOCATION_SOURCE_REVIEW",
    "B": "AUTHORIZE_COMPONENT_GEOMETRY_AUTHORITY",
    "C": "AUTHORIZE_TOPOLOGY_SIZING_PLACEMENT_RULE_AUTHORITY",
    "D": "REJECT_ALL_AUTHORITY_LANES",
}

REQUIRED_CONSTRAINTS = {
    "no_production_approval",
    "no_customer_pdf_dxf_dwg_generation_before_authorized_renderer_gate",
    "no_completed_reference_inference",
    "no_post_design_label_generator_authority",
    "no_private_model_identifier_public_lookup",
    "no_source_root_mutation",
    "no_private_artifact_staging",
    "tests_before_any_fix",
    "independent_audit_before_model_promotion",
}


def resolve_repo_relative(rel_path: str, errors: list[str], code_prefix: str) -> Path | None:
    normalized = rel_path.replace("\\", "/").strip()
    candidate = Path(normalized)
    if candidate.is_absolute() or normalized.startswith("../") or "/../" in normalized:
        errors.append(f"{code_prefix}_PATH_OUTSIDE_REPO")
        return None
    path = (ROOT / normalized).resolve(strict=False)
    try:
        path.relative_to(ROOT)
    except ValueError:
        errors.append(f"{code_prefix}_PATH_OUTSIDE_REPO")
        return None
    return path


def append_hash_check(
    *,
    rel_path: str,
    expected_hash: str,
    errors: list[str],
    missing_code: str,
    mismatch_code: str,
    path_code_prefix: str,
) -> dict[str, str]:
    path = resolve_repo_relative(rel_path, errors, path_code_prefix)
    row = {
        "path": rel_path,
        "expected_sha256": str(expected_hash).upper(),
        "actual_sha256": "",
        "status": "FAIL",
    }
    if path is None:
        return row
    if not path.exists() or not path.is_file():
        errors.append(missing_code)
        return row
    row["actual_sha256"] = sha256_file(path)
    row["status"] = "PASS" if row["actual_sha256"] == row["expected_sha256"] else "FAIL"
    if row["status"] != "PASS":
        errors.append(mismatch_code)
    return row


def validate_decision(decision: dict[str, Any], *, decision_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    schema_errors = validate(decision, read_json(SCHEMA_PATH))
    errors.extend(f"SCHEMA:{err}" for err in schema_errors)

    selected = decision.get("selected_choice_ids", [])
    if not isinstance(selected, list):
        selected = []
    normalized_choices = [str(choice).strip().upper() for choice in selected]
    if not normalized_choices:
        errors.append("NO_AUTHORITY_CHOICES_SELECTED")
    if len(set(normalized_choices)) != len(normalized_choices):
        errors.append("DUPLICATE_AUTHORITY_CHOICE")
    invalid_choices = sorted(choice for choice in set(normalized_choices) if choice not in CHOICE_LABELS)
    for choice in invalid_choices:
        errors.append(f"INVALID_AUTHORITY_CHOICE:{choice}")
    if "D" in normalized_choices and len(normalized_choices) > 1:
        errors.append("REJECT_ALL_MUTUALLY_EXCLUSIVE")

    if not str(decision.get("signed_by", "")).strip():
        errors.append("MISSING_SIGNER")
    signed_at = str(decision.get("signed_at", "")).strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", signed_at):
        errors.append("INVALID_SIGNED_AT_DATE")
    if not str(decision.get("signed_statement", "")).strip():
        errors.append("MISSING_SIGNED_STATEMENT")

    acknowledged = set(decision.get("non_negotiable_constraints_acknowledged") or [])
    missing_constraints = sorted(REQUIRED_CONSTRAINTS - acknowledged)
    for constraint in missing_constraints:
        errors.append(f"MISSING_NON_NEGOTIABLE_CONSTRAINT_ACK:{constraint}")

    if decision.get("implementation_requires_regression_tests") is not True:
        errors.append("REGRESSION_TEST_REQUIREMENT_NOT_ACKNOWLEDGED")
    if decision.get("independent_audit_before_model_promotion") is not True:
        errors.append("INDEPENDENT_AUDIT_REQUIREMENT_NOT_ACKNOWLEDGED")
    if decision.get("customer_pdf_dxf_dwg_generation_authorized") is not False:
        errors.append("CUSTOMER_DRAWING_GENERATION_NOT_ALLOWED_AT_DECISION_GATE")
    if decision.get("production_approval_declared") is not False:
        errors.append("PRODUCTION_APPROVAL_FORBIDDEN")

    bound = decision.get("bound_decision_packet") or {}
    hash_checks = [
        append_hash_check(
            rel_path=str(bound.get("json_path", "")),
            expected_hash=str(bound.get("json_sha256", "")),
            errors=errors,
            missing_code="BOUND_DECISION_PACKET_MISSING",
            mismatch_code="BOUND_DECISION_PACKET_HASH_MISMATCH",
            path_code_prefix="BOUND_DECISION_PACKET",
        ),
        append_hash_check(
            rel_path=str(bound.get("template_path", "")),
            expected_hash=str(bound.get("template_sha256", "")),
            errors=errors,
            missing_code="BOUND_DECISION_TEMPLATE_MISSING",
            mismatch_code="BOUND_DECISION_TEMPLATE_HASH_MISMATCH",
            path_code_prefix="BOUND_DECISION_TEMPLATE",
        ),
    ]

    selected_authority_lanes = [
        {"choice_id": choice, "label": CHOICE_LABELS[choice]}
        for choice in normalized_choices
        if choice in CHOICE_LABELS and choice != "D"
    ]
    reject_all = normalized_choices == ["D"]
    result = {
        "schema_version": "sheetmetal-v1.signed_authority_decision_validation.v1",
        "status": "FAIL" if errors else "PASS",
        "decision_path": str(decision_path),
        "decision_sha256_canonical": sha256_json(decision),
        "selected_choice_ids": normalized_choices,
        "selected_authority_lanes": selected_authority_lanes,
        "reject_all_authority_lanes": reject_all,
        "implementation_can_start": False,
        "implementation_next_gate": "ADD_REGRESSION_TESTS_BEFORE_ACCEPTED_LANE_FIX" if selected_authority_lanes else "TERMINAL_REVIEW_OR_NO_IMPLEMENTATION",
        "customer_pdf_dxf_dwg_generation_authorized": False,
        "production_approval_declared": False,
        "hash_checks": hash_checks,
        "errors": errors,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a signed SMV1 source/rule authority decision without selecting authority on behalf of the signer.")
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    decision = read_json(args.decision)
    result = validate_decision(decision, decision_path=args.decision)
    write_json(args.output, result)
    print(json.dumps({"status": result["status"], "errors": result["errors"]}, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
