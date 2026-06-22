from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_sanitized_generator_bundle import sanitize_sheet_to_csv
from harness_lib import detect_forbidden_text, read_json, sha256_file, sha256_json, validate_file, write_json
from source_guard import csv_rows, source_path_from_row, worksheet_fingerprint


POLICY_VERSION = "source_guard_policy_v2_autonomous_eval"
REVIEW_ROLES = [
    "source_role_classifier",
    "project_identity_reviewer",
    "workbook_forensics_reviewer",
    "leakage_red_team",
]
FORBIDDEN_PATH_TERMS = [
    "生管文件",
    "電機施工圖",
    "生管課用圖",
    "生管用圖",
    "鈑金施工圖",
    "沖孔施工圖",
    "target_output",
    "reference_only_sentinel",
    "completed_target",
]
APPROVABLE_PROPOSED_STATES = {"CANDIDATE", "NEEDS_HUMAN_REVIEW"}
APPROVABLE_ROLES = {
    "allowed_contract_workbook",
    "allowed_material_list_workbook",
    "allowed_supporting_workbook",
    "spreadsheet_other",
}


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def split_pipe(text: str) -> list[str]:
    if not text:
        return []
    return [part for part in text.split("|") if part]


def decisions_by_project(decisions_path: Path) -> dict[str, list[dict[str, str]]]:
    by_project: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in csv_rows(decisions_path):
        by_project[row.get("project_id", "")].append(row)
    return by_project


def load_file_rows(path: Path) -> dict[str, dict[str, str]]:
    return {row["file_id"]: row for row in csv_rows(path)}


def current_git_head(root: Path) -> str:
    git = Path(r"C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe")
    if not git.exists():
        return "GIT_UNAVAILABLE"
    result = subprocess.run([str(git), "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True)
    if result.returncode:
        return "GIT_UNAVAILABLE"
    return result.stdout.strip()


def candidate_rows(readiness: Path) -> list[dict[str, str]]:
    rows = csv_rows(readiness)
    return [row for row in rows if (row.get("current_parser_bundle_possible") or "").lower() == "true"]


def rank_candidates(candidates: list[dict[str, str]]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    family_seen: Counter[str] = Counter()
    for row in candidates:
        family_seen[row.get("family_id", "")] += 1
    for row in candidates:
        parser_success = int(row.get("reviewable_fingerprinted_visible_xlsx_rows") or 0)
        parser_required = int(row.get("parser_required_rows") or 0)
        auto_denied = int(row.get("auto_denied_rows") or 0)
        quarantined = int(row.get("quarantined_rows") or 0)
        workbook_count = int(row.get("workbook_count") or 0)
        decision_rows = int(row.get("candidate_decision_rows") or 0)
        family_duplicate = family_seen[row.get("family_id", "")] > 1
        score = (
            parser_success * 100
            - parser_required * 8
            - auto_denied * 20
            - quarantined * 25
            - workbook_count * 3
            - decision_rows
            - (30 if family_duplicate else 0)
        )
        ranked.append({
            "project_id": row["project_id"],
            "family_id": row.get("family_id", ""),
            "score": score,
            "ranking_factors": {
                "deterministic_parser_success_rows": parser_success,
                "parser_required_rows": parser_required,
                "auto_denied_rows": auto_denied,
                "quarantined_rows": quarantined,
                "permitted_source_completeness_proxy": parser_success,
                "panel_complexity_proxy_workbook_count": workbook_count,
                "candidate_decision_rows": decision_rows,
                "family_duplicate_in_batch": family_duplicate,
                "ordinary_first_calibration_penalty": 30 if family_duplicate else 0,
                "primary_blocker": row.get("primary_blocker", ""),
            },
            "source_row": row,
        })
    ranked.sort(key=lambda item: (-item["score"], item["project_id"]))
    return ranked


def command_identify(args: argparse.Namespace) -> None:
    root = Path.cwd()
    candidates = candidate_rows(args.readiness)
    by_project = decisions_by_project(args.decisions)
    ranked = rank_candidates(candidates)
    manifest = {
        "manifest_id": "autonomous_eval_batch_001",
        "batch_id": "batch-001",
        "policy_version": POLICY_VERSION,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_head": current_git_head(root),
        "source_hash_reverification": str(args.source_hash_report),
        "candidate_count": len(ranked),
        "candidates": [],
    }
    for rank, item in enumerate(ranked, start=1):
        pid = item["project_id"]
        rows = by_project.get(pid, [])
        reviewable = [
            row["decision_id"] for row in rows
            if row.get("proposed_decision") in APPROVABLE_PROPOSED_STATES and row.get("worksheet_fingerprint")
        ]
        excluded = [row["decision_id"] for row in rows if row["decision_id"] not in reviewable]
        manifest["candidates"].append({
            "rank": rank,
            "project_id": pid,
            "family_id": item["family_id"],
            "score": item["score"],
            "reviewable_decision_ids": reviewable,
            "excluded_decision_ids": excluded,
            "ranking_factors": item["ranking_factors"],
        })
    write_json(args.output_manifest, manifest)

    lines = [
        "# Autonomous Candidate Ranking",
        "",
        "Completed-reference PDF content was not inspected for this ranking.",
        "",
        "| rank | project_id | score | reviewable rows | caveats |",
        "|---:|---|---:|---:|---|",
    ]
    for candidate in manifest["candidates"]:
        factors = candidate["ranking_factors"]
        caveats = []
        if factors["parser_required_rows"]:
            caveats.append(f"{factors['parser_required_rows']} parser-required rows excluded")
        if factors["auto_denied_rows"]:
            caveats.append(f"{factors['auto_denied_rows']} auto-denied rows excluded")
        if factors["family_duplicate_in_batch"]:
            caveats.append("duplicate family")
        if not caveats:
            caveats.append("none")
        lines.append(
            f"| {candidate['rank']} | `{candidate['project_id']}` | {candidate['score']} | "
            f"{len(candidate['reviewable_decision_ids'])} | {'; '.join(caveats)} |"
        )
    args.ranking.parent.mkdir(parents=True, exist_ok=True)
    args.ranking.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "candidates": [c["project_id"] for c in manifest["candidates"]]}, ensure_ascii=False))


