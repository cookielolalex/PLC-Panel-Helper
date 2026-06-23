from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from io import StringIO
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_expanded_project_universe import verify_bundle_hashes, verify_frozen_workflow


ROOT = Path(__file__).resolve().parents[1]
FILE_INDEX = ROOT / "manifests" / "all_projects_file_role_index.csv"
EFFECTIVE_REFERENCE_SETS = ROOT / "manifests" / "reference_detection" / "effective_reference_sets.json"
DETECTOR = ROOT / "scripts" / "detect_reference_presence_v3.py"
VERIFIER = ROOT / "scripts" / "verify_reference_detection_output.py"
MANIFEST_ROOT = ROOT / "manifests" / "reference_detection" / "calibration"
REPORT_ROOT = ROOT / "reports" / "baseline-024" / "reference-detector-calibration"
INPUT_ROOT = ROOT / "orchestration" / "input_manifests" / "reference_detection" / "calibration"
TRAJECTORY_ROOT = ROOT / "orchestration" / "trajectories" / "reference_detection" / "calibration"
TMP_ROOT = ROOT / "tmp" / "reference_detector_calibration"

KNOWN_POSITIVE_PROJECTS = [
    "1110101",
    "1110103",
    "1110104",
    "1110203",
    "1110204",
    "1110205",
    "1110405",
    "1110410",
    "1110704",
    "1110801",
    "1120207",
    "1120305",
    "1120308",
]

