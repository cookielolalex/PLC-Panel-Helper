from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXCEL_EXTENSIONS = {".xlsx", ".xlsm"}
SAFE_FILE_ROLES = {
    "allowed_contract_workbook",
    "allowed_material_list_workbook",
    "allowed_supporting_workbook",
}
FORBIDDEN_FILE_ROLES = {
    "forbidden_production_control_file",
    "forbidden_electrical_drawing",
    "completed_production_drawing_reference",
    "completed_sheetmetal_drawing_reference",
    "completed_punch_drawing_reference",
}
TARGET_OUTPUT_PREFIXES = ("01_", "02_", "03_")
ALLOW_DECISION = "ALLOW_GENERATOR_INPUT"


class SourceGuardError(Exception):
    pass


@dataclass(frozen=True)
class GuardResult:
    status: str
    errors: list[str]
    warnings: list[str]
    allowed_file_ids: list[str]
    allowed_sheet_ids: list[str]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def sha256_json(data: Any) -> str:
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def row_sha256(row: dict[str, Any]) -> str:
    stable = {k: row.get(k, "") for k in sorted(row)}
    return sha256_json(stable)


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "")
        if value:
            indexed[value] = row
    return indexed


def is_target_like_name(name: str) -> bool:
    base = Path(name).name
    return base.startswith(TARGET_OUTPUT_PREFIXES) and base.lower().endswith(".pdf")


def forbidden_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if row.get("generator_eligibility") == "FORBIDDEN":
        reasons.append("generator_eligibility_forbidden")
    if row.get("primary_role") in FORBIDDEN_FILE_ROLES:
        reasons.append(f"forbidden_role:{row.get('primary_role')}")
    if boolish(row.get("forbidden_signature_match", "")):
        reasons.append("forbidden_signature_match")
    if row.get("drawing_output_type"):
        reasons.append(f"drawing_output_type:{row.get('drawing_output_type')}")
    for key in ("relative_path", "file_name", "bundle_path"):
        value = str(row.get(key, ""))
        if value and is_target_like_name(value):
            reasons.append(f"target_like_name:{key}")
    return reasons


def file_allow_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    reasons.extend(forbidden_reasons(row))
    ext = str(row.get("extension") or Path(str(row.get("file_name", ""))).suffix).lower()
    if ext not in EXCEL_EXTENSIONS:
        reasons.append(f"unsupported_extension:{ext or 'missing'}")
    if row.get("primary_role") not in SAFE_FILE_ROLES:
        reasons.append(f"not_safe_file_role:{row.get('primary_role') or 'missing'}")
    if not row.get("project_id"):
        reasons.append("missing_project_id")
    digest = str(row.get("sha256", ""))
    if not digest or digest == "NOT_HASHED":
        reasons.append("missing_current_file_hash")
    return reasons


def sheet_allow_reasons(sheet: dict[str, Any], workbook: dict[str, Any] | None) -> list[str]:
    reasons: list[str] = []
    reasons.extend(forbidden_reasons(sheet))
    if workbook is None:
        reasons.append("missing_workbook_file_row")
        return reasons
    reasons.extend(f"workbook_{reason}" for reason in file_allow_reasons(workbook))
    if str(sheet.get("visibility", "")).lower() not in {"visible", ""}:
        reasons.append(f"non_visible_sheet:{sheet.get('visibility')}")
    if sheet.get("stale_template_status") != "CURRENT_PROJECT_ID_MATCH":
        reasons.append(f"not_current_project_sheet:{sheet.get('stale_template_status') or 'missing'}")
    if not sheet.get("sheet_name"):
        reasons.append("missing_sheet_name")
    return reasons


