from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from build_sanitized_generator_bundle import sanitize_sheet_to_csv
from harness_lib import detect_forbidden_text, sha256_file, sha256_json, write_json
from legacy_xls_parser import build_decisions as build_legacy_xls_decisions
from source_guard import (
    DECISION_FIELDS,
    SOURCE_ROOT_PATH,
    csv_rows,
    csv_write,
    decisions_for_project,
    flatten_decision,
    source_path_from_row,
    worksheet_fingerprint,
)


POLICY_VERSION = "source_guard_policy_v2_autonomous_eval"
BASELINE_ID = "baseline-024-cycle-000"
PLAN_ID = "baseline024_phase_c_backfill_plan_v1"
REVIEW_ROLES = [
    "source_role_classifier",
    "project_identity_reviewer",
    "workbook_forensics_reviewer",
    "leakage_red_team",
]
APPROVABLE_PROPOSED_STATES = {"CANDIDATE", "NEEDS_HUMAN_REVIEW"}
APPROVABLE_ROLES = {
    "allowed_contract_workbook",
    "allowed_material_list_workbook",
    "allowed_supporting_workbook",
    "spreadsheet_other",
}
EXTRA_DECISION_FIELDS = ["sanitized_csv_path", "sanitized_csv_sha256", "non_empty_rows"]


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def split_pipe(text: str) -> list[str]:
    return [part for part in (text or "").split("|") if part]


def safe_name(text: str) -> str:
    cleaned = []
    for ch in text:
        cleaned.append(ch if ch.isalnum() or ch in "-_" else "_")
    return "".join(cleaned).strip("_") or "item"


