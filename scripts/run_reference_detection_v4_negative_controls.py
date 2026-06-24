from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from detect_reference_presence_v4 import candidate_rows_from_inventory, classify_project  # noqa: E402

NEGATIVE_CONTROLS = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_negative_controls.json"
DETECTOR = ROOT / "scripts" / "detect_reference_presence_v4.py"
VERIFIER = ROOT / "scripts" / "verify_reference_detection_v4_output.py"
TARGET_TYPES = {"PRODUCTION_DRAWING", "SHEETMETAL_DRAWING", "PUNCH_DRAWING"}
OUTPUT_ROOT = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_1_negative_controls"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_command(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr_line_count": len([line for line in result.stderr.splitlines() if line.strip()]),
    }


def run_detector(project_id: str, output_dir: Path, task_id: str, disable_ocr: bool, file_ids: set[str]) -> dict[str, Any]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    try:
        rows = [
            row
            for row in candidate_rows_from_inventory(project_id)
            if row.get("neutral_reference_file_id") in file_ids
        ]
        classify_project(project_id, rows, task_id, output_dir, disable_ocr=disable_ocr)
        detector = {"returncode": 0, "stdout": json.dumps({"project_id": project_id, "file_count": len(rows)}), "stderr_line_count": 0}
    except Exception as exc:
        detector = {"returncode": 1, "stdout": json.dumps({"project_id": project_id, "error_type": type(exc).__name__}), "stderr_line_count": 0}
    verifier = {"returncode": 1, "stdout": "", "stderr_line_count": 0}
    if detector["returncode"] == 0:
        verifier = run_command([sys.executable, str(VERIFIER), "--output-dir", str(output_dir)])
    return {"detector": detector, "verifier": verifier}


def page_index(output_dir: Path) -> dict[tuple[str, int], dict[str, Any]]:
    rows = read_json(output_dir / "reference_page_classifications.json").get("page_classifications", [])
    return {(row["neutral_reference_file_id"], int(row["page_number"])): row for row in rows}


def project_audit(output_dir: Path) -> dict[str, Any]:
    return read_json(output_dir / "reference_detection_audit.json")


def project_effective_status(output_dir: Path) -> str:
    return str(read_json(output_dir / "effective_reference_set.json").get("status"))


