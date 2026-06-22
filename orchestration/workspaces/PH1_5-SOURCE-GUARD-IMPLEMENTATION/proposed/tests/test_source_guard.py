from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from source_guard import (  # noqa: E402
    build_review_items,
    build_sanitized_bundle_manifest,
    row_sha256,
    validate_approval,
)


def synthetic_file_row(**overrides: str) -> dict[str, str]:
    row = {
        "file_id": "FILE-SAFE-001",
        "source_root": "SRC-SYNTHETIC",
        "relative_path": "1150001/input.xlsx",
        "archive_member_path": "",
        "project_id": "1150001",
        "project_name": "Synthetic project",
        "customer": "Synthetic customer",
        "file_name": "input.xlsx",
        "extension": ".xlsx",
        "size_bytes": "10",
        "modified_time": "0",
        "sha256": "A" * 64,
        "content_fingerprint": "A" * 64,
        "duplicate_of": "",
        "primary_role": "allowed_contract_workbook",
        "secondary_tags": "",
        "drawing_output_type": "",
        "generator_eligibility": "HUMAN_REVIEW_REQUIRED",
        "forbidden_signature_match": "False",
        "classification_confidence": "0.75",
        "basis": "synthetic_test",
        "parse_status": "PARSED",
        "review_status": "BOOTSTRAP_CLASSIFIED",
        "notes": "",
        "absolute_path": "",
    }
    row.update(overrides)
    return row


def synthetic_sheet_row(**overrides: str) -> dict[str, str]:
    row = {
        "sheet_id": "SHEET-SAFE-001",
        "workbook_file_id": "FILE-SAFE-001",
        "sheet_name": "CurrentInput",
        "visibility": "visible",
        "used_range": "A1:D10",
        "print_area": "",
        "named_ranges": "",
        "external_links": "",
        "detected_project_id": "1150001",
        "detected_customer": "Synthetic customer",
        "detected_project_name": "Synthetic project",
        "detected_date": "2026-06-22",
        "detected_revision": "0",
        "stale_template_status": "CURRENT_PROJECT_ID_MATCH",
        "stale_evidence": "",
        "generator_eligibility": "HUMAN_REVIEW_REQUIRED",
        "approved_by": "",
        "approval_time": "",
        "parse_status": "PARSED",
        "notes": "",
    }
    row.update(overrides)
    return row


def approval_for(row: dict[str, str], item_type: str, item_id: str) -> dict[str, object]:
    return {
        "approval_id": "APPROVAL-SYNTHETIC",
        "created_at": "2026-06-22T00:00:00Z",
        "approved_by": "synthetic-reviewer",
        "signed_human_decision": {
            "signer": "synthetic-reviewer",
            "signed_at": "2026-06-22T00:00:00Z",
            "statement": "Synthetic approval for regression testing only.",
            "signature_sha256": "B" * 64,
        },
        "bound_inputs": {
            "file_role_index_sha256": "C" * 64,
            "workbook_sheet_index_sha256": "D" * 64,
        },
        "decisions": [{
            "decision_id": "DECISION-001",
            "item_type": item_type,
            "item_id": item_id,
            "decision": "ALLOW_GENERATOR_INPUT",
            "current_row_sha256": row_sha256(row),
            "effective_project_id": "1150001",
            "rationale": "Synthetic current project workbook/sheet.",
        }],
    }


def test_forbidden_file_role_cannot_be_approved() -> None:
    file_row = synthetic_file_row(
        primary_role="forbidden_electrical_drawing",
        generator_eligibility="FORBIDDEN",
        file_name="target.pdf",
        extension=".pdf",
    )
    approval = approval_for(file_row, "file", "FILE-SAFE-001")
    result = validate_approval(approval, [file_row], [])
    assert result.status == "FAIL"
    assert not result.allowed_file_ids
    assert any("forbidden_role" in error for error in result.errors)


def test_stale_hash_rejected() -> None:
    file_row = synthetic_file_row()
    approval = approval_for(file_row, "file", "FILE-SAFE-001")
    approval["decisions"][0]["current_row_sha256"] = "0" * 64
    result = validate_approval(approval, [file_row], [])
    assert result.status == "FAIL"
    assert result.errors == ["file_decision_stale_hash:FILE-SAFE-001"]


def test_current_synthetic_sheet_approval_passes() -> None:
    file_row = synthetic_file_row()
    sheet_row = synthetic_sheet_row()
    approval = approval_for(sheet_row, "worksheet", "SHEET-SAFE-001")
    result = validate_approval(approval, [file_row], [sheet_row])
    assert result.status == "PASS"
    assert result.allowed_file_ids == ["FILE-SAFE-001"]
    assert result.allowed_sheet_ids == ["SHEET-SAFE-001"]
    manifest = build_sanitized_bundle_manifest(
        approval=approval,
        guard_result=result,
        file_rows=[file_row],
        sheet_rows=[sheet_row],
        bundle_root=Path("tmp/synthetic-bundle"),
        run_id="SYNTHETIC",
        project_id="1150001",
        copy_files=False,
    )
    assert manifest["status"] == "PASS"
    assert manifest["allowed_files"][0]["source_file_id"] == "FILE-SAFE-001"
    assert "absolute_path" not in manifest["allowed_files"][0]


def test_review_batch_keeps_generator_visibility_false_inputs() -> None:
    file_row = synthetic_file_row()
    sheet_row = synthetic_sheet_row()
    queue = [{
        "queue_id": "Q-001",
        "item_type": "worksheet",
        "item_id": "SHEET-SAFE-001",
        "reason": "HUMAN_REVIEW_REQUIRED",
        "status": "HUMAN_REVIEW_REQUIRED",
    }]
    items = build_review_items(queue, [file_row], [sheet_row])
    assert len(items) == 1
    assert items[0]["current_generator_eligibility"] == "HUMAN_REVIEW_REQUIRED"
    assert items[0]["source_row_sha256"] == row_sha256(sheet_row)