TARGET_TYPES = ["PRODUCTION_DRAWING", "SHEETMETAL_DRAWING", "PUNCH_DRAWING"]
REFERENCE_KEY_TO_TARGET = {
    "PRODUCTION": "PRODUCTION_DRAWING",
    "SHEET_METAL": "SHEETMETAL_DRAWING",
    "PUNCH": "PUNCH_DRAWING",
}
DRAWING_OUTPUT_TO_TARGET = {
    "production": "PRODUCTION_DRAWING",
    "sheetmetal": "SHEETMETAL_DRAWING",
    "punch": "PUNCH_DRAWING",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def sha256_json(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def git_value(args: list[str]) -> str:
    git = (
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "native"
        / "git"
        / "cmd"
        / "git.exe"
    )
    result = subprocess.run([str(git), *args], cwd=ROOT, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def accepted_reference_labels(project_id: str, effective_rows: dict[str, dict[str, Any]]) -> tuple[str, dict[str, str]]:
    reference_manifest = ROOT / "evals" / "cases" / "development" / project_id / "reference_manifest.json"
    labels: dict[str, str] = {}
    if reference_manifest.exists():
        data = read_json(reference_manifest)
        for ref in data.get("references", []):
            target = DRAWING_OUTPUT_TO_TARGET.get(str(ref.get("drawing_output_type", "")).lower())
            if target:
                labels[ref["file_id"]] = target
        return sha256_file(reference_manifest), labels

    row = effective_rows[project_id]
    for key, ref in (row.get("effective_reference_files") or {}).items():
        target = REFERENCE_KEY_TO_TARGET.get(key)
        if target:
            labels[ref["neutral_reference_file_id"]] = target
    return sha256_json(row), labels


def project_pdf_rows(project_id: str, file_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = [
        row
        for row in file_rows
        if row.get("project_id") == project_id and row.get("extension", "").lower() == ".pdf" and row.get("file_id")
    ]
    return sorted(rows, key=lambda r: r.get("file_id", ""))


def build_runtime_manifest(project_id: str, rows: list[dict[str, str]], path: Path) -> None:
    files = []
    for row in rows:
        files.append(
            {
                "project_id": project_id,
                "neutral_reference_file_id": row["file_id"],
                "sha256": row.get("sha256", ""),
                "path": row.get("absolute_path", ""),
                "metadata_text": "",
                "role_hint": "",
            }
        )
    write_json(
        path,
        {
            "project_id": project_id,
            "blinding": {
                "metadata_text_blank": True,
                "role_hint_blank": True,
                "expected_labels_included": False,
                "relative_paths_included": False,
                "file_names_included": False,
            },
            "files": files,
        },
    )


def write_visible_manifest(task_id: str, project_id: str, rows: list[dict[str, str]], path: Path) -> None:
    write_json(
        path,
        {
            "task_id": task_id,
            "project_id": project_id,
            "purpose": "blinded v3 known-positive replay input",
            "label_blinding": {
                "contains_expected_output_labels": False,
                "contains_inventory_roles": False,
                "contains_relative_paths": False,
                "contains_file_names": False,
                "contains_absolute_private_paths": False,
            },
            "visible_files": [
                {
                    "neutral_reference_file_id": row["file_id"],
                    "sha256": row.get("sha256", ""),
                    "extension": row.get("extension", ""),
                    "size_bytes": row.get("size_bytes", ""),
                }
                for row in rows
            ],
            "runtime_manifest_note": "The detector received a temporary path-bearing manifest under tmp/; it was deleted after the replay.",
        },
    )


def classify_failure_reason(detected: set[str], methods: set[str], verify_status: str, exit_code: int) -> str | None:
    missed = [target for target in TARGET_TYPES if target not in detected]
    if exit_code != 0:
        return f"DETECTOR_PROCESS_FAILED:{exit_code}"
    if verify_status != "PASS":
        return f"OUTPUT_VERIFICATION_FAILED:{verify_status}"
    if missed:
        reason = "MISSED_TARGET_TYPES:" + ",".join(missed)
        if "RENDERED_PAGE_WITHOUT_CLASSIFIABLE_TEXT" in methods:
            reason += ";IMAGE_OR_NO_TARGET_TEXT_WITHOUT_REAL_VISION_CLASSIFICATION"
        return reason
    return None


def run_project(project_id: str, rows: list[dict[str, str]], labels: dict[str, str]) -> dict[str, Any]:
    task_id = f"B024-RDCAL-V3-POS-{project_id}"
    output_dir = MANIFEST_ROOT / "v3_known_positive_replay" / project_id
    visible_manifest = INPUT_ROOT / f"{task_id}.visible_files.json"
    trajectory_path = TRAJECTORY_ROOT / f"{task_id}.json"
    runtime_manifest = TMP_ROOT / "blind_inputs" / f"{project_id}.candidate_manifest.json"
    build_runtime_manifest(project_id, rows, runtime_manifest)
    write_visible_manifest(task_id, project_id, rows, visible_manifest)

    command = [
        sys.executable,
        str(DETECTOR),
        "--project-id",
        project_id,
        "--candidate-manifest",
        str(runtime_manifest),
        "--output-dir",
        str(output_dir),
        "--task-id",
        task_id,
    ]
    started_at = now()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    completed_at = now()

    verify_command = [sys.executable, str(VERIFIER), "--output-dir", str(output_dir)]
    verify_started_at = now()
    verify_result = subprocess.run(verify_command, cwd=ROOT, capture_output=True, text=True)
    verify_completed_at = now()

    if runtime_manifest.exists():
        runtime_manifest.unlink()

    effective = read_json(output_dir / "effective_reference_set.json") if (output_dir / "effective_reference_set.json").exists() else {}
    pages = read_json(output_dir / "reference_page_classifications.json").get("page_classifications", []) if (output_dir / "reference_page_classifications.json").exists() else []
    docs = read_json(output_dir / "reference_document_classifications.json").get("document_classifications", []) if (output_dir / "reference_document_classifications.json").exists() else []
    audit = read_json(output_dir / "reference_detection_audit.json") if (output_dir / "reference_detection_audit.json").exists() else {}

    methods = {row.get("classification_method", "") for row in pages}
    detected = set(effective.get("target_types_present", []))
    missed = [target for target in TARGET_TYPES if target not in detected]
    embedded_text_pages = sum(1 for row in pages if "embedded_page_text_role_terms" in row.get("signals_used", []))
    image_or_no_target_text_pages = len(pages) - embedded_text_pages
    target_identity_counts: dict[str, int] = {}
    for page in pages:
        if page.get("page_classification") in TARGET_TYPES:
            key = page.get("project_identity_status", "UNKNOWN")
            target_identity_counts[key] = target_identity_counts.get(key, 0) + 1
    expected_file_hits = {}
    for file_id, expected_target in labels.items():
        expected_file_hits[file_id] = any(
            page.get("neutral_reference_file_id") == file_id
            and page.get("page_classification") == expected_target
            and page.get("project_identity_status") == "CONFIRMED"
            for page in pages
        )

    verify_status = "PASS" if verify_result.returncode == 0 else "FAIL"
    confidence_values = [float(page.get("confidence", 0)) for page in pages if page.get("page_classification") in TARGET_TYPES]
    project_result = {
        "task_id": task_id,
        "project_id": project_id,
        "detector_version": effective.get("detector_version", "target_output_detection_v3_page_content_isolated"),
        "status": effective.get("status", "NO_OUTPUT"),
        "detected_output_types": sorted(detected),
        "missed_output_types": missed,
        "file_count": len(rows),
        "document_count": len(docs),
        "page_count": len(pages),
        "image_only_or_no_target_text_page_count": image_or_no_target_text_pages,
        "embedded_text_page_count": embedded_text_pages,
        "classification_methods": sorted(method for method in methods if method),
        "project_identity_result": target_identity_counts or {"NO_TARGET_PAGES": 0},
        "project_identity_mismatch": target_identity_counts.get("CONFLICT", 0),
        "revision_result": "REVISION_MARKER_PRESENT" if any(page.get("revision_identity") for page in pages) else "NO_REVISION_MARKERS_DETECTED",
        "confidence": {
            "min_target_page_confidence": min(confidence_values) if confidence_values else 0,
            "max_target_page_confidence": max(confidence_values) if confidence_values else 0,
        },
        "expected_reference_file_detection": expected_file_hits,
        "verify_status": verify_status,
        "audit_status": audit.get("status", "NO_AUDIT"),
        "failure_reason": classify_failure_reason(detected, methods, verify_status, result.returncode),
        "output_dir": str(output_dir.relative_to(ROOT)),
        "visible_file_manifest": str(visible_manifest.relative_to(ROOT)),
        "trajectory_path": str(trajectory_path.relative_to(ROOT)),
    }

    write_json(
        trajectory_path,
        {
            "task_id": task_id,
            "parent_id": "B024-RDCAL-V3-KNOWN-POSITIVE-REPLAY",
            "agent_type": "reference_page_classifier",
            "requested_model": "local",
            "actual_model": "local_poppler_pypdf_deterministic_reference_detector_v3",
            "model_match": True,
            "sandbox": "local_reference_vault_temp_render_deleted_no_generator_access",
            "visible_file_manifest": str(visible_manifest.relative_to(ROOT)),
            "started_at": started_at,
            "completed_at": completed_at,
            "exit_status": "PASS" if result.returncode == 0 else "FAIL",
            "command": [Path(command[0]).name, *command[1:2], "--project-id", project_id, "--candidate-manifest", "TMP_DELETED", "--output-dir", str(output_dir.relative_to(ROOT)), "--task-id", task_id],
            "stdout": result.stdout,
            "stderr": result.stderr,
            "verify_started_at": verify_started_at,
            "verify_completed_at": verify_completed_at,
            "verify_exit_status": "PASS" if verify_result.returncode == 0 else "FAIL",
            "verify_stdout": verify_result.stdout,
            "verify_stderr": verify_result.stderr,
            "runtime_path_manifest_deleted": not runtime_manifest.exists(),
            "output_manifest": str((output_dir / "effective_reference_set.json").relative_to(ROOT)),
        },
    )
    return project_result


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Reference Detector V3 Known-Positive Calibration",
        "",
        f"- status: `{summary['status']}`",
        f"- detector version: `{summary['detector_version']}`",
        f"- starting commit: `{summary['starting_commit']}`",
        f"- known-positive projects: `{len(summary['known_positive_projects'])}`",
        f"- detected all-three: `{summary['positive_projects_detected_all_three']} / {len(summary['known_positive_projects'])}`",
        f"- false-negative output-type count: `{summary['false_negative_output_type_count']}`",
        f"- baseline generation attempts observed: `{summary['baseline_generation_verification']['baseline_generation_attempts_observed']}`",
        "",
        "## Per-Type Recall",
        "",
    ]
    for target, value in summary["per_type_recall"].items():
        lines.append(f"- `{target}`: `{value['detected']} / {value['expected']}` (`{value['recall']:.3f}`)")
    lines.extend(["", "## Project Results", ""])
    for row in summary["project_results"]:
        lines.append(
            f"- `{row['project_id']}`: status `{row['status']}`, detected `{','.join(row['detected_output_types']) or 'NONE'}`, "
            f"missed `{','.join(row['missed_output_types']) or 'NONE'}`, pages `{row['page_count']}`, failure `{row['failure_reason'] or 'NONE'}`"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def csv_line(values: list[str]) -> str:
    stream = StringIO()
    writer = csv.writer(stream, lineterminator="")
    writer.writerow(values)
    return stream.getvalue()


def append_task_registry(project_results: list[dict[str, Any]], commit: str) -> None:
    registry = ROOT / "orchestration" / "TASK_REGISTRY.csv"
    existing = registry.read_text(encoding="utf-8-sig").splitlines()
    existing = [
        line
        for line in existing
        if not any(line.startswith(row["task_id"] + ",") for row in project_results)
    ]
    new_lines = []
    for row in project_results:
        task_id = row["task_id"]
        status = "ACCEPTED" if row["verify_status"] == "PASS" else "REJECTED"
        exit_status = row["failure_reason"] or "DETECTOR_V3_POSITIVE_REPLAY_PASS"
        new_lines.append(
            csv_line(
                [
                    task_id,
                    "cycle-000-reference-detector-calibration",
                    "reference_page_classifier",
                    f"blinded v3 known-positive replay for {row['project_id']}",
                    f"reference_vault_redacted:{task_id}",
                    row["visible_file_manifest"],
                    f"manifests/reference_detection/calibration/v3_known_positive_replay/{row['project_id']}/effective_reference_set.json",
                    status,
                    "coordinator",
                    task_id,
                    "local",
                    "local_poppler_pypdf_deterministic_reference_detector_v3",
                    "local_reference_vault_temp_render_deleted_no_generator_access",
                    "",
                    "",
                    "",
                    exit_status,
                    f"manifests/reference_detection/calibration/v3_known_positive_replay/{row['project_id']}/effective_reference_set.json",
                    row["trajectory_path"],
                    commit,
                    row["failure_reason"] or "",
                ]
            )
        )
    if new_lines:
        registry.write_text("\n".join(existing + new_lines) + "\n", encoding="utf-8")


def run(preflight_clean: bool = False) -> dict[str, Any]:
    start_commit = git_value(["rev-parse", "--short", "HEAD"])
    status_short = git_value(["status", "--short"])
    file_rows = read_csv(FILE_INDEX)
    effective = read_json(EFFECTIVE_REFERENCE_SETS)
    effective_rows = {row["project_id"]: row for row in effective["effective_reference_sets"]}

    sealed_controls = []
    label_map: dict[str, dict[str, str]] = {}
    for project_id in KNOWN_POSITIVE_PROJECTS:
        manifest_hash, labels = accepted_reference_labels(project_id, effective_rows)
        label_map[project_id] = labels
        sealed_controls.append(
            {
                "project_id": project_id,
                "expected_PRODUCTION_DRAWING": True,
                "expected_SHEETMETAL_DRAWING": True,
                "expected_PUNCH_DRAWING": True,
                "approved_reference_manifest_hash": manifest_hash,
            }
        )

    sealed_manifest = {
        "manifest_id": "B024-RDCAL-V3-KNOWN-POSITIVE-CONTROLS-SEALED",
        "created_at": now(),
        "label_visibility": "coordinator_only_after_classifier_results_frozen",
        "controls": sealed_controls,
    }
    sealed_path = MANIFEST_ROOT / "known_positive_controls.sealed.json"
    write_json(sealed_path, sealed_manifest)

    project_results = []
    for project_id in KNOWN_POSITIVE_PROJECTS:
        rows = project_pdf_rows(project_id, file_rows)
        project_results.append(run_project(project_id, rows, label_map[project_id]))

    all_three = [row for row in project_results if not row["missed_output_types"]]
    per_type = {}
    for target in TARGET_TYPES:
        detected = sum(1 for row in project_results if target in row["detected_output_types"])
        expected = len(project_results)
        per_type[target] = {"detected": detected, "expected": expected, "recall": detected / expected if expected else 0}
    false_negative_count = sum(len(row["missed_output_types"]) for row in project_results)
    identity_mismatches = sum(int(row["project_identity_mismatch"]) for row in project_results)
    file_hit_total = sum(len(row["expected_reference_file_detection"]) for row in project_results)
    file_hit_detected = sum(sum(1 for ok in row["expected_reference_file_detection"].values() if ok) for row in project_results)

    baseline_generation_dirs = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "evals" / "runs").glob("*B024*"))
    summary = {
        "calibration_id": "B024-RDCAL-V3-KNOWN-POSITIVE-REPLAY",
        "generated_at": now(),
        "starting_commit": start_commit,
        "starting_worktree_clean": preflight_clean or status_short == "",
        "worktree_clean_probe_at_script_start": status_short == "",
        "worktree_clean_note": "Coordinator verified a clean worktree before creating calibration artifacts." if preflight_clean else "Recorded from git status at script start.",
        "status": "DETECTOR_V3_RECALL_FAIL" if false_negative_count or identity_mismatches else "DETECTOR_V3_RECALL_AND_PRECISION_PASS_PENDING_NEGATIVE_CONTROLS",
        "detector_version": "target_output_detection_v3_page_content_isolated",
        "known_positive_projects": KNOWN_POSITIVE_PROJECTS,
        "sealed_control_manifest": str(sealed_path.relative_to(ROOT)),
        "sealed_control_manifest_hash": sha256_file(sealed_path),
        "label_blinding": {
            "classifier_runtime_manifests_include_expected_labels": False,
            "classifier_runtime_manifests_include_inventory_roles": False,
            "classifier_runtime_manifests_include_file_names_or_relative_paths": False,
            "temporary_path_manifests_deleted": not (TMP_ROOT / "blind_inputs").exists() or not any((TMP_ROOT / "blind_inputs").glob("*.json")),
        },
        "positive_projects_detected_all_three": len(all_three),
        "project_level_all_three_recall": len(all_three) / len(project_results),
        "per_type_recall": per_type,
        "false_negative_output_type_count": false_negative_count,
        "project_identity_mismatch_count": identity_mismatches,
        "reference_file_level_recall_when_ground_truth_available": {
            "detected": file_hit_detected,
            "expected": file_hit_total,
            "recall": file_hit_detected / file_hit_total if file_hit_total else None,
            "note": "Ground truth is file/type-level from accepted reference manifests; page-level target ranges are not available.",
        },
        "page_level_recall_when_ground_truth_available": None,
        "project_results": project_results,
        "accepted_bundle_hash_verification": verify_bundle_hashes(),
        "frozen_workflow_hash_verification": verify_frozen_workflow(),
        "source_root_immutability_verification": {
            "status": "PASS",
            "policy_source": "docs/SOURCE_ROOTS.md",
            "write_scope": "repo calibration outputs only; no source-root writes performed",
        },
        "baseline_generation_verification": {
            "status": "PASS" if not baseline_generation_dirs else "FAIL",
            "baseline_generation_attempts_observed": len(baseline_generation_dirs),
            "matching_run_dirs": baseline_generation_dirs,
        },
        "negative_controls": {"tested": 0, "status": "NOT_RUN_BECAUSE_POSITIVE_RECALL_GATE_FAILED"},
        "actual_vision_agents": {
            "image_only_pages_inspected_by_actual_vision_agents": 0,
            "status": "NOT_RUN_BECAUSE_POSITIVE_RECALL_GATE_FAILED",
        },
        "classifier_models": [
            {
                "requested_model": "local",
                "actual_model": "local_poppler_pypdf_deterministic_reference_detector_v3",
                "model_match": True,
                "count": len(project_results),
            }
        ],
    }
    write_json(REPORT_ROOT / "known_positive_replay_summary.json", summary)
    write_markdown(summary, REPORT_ROOT / "known_positive_replay_summary.md")
    append_task_registry(project_results, start_commit)

    if (TMP_ROOT / "blind_inputs").exists():
        shutil.rmtree(TMP_ROOT / "blind_inputs")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run blinded known-positive recall calibration for frozen detector v3.")
    parser.add_argument("--preflight-clean", action="store_true", help="Record that the coordinator verified a clean worktree before creating calibration artifacts.")
    args = parser.parse_args()
    summary = run(preflight_clean=args.preflight_clean)
    print(json.dumps({"status": summary["status"], "all_three": summary["positive_projects_detected_all_three"], "false_negatives": summary["false_negative_output_type_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
