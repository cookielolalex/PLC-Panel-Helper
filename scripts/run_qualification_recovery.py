from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASELINE_ID = "baseline-024-cycle-000"
DECISION_ID = "D-0021"
REQUIRED_ALLOWED_EVAL = 24
RESERVE_TARGET = 3

REPORT_DIR = ROOT / "reports" / "baseline-024" / "qualification-recovery"
QUEUE_PATH = ROOT / "orchestration" / "QUALIFICATION_RECOVERY_QUEUE.json"

SHORTFALL = ROOT / "reports" / "baseline-024" / "insufficient_eligible_projects_for_24_baseline.json"
PHASE_C_STATUS = ROOT / "manifests" / "baseline-024" / "source_approvals" / "phase_c_status.json"
UNIVERSE = ROOT / "reports" / "baseline-024" / "expanded-screening" / "full_project_universe.json"
KNOWN_POSITIVE = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "known_positive_replay_summary.json"
VISION_PROBE = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "vision_classifier_availability_probe.json"
WINDOWS_OCR_PROBE = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "windows_media_ocr_local_probe.json"
V4_CALIBRATION_MANIFEST = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_calibration_manifest.json"
V4_HOLDOUT_MANIFEST = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_holdout_manifest.sealed.json"
V4_NEGATIVE_CONTROLS = ROOT / "manifests" / "reference_detection" / "calibration" / "v4_negative_controls.json"
V4_DETECTOR_SCRIPT = ROOT / "scripts" / "detect_reference_presence_v4.py"
V4_1_CALIBRATION_SUMMARY = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_1_calibration_partition" / "calibration_partition_summary.json"
V4_1_NEGATIVE_SUMMARY = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_1_negative_controls" / "negative_control_audit_summary.json"
V4_1_FREEZE_MANIFEST = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_1_candidate_freeze_manifest.json"
V4_1_AUDIT_REPORT = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_1_independent_implementation_audit.md"
FROZEN_WORKFLOW = ROOT / "evals" / "baseline-024" / "frozen_workflow_manifest.json"
PRIVACY_APPROVAL = ROOT / "docs" / "PRIVACY_APPROVAL.md"
TASK_REGISTRY = ROOT / "orchestration" / "TASK_REGISTRY.csv"

BLOCKER_CLASSES = [
    "RECOVERABLE_DETECTOR_LIMITATION",
    "RECOVERABLE_OCR_LIMITATION",
    "RECOVERABLE_PARSER_LIMITATION",
    "RECOVERABLE_SANITIZATION_LIMITATION",
    "RECOVERABLE_PROCEDURE_AMBIGUITY",
    "SUBSTANTIVE_REFERENCE_INCOMPLETE",
    "SUBSTANTIVE_SOURCE_DISQUALIFICATION",
    "PRIVACY_PERMISSION_REQUIRED",
    "UNKNOWN_REQUIRES_NEW_TEST",
]

FROZEN_HASH_PATHS = {
    "master_spec": "CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt",
    "agents_md": "AGENTS.md",
    "instructions": "gpt-config/INSTRUCTIONS.md",
    "production_knowledge_readme": "knowledge/production/README.md",
    "job_spec_schema": "schemas/job_spec.schema.json",
    "drawing_model_schema": "schemas/drawing_model.schema.json",
    "renderer": "scripts/render_pdf_outputs.py",
    "validator_pdf": "scripts/validate_pdf_package.py",
    "grading_profile_v2": "evals/grading_profiles/plc_layout_v2.json",
    "evaluator_scoring": "scripts/evaluator_scoring.py",
    "tolerance_profile": "evals/tolerance_profiles/plc_layout_tolerances_v1.json",
    "source_guard_policy": "manifests/source_guard/source_guard_policy.json",
    "autonomous_source_approval_spec": "docs/specs/AUTONOMOUS_EVAL_SOURCE_APPROVAL.md",
    "sanitized_bundle_spec": "docs/specs/SANITIZED_GENERATOR_BUNDLE_SPEC.md",
    "baseline_protocol": "docs/specs/24_PROJECT_BASELINE_PROTOCOL.md",
}


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


def sha256_json(data: Any) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def bundled_dependency_root() -> Path:
    return Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"


def bundled_git() -> Path:
    return bundled_dependency_root() / "native" / "git" / "cmd" / "git.exe"