def current_git_head(root: Path) -> str:
    git = Path(r"C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe")
    if not git.exists():
        return "GIT_UNAVAILABLE"
    proc = subprocess.run([str(git), "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True)
    return proc.stdout.strip() if proc.returncode == 0 else "GIT_UNAVAILABLE"


def candidate_projects(source_readiness: Path) -> list[dict[str, Any]]:
    data = read_json(source_readiness)
    return list(data["metadata_only_candidate_pool"]["projects"])


def current_decision_rows(project_id: str, file_index: Path, sheet_index: Path) -> list[dict[str, Any]]:
    return [flatten_decision(row) for row in decisions_for_project(project_id, file_index, sheet_index, True)]


def analyze_project(project: dict[str, Any], file_index: Path, sheet_index: Path) -> dict[str, Any]:
    rows = current_decision_rows(project["project_id"], file_index, sheet_index)
    counts = Counter(row.get("proposed_decision", "") for row in rows)
    formats = Counter(row.get("workbook_format", "") for row in rows)
    reviewable = [
        row
        for row in rows
        if row.get("proposed_decision") in APPROVABLE_PROPOSED_STATES
        and row.get("worksheet_visibility") == "visible"
        and row.get("worksheet_fingerprint")
    ]
    parser_required = counts.get("PARSER_REQUIRED", 0)
    score = (
        len(reviewable) * 100
        + int(project.get("workbook_count") or 0)
        - counts.get("AUTO_DENIED", 0) * 15
        - counts.get("QUARANTINED", 0) * 8
        - parser_required
    )
    return {
        "project_id": project["project_id"],
        "project_name": project.get("project_name", ""),
        "workbook_count": project.get("workbook_count", 0),
        "generator_candidate_status": project.get("generator_candidate_status", ""),
        "completed_reference_content_inspected_for_selection": False,
        "current_reviewable_rows": len(reviewable),
        "parser_required_rows": parser_required,
        "decision_counts": dict(counts),
        "workbook_formats": dict(formats),
        "ranking_score": score,
    }


def command_plan(args: argparse.Namespace) -> None:
    projects = candidate_projects(args.source_readiness)
    analyses = [analyze_project(project, args.file_index, args.sheet_index) for project in projects]
    analyses.sort(key=lambda item: (-item["current_reviewable_rows"], -item["ranking_score"], item["project_id"]))
    batches = []
    for index in range(0, len(analyses), args.batch_size):
        batch_no = len(batches) + 1
        batch_id = f"batch-{batch_no:03d}"
        members = analyses[index : index + args.batch_size]
        batches.append(
            {
                "batch_id": batch_id,
                "project_ids": [item["project_id"] for item in members],
                "projects": members,
            }
        )

    plan = {
        "plan_id": PLAN_ID,
        "baseline_id": BASELINE_ID,
        "status": "PHASE_C_BACKFILL_PLAN_READY",
        "created_at": now(),
        "git_head": current_git_head(Path.cwd()),
        "source_readiness": str(args.source_readiness),
        "batch_size": args.batch_size,
        "candidate_count": len(analyses),
        "batches": batches,
        "completed_reference_content_inspected_for_selection": False,
    }
    out = args.output_root / "backfill_plan.json"
    write_json(out, plan)

    lines = [
        "# Baseline-024 Phase C Source Backfill Plan",
        "",
        "Completed-reference content was not inspected for this ranking.",
        "",
        "| batch | project_id | current reviewable rows | parser-required rows | ranking score |",
        "|---|---|---:|---:|---:|",
    ]
    for batch in batches:
        for project in batch["projects"]:
            lines.append(
                f"| `{batch['batch_id']}` | `{project['project_id']}` | "
                f"{project['current_reviewable_rows']} | {project['parser_required_rows']} | {project['ranking_score']} |"
            )
    report = args.output_root / "backfill_plan.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "batches": len(batches), "candidates": len(analyses)}, ensure_ascii=False))


def load_file_rows(file_index: Path) -> dict[str, dict[str, str]]:
    return {row["file_id"]: row for row in csv_rows(file_index)}


def xls_rows_from_legacy_parser(
    project_id: str,
    base_rows: list[dict[str, Any]],
    file_index: Path,
    output_root: Path,
) -> list[dict[str, Any]]:
    if not base_rows:
        return []
    project_root = output_root / "legacy_xls" / project_id
    base_csv = project_root / f"{project_id}_base_xls_decisions.csv"
    write_csv(base_csv, base_rows, DECISION_FIELDS + EXTRA_DECISION_FIELDS)
    report = build_legacy_xls_decisions(project_id, base_csv, file_index, project_root)
    if report.get("status") != "PASS":
        raise SystemExit(f"legacy xls parse failed for {project_id}")
    full = read_json(project_root / f"source_decisions_{project_id}_legacy_xls.full.json")
    return [flatten_decision(row) for row in full]


def combined_decisions_for_project(project_id: str, args: argparse.Namespace, batch_root: Path) -> list[dict[str, Any]]:
    rows = current_decision_rows(project_id, args.file_index, args.sheet_index)
    xlsx_rows = [row for row in rows if row.get("workbook_format") != "xls"]
    xls_base_rows = [row for row in rows if row.get("workbook_format") == "xls"]
    xls_rows = xls_rows_from_legacy_parser(project_id, xls_base_rows, args.file_index, batch_root)
    combined = xlsx_rows + xls_rows
    combined.sort(key=lambda row: (row.get("project_id", ""), row.get("file_id", ""), row.get("sheet_id", ""), row.get("decision_id", "")))
    return combined


def prefilter_from_row(row: dict[str, Any], files: dict[str, dict[str, str]]) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    reasons = set(split_pipe(str(row.get("reason_codes", ""))))
    state = "SUBMIT_TO_REVIEW"

    def add_check(name: str, status: str, evidence: str) -> None:
        checks.append({"check": name, "status": status, "evidence": evidence})

    proposed = row.get("proposed_decision", "")
    if row.get("source_root_id") != "SRC-ALL-PROJECTS":
        state = "AUTO_DENIED"
        reasons.add("OUTSIDE_APPROVED_ROOT")
        add_check("source_root", "FAIL", str(row.get("source_root_id", "")))
    else:
        add_check("source_root", "PASS", "SRC-ALL-PROJECTS")

    if proposed == "AUTO_DENIED":
        state = "AUTO_DENIED"
    elif proposed == "PARSER_REQUIRED":
        state = "PARSER_REQUIRED"
    elif proposed in {"QUARANTINED", "SUPERSEDED"}:
        state = "QUARANTINED"
    elif proposed not in APPROVABLE_PROPOSED_STATES:
        state = "QUARANTINED"
        reasons.add(f"UNAPPROVABLE_PROPOSED_STATE_{proposed}")

    if detect_forbidden_text(str(row.get("relative_path", ""))) or detect_forbidden_text(str(row.get("worksheet_name", ""))):
        state = "AUTO_DENIED"
        reasons.add("FORBIDDEN_PATH_OR_NAME_SIGNAL")
    if row.get("detected_document_role") not in APPROVABLE_ROLES:
        if state == "SUBMIT_TO_REVIEW":
            state = "QUARANTINED"
        reasons.add(f"UNSUPPORTED_SOURCE_ROLE_{row.get('detected_document_role', 'UNKNOWN')}")
    if row.get("worksheet_visibility") != "visible":
        state = "QUARANTINED" if state != "AUTO_DENIED" else state
        reasons.add("WORKSHEET_NOT_VISIBLE")
    if not row.get("worksheet_fingerprint"):
        state = "PARSER_REQUIRED" if state != "AUTO_DENIED" else state
        reasons.add("MISSING_WORKSHEET_FINGERPRINT")
    if row.get("formula_dependency_status") not in {"", "NONE"}:
        state = "QUARANTINED" if state != "AUTO_DENIED" else state
        reasons.add("FORMULA_DEPENDENCY_NOT_NONE")
    if row.get("external_link_status") not in {"", "NONE"}:
        state = "QUARANTINED" if state != "AUTO_DENIED" else state
        reasons.add("EXTERNAL_LINK_NOT_NONE")
    if row.get("named_range_status") not in {"", "NONE"}:
        state = "QUARANTINED" if state != "AUTO_DENIED" else state
        reasons.add("NAMED_RANGE_NOT_NONE")
    if row.get("revision_status") not in {"", "CURRENT_OR_UNKNOWN"}:
        state = "QUARANTINED" if state != "AUTO_DENIED" else state
        reasons.add("REVISION_STATUS_NOT_CURRENT")

    detected_ids = split_pipe(str(row.get("detected_project_identifiers", "")))
    if row.get("project_id") not in detected_ids:
        state = "QUARANTINED" if state == "SUBMIT_TO_REVIEW" else state
        reasons.add("PROJECT_ID_NOT_SUPPORTED_BY_DETECTED_IDENTIFIERS")
    elif any(pid != row.get("project_id") for pid in detected_ids):
        state = "AUTO_DENIED"
        reasons.add("CROSS_PROJECT_IDENTITY")

    file_row = files[row["file_id"]]
    source_path = source_path_from_row(file_row)
    try:
        actual_hash = sha256_file(source_path)
        if actual_hash.upper() == str(row.get("file_sha256", "")).upper():
            add_check("file_sha256", "PASS", actual_hash)
        else:
            state = "AUTO_DENIED"
            reasons.add("SOURCE_MUTATION")
            add_check("file_sha256", "FAIL", actual_hash)
    except Exception as exc:
        state = "AUTO_DENIED"
        reasons.add("SOURCE_MISSING_OR_UNREADABLE")
        add_check("file_sha256", "FAIL", f"{type(exc).__name__}: {exc}")

    if row.get("workbook_format") == "xls" and row.get("sanitized_csv_path"):
        csv_path = Path(str(row["sanitized_csv_path"]))
        if csv_path.exists() and sha256_file(csv_path).upper() == str(row.get("sanitized_csv_sha256", "")).upper():
            add_check("legacy_xls_parser_output", "PASS", str(row.get("sanitized_csv_sha256", "")))
        else:
            state = "PARSER_REQUIRED" if state != "AUTO_DENIED" else state
            reasons.add("LEGACY_XLS_PARSER_OUTPUT_MISSING_OR_CHANGED")
            add_check("legacy_xls_parser_output", "FAIL", str(csv_path))
    elif row.get("worksheet_fingerprint") and state not in {"AUTO_DENIED", "PARSER_REQUIRED"}:
        try:
            fp = worksheet_fingerprint(source_path, str(row["worksheet_name"]))
            if fp["fingerprint"] == row["worksheet_fingerprint"]:
                add_check("worksheet_fingerprint", "PASS", fp["fingerprint"])
            else:
                state = "AUTO_DENIED"
                reasons.add("WORKSHEET_FINGERPRINT_MUTATION")
                add_check("worksheet_fingerprint", "FAIL", fp["fingerprint"])
        except Exception as exc:
            state = "PARSER_REQUIRED" if state != "AUTO_DENIED" else state
            reasons.add("WORKSHEET_FINGERPRINT_UNREADABLE")
            add_check("worksheet_fingerprint", "FAIL", f"{type(exc).__name__}: {exc}")

    return {
        "decision_id": row["decision_id"],
        "file_id": row["file_id"],
        "sheet_id": row.get("sheet_id", ""),
        "project_id": row["project_id"],
        "relative_path": row["relative_path"],
        "detected_document_role": row.get("detected_document_role", ""),
        "file_sha256": row["file_sha256"],
        "worksheet_name": row.get("worksheet_name", ""),
        "worksheet_visibility": row.get("worksheet_visibility", ""),
        "worksheet_fingerprint": row.get("worksheet_fingerprint", ""),
        "proposed_decision": proposed,
        "prefilter_state": state,
        "reason_codes": sorted(reasons),
        "checks": checks,
        "reviewable": state == "SUBMIT_TO_REVIEW",
    }


def command_prepare_batch(args: argparse.Namespace) -> None:
    plan = read_json(args.plan)
    batches = {batch["batch_id"]: batch for batch in plan["batches"]}
    if args.batch_id not in batches:
        raise SystemExit(f"unknown batch {args.batch_id}")
    batch = batches[args.batch_id]
    batch_root = args.output_root / args.batch_id
    project_root = batch_root / "project_manifests"
    batch_root.mkdir(parents=True, exist_ok=True)
    files = load_file_rows(args.file_index)

    all_rows: list[dict[str, Any]] = []
    project_summaries = []
    for project_id in batch["project_ids"]:
        rows = combined_decisions_for_project(project_id, args, batch_root)
        all_rows.extend(rows)
        out_dir = project_root / project_id
        out_dir.mkdir(parents=True, exist_ok=True)
        items = [prefilter_from_row(row, files) for row in rows]
        counts = Counter(item["prefilter_state"] for item in items)
        prefilter = {
            "prefilter_id": f"baseline024_{args.batch_id}_prefilter_{project_id}",
            "project_id": project_id,
            "policy_version": POLICY_VERSION,
            "status": "PASS_SUBMIT_TO_REVIEW" if counts["SUBMIT_TO_REVIEW"] else "NO_REVIEWABLE_ITEMS",
            "items": items,
            "summary": dict(counts),
            "run_metadata": {
                "baseline_id": BASELINE_ID,
                "batch_id": args.batch_id,
                "created_at": now(),
                "source_decisions": str(batch_root / "source_decisions.csv"),
                "file_index": str(args.file_index),
                "sheet_index": str(args.sheet_index),
            },
        }
        review_input = {
            "project_id": project_id,
            "policy_version": POLICY_VERSION,
            "reviewable_items": [item for item in items if item["reviewable"]],
            "excluded_items": [item for item in items if not item["reviewable"]],
        }
        write_json(out_dir / "deterministic_prefilter.json", prefilter)
        write_json(out_dir / "review_input.json", review_input)
        project_summaries.append(
            {
                "project_id": project_id,
                "status": prefilter["status"],
                "summary": dict(counts),
                "prefilter_path": str(out_dir / "deterministic_prefilter.json"),
                "review_input_path": str(out_dir / "review_input.json"),
            }
        )

    fields = DECISION_FIELDS + [field for field in EXTRA_DECISION_FIELDS if field not in DECISION_FIELDS]
    write_csv(batch_root / "source_decisions.csv", all_rows, fields)
    batch_manifest = {
        "batch_id": args.batch_id,
        "baseline_id": BASELINE_ID,
        "status": "PREFILTER_READY_FOR_SPECIALIST_REVIEWS",
        "policy_version": POLICY_VERSION,
        "created_at": now(),
        "git_head": current_git_head(Path.cwd()),
        "project_ids": batch["project_ids"],
        "source_decisions": str(batch_root / "source_decisions.csv"),
        "project_manifest_root": str(project_root),
        "counts": dict(Counter(row.get("proposed_decision", "") for row in all_rows)),
        "projects": project_summaries,
        "completed_reference_content_inspected_for_selection": False,
    }
    write_json(batch_root / "batch_manifest.json", batch_manifest)
    write_json(project_root / "prefilter_summary.json", {"policy_version": POLICY_VERSION, "projects": project_summaries})
    print(json.dumps({"status": "PASS", "batch_id": args.batch_id, "projects": batch["project_ids"]}, ensure_ascii=False))


def copy_xls_parser_artifact(row: dict[str, Any], output_path: Path) -> int:
    source = Path(str(row["sanitized_csv_path"]))
    text = source.read_text(encoding="utf-8-sig")
    text = text.replace(str(SOURCE_ROOT_PATH), "[SRC-ALL-PROJECTS]")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8-sig", newline="")
    with output_path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for line in f if line.strip())


def load_batch_decisions(batch_root: Path) -> dict[str, dict[str, str]]:
    return {row["decision_id"]: row for row in csv_rows(batch_root / "source_decisions.csv")}


def command_build_bundles(args: argparse.Namespace) -> None:
    batch_root = args.source_root / args.batch_id
    project_root = batch_root / "project_manifests"
    bundle_root = args.bundle_root / args.batch_id
    working_root = bundle_root / "_working"
    accepted_root = bundle_root / "accepted"
    rejected_root = bundle_root / "rejected"
    decisions = load_batch_decisions(batch_root)
    files = load_file_rows(args.file_index)
    built = []
    rejected = []
    for project_dir in sorted(p for p in project_root.iterdir() if p.is_dir()):
        adjudication_path = project_dir / "adjudication.json"
        if not adjudication_path.exists():
            continue
        adjudication = read_json(adjudication_path)
        approved = [item for item in adjudication["items"] if item["final_state"] == "AGENT_QUORUM_APPROVED_EVAL"]
        if not approved:
            continue
        project_id = adjudication["project_id"]
        out_dir = working_root / project_id
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        artifacts = []
        provenance = []
        approval_rows = []
        for item in approved:
            decision = decisions[item["decision_id"]]
            file_row = files[decision["file_id"]]
            workbook_path = source_path_from_row(file_row)
            if sha256_file(workbook_path).upper() != decision["file_sha256"].upper():
                raise SystemExit(f"source hash changed {item['decision_id']}")
            safe_sheet = safe_name(str(decision.get("worksheet_name", "")))
            safe_file = f"{decision['decision_id']}_{safe_sheet}.csv"
            artifact_path = out_dir / "sanitized_inputs" / safe_file
            if decision.get("sanitized_csv_path"):
                row_count = copy_xls_parser_artifact(decision, artifact_path)
            else:
                fp = worksheet_fingerprint(workbook_path, decision["worksheet_name"])
                if fp["fingerprint"] != decision["worksheet_fingerprint"]:
                    raise SystemExit(f"worksheet fingerprint changed {item['decision_id']}")
                row_count = sanitize_sheet_to_csv(workbook_path, decision["worksheet_name"], artifact_path)
            preview_path = out_dir / "previews" / f"{decision['decision_id']}_{safe_sheet}.md"
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            preview_path.write_text(
                "\n".join(
                    [
                        "# Sanitized Preview",
                        "",
                        f"Decision: `{decision['decision_id']}`",
                        f"Worksheet: `{decision['worksheet_name']}`",
                        f"Rows: {row_count}",
                        "Original workbook excluded from bundle.",
                        "",
                    ]
                ),
                encoding="utf-8",
                newline="\n",
            )
            artifact_hash = sha256_file(artifact_path)
            artifacts.append(
                {
                    "artifact_id": decision["decision_id"],
                    "path": str(artifact_path.relative_to(out_dir)),
                    "sha256": artifact_hash,
                    "source_decision_id": decision["decision_id"],
                }
            )
            provenance.append(
                {
                    "source_decision_id": decision["decision_id"],
                    "source_file_id": decision["file_id"],
                    "source_sheet_id": decision["sheet_id"],
                    "neutral_source_id": f"SRC-{decision['decision_id']}",
                    "sanitized_artifact": str(artifact_path.relative_to(out_dir)),
                }
            )
            approval_rows.append(
                {
                    "decision_id": decision["decision_id"],
                    "human_decision": "NOT_APPLICABLE_EVAL",
                    "agent_decision": "AGENT_QUORUM_APPROVED_EVAL",
                    "reviewer": "source_adjudicator",
                    "file_sha256": decision["file_sha256"],
                    "worksheet_fingerprint": decision["worksheet_fingerprint"],
                    "notes": "Autonomous evaluation-only quorum; not production approval.",
                }
            )

        bundle_id = f"baseline024-{args.batch_id}-{project_id}"
        bundle_manifest = {
            "bundle_id": bundle_id,
            "project_id": project_id,
            "policy_version": POLICY_VERSION,
            "status": "BUILT_PENDING_VERIFICATION",
            "approval_mode": "AUTONOMOUS_EVALUATION_ONLY",
            "artifacts": artifacts,
        }
        approval_manifest = {
            "approval_manifest_id": f"approval-{bundle_id}",
            "policy_version": POLICY_VERSION,
            "status": "PASS",
            "approval_mode": "AUTONOMOUS_EVALUATION_ONLY",
            "decisions": approval_rows,
            "approved_count": len(approval_rows),
            "approval_manifest_hash": "",
        }
        approval_manifest["approval_manifest_hash"] = sha256_json(approval_manifest)
        visible_file_manifest = {
            "bundle_id": bundle_id,
            "files": [{"path": artifact["path"], "sha256": artifact["sha256"]} for artifact in artifacts],
        }
        write_json(out_dir / "bundle_manifest.json", bundle_manifest)
        write_json(out_dir / "approval_manifest.json", approval_manifest)
        write_json(out_dir / "visible_file_manifest.json", visible_file_manifest)
        write_json(out_dir / "provenance_map.json", {"bundle_id": bundle_id, "rows": provenance})
        write_json(out_dir / "verification_results.json", {"status": "PENDING_VERIFICATION", "errors": ["BUNDLE_NOT_VERIFIED"], "warnings": [], "artifact_count": len(artifacts)})
        write_json(out_dir / "bundle_hashes.json", {})
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/verify_generator_bundle.py",
                "--bundle-dir",
                str(out_dir),
                "--output",
                str(out_dir / "verification_results.json"),
            ],
            cwd=Path.cwd(),
            text=True,
            capture_output=True,
        )
        if proc.returncode:
            write_json(
                out_dir / "build_status.json",
                {
                    "status": "REJECTED_BY_BUNDLE_VERIFICATION",
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "created_at": now(),
                },
            )
            rejected_dir = rejected_root / project_id
            if rejected_dir.exists():
                shutil.rmtree(rejected_dir)
            rejected_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(out_dir), str(rejected_dir))
            rejected.append(
                {
                    "project_id": project_id,
                    "bundle_dir": str(rejected_dir),
                    "artifact_count": len(artifacts),
                    "reason": "BUNDLE_VERIFICATION_FAILED",
                }
            )
            continue
        write_json(
            out_dir / "bundle_hashes.json",
            {
                "bundle_manifest": sha256_file(out_dir / "bundle_manifest.json"),
                "approval_manifest": sha256_file(out_dir / "approval_manifest.json"),
                "visible_file_manifest": sha256_file(out_dir / "visible_file_manifest.json"),
                "provenance_map": sha256_file(out_dir / "provenance_map.json"),
                "verification_results": sha256_file(out_dir / "verification_results.json"),
                "artifacts": artifacts,
            },
        )
        write_json(out_dir / "build_status.json", {"status": "VERIFIED", "created_at": now()})
        accepted_dir = accepted_root / project_id
        if accepted_dir.exists():
            shutil.rmtree(accepted_dir)
        accepted_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(out_dir), str(accepted_dir))
        built.append({"project_id": project_id, "bundle_dir": str(accepted_dir), "artifact_count": len(artifacts)})
    if working_root.exists() and not any(working_root.iterdir()):
        working_root.rmdir()
    status = "PASS" if not rejected else "PASS_WITH_REJECTIONS"
    write_json(
        bundle_root / "bundle_build_summary.json",
        {
            "baseline_id": BASELINE_ID,
            "batch_id": args.batch_id,
            "policy_version": POLICY_VERSION,
            "status": status,
            "built": built,
            "rejected": rejected,
        },
    )
    print(json.dumps({"status": status, "batch_id": args.batch_id, "built": built, "rejected": rejected}, ensure_ascii=False))