def prefilter_decision(row: dict[str, str], file_row: dict[str, str]) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    reasons = set(split_pipe(row.get("reason_codes", "")))
    state = "SUBMIT_TO_REVIEW"

    def add_check(name: str, status: str, evidence: str) -> None:
        checks.append({"check": name, "status": status, "evidence": evidence})

    proposed = row.get("proposed_decision", "")
    rel = row.get("relative_path", "")
    if row.get("source_root_id") != "SRC-ALL-PROJECTS":
        state = "AUTO_DENIED"
        reasons.add("OUTSIDE_APPROVED_ROOT")
        add_check("source_root", "FAIL", row.get("source_root_id", ""))
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

    if any(term in rel for term in FORBIDDEN_PATH_TERMS) or detect_forbidden_text(rel):
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

    detected_ids = split_pipe(row.get("detected_project_identifiers", ""))
    if row.get("project_id") not in detected_ids:
        state = "QUARANTINED" if state == "SUBMIT_TO_REVIEW" else state
        reasons.add("PROJECT_ID_NOT_SUPPORTED_BY_DETECTED_IDENTIFIERS")
    elif len([pid for pid in detected_ids if pid != row.get("project_id")]) > 0:
        state = "AUTO_DENIED"
        reasons.add("CROSS_PROJECT_IDENTITY")

    path = source_path_from_row(file_row)
    try:
        actual_hash = sha256_file(path)
        if actual_hash.upper() == row.get("file_sha256", "").upper():
            add_check("file_sha256", "PASS", actual_hash)
        else:
            state = "AUTO_DENIED"
            reasons.add("SOURCE_MUTATION")
            add_check("file_sha256", "FAIL", actual_hash)
    except Exception as exc:
        state = "AUTO_DENIED"
        reasons.add("SOURCE_MISSING_OR_UNREADABLE")
        add_check("file_sha256", "FAIL", f"{type(exc).__name__}: {exc}")

    if row.get("worksheet_fingerprint") and state not in {"AUTO_DENIED", "PARSER_REQUIRED"}:
        try:
            fp = worksheet_fingerprint(path, row["worksheet_name"])
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