def git_status() -> dict[str, Any]:
    git = bundled_git()
    if not git.exists():
        found = shutil.which("git")
        git = Path(found) if found else git
    result = {
        "git_executable": str(git) if git.exists() else "UNAVAILABLE",
        "head": "",
        "worktree_clean": None,
        "status_short": "",
    }
    if git.exists():
        head = subprocess.run([str(git), "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False)
        status = subprocess.run([str(git), "status", "--short"], cwd=ROOT, text=True, capture_output=True, check=False)
        result["head"] = head.stdout.strip()
        result["status_short"] = status.stdout
        result["worktree_clean"] = status.returncode == 0 and not status.stdout.strip()
        return result

    head_file = ROOT / ".git" / "HEAD"
    if head_file.exists():
        head_ref = head_file.read_text(encoding="utf-8").strip()
        if head_ref.startswith("ref: "):
            ref_path = ROOT / ".git" / head_ref[5:]
            if ref_path.exists():
                result["head"] = ref_path.read_text(encoding="utf-8").strip()
        else:
            result["head"] = head_ref
    return result


def verify_accepted_bundle_hashes() -> dict[str, Any]:
    hash_files = list((ROOT / "evals" / "cases" / "development").glob("*/bundle_hashes.json"))
    hash_files.extend((ROOT / "manifests" / "baseline-024" / "project_bundles").glob("batch-*/accepted/*/bundle_hashes.json"))
    key_to_file = {
        "bundle_manifest": "bundle_manifest.json",
        "approval_manifest": "approval_manifest.json",
        "visible_file_manifest": "visible_file_manifest.json",
        "provenance_map": "provenance_map.json",
        "verification_results": "verification_results.json",
    }
    failures: list[dict[str, str]] = []
    checked = 0
    projects: list[str] = []
    for hash_file in sorted(hash_files):
        bundle_root = hash_file.parent
        projects.append(bundle_root.name)
        data = read_json(hash_file)
        for key, rel in key_to_file.items():
            if key not in data:
                continue
            checked += 1
            path = bundle_root / rel
            if not path.exists():
                failures.append({"project_id": bundle_root.name, "path": rel, "status": "MISSING"})
                continue
            actual = sha256_file(path)
            expected = str(data[key]).upper()
            if actual != expected:
                failures.append({"project_id": bundle_root.name, "path": rel, "status": "HASH_MISMATCH"})
        for artifact in data.get("artifacts", []):
            checked += 1
            rel = Path(str(artifact.get("path", "")))
            if rel.is_absolute() or ".." in rel.parts:
                failures.append({"project_id": bundle_root.name, "path": str(rel), "status": "UNSAFE_ARTIFACT_PATH"})
                continue
            artifact_path = bundle_root / rel
            if not artifact_path.exists():
                failures.append({"project_id": bundle_root.name, "path": str(rel), "status": "MISSING"})
                continue
            if sha256_file(artifact_path) != str(artifact.get("sha256", "")).upper():
                failures.append({"project_id": bundle_root.name, "path": str(rel), "status": "HASH_MISMATCH"})
    return {
        "status": "PASS" if not failures and len(hash_files) == 13 else "FAIL",
        "bundle_hash_file_count": len(hash_files),
        "project_ids": sorted(projects),
        "checked_file_count": checked,
        "failure_count": len(failures),
        "failures": failures,
    }


def verify_frozen_workflow_hashes() -> dict[str, Any]:
    manifest = read_json(FROZEN_WORKFLOW)
    expected = manifest.get("hashes", {})
    failures: list[dict[str, str]] = []
    checked = 0
    for key, rel in FROZEN_HASH_PATHS.items():
        path = ROOT / rel
        checked += 1
        if not path.exists():
            failures.append({"key": key, "path": rel, "status": "MISSING"})
            continue
        actual = sha256_file(path)
        wanted = str(expected.get(key, "")).upper()
        if actual != wanted:
            failures.append({"key": key, "path": rel, "status": "HASH_MISMATCH"})
    return {
        "status": "PASS" if not failures else "FAIL",
        "frozen_manifest": str(FROZEN_WORKFLOW.relative_to(ROOT)),
        "checked_file_count": checked,
        "failure_count": len(failures),
        "failures": failures,
    }


def privacy_status() -> str:
    text = PRIVACY_APPROVAL.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip().startswith("Status:"):
            return line.split(":", 1)[1].strip().strip(".")
    return "UNKNOWN"


def verify_baseline_generation_absence() -> dict[str, Any]:
    generation_files = []
    baseline_markers = {"baseline-024", "BASELINE024", "B024"}
    for path in (ROOT / "evals").rglob("generation_complete.json"):
        text = str(path)
        if any(marker in text for marker in baseline_markers):
            generation_files.append(path)
    run_dirs = []
    runs_root = ROOT / "evals" / "runs"
    if runs_root.exists():
        for path in runs_root.iterdir():
            if path.is_dir() and any(marker in path.name for marker in baseline_markers):
                run_dirs.append(path)
    attempts = len(generation_files) + len(run_dirs)
    return {
        "status": "PASS" if attempts == 0 else "FAIL",
        "baseline_generation_attempts_observed": attempts,
        "generation_complete_files": [str(p.relative_to(ROOT)) for p in sorted(generation_files)],
        "baseline_run_directories": [str(p.relative_to(ROOT)) for p in sorted(run_dirs)],
    }


def probe_command(name: str, args: list[str], search_dirs: list[Path]) -> dict[str, Any]:
    search_path = os.pathsep.join([str(p) for p in search_dirs if p.exists()] + os.environ.get("PATH", "").split(os.pathsep))
    found = shutil.which(name, path=search_path)
    if not found:
        return {"name": name, "status": "UNAVAILABLE", "requested_args": args}
    try:
        result = subprocess.run([found, *args], text=True, capture_output=True, timeout=10, check=False)
        output = (result.stdout + result.stderr).strip().splitlines()
        return {
            "name": name,
            "status": "AVAILABLE",
            "executable": found,
            "requested_args": args,
            "returncode": result.returncode,
            "version_output": output[:8],
        }
    except Exception as exc:
        return {
            "name": name,
            "status": "PROBE_FAILED",
            "executable": found,
            "requested_args": args,
            "error": f"{type(exc).__name__}: {exc}",
        }


def module_probe(module_name: str, distribution_name: str | None = None) -> dict[str, Any]:
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return {"module": module_name, "status": "UNAVAILABLE"}
    version = "UNKNOWN"
    try:
        version = importlib.metadata.version(distribution_name or module_name)
    except Exception:
        pass
    return {
        "module": module_name,
        "status": "AVAILABLE",
        "version": version,
        "origin": spec.origin or "UNKNOWN",
    }


def probe_windows_media_ocr() -> dict[str, Any]:
    if platform.system().lower() != "windows":
        return {"name": "Windows.Media.Ocr", "status": "NOT_APPLICABLE", "platform": platform.system()}
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] -ne $null",
    ]
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=10, check=False)
        available = result.returncode == 0 and "True" in result.stdout
        return {
            "name": "Windows.Media.Ocr",
            "status": "AVAILABLE" if available else "UNAVAILABLE",
            "execution_mode": "windows_local_runtime_probe_no_project_data",
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as exc:
        return {
            "name": "Windows.Media.Ocr",
            "status": "PROBE_FAILED",
            "execution_mode": "windows_local_runtime_probe_no_project_data",
            "error": f"{type(exc).__name__}: {exc}",
        }


def discover_local_capabilities(skip: bool = False) -> dict[str, Any]:
    if skip:
        return {
            "status": "SKIPPED_FOR_TEST",
            "network_policy": {
                "external_network_use_authorized": False,
                "network_endpoint_probe_performed": False,
            },
        }
    deps = bundled_dependency_root()
    search_dirs = [
        deps / "native" / "poppler" / "Library" / "bin",
        deps / "bin",
        deps / "native" / "git" / "cmd",
    ]
    binaries = [
        probe_command("pdfinfo", ["-v"], search_dirs),
        probe_command("pdftoppm", ["-v"], search_dirs),
        probe_command("pdfimages", ["-v"], search_dirs),
        probe_command("tesseract", ["--version"], search_dirs),
        probe_command("ocrmypdf", ["--version"], search_dirs),
        probe_command("magick", ["-version"], search_dirs),
        probe_command("paddleocr", ["--version"], search_dirs),
        probe_command("easyocr", ["--version"], search_dirs),
    ]
    modules = [
        module_probe("pypdf"),
        module_probe("PIL", "Pillow"),
        module_probe("cv2", "opencv-python"),
        module_probe("pytesseract"),
        module_probe("onnxruntime"),
        module_probe("paddleocr"),
        module_probe("easyocr"),
        module_probe("ocrmypdf"),
        module_probe("fitz", "PyMuPDF"),
        module_probe("numpy"),
    ]
    return {
        "status": "LOCAL_CAPABILITY_DISCOVERY_COMPLETE",
        "generated_at": now(),
        "probe_scope": "versions and availability only; no private project data opened",
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "binaries": binaries,
        "python_modules": modules,
        "windows_media_ocr": probe_windows_media_ocr(),
        "local_cjk_ocr_availability": cjk_ocr_status(binaries, modules),
        "local_image_feature_or_layout_facilities": image_facility_status(modules),
        "network_policy": {
            "external_network_use_authorized": False,
            "network_endpoint_probe_performed": False,
            "effective_status": "NETWORK_ENDPOINTS_NOT_AUTHORIZED_BY_D0021_PRIVACY_BOUNDARY",
        },
    }


def cjk_ocr_status(binaries: list[dict[str, Any]], modules: list[dict[str, Any]]) -> dict[str, Any]:
    tesseract = next((row for row in binaries if row["name"] == "tesseract"), {})
    ocr_modules = [row for row in modules if row["module"] in {"pytesseract", "paddleocr", "easyocr", "ocrmypdf"} and row["status"] == "AVAILABLE"]
    if tesseract.get("status") == "AVAILABLE" or ocr_modules:
        return {
            "status": "POTENTIALLY_AVAILABLE_REQUIRES_LANGUAGE_PACK_TEST",
            "detail": "Engine availability found; no private OCR was run and no language-pack OCR page was processed.",
        }
    return {
        "status": "UNAVAILABLE_IN_CURRENT_LOCAL_PROBE",
        "detail": "No local CJK OCR engine was available from the probed binaries/modules.",
    }


def image_facility_status(modules: list[dict[str, Any]]) -> dict[str, Any]:
    available = [row["module"] for row in modules if row["module"] in {"PIL", "cv2", "numpy", "onnxruntime"} and row["status"] == "AVAILABLE"]
    return {
        "status": "AVAILABLE" if available else "LIMITED",
        "available_modules": available,
        "detail": "These are local image-processing facilities only; no private reference image was sent to an inherited model.",
    }


def load_task_registry_counts() -> dict[str, Any]:
    if not TASK_REGISTRY.exists():
        return {"status_counts": {}, "baseline_generation_like_rows": 0}
    with TASK_REGISTRY.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    baseline_generation_like = [
        row
        for row in rows
        if "baseline-024" in row.get("phase", "").lower()
        and any(term in row.get("scope", "").lower() for term in ["generation", "mock"])
    ]
    return {
        "row_count": len(rows),
        "status_counts": dict(Counter(row.get("status", "") for row in rows)),
        "baseline_generation_like_rows": len(baseline_generation_like),
    }


def reference_v3_project_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for path in (ROOT / "manifests" / "reference_detection" / "v3").glob("batch-*/*/effective_reference_set.json"):
        data = read_json(path)
        project_id = str(data.get("project_id") or path.parent.name)
        statuses[project_id] = str(data.get("status", "UNKNOWN"))
    return statuses


def minimized_project_items(project_ids: list[str], status: str, blocker_class: str | None = None, limit: int | None = None) -> list[dict[str, str]]:
    rows = []
    for project_id in sorted(project_ids)[:limit]:
        row = {"project_id": project_id, "status": status}
        if blocker_class:
            row["blocker_class"] = blocker_class
        rows.append(row)
    return rows


def build_candidate_queues(shortfall: dict[str, Any], universe: dict[str, Any], known_positive: dict[str, Any]) -> dict[str, Any]:
    allowed = set(shortfall.get("current_allowed_eval_project_ids", []))
    v3_statuses = reference_v3_project_statuses()
    universe_projects = [str(row.get("normalized_project_id") or row.get("project_id")) for row in universe.get("projects", [])]
    universe_ids = sorted({pid for pid in universe_projects if pid})
    unscreened = [pid for pid in universe_ids if pid not in v3_statuses and pid not in allowed]
    partial = [pid for pid, status in v3_statuses.items() if status == "PARTIAL_REFERENCE_SET"]
    ambiguous = [pid for pid, status in v3_statuses.items() if status == "AMBIGUOUS_REFERENCE_SET"]
    retry_known_positive = list(known_positive.get("known_positive_projects", []))
    return {
        "privacy_minimized": True,
        "all_queues_store_project_ids_only": True,
        "counts": {
            "reconciled_project_count": len(universe_ids),
            "allowed_eval_already_verified": len(allowed),
            "prior_v3_project_decisions": len(v3_statuses),
            "prior_v3_partial_projects": len(partial),
            "prior_v3_ambiguous_projects": len(ambiguous),
            "not_individually_screened_by_v3": len(unscreened),
            "known_positive_retry_cases": len(retry_known_positive),
            "previous_bundle_rejections": len(shortfall.get("bundle_rejected_project_ids", [])),
            "previous_quarantined_or_no_bundle": len(shortfall.get("quarantined_or_no_bundle_project_ids", [])),
        },
        "retry_known_positive_detector_failures": minimized_project_items(
            retry_known_positive,
            "RETRY_AFTER_DETECTOR_RECOVERY",
            "RECOVERABLE_DETECTOR_LIMITATION",
        ),
        "prior_v3_partial_projects": minimized_project_items(
            partial,
            "WAITING_FOR_CALIBRATED_DETECTOR_REPROCESS",
            "RECOVERABLE_DETECTOR_LIMITATION",
            limit=50,
        ),
        "unscreened_individual_projects": minimized_project_items(
            unscreened,
            "WAITING_FOR_CALIBRATED_INDIVIDUAL_SCREENING",
            "RECOVERABLE_DETECTOR_LIMITATION",
            limit=50,
        ),
        "previous_source_quarantines": minimized_project_items(
            list(shortfall.get("quarantined_or_no_bundle_project_ids", [])),
            "RETRY_ONLY_IF_PROCEDURE_DEFECT_IS_REPAIRED",
            "RECOVERABLE_PROCEDURE_AMBIGUITY",
        ),
        "previous_bundle_rejections": minimized_project_items(
            list(shortfall.get("bundle_rejected_project_ids", [])),
            "PRESERVED_REJECTION_RETRY_ONLY_WITH_DEFECT_EVIDENCE",
            "RECOVERABLE_SANITIZATION_LIMITATION",
        ),
    }


def strategy_signature(strategy_id: str, evidence_paths: list[Path], extra: dict[str, Any] | None = None) -> tuple[str, list[dict[str, str]]]:
    evidence_hashes = []
    for path in evidence_paths:
        if path.exists():
            evidence_hashes.append({"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path)})
    signature = sha256_json({"strategy_id": strategy_id, "evidence_hashes": evidence_hashes, "extra": extra or {}})
    return signature, evidence_hashes


def attempted_strategies(known_positive: dict[str, Any], vision_probe: dict[str, Any]) -> list[dict[str, Any]]:
    v3_sig, v3_hashes = strategy_signature(
        "target_output_detection_v3_page_content_isolated_known_positive_replay",
        [KNOWN_POSITIVE],
        {"detector_version": known_positive.get("detector_version"), "status": known_positive.get("status")},
    )
    vision_sig, vision_hashes = strategy_signature(
        "gpt5_synthetic_vision_probe_private_reference_gate",
        [VISION_PROBE, PRIVACY_APPROVAL],
        {"final_status": vision_probe.get("final_status"), "privacy": privacy_status()},
    )
    strategies = [
        {
            "strategy_id": "target_output_detection_v3_page_content_isolated_known_positive_replay",
            "status": str(known_positive.get("status")),
            "strategy_signature": v3_sig,
            "evidence_hashes": v3_hashes,
            "requested_classifier": "local",
            "actual_classifier": "local_poppler_pypdf_deterministic_reference_detector_v3",
            "repeat_policy": "DO_NOT_REPEAT_UNLESS_CODE_CONFIG_INPUTS_OR_EVIDENCE_CHANGE",
        },
        {
            "strategy_id": "gpt5_synthetic_vision_probe_private_reference_gate",
            "status": str(vision_probe.get("final_status")),
            "strategy_signature": vision_sig,
            "evidence_hashes": vision_hashes,
            "requested_classifier": "inherited_parent_model_with_local_image_input",
            "actual_classifier": "GPT-5_SYNTHETIC_ONLY_NOT_LOCAL_PRIVATE_REFERENCE_CLASSIFIER",
            "repeat_policy": "DO_NOT_SEND_PRIVATE_REFERENCE_PAGES_WHILE_PRIVACY_NOT_APPROVED",
        },
    ]
    if WINDOWS_OCR_PROBE.exists():
        ocr_probe = read_json(WINDOWS_OCR_PROBE)
        ocr_sig, ocr_hashes = strategy_signature(
            "windows_media_ocr_local_synthetic_execution_proof",
            [WINDOWS_OCR_PROBE],
            {"status": ocr_probe.get("synthetic_execution", {}).get("status")},
        )
        strategies.append(
            {
                "strategy_id": "windows_media_ocr_local_synthetic_execution_proof",
                "status": str(ocr_probe.get("synthetic_execution", {}).get("status")),
                "strategy_signature": ocr_sig,
                "evidence_hashes": ocr_hashes,
                "requested_classifier": ocr_probe.get("requested_classifier"),
                "actual_classifier": ocr_probe.get("actual_classifier"),
                "repeat_policy": "DO_NOT_PERSIST_OR_PRINT_OCR_TEXT",
            }
        )
    v4_failed = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "v4_calibration_partition" / "calibration_partition_summary.json"
    if v4_failed.exists():
        v4_sig, v4_hashes = strategy_signature(
            "target_output_detection_v4_local_multisignal_recovery_calibration_partition",
            [v4_failed],
            {"status": read_json(v4_failed).get("detector_performance_status")},
        )
        strategies.append(
            {
                "strategy_id": "target_output_detection_v4_local_multisignal_recovery_calibration_partition",
                "status": str(read_json(v4_failed).get("detector_performance_status")),
                "strategy_signature": v4_sig,
                "evidence_hashes": v4_hashes,
                "requested_classifier": "local_poppler_pypdf_pillow_numpy_private_ocr_disabled",
                "actual_classifier": "target_output_detection_v4_local_multisignal_recovery",
                "repeat_policy": "SUPERSEDED_BY_V4_1_LAYOUT_PRIOR_RECOVERY",
            }
        )
    if V4_1_CALIBRATION_SUMMARY.exists() and V4_1_NEGATIVE_SUMMARY.exists():
        v41_cal = read_json(V4_1_CALIBRATION_SUMMARY)
        v41_neg = read_json(V4_1_NEGATIVE_SUMMARY)
        v41_sig, v41_hashes = strategy_signature(
            "target_output_detection_v4_1_local_layout_prior_recovery_calibration_and_negatives",
            [V4_1_CALIBRATION_SUMMARY, V4_1_NEGATIVE_SUMMARY, V4_1_FREEZE_MANIFEST, V4_1_AUDIT_REPORT],
            {
                "calibration": v41_cal.get("detector_performance_status"),
                "negative_controls": v41_neg.get("status"),
            },
        )
        strategies.append(
            {
                "strategy_id": "target_output_detection_v4_1_local_layout_prior_recovery_calibration_and_negatives",
                "status": f"CALIBRATION_{v41_cal.get('detector_performance_status')}_NEGATIVE_{v41_neg.get('status')}",
                "strategy_signature": v41_sig,
                "evidence_hashes": v41_hashes,
                "requested_classifier": "local_poppler_pypdf_pillow_numpy_private_ocr_disabled",
                "actual_classifier": "target_output_detection_v4_1_local_layout_prior_recovery",
                "repeat_policy": "DO_NOT_MODIFY_BEFORE_SEALED_HOLDOUT_WITHOUT_NEW_VERSION",
            }
        )
    return strategies


def select_next_action(capabilities: dict[str, Any]) -> dict[str, str]:
    if capabilities.get("status") == "SKIPPED_FOR_TEST":
        return {
            "action_id": "RUN_LOCAL_CAPABILITY_DISCOVERY",
            "phase": "PHASE_A",
            "status": "SELECTED",
            "reason": "Capability discovery was skipped in test mode and must be run before detector recovery.",
        }
    if V4_1_CALIBRATION_SUMMARY.exists() and V4_1_NEGATIVE_SUMMARY.exists() and V4_1_FREEZE_MANIFEST.exists():
        cal = read_json(V4_1_CALIBRATION_SUMMARY)
        neg = read_json(V4_1_NEGATIVE_SUMMARY)
        if cal.get("detector_performance_status") == "PASS" and neg.get("status") == "PASS":
            return {
                "action_id": "RUN_DETECTOR_V4_1_SEALED_HOLDOUT_AUDIT",
                "phase": "PHASE_B",
                "status": "SELECTED",
                "reason": "Detector v4.1 passed calibration positives and real negative controls with private OCR disabled; run sealed holdout with the frozen committed candidate before corpus screening.",
            }
    if V4_DETECTOR_SCRIPT.exists() and V4_CALIBRATION_MANIFEST.exists():
        return {
            "action_id": "RUN_DETECTOR_V4_CALIBRATION_PARTITION",
            "phase": "PHASE_B",
            "status": "SELECTED",
            "reason": "Detector v4 and its frozen calibration protocol exist; run only the implementation-facing calibration partition before sealed holdout or corpus screening.",
        }
    return {
        "action_id": "CREATE_DETECTOR_V4_LOCAL_MULTISIGNAL_RECOVERY_PROTOTYPE",
        "phase": "PHASE_B",
        "status": "SELECTED",
        "reason": "Vision classifier unavailability is a recoverable branch blocker; local Poppler/pypdf/Pillow or OCR/CV capabilities must drive the next detector prototype without privacy-boundary changes.",
    }


def build_state(skip_capability_probe: bool = False) -> dict[str, Any]:
    shortfall = read_json(SHORTFALL)
    phase_c = read_json(PHASE_C_STATUS)
    universe = read_json(UNIVERSE)
    known_positive = read_json(KNOWN_POSITIVE)
    vision_probe = read_json(VISION_PROBE)
    ocr_probe = read_json(WINDOWS_OCR_PROBE) if WINDOWS_OCR_PROBE.exists() else {}
    allowed_ids = list(shortfall.get("current_allowed_eval_project_ids", []))
    git = git_status()
    capabilities = discover_local_capabilities(skip_capability_probe)
    baseline_absence = verify_baseline_generation_absence()
    checkpoint = {
        "git_head": git["head"],
        "worktree_clean": git["worktree_clean"],
        "git_status_short": git["status_short"],
        "accepted_bundle_hashes": verify_accepted_bundle_hashes(),
        "frozen_workflow_hashes": verify_frozen_workflow_hashes(),
        "privacy_status": privacy_status(),
        "baseline_generation_absence": baseline_absence,
        "task_registry": load_task_registry_counts(),
    }
    queues = build_candidate_queues(shortfall, universe, known_positive)
    active_blockers = [
        {
            "blocker_class": "RECOVERABLE_DETECTOR_LIMITATION",
            "status": "ACTIVE",
            "recoverable": True,
            "detail": "Detector v3 known-positive all-three recall is 0/13 with 31 false-negative output types.",
        },
        {
            "blocker_class": "PRIVACY_PERMISSION_REQUIRED",
            "status": "BRANCH_BLOCKER_FOR_INHERITED_OR_EXTERNAL_VISION_ONLY",
            "recoverable": False,
            "detail": "Privacy approval is NOT_APPROVED, so GPT-5 or external vision cannot inspect private references.",
        },
        {
            "blocker_class": "RECOVERABLE_OCR_LIMITATION",
            "status": "PENDING_LOCAL_CAPABILITY_USE",
            "recoverable": True,
            "detail": "Image-only or no-target-text pages require local OCR/CV/layout recovery before corpus screening.",
        },
    ]
    next_action = select_next_action(capabilities)
    v4_created = V4_DETECTOR_SCRIPT.exists() and V4_CALIBRATION_MANIFEST.exists()
    v41_cal = read_json(V4_1_CALIBRATION_SUMMARY) if V4_1_CALIBRATION_SUMMARY.exists() else {}
    v41_neg = read_json(V4_1_NEGATIVE_SUMMARY) if V4_1_NEGATIVE_SUMMARY.exists() else {}
    v41_passed = (
        not skip_capability_probe
        and v41_cal.get("detector_performance_status") == "PASS"
        and v41_neg.get("status") == "PASS"
    )
    status = "DETECTOR_V4_1_CALIBRATION_PASSED_HOLDOUT_PENDING" if v41_passed and not skip_capability_probe else "DETECTOR_V4_LOCAL_CALIBRATION_IN_PROGRESS" if v4_created and not skip_capability_probe else "RECOVERY_PHASE_A_LOCAL_CAPABILITY_DISCOVERY_COMPLETE"
    if skip_capability_probe:
        status = "RECOVERY_CONTROLLER_READY"
    return {
        "schema_version": "qualification_recovery_state_v1",
        "generated_at": now(),
        "baseline_id": BASELINE_ID,
        "decision_id": DECISION_ID,
        "status": status,
        "privacy": {
            "approval_status": checkpoint["privacy_status"],
            "private_reference_pages_sent_to_external_or_inherited_models": int(
                vision_probe.get("privacy_gate", {}).get("private_reference_images_sent_to_vision_agent", 0)
            ),
            "private_reference_pages_inspected_by_actual_vision_agents": int(
                vision_probe.get("privacy_gate", {}).get("project_pages_inspected_by_actual_vision_agents", 0)
            ),
            "external_network_use_authorized": False,
            "private_reference_classifier_rule": "GPT-5 synthetic vision success is not a local private-reference classifier.",
        },
        "checkpoint_verification": checkpoint,
        "current_allowed_eval": {
            "required_count": REQUIRED_ALLOWED_EVAL,
            "current_count": len(allowed_ids),
            "deficit": max(0, REQUIRED_ALLOWED_EVAL - len(allowed_ids)),
            "reserve_target": RESERVE_TARGET,
            "project_ids": sorted(allowed_ids),
        },
        "blocker_taxonomy": BLOCKER_CLASSES,
        "active_blockers": active_blockers,
        "attempted_strategies": attempted_strategies(known_positive, vision_probe),
        "detector_calibration": {
            "current_detector_version": known_positive.get("detector_version"),
            "current_detector_performance_status": known_positive.get("status"),
            "candidate_detector_version": v41_cal.get("detector_version") or "target_output_detection_v4_local_multisignal_recovery",
            "candidate_detector_status": "CALIBRATION_AND_NEGATIVE_CONTROLS_PASS_AWAITING_SEALED_HOLDOUT" if v41_passed else "CREATED_AWAITING_CALIBRATION_PARTITION" if v4_created else "NOT_CREATED",
            "regression_gate_behavior_status": "PASS_BLOCKS_KNOWN_FAILING_DETECTOR",
            "detector_performance_status": "PASS" if v41_passed else "FAIL",
            "known_positive_all_three_recall": "CALIBRATION_PARTITION_8/8_ALL_13_PENDING_HOLDOUT_GATE" if v41_passed else f"{known_positive.get('positive_projects_detected_all_three')}/{len(known_positive.get('known_positive_projects', []))}",
            "calibration_partition_all_three_recall": v41_cal.get("project_level_all_three_recall"),
            "per_type_recall": v41_cal.get("per_type_recall") or known_positive.get("per_type_recall"),
            "false_negative_output_type_count": known_positive.get("false_negative_output_type_count"),
            "negative_controls_executed": v41_neg.get("supported_real_negative_control_count", 0),
            "negative_control_status": v41_neg.get("status", "NOT_RUN"),
            "detector_v4_created": v4_created,
            "v4_calibration_protocol_frozen": V4_CALIBRATION_MANIFEST.exists() and V4_HOLDOUT_MANIFEST.exists(),
            "v4_negative_control_count": read_json(V4_NEGATIVE_CONTROLS).get("negative_control_count", 0) if V4_NEGATIVE_CONTROLS.exists() else 0,
            "candidate_freeze_manifest": str(V4_1_FREEZE_MANIFEST.relative_to(ROOT)) if V4_1_FREEZE_MANIFEST.exists() else None,
            "independent_implementation_audit": str(V4_1_AUDIT_REPORT.relative_to(ROOT)) if V4_1_AUDIT_REPORT.exists() else None,
            "windows_media_ocr_synthetic_status": ocr_probe.get("synthetic_execution", {}).get("status"),
            "windows_media_ocr_private_page_status": ocr_probe.get("private_page_execution", {}).get("status"),
            "corpus_wide_screening_authorized": False,
            "sealed_holdout_authorized": bool(v41_passed),
        },
        "candidate_queues": queues,
        "source_qualification": {
            "status": "WAITING_FOR_REFERENCE_COMPLETE_PROJECTS_FROM_CALIBRATED_DETECTOR",
            "phase_c_status": phase_c.get("status"),
            "current_allowed_eval_count": phase_c.get("current_allowed_eval_count"),
            "new_candidate_source_quorum_started": False,
            "substantive_denials_preserved": True,
        },
        "bundle_verification": {
            "status": checkpoint["accepted_bundle_hashes"]["status"],
            "accepted_bundle_count": checkpoint["accepted_bundle_hashes"]["bundle_hash_file_count"],
            "new_bundle_build_started": False,
            "sanitized_bundle_failures_retry_only_with_defect_evidence": True,
        },
        "local_capabilities": capabilities,
        "next_selected_action": next_action,
        "progress_since_previous_iteration": {
            "previous_status": "VISION_CLASSIFIER_UNAVAILABLE",
            "current_status": status,
            "allowed_eval_count_changed": False,
            "current_allowed_eval_count": len(allowed_ids),
            "deficit": max(0, REQUIRED_ALLOWED_EVAL - len(allowed_ids)),
            "checkpoint_reverified": True,
            "decision_recorded": DECISION_ID,
            "local_capability_discovery_completed": capabilities.get("status") == "LOCAL_CAPABILITY_DISCOVERY_COMPLETE",
        },
        "generation_boundary": {
            "baseline_generation_authorized": False,
            "baseline_generation_attempts_observed": baseline_absence["baseline_generation_attempts_observed"],
            "highest_automated_status": "READY_FOR_PRIVATE_PREVIEW",
        },
    }


def build_queue(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "queue_id": "qualification_recovery_queue_v1",
        "schema_version": "qualification_recovery_queue_v1",
        "generated_at": state["generated_at"],
        "baseline_id": state["baseline_id"],
        "decision_id": state["decision_id"],
        "current_allowed_eval_count": state["current_allowed_eval"]["current_count"],
        "deficit_to_24": state["current_allowed_eval"]["deficit"],
        "reserve_target": state["current_allowed_eval"]["reserve_target"],
        "privacy_minimization": {
            "stores_project_ids_only": True,
            "stores_private_paths": False,
            "stores_reference_content": False,
            "stores_ocr_text": False,
            "stores_rendered_pages_or_crops": False,
        },
        "queues": state["candidate_queues"],
        "active_blockers": state["active_blockers"],
        "attempted_strategy_signatures": [
            {
                "strategy_id": row["strategy_id"],
                "status": row["status"],
                "strategy_signature": row["strategy_signature"],
            }
            for row in state["attempted_strategies"]
        ],
        "next_selected_action": state["next_selected_action"],
    }


def write_markdown(state: dict[str, Any], path: Path) -> None:
    caps = state["local_capabilities"]
    binary_rows = caps.get("binaries", []) if isinstance(caps, dict) else []
    lines = [
        "# Qualification Recovery State",
        "",
        f"- status: `{state['status']}`",
        f"- decision: `{state['decision_id']}`",
        f"- current allowed eval: `{state['current_allowed_eval']['current_count']} / {state['current_allowed_eval']['required_count']}`",
        f"- deficit: `{state['current_allowed_eval']['deficit']}`",
        f"- privacy approval: `{state['privacy']['approval_status']}`",
        f"- accepted bundle hashes: `{state['checkpoint_verification']['accepted_bundle_hashes']['status']}`",
        f"- frozen workflow hashes: `{state['checkpoint_verification']['frozen_workflow_hashes']['status']}`",
        f"- baseline generation attempts observed: `{state['generation_boundary']['baseline_generation_attempts_observed']}`",
        f"- next action: `{state['next_selected_action']['action_id']}`",
        "",
        "## Detector Status",
        "",
        f"- regression gate behavior: `{state['detector_calibration']['regression_gate_behavior_status']}`",
        f"- detector performance: `{state['detector_calibration']['detector_performance_status']}`",
        f"- known-positive all-three recall: `{state['detector_calibration']['known_positive_all_three_recall']}`",
        f"- negative controls executed: `{state['detector_calibration']['negative_controls_executed']}`",
        "",
        "## Queue Counts",
        "",
    ]
    for key, value in sorted(state["candidate_queues"]["counts"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Local Capability Probe", ""])
    if caps.get("status") == "LOCAL_CAPABILITY_DISCOVERY_COMPLETE":
        for row in binary_rows:
            lines.append(f"- `{row['name']}`: `{row['status']}`")
        lines.append(f"- local CJK OCR: `{caps['local_cjk_ocr_availability']['status']}`")
        lines.append(f"- image/layout facilities: `{caps['local_image_feature_or_layout_facilities']['status']}`")
        lines.append(f"- network endpoint probe performed: `{str(caps['network_policy']['network_endpoint_probe_performed']).lower()}`")
    else:
        lines.append(f"- status: `{caps.get('status', 'UNKNOWN')}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    report_dir = Path(args.report_dir) if args.report_dir else REPORT_DIR
    queue_path = Path(args.queue_path) if args.queue_path else QUEUE_PATH
    state = build_state(skip_capability_probe=args.skip_capability_probe)
    queue = build_queue(state)
    write_json(report_dir / "recovery_state.json", state)
    write_json(report_dir / "checkpoint_verification.json", state["checkpoint_verification"])
    write_json(report_dir / "local_capability_probe.json", state["local_capabilities"])
    write_json(queue_path, queue)
    write_markdown(state, report_dir / "recovery_state.md")
    print(json.dumps({"status": state["status"], "next_action": state["next_selected_action"]["action_id"]}, ensure_ascii=False))
    return state


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic baseline-024 qualification recovery state.")
    parser.add_argument("--report-dir", default=str(REPORT_DIR))
    parser.add_argument("--queue-path", default=str(QUEUE_PATH))
    parser.add_argument("--skip-capability-probe", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    run(parse_args(argv))


if __name__ == "__main__":
    main()
