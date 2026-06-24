from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness_lib import repo_root, sha256_file, write_json


ROOT = repo_root()

PACKET_JSON = Path("reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_authority_decision_packet.json")
TEMPLATE_JSON = Path("reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_template.json")

CONSTRAINT_ACKNOWLEDGEMENT_ORDER = [
    "no_production_approval",
    "no_customer_pdf_dxf_dwg_generation_before_authorized_renderer_gate",
    "no_completed_reference_inference",
    "no_post_design_label_generator_authority",
    "no_private_model_identifier_public_lookup",
    "no_source_root_mutation",
    "no_private_artifact_staging",
    "tests_before_any_fix",
    "independent_audit_before_model_promotion",
]


def build_unsigned_draft(*, decision_id: str) -> dict:
    return {
        "schema_version": "sheetmetal-v1.signed_authority_decision.v1",
        "decision_id": decision_id,
        "active_goal": "SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1",
        "bound_decision_packet": {
            "json_path": PACKET_JSON.as_posix(),
            "json_sha256": sha256_file(ROOT / PACKET_JSON),
            "template_path": TEMPLATE_JSON.as_posix(),
            "template_sha256": sha256_file(ROOT / TEMPLATE_JSON),
        },
        "selected_choice_ids": [],
        "signed_by": "",
        "signed_at": "YYYY-MM-DD",
        "signed_statement": "I authorize the following SMV1 source/rule authority choice(s): <A/B/C or D>.",
        "non_negotiable_constraints_acknowledged": CONSTRAINT_ACKNOWLEDGEMENT_ORDER,
        "implementation_requires_regression_tests": True,
        "independent_audit_before_model_promotion": True,
        "customer_pdf_dxf_dwg_generation_authorized": False,
        "production_approval_declared": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Write an unsigned SMV1 source/rule authority decision JSON draft.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--decision-id", default="DRAFT-SMV1-SIGNED-AUTHORITY")
    args = parser.parse_args()

    draft = build_unsigned_draft(decision_id=args.decision_id)
    write_json(args.output, draft)
    print(json.dumps({"status": "DRAFT_UNSIGNED_NOT_VALID_FOR_IMPLEMENTATION", "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