def command_prefilter(args: argparse.Namespace) -> None:
    manifest = read_json(args.candidate_manifest)
    by_project = decisions_by_project(args.decisions)
    files = load_file_rows(args.file_index)
    aggregate = {"policy_version": POLICY_VERSION, "projects": [], "counts": Counter()}
    for candidate in manifest["candidates"]:
        pid = candidate["project_id"]
        out_dir = args.output_root / pid
        out_dir.mkdir(parents=True, exist_ok=True)
        items = []
        for row in by_project.get(pid, []):
            items.append(prefilter_decision(row, files[row["file_id"]]))
        counts = Counter(item["prefilter_state"] for item in items)
        status = "PASS_SUBMIT_TO_REVIEW" if counts["SUBMIT_TO_REVIEW"] else "NO_REVIEWABLE_ITEMS"
        prefilter = {
            "prefilter_id": f"deterministic_prefilter_{pid}",
            "project_id": pid,
            "policy_version": POLICY_VERSION,
            "status": status,
            "items": items,
            "summary": dict(counts),
            "run_metadata": {
                "source_decisions": str(args.decisions),
                "file_index": str(args.file_index),
                "candidate_manifest": str(args.candidate_manifest),
            },
        }
        review_input = {
            "project_id": pid,
            "policy_version": POLICY_VERSION,
            "reviewable_items": [item for item in items if item["reviewable"]],
            "excluded_items": [item for item in items if not item["reviewable"]],
        }
        write_json(out_dir / "deterministic_prefilter.json", prefilter)
        write_json(out_dir / "review_input.json", review_input)
        aggregate["projects"].append({
            "project_id": pid,
            "status": status,
            "summary": dict(counts),
            "prefilter_path": str(out_dir / "deterministic_prefilter.json"),
            "review_input_path": str(out_dir / "review_input.json"),
        })
        aggregate["counts"].update(counts)
    aggregate["counts"] = dict(aggregate["counts"])
    write_json(args.output_root / "prefilter_summary.json", aggregate)
    print(json.dumps({"status": "PASS", "counts": aggregate["counts"]}, ensure_ascii=False))


def role_decision(role: str, item: dict[str, Any]) -> tuple[str, list[str], list[str], list[str], float]:
    state = item["prefilter_state"]
    reasons = list(item.get("reason_codes", []))
    risks: list[str] = []
    unresolved: list[str] = []
    if state == "AUTO_DENIED":
        return "DENY", reasons, ["DETERMINISTIC_DENIAL"], [], 1.0
    if state == "PARSER_REQUIRED":
        return "DENY", reasons + ["PARSER_REQUIRED"], ["UNSUPPORTED_PARSER"], [], 1.0
    if state != "SUBMIT_TO_REVIEW":
        return "QUARANTINE", reasons, ["PREFILTER_QUARANTINE"], [], 0.95

    if role == "source_role_classifier":
        if item.get("detected_document_role") in APPROVABLE_ROLES:
            return "ALLOW_EVAL", ["PERMITTED_CURRENT_PROJECT_INPUT_ROLE"], [], [], 0.86
        return "DENY", ["FORBIDDEN_OR_UNCLEAR_ROLE"], ["ROLE_UNSUPPORTED"], [], 0.95
    if role == "project_identity_reviewer":
        if "PROJECT_ID_NOT_SUPPORTED_BY_DETECTED_IDENTIFIERS" in reasons:
            return "QUARANTINE", ["PROJECT_ID_NOT_SUPPORTED"], ["IDENTITY_AMBIGUOUS"], ["project identity not supported"], 0.72
        risks = ["WORKSHEET_CONTENT_IDENTITY_LIMITED"] if "INSUFFICIENT_IDENTITY" in reasons else []
        return "ALLOW_EVAL", ["PROJECT_ID_SUPPORTED_BY_PATH_AND_INVENTORY", "NO_CROSS_PROJECT_SIGNAL"], risks, [], 0.8
    if role == "workbook_forensics_reviewer":
        forensic_blockers = {
            "WORKSHEET_NOT_VISIBLE",
            "FORMULA_DEPENDENCY_NOT_NONE",
            "EXTERNAL_LINK_NOT_NONE",
            "NAMED_RANGE_NOT_NONE",
            "WORKSHEET_FINGERPRINT_UNREADABLE",
        }
        if forensic_blockers.intersection(reasons):
            return "QUARANTINE", sorted(forensic_blockers.intersection(reasons)), ["FORENSIC_BLOCKER"], [], 0.9
        return "ALLOW_EVAL", ["VISIBLE_SUPPORTED_WORKSHEET", "NO_EXTERNAL_LINKS_OR_DENIED_DEPENDENCIES"], [], [], 0.88
    if role == "leakage_red_team":
        leakage_blockers = {"FORBIDDEN_PATH_OR_NAME_SIGNAL", "FORBIDDEN_LABEL_OR_ROLE", "FORBIDDEN_SOURCE"}
        if leakage_blockers.intersection(reasons):
            return "DENY", sorted(leakage_blockers.intersection(reasons)), ["REFERENCE_LEAKAGE_SIGNAL"], [], 0.96
        return "ALLOW_EVAL", ["NO_REFERENCE_LEAKAGE_SIGNAL_IN_ALLOWED_METADATA"], [], [], 0.83
    raise ValueError(f"unknown role: {role}")


