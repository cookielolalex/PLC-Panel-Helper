from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from detect_reference_presence_v4 import candidate_rows_from_inventory, classify_project  # noqa: E402

HOLDOUT_MANIFEST = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_holdout_manifest.sealed.json"
TARGET_TYPES = {"PRODUCTION_DRAWING", "SHEETMETAL_DRAWING", "PUNCH_DRAWING"}
OUTPUT_ROOT = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_1_sealed_holdout"
TMP_ROOT = ROOT / "tmp" / "reference_detection_v4_holdout_audit"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def anonymized_project_key(project_id: str) -> str:
    return hashlib.sha256(f"sealed-holdout-v4-1:{project_id}".encode("utf-8")).hexdigest()[:12].upper()


def project_metrics(output_dir: Path) -> dict[str, Any]:
    effective = read_json(output_dir / "effective_reference_set.json")
    pages = read_json(output_dir / "reference_page_classifications.json").get("page_classifications", [])
    audit = read_json(output_dir / "reference_detection_audit.json")
    target_types = set(effective.get("target_types_present", []))
    counts = Counter(row.get("page_classification", "UNKNOWN") for row in pages)
    return {
        "detector_version": effective.get("detector_version"),
        "status": effective.get("status"),
        "detected_all_three": target_types >= TARGET_TYPES,
        "target_types_present": sorted(target_types),
        "missing_target_types": sorted(TARGET_TYPES - target_types),
        "unclassified_count": counts["UNCLASSIFIED"],
        "ambiguous_count": counts["AMBIGUOUS"],
        "private_ocr_page_count": sum(1 for row in pages if "WINDOWS_MEDIA_OCR" in row.get("evidence_channel_codes", [])),
        "temporary_workspace_removed": bool(audit.get("temporary_workspace_removed")),
        "data_minimization_pass": bool(audit.get("data_minimization_pass")),
        "generator_isolation_pass": bool(audit.get("generator_isolation_pass")),
        "source_review_blindness_pass": bool(audit.get("source_review_blindness_pass")),
    }