def audit_one_bundle(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    required = [
        "bundle_manifest.json",
        "approval_manifest.json",
        "visible_file_manifest.json",
        "provenance_map.json",
        "verification_results.json",
        "bundle_hashes.json",
    ]
    for rel in required:
        if not (bundle_dir / rel).exists():
            errors.append(f"MISSING_{rel}")
    if errors:
        return errors
    verification = read_json(bundle_dir / "verification_results.json")
    if verification.get("status") != "PASS":
        errors.append("VERIFICATION_NOT_PASS")
    for path in bundle_dir.rglob("*"):
        if path.is_symlink():
            errors.append(f"SYMLINK:{path.relative_to(bundle_dir)}")
        if path.is_file() and path.suffix.lower() in {".xls", ".xlsx", ".xlsm", ".xlsb"}:
            errors.append(f"ORIGINAL_WORKBOOK_EXTENSION:{path.relative_to(bundle_dir)}")
        if path.is_file():
            rel = str(path.relative_to(bundle_dir))
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = ""
            if str(SOURCE_ROOT_PATH) in text:
                errors.append(f"ABSOLUTE_SOURCE_PATH_LEAK:{rel}")
            if detect_forbidden_text(rel) or detect_forbidden_text(text):
                errors.append(f"FORBIDDEN_SENTINEL:{rel}")
    return sorted(set(errors))


def command_audit_bundles(args: argparse.Namespace) -> None:
    bundle_root = args.bundle_root / args.batch_id / "accepted"
    projects = []
    errors: list[str] = []
    if not bundle_root.exists():
        errors.append("BUNDLE_ROOT_MISSING")
    else:
        for bundle_dir in sorted(p for p in bundle_root.iterdir() if p.is_dir()):
            project_errors = audit_one_bundle(bundle_dir)
            manifest = read_json(bundle_dir / "bundle_manifest.json") if (bundle_dir / "bundle_manifest.json").exists() else {}
            projects.append(
                {
                    "project_id": bundle_dir.name,
                    "artifact_count": len(manifest.get("artifacts", [])),
                    "status": "PASS" if not project_errors else "FAIL",
                    "errors": project_errors,
                }
            )
            errors.extend(f"{bundle_dir.name}:{err}" for err in project_errors)
    status = "EVAL_SOURCE_BUNDLE_AUDIT_PASS" if not errors else "EVAL_SOURCE_BUNDLE_AUDIT_FAIL"
    result = {
        "audit_id": f"baseline024_{args.batch_id}_source_bundle_audit",
        "baseline_id": BASELINE_ID,
        "batch_id": args.batch_id,
        "policy_version": POLICY_VERSION,
        "status": status,
        "projects": projects,
        "errors": sorted(set(errors)),
        "created_at": now(),
        "git_head": current_git_head(Path.cwd()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, result)
    print(json.dumps({"status": status, "projects": len(projects), "errors": len(errors)}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline-024 Phase C source backfill helper.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan")
    plan.add_argument("--source-readiness", type=Path, default=Path("evals/baseline-024/source_readiness.json"))
    plan.add_argument("--file-index", type=Path, default=Path("manifests/all_projects_file_role_index.csv"))
    plan.add_argument("--sheet-index", type=Path, default=Path("manifests/all_projects_workbook_sheet_index.csv"))
    plan.add_argument("--output-root", type=Path, default=Path("manifests/baseline-024/source_candidates"))
    plan.add_argument("--batch-size", type=int, default=6)
    plan.set_defaults(func=command_plan)

    prepare = sub.add_parser("prepare-batch")
    prepare.add_argument("--plan", type=Path, default=Path("manifests/baseline-024/source_candidates/backfill_plan.json"))
    prepare.add_argument("--batch-id", required=True)
    prepare.add_argument("--file-index", type=Path, default=Path("manifests/all_projects_file_role_index.csv"))
    prepare.add_argument("--sheet-index", type=Path, default=Path("manifests/all_projects_workbook_sheet_index.csv"))
    prepare.add_argument("--output-root", type=Path, default=Path("manifests/baseline-024/source_candidates"))
    prepare.set_defaults(func=command_prepare_batch)

    build = sub.add_parser("build-bundles")
    build.add_argument("--batch-id", required=True)
    build.add_argument("--source-root", type=Path, default=Path("manifests/baseline-024/source_candidates"))
    build.add_argument("--bundle-root", type=Path, default=Path("manifests/baseline-024/project_bundles"))
    build.add_argument("--file-index", type=Path, default=Path("manifests/all_projects_file_role_index.csv"))
    build.set_defaults(func=command_build_bundles)

    audit = sub.add_parser("audit-bundles")
    audit.add_argument("--batch-id", required=True)
    audit.add_argument("--bundle-root", type=Path, default=Path("manifests/baseline-024/project_bundles"))
    audit.add_argument("--output", type=Path, required=True)
    audit.set_defaults(func=command_audit_bundles)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