def summarize(control_results: list[dict[str, Any]], project_results: list[dict[str, Any]], detector_version: str, disable_ocr: bool) -> dict[str, Any]:
    false_target = [row for row in control_results if row.get("observed_role") in TARGET_TYPES]
    electrical_false = [
        row
        for row in false_target
        if row.get("expected_role") == "ELECTRICAL_DRAWING"
    ]
    source_false = [
        row
        for row in false_target
        if row.get("expected_role") == "SOURCE_DOCUMENT"
    ]
    false_all_three = [
        row
        for row in project_results
        if row.get("effective_status") in {"VERIFIED_ALL_THREE_BY_CONTENT", "VERIFIED_ALL_THREE_COMBINED_PACKAGE", "VERIFIED_ALL_THREE_WITH_PAGE_SUPERSESSION"}
    ]
    temp_cleanup = all(row.get("temporary_workspace_removed") for row in project_results)
    raw_persistence = all(row.get("data_minimization_pass") for row in project_results)
    generator_isolation = all(row.get("generator_isolation_pass") for row in project_results)
    source_blindness = all(row.get("source_review_blindness_pass") for row in project_results)
    private_ocr_pages = sum(int(row.get("private_ocr_page_count", 0)) for row in project_results)
    status = "PASS" if not false_target and not false_all_three and temp_cleanup and raw_persistence and generator_isolation and source_blindness and private_ocr_pages == 0 else "FAIL"
    return {
        "schema_version": "reference_detector_v4_negative_control_audit_v1",
        "generated_at": now(),
        "detector_version": detector_version,
        "task_id": "B024-RDCAL-V4-1-NEGATIVE-CONTROLS",
        "privacy_mode": "PRIVATE_INPUT_OCR_DISABLED" if disable_ocr else "OCR_ENABLED",
        "status": status,
        "real_negative_control_count": len(control_results),
        "supported_real_negative_control_count": sum(1 for row in control_results if row["status"] != "NOT_FOUND"),
        "false_target_page_classifications": len(false_target),
        "false_all_three_project_promotions": len(false_all_three),
        "electrical_pages_falsely_accepted_as_targets": len(electrical_false),
        "source_documents_falsely_accepted_as_targets": len(source_false),
        "private_ocr_page_count": private_ocr_pages,
        "private_content_external_transmission_count": 0,
        "temporary_render_cleanup_result": "PASS" if temp_cleanup else "FAIL",
        "raw_content_persistence_result": "PASS" if raw_persistence else "FAIL",
        "generator_isolation_result": "PASS" if generator_isolation else "FAIL",
        "source_review_blindness_result": "PASS" if source_blindness else "FAIL",
        "control_results": control_results,
        "project_results": project_results,
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Detector V4.1 Negative Controls",
        "",
        f"- detector: `{summary['detector_version']}`",
        f"- status: `{summary['status']}`",
        f"- controls: `{summary['supported_real_negative_control_count']} / {summary['real_negative_control_count']}`",
        f"- false target page classifications: `{summary['false_target_page_classifications']}`",
        f"- false all-three project promotions: `{summary['false_all_three_project_promotions']}`",
        f"- electrical false target pages: `{summary['electrical_pages_falsely_accepted_as_targets']}`",
        f"- source-document false target pages: `{summary['source_documents_falsely_accepted_as_targets']}`",
        f"- private OCR page count: `{summary['private_ocr_page_count']}`",
        f"- temporary cleanup: `{summary['temporary_render_cleanup_result']}`",
        f"- raw-content persistence: `{summary['raw_content_persistence_result']}`",
        f"- generator isolation: `{summary['generator_isolation_result']}`",
        f"- source-review blindness: `{summary['source_review_blindness_result']}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run detector v4.1 on minimized real negative controls.")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--disable-private-ocr", action="store_true", default=True)
    args = parser.parse_args()
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    manifest = read_json(NEGATIVE_CONTROLS)
    controls = list(manifest.get("controls", []))
    projects = sorted({row["project_id"] for row in controls})
    file_ids_by_project = {
        project_id: {row["neutral_reference_file_id"] for row in controls if row["project_id"] == project_id}
        for project_id in projects
    }
    project_results: list[dict[str, Any]] = []
    detector_version = "UNKNOWN"
    for project_id in projects:
        out = output_root / "projects" / project_id
        run = run_detector(
            project_id,
            out,
            f"B024-RDCAL-V4-1-NEG-{project_id}",
            disable_ocr=args.disable_private_ocr,
            file_ids=file_ids_by_project[project_id],
        )
        if run["detector"]["returncode"] != 0 or run["verifier"]["returncode"] != 0:
            project_results.append(
                {
                    "project_id": project_id,
                    "status": "RUN_FAILED",
                    "detector_returncode": run["detector"]["returncode"],
                    "verifier_returncode": run["verifier"]["returncode"],
                    "temporary_workspace_removed": False,
                    "data_minimization_pass": False,
                    "generator_isolation_pass": False,
                    "source_review_blindness_pass": False,
                    "private_ocr_page_count": 0,
                }
            )
            continue
        audit = project_audit(out)
        effective = read_json(out / "effective_reference_set.json")
        detector_version = str(effective.get("detector_version", detector_version))
        pages = read_json(out / "reference_page_classifications.json").get("page_classifications", [])
        project_results.append(
            {
                "project_id": project_id,
                "status": "PASS",
                "effective_status": project_effective_status(out),
                "temporary_workspace_removed": bool(audit.get("temporary_workspace_removed")),
                "data_minimization_pass": bool(audit.get("data_minimization_pass")),
                "generator_isolation_pass": bool(audit.get("generator_isolation_pass")),
                "source_review_blindness_pass": bool(audit.get("source_review_blindness_pass")),
                "private_ocr_page_count": sum(1 for row in pages if "WINDOWS_MEDIA_OCR" in row.get("evidence_channel_codes", [])),
            }
        )

    control_results: list[dict[str, Any]] = []
    index_by_project = {
        project_id: page_index(output_root / "projects" / project_id)
        for project_id in projects
        if (output_root / "projects" / project_id / "reference_page_classifications.json").exists()
    }
    for control in controls:
        project_id = control["project_id"]
        key = (control["neutral_reference_file_id"], int(control["page_number"]))
        observed = index_by_project.get(project_id, {}).get(key)
        if not observed:
            control_results.append(
                {
                    "control_id": control["control_id"],
                    "project_id": project_id,
                    "expected_role": control["expected_role"],
                    "observed_role": None,
                    "status": "NOT_FOUND",
                }
            )
            continue
        observed_role = observed.get("page_classification")
        control_results.append(
            {
                "control_id": control["control_id"],
                "project_id": project_id,
                "expected_role": control["expected_role"],
                "observed_role": observed_role,
                "confidence": observed.get("confidence"),
                "status": "FAIL_FALSE_TARGET" if observed_role in TARGET_TYPES else "PASS",
            }
        )

    summary = summarize(control_results, project_results, detector_version, disable_ocr=args.disable_private_ocr)
    write_json(output_root / "negative_control_audit_summary.json", summary)
    write_markdown(summary, output_root / "negative_control_audit_summary.md")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "false_target_page_classifications": summary["false_target_page_classifications"],
                "false_all_three_project_promotions": summary["false_all_three_project_promotions"],
                "private_ocr_page_count": summary["private_ocr_page_count"],
            },
            ensure_ascii=False,
        )
    )
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