def summarize(rows: list[dict[str, Any]], cleanup_ok: bool, detail_outputs_deleted: bool) -> dict[str, Any]:
    detector_version = rows[0].get("detector_version", "UNKNOWN") if rows else "UNKNOWN"
    per_type = {}
    for target in sorted(TARGET_TYPES):
        detected = sum(1 for row in rows if target in row.get("target_types_present", []))
        per_type[target] = {"detected": detected, "expected": len(rows), "recall": detected / len(rows) if rows else 0.0}
    all_three = sum(1 for row in rows if row.get("detected_all_three"))
    private_ocr = sum(int(row.get("private_ocr_page_count", 0)) for row in rows)
    temp_cleanup = cleanup_ok and all(row.get("temporary_workspace_removed") for row in rows)
    raw_persistence = all(row.get("data_minimization_pass") for row in rows)
    generator_isolation = all(row.get("generator_isolation_pass") for row in rows)
    source_blindness = all(row.get("source_review_blindness_pass") for row in rows)
    status = "PASS" if all_three == len(rows) and private_ocr == 0 and temp_cleanup and raw_persistence and generator_isolation and source_blindness and detail_outputs_deleted else "FAIL"
    failure_classes = Counter()
    for row in rows:
        if not row.get("detected_all_three"):
            if row.get("missing_target_types"):
                failure_classes["MISSING_TARGET_TYPE"] += 1
            if row.get("ambiguous_count"):
                failure_classes["AMBIGUOUS_PAGES"] += 1
            if row.get("unclassified_count"):
                failure_classes["UNCLASSIFIED_PAGES"] += 1
    return {
        "schema_version": "reference_detector_v4_1_sealed_holdout_audit_v1",
        "generated_at": now(),
        "detector_version": detector_version,
        "task_id": "B024-RDCAL-V4-1-SEALED-HOLDOUT",
        "privacy_mode": "PRIVATE_INPUT_OCR_DISABLED",
        "status": status,
        "holdout_project_count": len(rows),
        "project_level_all_three_recall": {"detected": all_three, "expected": len(rows), "recall": all_three / len(rows) if rows else 0.0},
        "per_type_recall": per_type,
        "private_ocr_page_count": private_ocr,
        "private_content_external_transmission_count": 0,
        "temporary_render_cleanup_result": "PASS" if temp_cleanup else "FAIL",
        "raw_content_persistence_result": "PASS" if raw_persistence else "FAIL",
        "generator_isolation_result": "PASS" if generator_isolation else "FAIL",
        "source_review_blindness_result": "PASS" if source_blindness else "FAIL",
        "holdout_identity_persisted": False,
        "holdout_project_ids_persisted": False,
        "holdout_file_ids_persisted": False,
        "detailed_detector_outputs_persisted": False,
        "temporary_detail_outputs_deleted": detail_outputs_deleted,
        "holdout_manifest_hash": sha256_file(HOLDOUT_MANIFEST),
        "aggregate_failure_classes": dict(failure_classes),
        "corpus_screening_authorized": status == "PASS",
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Detector V4.1 Sealed Holdout Audit",
        "",
        f"- detector: `{summary['detector_version']}`",
        f"- status: `{summary['status']}`",
        f"- holdout project count: `{summary['holdout_project_count']}`",
        f"- all-three recall: `{summary['project_level_all_three_recall']['detected']} / {summary['project_level_all_three_recall']['expected']}`",
        f"- private OCR page count: `{summary['private_ocr_page_count']}`",
        f"- external transmission count: `{summary['private_content_external_transmission_count']}`",
        f"- temporary cleanup: `{summary['temporary_render_cleanup_result']}`",
        f"- raw-content persistence: `{summary['raw_content_persistence_result']}`",
        f"- generator isolation: `{summary['generator_isolation_result']}`",
        f"- source-review blindness: `{summary['source_review_blindness_result']}`",
        f"- detailed outputs persisted: `{str(summary['detailed_detector_outputs_persisted']).lower()}`",
        "",
        "## Per-Type Recall",
        "",
    ]
    for target, row in sorted(summary["per_type_recall"].items()):
        lines.append(f"- `{target}`: `{row['detected']} / {row['expected']}`")
    lines.extend(["", "## Aggregate Failure Classes", ""])
    if summary["aggregate_failure_classes"]:
        for key, value in sorted(summary["aggregate_failure_classes"].items()):
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run sealed holdout audit with minimized aggregate output.")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--tmp-root", type=Path, default=TMP_ROOT)
    args = parser.parse_args()
    manifest = read_json(HOLDOUT_MANIFEST)
    project_ids = list(manifest.get("holdout_project_ids", []))
    run_tmp = args.tmp_root / datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rows: list[dict[str, Any]] = []
    cleanup_ok = False
    try:
        for project_id in project_ids:
            out = run_tmp / "projects" / anonymized_project_key(project_id)
            classify_project(
                project_id,
                candidate_rows_from_inventory(project_id),
                f"B024-RDCAL-V4-1-HOLDOUT-{anonymized_project_key(project_id)}",
                out,
                disable_ocr=True,
            )
            rows.append(project_metrics(out))
        cleanup_ok = True
    finally:
        if run_tmp.exists():
            shutil.rmtree(run_tmp)
        if args.tmp_root.exists() and not any(args.tmp_root.iterdir()):
            args.tmp_root.rmdir()
    detail_outputs_deleted = not run_tmp.exists() and not args.tmp_root.exists()
    summary = summarize(rows, cleanup_ok=cleanup_ok, detail_outputs_deleted=detail_outputs_deleted)
    args.output_root.mkdir(parents=True, exist_ok=True)
    write_json(args.output_root / "sealed_holdout_audit_summary.json", summary)
    write_markdown(summary, args.output_root / "sealed_holdout_audit_summary.md")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "holdout_project_count": summary["holdout_project_count"],
                "all_three": summary["project_level_all_three_recall"],
                "private_ocr_page_count": summary["private_ocr_page_count"],
            },
            ensure_ascii=False,
        )
    )
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