def build_review_items(
    queue_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    sheet_rows: list[dict[str, str]],
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    files = index_by(file_rows, "file_id")
    sheets = index_by(sheet_rows, "sheet_id")
    items: list[dict[str, Any]] = []
    for queue in queue_rows:
        item_type = queue.get("item_type", "")
        item_id = queue.get("item_id", "")
        if queue.get("status") != "HUMAN_REVIEW_REQUIRED":
            continue
        if item_type == "file":
            row = files.get(item_id)
            if row is None:
                continue
            item = {
                "queue_id": queue.get("queue_id", ""),
                "item_type": "file",
                "item_id": item_id,
                "reason": queue.get("reason", ""),
                "status": queue.get("status", ""),
                "source_root": row.get("source_root", ""),
                "relative_path": row.get("relative_path", ""),
                "primary_role": row.get("primary_role", ""),
                "current_generator_eligibility": row.get("generator_eligibility", ""),
                "source_row_sha256": row_sha256(row),
                "reviewer_instruction": "Review metadata and source file manually; approve only current project Excel inputs.",
            }
        elif item_type == "worksheet":
            row = sheets.get(item_id)
            if row is None:
                continue
            workbook = files.get(row.get("workbook_file_id", ""))
            item = {
                "queue_id": queue.get("queue_id", ""),
                "item_type": "worksheet",
                "item_id": item_id,
                "reason": queue.get("reason", ""),
                "status": queue.get("status", ""),
                "source_root": workbook.get("source_root", "") if workbook else "",
                "relative_path": workbook.get("relative_path", "") if workbook else "",
                "workbook_file_id": row.get("workbook_file_id", ""),
                "sheet_name": row.get("sheet_name", ""),
                "stale_template_status": row.get("stale_template_status", ""),
                "visibility": row.get("visibility", ""),
                "current_generator_eligibility": row.get("generator_eligibility", ""),
                "source_row_sha256": row_sha256(row),
                "reviewer_instruction": "Approve only if the sheet is current-project evidence and not a stale or hidden template.",
            }
        else:
            continue
        items.append(item)
        if max_items is not None and len(items) >= max_items:
            break
    return items


def validate_bound_inputs(
    approval: dict[str, Any],
    file_role_index: Path,
    workbook_sheet_index: Path,
) -> list[str]:
    errors: list[str] = []
    bound = approval.get("bound_inputs", {})
    actual_file_hash = sha256_file(file_role_index)
    actual_sheet_hash = sha256_file(workbook_sheet_index)
    if bound.get("file_role_index_sha256") != actual_file_hash:
        errors.append("file_role_index_sha256_mismatch")
    if bound.get("workbook_sheet_index_sha256") != actual_sheet_hash:
        errors.append("workbook_sheet_index_sha256_mismatch")
    return errors


def validate_approval(
    approval: dict[str, Any],
    file_rows: list[dict[str, str]],
    sheet_rows: list[dict[str, str]],
) -> GuardResult:
    errors: list[str] = []
    warnings: list[str] = []
    allowed_files: set[str] = set()
    allowed_sheets: set[str] = set()
    files = index_by(file_rows, "file_id")
    sheets = index_by(sheet_rows, "sheet_id")

    signature = approval.get("signed_human_decision", {})
    for key in ("signer", "signed_at", "statement", "signature_sha256"):
        if not signature.get(key):
            errors.append(f"missing_signature_field:{key}")

    for decision in approval.get("decisions", []):
        if decision.get("decision") != ALLOW_DECISION:
            warnings.append(f"non_allow_decision_skipped:{decision.get('decision_id', '')}")
            continue
        item_type = decision.get("item_type")
        item_id = decision.get("item_id", "")
        if item_type == "file":
            row = files.get(item_id)
            if row is None:
                errors.append(f"file_decision_missing_row:{item_id}")
                continue
            if decision.get("current_row_sha256") != row_sha256(row):
                errors.append(f"file_decision_stale_hash:{item_id}")
                continue
            reasons = file_allow_reasons(row)
            if reasons:
                errors.append(f"file_decision_rejected:{item_id}:{'|'.join(reasons)}")
                continue
            allowed_files.add(item_id)
        elif item_type == "worksheet":
            row = sheets.get(item_id)
            if row is None:
                errors.append(f"sheet_decision_missing_row:{item_id}")
                continue
            if decision.get("current_row_sha256") != row_sha256(row):
                errors.append(f"sheet_decision_stale_hash:{item_id}")
                continue
            workbook_id = row.get("workbook_file_id", "")
            workbook = files.get(workbook_id)
            reasons = sheet_allow_reasons(row, workbook)
            if reasons:
                errors.append(f"sheet_decision_rejected:{item_id}:{'|'.join(reasons)}")
                continue
            allowed_sheets.add(item_id)
            allowed_files.add(workbook_id)
        else:
            errors.append(f"unknown_decision_item_type:{item_type}")

    status = "PASS" if not errors and (allowed_files or allowed_sheets) else "HUMAN_REVIEW_REQUIRED"
    if errors:
        status = "FAIL"
    return GuardResult(
        status=status,
        errors=errors,
        warnings=warnings,
        allowed_file_ids=sorted(allowed_files),
        allowed_sheet_ids=sorted(allowed_sheets),
    )


def copy_approved_file(src: Path, bundle_root: Path, row: dict[str, Any]) -> dict[str, str]:
    if src.is_symlink():
        raise SourceGuardError(f"refusing_symlink_source:{src}")
    target = bundle_root / "evidence" / f"{row['file_id']}{Path(src).suffix.lower()}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)
    return {
        "source_file_id": row["file_id"],
        "bundle_path": str(target.relative_to(bundle_root)).replace("\\", "/"),
        "sha256": sha256_file(target),
        "extension": Path(target).suffix.lower(),
        "primary_role": row.get("primary_role", ""),
    }


def build_sanitized_bundle_manifest(
    approval: dict[str, Any],
    guard_result: GuardResult,
    file_rows: list[dict[str, str]],
    sheet_rows: list[dict[str, str]],
    bundle_root: Path,
    run_id: str,
    project_id: str,
    copy_files: bool,
) -> dict[str, Any]:
    files = index_by(file_rows, "file_id")
    sheets = index_by(sheet_rows, "sheet_id")
    allowed_files: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []

    for file_id in guard_result.allowed_file_ids:
        row = files[file_id]
        if copy_files:
            absolute_path = row.get("absolute_path", "")
            if not absolute_path:
                raise SourceGuardError(f"approved_file_missing_absolute_path:{file_id}")
            allowed_files.append(copy_approved_file(Path(absolute_path), bundle_root, row))
        else:
            allowed_files.append({
                "source_file_id": file_id,
                "bundle_path": f"evidence/{file_id}{row.get('extension', '')}",
                "sha256": row.get("sha256", ""),
                "extension": row.get("extension", ""),
                "primary_role": row.get("primary_role", ""),
            })

    allowed_sheets = [
        {
            "sheet_id": sheet_id,
            "workbook_file_id": sheets[sheet_id].get("workbook_file_id", ""),
            "sheet_name": sheets[sheet_id].get("sheet_name", ""),
        }
        for sheet_id in guard_result.allowed_sheet_ids
    ]
    for row in file_rows:
        if row.get("file_id") not in guard_result.allowed_file_ids:
            excluded.append({"id": row.get("file_id", ""), "reason": "not_in_validated_source_approval"})
    for row in sheet_rows:
        if row.get("sheet_id") not in guard_result.allowed_sheet_ids:
            excluded.append({"id": row.get("sheet_id", ""), "reason": "not_in_validated_source_approval"})

    return {
        "manifest_id": f"sanitized-generator-input-{run_id}",
        "project_id": project_id,
        "run_id": run_id,
        "status": guard_result.status,
        "source_approval_id": approval.get("approval_id", ""),
        "bundle_root": str(bundle_root),
        "allowed_files": allowed_files,
        "allowed_sheets": allowed_sheets,
        "excluded": excluded,
        "verification": {"status": "NOT_RUN", "errors": []},
    }


def has_windows_reparse_point(path: Path) -> bool:
    attrs = getattr(path.stat(), "st_file_attributes", 0)
    return bool(attrs & getattr(os.stat_result, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def verify_bundle_manifest(manifest: dict[str, Any], bundle_root: Path) -> list[str]:
    errors: list[str] = []
    root = bundle_root.resolve()
    for row in manifest.get("allowed_files", []):
        bundle_path = str(row.get("bundle_path", ""))
        if not bundle_path or Path(bundle_path).is_absolute():
            errors.append(f"invalid_bundle_path:{bundle_path}")
            continue
        if ".." in Path(bundle_path).parts:
            errors.append(f"bundle_path_escapes_root:{bundle_path}")
            continue
        if forbidden_reasons(row):
            errors.append(f"forbidden_bundle_metadata:{bundle_path}:{'|'.join(forbidden_reasons(row))}")
        path = (root / bundle_path).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"resolved_bundle_path_escapes_root:{bundle_path}")
            continue
        if path.exists():
            if path.is_symlink() or has_windows_reparse_point(path):
                errors.append(f"bundle_reparse_point_rejected:{bundle_path}")
            if path.is_file():
                actual = sha256_file(path)
                if row.get("sha256") and row.get("sha256") != actual:
                    errors.append(f"bundle_hash_mismatch:{bundle_path}")
        else:
            errors.append(f"bundle_file_missing:{bundle_path}")
    return errors