def command_review(args: argparse.Namespace) -> None:
    if args.role not in REVIEW_ROLES:
        raise SystemExit(f"unknown role {args.role}")
    items: list[dict[str, Any]] = []
    for project_dir in sorted(p for p in args.prefilter_root.iterdir() if p.is_dir()):
        prefilter = read_json(project_dir / "deterministic_prefilter.json")
        for item in prefilter["items"]:
            decision, reasons, risks, unresolved, confidence = role_decision(args.role, item)
            items.append({
                "project_id": item["project_id"],
                "file_id": item["file_id"],
                "decision_id": item["decision_id"],
                "file_sha256": item["file_sha256"],
                "worksheet_name": item.get("worksheet_name"),
                "worksheet_fingerprint": item.get("worksheet_fingerprint"),
                "project_identity": item["project_id"],
                "decision": decision,
                "reason_codes": reasons,
                "evidence_ids": [item["decision_id"], item["file_id"], item.get("sheet_id", "")],
                "detected_risks": risks,
                "unresolved_issues": unresolved,
                "confidence": confidence,
                "run_metadata": {"mode": "deterministic_specialist_review"},
            })
    review = {
        "review_id": f"{args.role}_batch_001",
        "reviewer_role": args.role,
        "policy_version": POLICY_VERSION,
        "items": items,
        "run_metadata": {
            "prefilter_root": str(args.prefilter_root),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "independence_note": "Generated from role-specific deterministic rules without reading other reviewer outputs.",
        },
    }
    write_json(args.output, review)
    errors = validate_file(args.output, args.schema)
    if errors:
        raise SystemExit(f"review schema errors: {errors}")
    print(json.dumps({"status": "PASS", "role": args.role, "items": len(items)}, ensure_ascii=False))


