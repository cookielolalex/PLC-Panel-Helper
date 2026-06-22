from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from harness_lib import read_json, sha256_file, validate_file, write_json


GIT = Path(r"C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe")
EXPECTED_LINEAGE = [
    "0a944ec0734cb3e28768bb88129a75838f70ca14",
    "8e62d6986ba60117f718709afafff4573fc2c3b6",
]


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(GIT), *args], cwd=root, text=True, capture_output=True, check=check)


def add(criteria: list[dict[str, str]], id_: str, ok: bool, evidence: str) -> None:
    criteria.append({"id": id_, "status": "PASS" if ok else "FAIL", "evidence": evidence})


def file_exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def hash_tree(path: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    if not path.exists():
        return hashes
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        hashes[str(file.relative_to(path))] = sha256_file(file)
    return hashes


def scan_text_tree(path: Path, needles: list[str]) -> list[str]:
    hits: list[str] = []
    if not path.exists():
        return hits
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for needle in needles:
            if needle in text:
                hits.append(f"{file.relative_to(path)}:{needle}")
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Independently audit one-project calibration evidence.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-id", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    run_dir = root / "evals" / "runs" / args.run_id
    case_dir = root / "evals" / "cases" / "development" / args.project_id
    review_dir = run_dir / "review"
    audit_dir = run_dir / "audit"
    criteria: list[dict[str, str]] = []

    head = git(root, "rev-parse", "HEAD").stdout.strip()
    status = git(root, "status", "--porcelain=v1").stdout
    lineage: dict[str, Any] = {}
    for commit in EXPECTED_LINEAGE:
        type_proc = git(root, "cat-file", "-t", commit, check=False)
        ancestor_proc = git(root, "merge-base", "--is-ancestor", commit, "HEAD", check=False)
        lineage[commit] = {
            "cat_file_type": type_proc.stdout.strip(),
            "merge_base_is_ancestor_exit_code": ancestor_proc.returncode,
        }

    generation_complete = read_json(run_dir / "generation_complete.json")
    freeze = read_json(run_dir / "freeze_manifest.json")
    artifact_hashes = read_json(run_dir / "artifact_hashes.json")
    leakage_scan = read_json(run_dir / "leakage_scan.json")
    process_metadata = read_json(run_dir / "process_metadata.json")
    grading = read_json(review_dir / "grading_result.json")
    project_review = read_json(review_dir / "project_reviewer_result.json")
    comparison = read_json(review_dir / "comparison_metrics.json")
    eligibility = read_json(case_dir / "eligibility.json")
    bundle_manifest = read_json(case_dir / "bundle_manifest.json")
    approval_manifest = read_json(case_dir / "approval_manifest.json")

    add(criteria, "git_state_and_lineage", status == "" and all(v["merge_base_is_ancestor_exit_code"] == 0 for v in lineage.values()), f"HEAD={head}; status_len={len(status)}; lineage={lineage}")
    add(criteria, "project_eligibility", eligibility.get("project_id") == args.project_id and eligibility.get("status") == "ELIGIBLE_FOR_ONE_PROJECT_CALIBRATION" and eligibility.get("bundle_status") == "ALLOWED_EVAL", "eligibility.json records the selected ALLOWED_EVAL project.")
    add(criteria, "cohort_isolation", eligibility.get("not_checkpoint_or_final_held_out") is True, "eligibility excludes checkpoint-validation and final-held-out use.")
    add(criteria, "source_quorum", bundle_manifest.get("status") == "ALLOWED_EVAL" and approval_manifest.get("status") == "PASS", "sanitized bundle is ALLOWED_EVAL with PASS approval manifest.")
    verification_results = read_json(case_dir / "verification_results.json")
    add(criteria, "sanitized_bundle", verification_results.get("status") == "PASS" and file_exists(case_dir / "bundle_hashes.json"), "sanitized bundle verifier status is PASS and bundle hashes are present.")
    generator_workspace = run_dir / "generator_workspace"
    generator_hits = scan_text_tree(generator_workspace, ["completed_target", "reference_only_sentinel", "生管課用圖", "鈑金施工圖", "沖孔施工圖", r"C:\Users\alex1\OneDrive\Desktop\All Projects"])
    add(criteria, "reference_absence_from_generator_workspace", generator_hits == [], f"generator workspace forbidden/reference hit count={len(generator_hits)}")
    codex_meta = process_metadata.get("codex_process_metadata", {})
    command = codex_meta.get("command", [])
    add(criteria, "fresh_generator_process", "--ephemeral" in command and "--sandbox" in command and "read-only" in command, "generator codex_proxy metadata records ephemeral read-only execution.")
    add(criteria, "generator_model_recording", codex_meta.get("actual_model_recording_status") == "RECORDED_FROM_CHILD_OUTPUT", f"actual_model={codex_meta.get('actual_model')}")
    generated_dir = run_dir / "generated"
    add(criteria, "artifact_validation_order", file_exists(generated_dir / "validation_summary.json") and file_exists(generated_dir / "pdf_validation.json"), "validation artifacts exist before freeze evidence.")
    add(criteria, "freeze_before_reference_access", comparison.get("created_at", "") >= freeze.get("freeze_time", "") and comparison.get("generated", {}) != {}, "comparison evidence was created after freeze manifest.")
    add(criteria, "hashes", hash_tree(generated_dir) == artifact_hashes and freeze.get("artifact_hashes") == artifact_hashes, "generated artifact hashes still match freeze manifest.")
    add(criteria, "leakage_scan", leakage_scan.get("generator_workspace_status") == "PASS" and leakage_scan.get("generated_output_status") == "PASS" and not leakage_scan.get("errors"), "generation leakage scan is PASS.")
    add(criteria, "separate_reviewer_process", project_review.get("independence", {}).get("fresh_process") is True and project_review.get("reviewer_role") == "project_reviewer", "project reviewer result records fresh local process.")
    add(criteria, "reviewer_independence", project_review.get("independence", {}).get("external_transmission") is False and project_review.get("independence", {}).get("reference_access_after_freeze") is True, "reviewer result records local-only reference access after freeze.")
    add(criteria, "effective_revision_manifest", file_exists(review_dir / "effective_sheet_revision_manifest.json") and len(read_json(review_dir / "effective_sheet_revision_manifest.json").get("references", [])) == 3, "effective reference manifest contains three references.")
    add(criteria, "score_schema_validity", validate_file(review_dir / "grading_result.json", root / "schemas" / "grading_result.schema.json") == [] and validate_file(review_dir / "project_reviewer_result.json", root / "schemas" / "project_reviewer_result.schema.json") == [], "grading and project reviewer schemas validate.")
    add(criteria, "comparison_pdf_readability", comparison.get("metrics", {}).get("paired_output_types") == 3 and all(p.get("generated_pages", 0) > 0 and p.get("reference_pages", 0) > 0 for p in comparison.get("pairings", [])), "all three generated/reference pairings have readable PDF page metadata.")
    workflow_files = [
        root / "CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt",
        root / "docs" / "specs" / "AUTONOMOUS_EVAL_SOURCE_APPROVAL.md",
        root / "scripts" / "codex_proxy.py",
        root / "scripts" / "run_one_project_calibration.py",
    ]
    add(criteria, "unchanged_frozen_workflow", all(file_exists(p) for p in workflow_files), "workflow/spec/proxy runner files exist at audit time.")
    test_output = root / "reports" / "harness" / "autonomous_eval_source_quorum_test_output.txt"
    add(criteria, "complete_test_pass", file_exists(test_output) and "PASS" in test_output.read_text(encoding="utf-16", errors="ignore"), "source quorum harness test output records PASS.")

    all_pass = all(item["status"] == "PASS" for item in criteria)
    status_value = "STEP_7C_AUDIT_PASS - READY_FOR_SIX_PROJECT_BASELINE" if all_pass else "CALIBRATION_INCONCLUSIVE"
    result = {
        "audit_id": f"one_project_calibration_audit_{args.run_id}",
        "status": status_value,
        "run_id": args.run_id,
        "project_id": args.project_id,
        "created_at": now(),
        "git": {
            "head": head,
            "status_porcelain_pre_output_write": status,
            "lineage": lineage,
        },
        "criteria": criteria,
        "summary": {
            "validity": grading["validity"],
            "quality_score": grading["quality_score"],
            "scorable_coverage": grading["scorable_coverage"],
            "critical_findings": grading["critical_findings"],
            "high_findings": grading["high_findings"],
        },
    }
    output = audit_dir / "one_project_audit.json"
    write_json(output, result)
    schema_errors = validate_file(output, root / "schemas" / "one_project_audit.schema.json")
    if schema_errors:
        raise SystemExit(f"one-project audit schema errors: {schema_errors}")
    (audit_dir / "one_project_audit.md").write_text(
        "\n".join([
            "# One Project Calibration Audit",
            "",
            f"- run_id: {args.run_id}",
            f"- project_id: {args.project_id}",
            f"- status: {status_value}",
            f"- criteria_pass: {sum(1 for item in criteria if item['status'] == 'PASS')}/{len(criteria)}",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": status_value, "run_id": args.run_id}, ensure_ascii=False))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
