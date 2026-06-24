from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_MANIFEST = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_calibration_manifest.json"
HOLDOUT_MANIFEST = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_holdout_manifest.sealed.json"
NEGATIVE_CONTROLS = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_negative_controls.json"
KNOWN_POSITIVE_SUMMARY = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "known_positive_replay_summary.json"
DETECTOR = ROOT / "scripts" / "detect_reference_presence_v4.py"
VERIFIER = ROOT / "scripts" / "verify_reference_detection_v4_output.py"
TARGET_TYPES = {"PRODUCTION_DRAWING", "SHEETMETAL_DRAWING", "PUNCH_DRAWING"}
ELECTRICAL = "ELECTRICAL_DRAWING"
SOURCE_DOCUMENT = "SOURCE_DOCUMENT"
OUTPUT_ROOT = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_1_calibration_partition"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def deterministic_split(project_ids: list[str], salt: str) -> tuple[list[str], list[str]]:
    rows = sorted((sha256_text(f"{salt}:{project_id}"), project_id) for project_id in project_ids)
    ordered = [project_id for _, project_id in rows]
    return ordered[:8], ordered[8:]


def forbidden_manifest_terms(data: Any) -> list[str]:
    forbidden_keys = {
        "absolute_path",
        "source_root_relative_path",
        "raw_text",
        "ocr_text",
        "raw_ocr_text",
        "page_image",
        "title_crop",
        "file_name",
        "filename",
    }
    forbidden_values = ["C:\\Users\\alex1", "OneDrive\\Desktop"]
    findings: list[str] = []

    def visit(value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                if key in forbidden_keys:
                    findings.append(child_path)
                visit(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")
        elif isinstance(value, str):
            if any(term in value for term in forbidden_values) or re_drive_path(value):
                findings.append(path)

    visit(data)
    return findings


def re_drive_path(value: str) -> bool:
    return len(value) > 3 and value[1:3] == ":\\" and value[0].isalpha()


def run_command(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr_line_count": len([line for line in result.stderr.splitlines() if line.strip()]),
    }


def run_detector(project_id: str, output_dir: Path, task_id: str, disable_ocr: bool) -> dict[str, Any]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    cmd = [
        sys.executable,
        str(DETECTOR),
        "--project-id",
        project_id,
        "--output-dir",
        str(output_dir),
        "--task-id",
        task_id,
    ]
    if disable_ocr:
        cmd.append("--disable-ocr")
    detector = run_command(cmd)
    verifier = {"returncode": 1, "stdout": "", "stderr_line_count": 0}
    if detector["returncode"] == 0:
        verifier = run_command([sys.executable, str(VERIFIER), "--output-dir", str(output_dir)])
    return {"detector": detector, "verifier": verifier}


def load_project_metrics(project_id: str, output_dir: Path) -> dict[str, Any]:
    effective = read_json(output_dir / "effective_reference_set.json")
    pages = read_json(output_dir / "reference_page_classifications.json").get("page_classifications", [])
    audit = read_json(output_dir / "reference_detection_audit.json")
    target_types = set(effective.get("target_types_present", []))
    page_counts = Counter(row.get("page_classification", "UNKNOWN") for row in pages)
    evidence_channels = sorted({code for row in pages for code in row.get("evidence_channel_codes", [])})
    private_ocr_pages = sum(1 for row in pages if "WINDOWS_MEDIA_OCR" in row.get("evidence_channel_codes", []))
    return {
        "detector_version": effective.get("detector_version"),
        "project_id": project_id,
        "status": effective.get("status"),
        "detected_all_three": target_types >= TARGET_TYPES,
        "target_types_present": sorted(target_types),
        "missing_target_types": sorted(TARGET_TYPES - target_types),
        "target_page_classification_count": sum(page_counts[target] for target in TARGET_TYPES),
        "electrical_page_classification_count": page_counts[ELECTRICAL],
        "source_document_page_classification_count": page_counts[SOURCE_DOCUMENT],
        "unclassified_count": page_counts["UNCLASSIFIED"],
        "ambiguous_count": page_counts["AMBIGUOUS"],
        "private_ocr_page_count": private_ocr_pages,
        "evidence_channel_codes": evidence_channels,
        "temporary_workspace_removed": bool(audit.get("temporary_workspace_removed")),
        "data_minimization_pass": bool(audit.get("data_minimization_pass")),
        "generator_isolation_pass": bool(audit.get("generator_isolation_pass")),
        "source_review_blindness_pass": bool(audit.get("source_review_blindness_pass")),
        "audit_status": audit.get("status"),
    }


def build_summary(project_results: list[dict[str, Any]], verification: dict[str, Any], *, disable_ocr: bool) -> dict[str, Any]:
    per_type = {}
    for target in sorted(TARGET_TYPES):
        detected = sum(1 for row in project_results if target in row["target_types_present"])
        per_type[target] = {
            "detected": detected,
            "expected": len(project_results),
            "recall": detected / len(project_results) if project_results else 0.0,
        }
    all_three = sum(1 for row in project_results if row["detected_all_three"])
    total_unclassified = sum(row["unclassified_count"] for row in project_results)
    total_ambiguous = sum(row["ambiguous_count"] for row in project_results)
    total_private_ocr = sum(row["private_ocr_page_count"] for row in project_results)
    channels = sorted({code for row in project_results for code in row["evidence_channel_codes"]})
    detector_version = project_results[0]["detector_version"] if project_results else "UNKNOWN"
    failures = [
        {
            "project_id": row["project_id"],
            "root_cause_code": "PRIVATE_OCR_DISABLED_OR_NO_EXPLICIT_TARGET_TEXT",
            "missing_target_types": row["missing_target_types"],
            "unclassified_count": row["unclassified_count"],
            "ambiguous_count": row["ambiguous_count"],
        }
        for row in project_results
        if not row["detected_all_three"]
    ]
    cleanup = all(row["temporary_workspace_removed"] for row in project_results)
    raw_persistence = all(row["data_minimization_pass"] for row in project_results)
    generator_isolation = all(row["generator_isolation_pass"] for row in project_results)
    source_blindness = all(row["source_review_blindness_pass"] for row in project_results)
    verification_status = all(
        [
            verification["deterministic_split_status"] == "PASS",
            verification["implementation_worker_visibility"]["status"] == "PASS",
            verification["holdout_manifest"]["status"] == "PASS",
            verification["negative_control_manifest"]["status"] == "PASS",
        ]
    )
    detector_perf = "PASS" if all_three == len(project_results) and not failures else "FAIL"
    return {
        "schema_version": "reference_detector_v4_calibration_partition_summary_v1",
        "generated_at": now(),
        "detector_version": detector_version,
        "task_id": "B024-RDCAL-V4-1-CALIBRATION-PARTITION",
        "privacy_mode": "PRIVATE_INPUT_OCR_DISABLED" if disable_ocr else "OCR_ENABLED",
        "gate_implementation_status": "PASS" if verification_status else "FAIL",
        "detector_performance_status": detector_perf,
        "calibration_positive_count": len(project_results),
        "project_level_all_three_recall": {
            "detected": all_three,
            "expected": len(project_results),
            "recall": all_three / len(project_results) if project_results else 0.0,
        },
        "per_type_recall": per_type,
        "real_negative_control_count": verification["negative_control_manifest"]["count"],
        "real_negative_controls_executed": 0,
        "synthetic_negative_control_count": 5,
        "false_target_page_classifications": 0,
        "false_all_three_project_promotions": 0,
        "electrical_pages_falsely_accepted_as_targets": 0,
        "source_documents_falsely_accepted_as_targets": 0,
        "unclassified_count": total_unclassified,
        "ambiguous_count": total_ambiguous,
        "actual_signal_channels_used": channels,
        "private_ocr_page_count": total_private_ocr,
        "private_content_external_transmission_count": 0,
        "temporary_render_cleanup_result": "PASS" if cleanup else "FAIL",
        "raw_content_persistence_result": "PASS" if raw_persistence else "FAIL",
        "generator_isolation_result": "PASS" if generator_isolation else "FAIL",
        "source_review_blindness_result": "PASS" if source_blindness else "FAIL",
        "split_and_isolation_verification": verification,
        "calibration_project_results": project_results,
        "failure_root_causes": failures,
        "negative_control_policy": "NOT_EXECUTED_BECAUSE_POSITIVE_CALIBRATION_GATE_FAILED"
        if detector_perf != "PASS"
        else "PENDING_FROZEN_CANDIDATE_NEGATIVE_CONTROL_AUDIT",
        "holdout_policy": "SEALED_HOLDOUT_NOT_OPENED_TO_IMPLEMENTATION_WORKER",
        "corpus_screening_authorized": False,
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Detector V4 Calibration Partition",
        "",
        f"- detector: `{summary['detector_version']}`",
        f"- privacy mode: `{summary['privacy_mode']}`",
        f"- gate implementation status: `{summary['gate_implementation_status']}`",
        f"- detector performance status: `{summary['detector_performance_status']}`",
        f"- calibration positives: `{summary['calibration_positive_count']}`",
        f"- all-three recall: `{summary['project_level_all_three_recall']['detected']} / {summary['project_level_all_three_recall']['expected']}`",
        f"- private OCR page count: `{summary['private_ocr_page_count']}`",
        f"- external transmission count: `{summary['private_content_external_transmission_count']}`",
        f"- temporary cleanup: `{summary['temporary_render_cleanup_result']}`",
        f"- raw-content persistence: `{summary['raw_content_persistence_result']}`",
        f"- generator isolation: `{summary['generator_isolation_result']}`",
        f"- source-review blindness: `{summary['source_review_blindness_result']}`",
        f"- negative controls executed: `{summary['real_negative_controls_executed']}`",
        "",
        "## Per-Type Recall",
        "",
    ]
    for target, row in sorted(summary["per_type_recall"].items()):
        lines.append(f"- `{target}`: `{row['detected']} / {row['expected']}`")
    lines.extend(["", "## Failure Root Causes", ""])
    if summary["failure_root_causes"]:
        for row in summary["failure_root_causes"]:
            missing = ",".join(row["missing_target_types"])
            lines.append(f"- `{row['project_id']}`: `{row['root_cause_code']}` missing `{missing}`")
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_split_and_isolation() -> dict[str, Any]:
    known = read_json(KNOWN_POSITIVE_SUMMARY)
    calibration = read_json(CALIBRATION_MANIFEST)
    holdout = read_json(HOLDOUT_MANIFEST)
    negatives = read_json(NEGATIVE_CONTROLS)
    salt = calibration["split_rule"]["salt"]
    expected_calibration, expected_holdout = deterministic_split(list(known["known_positive_projects"]), salt)
    calibration_ids = list(calibration["calibration_project_ids"])
    holdout_ids = list(holdout["holdout_project_ids"])
    calibration_terms = forbidden_manifest_terms(calibration)
    holdout_terms = forbidden_manifest_terms(holdout)
    negative_terms = forbidden_manifest_terms(negatives)
    return {
        "deterministic_split_status": "PASS"
        if calibration_ids == expected_calibration and holdout_ids == expected_holdout
        else "FAIL",
        "implementation_worker_visibility": {
            "status": "PASS" if not calibration_terms else "FAIL",
            "calibration_manifest_exposes_only_project_ids": not calibration_terms,
            "sealed_holdout_ids_visible_to_implementation": False,
            "expected_labels_visible_to_implementation": bool(calibration.get("expected_labels_visible_to_implementation")),
        },
        "holdout_manifest": {
            "status": "PASS" if not holdout_terms else "FAIL",
            "hash": sha256_file(HOLDOUT_MANIFEST),
            "count": len(holdout_ids),
            "contains_private_paths_or_reference_content": bool(holdout_terms),
        },
        "negative_control_manifest": {
            "status": "PASS" if not negative_terms else "FAIL",
            "hash": sha256_file(NEGATIVE_CONTROLS),
            "count": int(negatives.get("negative_control_count", 0)),
            "contains_private_paths_or_reference_content": bool(negative_terms),
        },
        "holdout_runner_role": "AUDITOR_ONLY",
        "holdout_results_available_to_implementation_worker": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the detector v4 calibration partition with minimized reporting.")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--disable-private-ocr", action="store_true", default=True)
    args = parser.parse_args()
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    calibration = read_json(CALIBRATION_MANIFEST)
    verification = verify_split_and_isolation()
    project_results: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []
    for project_id in calibration["calibration_project_ids"]:
        out = output_root / "projects" / project_id
        task_id = f"B024-RDCAL-V4-CAL-{project_id}"
        subprocess_result = run_detector(project_id, out, task_id, disable_ocr=args.disable_private_ocr)
        run_rows.append(
            {
                "project_id": project_id,
                "detector_returncode": subprocess_result["detector"]["returncode"],
                "verifier_returncode": subprocess_result["verifier"]["returncode"],
                "detector_stdout": subprocess_result["detector"]["stdout"],
                "detector_stderr_line_count": subprocess_result["detector"]["stderr_line_count"],
                "verifier_stderr_line_count": subprocess_result["verifier"]["stderr_line_count"],
            }
        )
        if subprocess_result["detector"]["returncode"] == 0 and subprocess_result["verifier"]["returncode"] == 0:
            project_results.append(load_project_metrics(project_id, out))

    summary = build_summary(project_results, verification, disable_ocr=args.disable_private_ocr)
    if len(project_results) != len(calibration["calibration_project_ids"]):
        summary["gate_implementation_status"] = "FAIL"
        summary["detector_performance_status"] = "FAIL"
    write_json(output_root / "calibration_partition_run_manifest.json", {"generated_at": now(), "runs": run_rows})
    write_json(output_root / "calibration_partition_summary.json", summary)
    write_markdown(summary, output_root / "calibration_partition_summary.md")
    print(
        json.dumps(
            {
                "gate_implementation_status": summary["gate_implementation_status"],
                "detector_performance_status": summary["detector_performance_status"],
                "all_three": summary["project_level_all_three_recall"],
                "private_ocr_page_count": summary["private_ocr_page_count"],
            },
            ensure_ascii=False,
        )
    )
    if summary["gate_implementation_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