def load_reviews(review_root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    reviews: dict[str, dict[str, dict[str, Any]]] = {}
    for role in REVIEW_ROLES:
        path = review_root / f"{role}_review.json"
        data = read_json(path)
        if data.get("reviewer_role") != role:
            raise SystemExit(f"review role mismatch in {path}")
        reviews[role] = {item["decision_id"]: item for item in data.get("items", [])}
    return reviews


def command_adjudicate(args: argparse.Namespace) -> None:
    reviews = load_reviews(args.review_root)
    summary_rows = []
    for project_dir in sorted(p for p in args.prefilter_root.iterdir() if p.is_dir()):
        prefilter = read_json(project_dir / "deterministic_prefilter.json")
        adjudicated_items = []
        for item in prefilter["items"]:
            decision_id = item["decision_id"]
            votes = {role: reviews[role].get(decision_id) for role in REVIEW_ROLES}
            reasons = set(item.get("reason_codes", []))
            unresolved: list[str] = []
            if item["prefilter_state"] != "SUBMIT_TO_REVIEW":
                final = item["prefilter_state"]
            else:
                final = "AGENT_QUORUM_APPROVED_EVAL"
                for role, vote in votes.items():
                    if not vote:
                        final = "QUARANTINED"
                        reasons.add(f"MISSING_{role}_VOTE")
                        continue
                    if vote.get("decision") != "ALLOW_EVAL":
                        final = "QUARANTINED" if vote.get("decision") == "QUARANTINE" else "AUTO_DENIED"
                    if vote.get("file_sha256", "").upper() != item.get("file_sha256", "").upper():
                        final = "QUARANTINED"
                        reasons.add(f"{role}_FILE_HASH_MISMATCH")
                    if vote.get("worksheet_fingerprint") != item.get("worksheet_fingerprint"):
                        final = "QUARANTINED"
                        reasons.add(f"{role}_WORKSHEET_FINGERPRINT_MISMATCH")
                    if vote.get("project_id") != item.get("project_id"):
                        final = "QUARANTINED"
                        reasons.add(f"{role}_PROJECT_ID_MISMATCH")
                    if vote.get("unresolved_issues"):
                        final = "QUARANTINED"
                        unresolved.extend([f"{role}:{x}" for x in vote["unresolved_issues"]])
                    reasons.update(vote.get("reason_codes", []))
            adjudicated_items.append({
                "decision_id": decision_id,
                "file_id": item.get("file_id", ""),
                "file_sha256": item.get("file_sha256", ""),
                "worksheet_name": item.get("worksheet_name", ""),
                "worksheet_fingerprint": item.get("worksheet_fingerprint", ""),
                "final_state": final,
                "reason_codes": sorted(reasons),
                "review_votes": {
                    role: (votes[role].get("decision") if votes.get(role) else "MISSING")
                    for role in REVIEW_ROLES
                },
                "unresolved_issues": sorted(set(unresolved)),
            })
        counts = Counter(item["final_state"] for item in adjudicated_items)
        if counts["AGENT_QUORUM_APPROVED_EVAL"]:
            status = "AGENT_QUORUM_APPROVED_EVAL"
        elif counts["AUTO_DENIED"] and not counts["PARSER_REQUIRED"] and not counts["QUARANTINED"]:
            status = "AUTO_DENIED"
        elif counts["PARSER_REQUIRED"] and not counts["QUARANTINED"]:
            status = "PARSER_REQUIRED"
        elif adjudicated_items:
            status = "QUARANTINED"
        else:
            status = "NO_REVIEWABLE_ITEMS"
        adjudication = {
            "adjudication_id": f"source_quorum_adjudication_{prefilter['project_id']}",
            "project_id": prefilter["project_id"],
            "policy_version": POLICY_VERSION,
            "status": status,
            "items": adjudicated_items,
            "summary": dict(counts),
            "run_metadata": {
                "prefilter": str(project_dir / "deterministic_prefilter.json"),
                "review_root": str(args.review_root),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }
        out = project_dir / "adjudication.json"
        write_json(out, adjudication)
        errors = validate_file(out, args.schema)
        if errors:
            raise SystemExit(f"adjudication schema errors {out}: {errors}")
        summary_rows.append({
            "project_id": prefilter["project_id"],
            "status": status,
            **dict(counts),
        })
    write_json(args.prefilter_root / "adjudication_summary.json", {"policy_version": POLICY_VERSION, "projects": summary_rows})
    print(json.dumps({"status": "PASS", "projects": summary_rows}, ensure_ascii=False))


def command_split_reviews(args: argparse.Namespace) -> None:
    for role in REVIEW_ROLES:
        review = read_json(args.review_root / f"{role}_review.json")
        by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in review["items"]:
            by_project[item["project_id"]].append(item)
        for project_id, items in by_project.items():
            out = args.project_root / project_id / {
                "source_role_classifier": "source_role_review.json",
                "project_identity_reviewer": "identity_review.json",
                "workbook_forensics_reviewer": "workbook_forensics_review.json",
                "leakage_red_team": "leakage_red_team_review.json",
            }[role]
            project_review = dict(review)
            project_review["items"] = items
            write_json(out, project_review)
    print(json.dumps({"status": "PASS"}, ensure_ascii=False))


def command_build_bundles(args: argparse.Namespace) -> None:
    decisions = {row["decision_id"]: row for row in csv_rows(args.decisions)}
    files = load_file_rows(args.file_index)
    built = []
    for project_dir in sorted(p for p in args.project_root.iterdir() if p.is_dir()):
        adjudication_path = project_dir / "adjudication.json"
        if not adjudication_path.exists():
            continue
        adjudication = read_json(adjudication_path)
        approved = [item for item in adjudication["items"] if item["final_state"] == "AGENT_QUORUM_APPROVED_EVAL"]
        if not approved:
            continue
        project_id = adjudication["project_id"]
        out_dir = args.bundle_root / project_id
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
            fp = worksheet_fingerprint(workbook_path, decision["worksheet_name"])
            if fp["fingerprint"] != decision["worksheet_fingerprint"]:
                raise SystemExit(f"worksheet fingerprint changed {item['decision_id']}")
            safe_sheet = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in decision["worksheet_name"])
            safe_name = f"{decision['decision_id']}_{safe_sheet}"
            artifact_path = out_dir / "sanitized_inputs" / f"{safe_name}.csv"
            row_count = sanitize_sheet_to_csv(workbook_path, decision["worksheet_name"], artifact_path)
            preview_path = out_dir / "previews" / f"{safe_name}.md"
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            preview_path.write_text(
                "\n".join([
                    "# Sanitized Preview",
                    "",
                    f"Decision: `{decision['decision_id']}`",
                    f"Worksheet: `{decision['worksheet_name']}`",
                    f"Rows: {row_count}",
                    "Original workbook excluded from bundle.",
                    "",
                ]),
                encoding="utf-8",
                newline="\n",
            )
            artifact_hash = sha256_file(artifact_path)
            artifacts.append({
                "artifact_id": decision["decision_id"],
                "path": str(artifact_path.relative_to(out_dir)),
                "sha256": artifact_hash,
                "source_decision_id": decision["decision_id"],
            })
            provenance.append({
                "source_decision_id": decision["decision_id"],
                "source_file_id": decision["file_id"],
                "source_sheet_id": decision["sheet_id"],
                "neutral_source_id": f"SRC-{decision['decision_id']}",
                "sanitized_artifact": str(artifact_path.relative_to(out_dir)),
            })
            approval_rows.append({
                "decision_id": decision["decision_id"],
                "human_decision": "NOT_APPLICABLE_EVAL",
                "agent_decision": "AGENT_QUORUM_APPROVED_EVAL",
                "reviewer": "source_adjudicator",
                "file_sha256": decision["file_sha256"],
                "worksheet_fingerprint": decision["worksheet_fingerprint"],
                "notes": "Autonomous evaluation-only quorum; not production approval.",
            })
        bundle_id = f"eval-bundle-{project_id}"
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
        write_json(out_dir / "verification_results.json", {
            "status": "PENDING_VERIFICATION",
            "errors": ["BUNDLE_NOT_VERIFIED"],
            "warnings": [],
            "artifact_count": len(artifacts),
        })
        write_json(out_dir / "bundle_hashes.json", {
            "bundle_manifest": sha256_file(out_dir / "bundle_manifest.json"),
            "approval_manifest": sha256_file(out_dir / "approval_manifest.json"),
            "visible_file_manifest": sha256_file(out_dir / "visible_file_manifest.json"),
            "provenance_map": sha256_file(out_dir / "provenance_map.json"),
            "verification_results": sha256_file(out_dir / "verification_results.json"),
            "artifacts": artifacts,
        })
        built.append({"project_id": project_id, "bundle_dir": str(out_dir), "artifact_count": len(artifacts)})
    write_json(args.bundle_root / "bundle_build_summary.json", {"policy_version": POLICY_VERSION, "built": built})
    print(json.dumps({"status": "PASS", "built": built}, ensure_ascii=False))


def command_audit_bundles(args: argparse.Namespace) -> None:
    errors: list[str] = []
    warnings: list[str] = []
    projects = []
    for bundle_dir in sorted(p for p in args.bundle_root.iterdir() if p.is_dir()):
        project_id = bundle_dir.name
        verification = bundle_dir / "verification_results.json"
        bundle_manifest = bundle_dir / "bundle_manifest.json"
        approval_manifest = bundle_dir / "approval_manifest.json"
        if not verification.exists():
            errors.append(f"{project_id}:MISSING_VERIFICATION_RESULTS")
            continue
        if read_json(verification).get("status") != "PASS":
            errors.append(f"{project_id}:BUNDLE_VERIFICATION_NOT_PASS")
        manifest = read_json(bundle_manifest)
        approval = read_json(approval_manifest)
        if approval.get("approval_mode") != "AUTONOMOUS_EVALUATION_ONLY":
            errors.append(f"{project_id}:APPROVAL_MODE_NOT_EVAL")
        if manifest.get("approval_mode") != "AUTONOMOUS_EVALUATION_ONLY":
            errors.append(f"{project_id}:BUNDLE_MODE_NOT_EVAL")
        for path in bundle_dir.rglob("*"):
            if path.is_symlink():
                errors.append(f"{project_id}:SYMLINK:{path}")
            if path.is_file() and path.suffix.lower() in {".xls", ".xlsx", ".xlsm", ".xlsb"}:
                errors.append(f"{project_id}:ORIGINAL_WORKBOOK_EXTENSION:{path}")
            if path.is_file():
                rel = str(path.relative_to(bundle_dir))
                if ".." in Path(rel).parts:
                    errors.append(f"{project_id}:PATH_TRAVERSAL:{rel}")
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    text = ""
                if r"C:\Users\alex1\OneDrive\Desktop\All Projects" in text:
                    errors.append(f"{project_id}:ABSOLUTE_SOURCE_PATH_LEAK:{rel}")
                if detect_forbidden_text(rel) or detect_forbidden_text(text):
                    errors.append(f"{project_id}:FORBIDDEN_SENTINEL:{rel}")
        projects.append({"project_id": project_id, "artifact_count": len(manifest.get("artifacts", []))})
    status = "EVAL_SOURCE_BUNDLE_AUDIT_FAIL" if errors else "EVAL_SOURCE_BUNDLE_AUDIT_PASS"
    result = {
        "audit_id": "eval_source_bundle_audit_batch_001",
        "policy_version": POLICY_VERSION,
        "status": status,
        "projects": projects,
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "run_metadata": {
            "bundle_root": str(args.bundle_root),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "git_head": current_git_head(Path.cwd()),
        },
    }
    write_json(args.output, result)
    print(json.dumps({"status": status, "errors": len(errors)}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous evaluation-only source approval workflow.")
    sub = parser.add_subparsers(dest="command", required=True)

    identify = sub.add_parser("identify")
    identify.add_argument("--readiness", type=Path, default=Path("reports/source_review_batches/batch-001/project_source_readiness.csv"))
    identify.add_argument("--decisions", type=Path, default=Path("manifests/source_guard/source_decisions.csv"))
    identify.add_argument("--source-hash-report", type=Path, default=Path("reports/source_hash_reverification_autonomous_eval.json"))
    identify.add_argument("--output-manifest", type=Path, default=Path("manifests/source_guard/autonomous_eval_batch_001.json"))
    identify.add_argument("--ranking", type=Path, default=Path("reports/source_review_batches/batch-001/autonomous_candidate_ranking.md"))
    identify.set_defaults(func=command_identify)

    prefilter = sub.add_parser("prefilter")
    prefilter.add_argument("--candidate-manifest", type=Path, default=Path("manifests/source_guard/autonomous_eval_batch_001.json"))
    prefilter.add_argument("--decisions", type=Path, default=Path("manifests/source_guard/source_decisions.csv"))
    prefilter.add_argument("--file-index", type=Path, default=Path("manifests/all_projects_file_role_index.csv"))
    prefilter.add_argument("--output-root", type=Path, default=Path("manifests/source_guard/project_manifests"))
    prefilter.set_defaults(func=command_prefilter)

    review = sub.add_parser("review")
    review.add_argument("--role", required=True)
    review.add_argument("--prefilter-root", type=Path, default=Path("manifests/source_guard/project_manifests"))
    review.add_argument("--output", type=Path, required=True)
    review.add_argument("--schema", type=Path, default=Path("schemas/source_quorum_review.schema.json"))
    review.set_defaults(func=command_review)

    split_reviews = sub.add_parser("split-reviews")
    split_reviews.add_argument("--review-root", type=Path, default=Path("manifests/source_guard/reviews/batch-001"))
    split_reviews.add_argument("--project-root", type=Path, default=Path("manifests/source_guard/project_manifests"))
    split_reviews.set_defaults(func=command_split_reviews)

    adjudicate = sub.add_parser("adjudicate")
    adjudicate.add_argument("--prefilter-root", type=Path, default=Path("manifests/source_guard/project_manifests"))
    adjudicate.add_argument("--review-root", type=Path, default=Path("manifests/source_guard/reviews/batch-001"))
    adjudicate.add_argument("--schema", type=Path, default=Path("schemas/source_quorum_adjudication.schema.json"))
    adjudicate.set_defaults(func=command_adjudicate)

    build = sub.add_parser("build-bundles")
    build.add_argument("--project-root", type=Path, default=Path("manifests/source_guard/project_manifests"))
    build.add_argument("--decisions", type=Path, default=Path("manifests/source_guard/source_decisions.csv"))
    build.add_argument("--file-index", type=Path, default=Path("manifests/all_projects_file_role_index.csv"))
    build.add_argument("--bundle-root", type=Path, default=Path("evals/cases/development"))
    build.set_defaults(func=command_build_bundles)

    audit = sub.add_parser("audit-bundles")
    audit.add_argument("--bundle-root", type=Path, default=Path("evals/cases/development"))
    audit.add_argument("--output", type=Path, default=Path("reports/source_review_batches/batch-001/eval_source_bundle_audit.json"))
    audit.set_defaults(func=command_audit_bundles)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
