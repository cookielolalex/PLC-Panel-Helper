from __future__ import annotations

import argparse
import csv
import html
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from harness_lib import sha256_file, write_json
from source_guard import DECISION_FIELDS, POLICY_VERSION, csv_rows, csv_write, decisions_for_project, family_id, flatten_decision


BATCH_ID = "batch-001"
DEFAULT_SEED = 20260622


def role_count(row: dict[str, str], name: str) -> int:
    try:
        return int(row.get(name, "0") or 0)
    except ValueError:
        return 0


def load_project_maps(project_manifest: Path, sheet_index: Path, file_index: Path) -> tuple[list[dict[str, str]], dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    projects = [row for row in csv_rows(project_manifest) if row.get("project_id") and row["project_id"] != "UNASSIGNED"]
    sheets_by_project: dict[str, list[dict[str, str]]] = defaultdict(list)
    files_by_project: dict[str, list[dict[str, str]]] = defaultdict(list)
    file_rows = csv_rows(file_index)
    file_project = {row["file_id"]: row.get("project_id", "") for row in file_rows}
    for row in file_rows:
        files_by_project[row.get("project_id", "")].append(row)
    for row in csv_rows(sheet_index):
        project_id = file_project.get(row.get("workbook_file_id", ""), "")
        if project_id:
            sheets_by_project[project_id].append(row)
    return projects, sheets_by_project, files_by_project


def project_has_usable_workbook(row: dict[str, str]) -> bool:
    return role_count(row, "workbook_count") > 0


def complete_reference(row: dict[str, str]) -> bool:
    return (row.get("has_all_three_completed_targets") or "").lower() == "true"


def sheet_risk_counts(sheets: list[dict[str, str]]) -> Counter:
    c = Counter()
    for sheet in sheets:
        stale = sheet.get("stale_template_status", "")
        if stale == "STALE_TEMPLATE_SHEET":
            c["stale"] += 1
        if stale in {"INSUFFICIENT_IDENTITY", "HUMAN_REVIEW_REQUIRED"}:
            c["identity"] += 1
        if sheet.get("visibility") in {"hidden", "veryHidden"} or stale == "HIDDEN_SHEET_REVIEW_REQUIRED":
            c["hidden"] += 1
        if (sheet.get("parse_status") or "").startswith("UNSUPPORTED") or "PARSER_REQUIRED" in stale:
            c["parser"] += 1
        if sheet.get("external_links"):
            c["external"] += 1
    return c


def file_risks(files: list[dict[str, str]]) -> Counter:
    c = Counter()
    for row in files:
        rel = row.get("relative_path", "")
        if "修改" in rel:
            c["revision"] += 1
        if row.get("extension") == ".xls":
            c["parser"] += 1
    return c


def select_projects(projects: list[dict[str, str]], sheets_by_project: dict[str, list[dict[str, str]]], files_by_project: dict[str, list[dict[str, str]]], seed: int) -> list[dict[str, Any]]:
    eligible = [p for p in projects if complete_reference(p) and project_has_usable_workbook(p)]
    # Active year 115 has no all-three-reference candidates in the current manifest.
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    used_projects: set[str] = set()
    used_families: set[str] = set()

    def add(project: dict[str, str], stratum: str, rationale: str) -> bool:
        pid = project["project_id"]
        fam = family_id(project.get("project_name", ""))
        if pid in used_projects:
            return False
        # Keep families separated when possible, but do not block strata forever.
        if fam in used_families and len(selected) < 10:
            return False
        selected.append({
            "project_id": pid,
            "family_id": fam,
            "stratum": stratum,
            "rationale": rationale,
            "project": project,
        })
        used_projects.add(pid)
        used_families.add(fam)
        return True

    def candidates(predicate):
        rows = [p for p in eligible if p["project_id"] not in used_projects and predicate(p)]
        rows.sort(key=lambda p: (family_id(p.get("project_name", "")) in used_families, p["project_id"]))
        return rows

    for p in candidates(lambda p: int(p.get("file_count", "0") or 0) <= 25 and int(p.get("workbook_count", "0") or 0) <= 6)[:3]:
        add(p, "straightforward_visible_candidate", "Small reference-complete project with workbook evidence.")

    for p in candidates(lambda p: int(p.get("file_count", "0") or 0) >= 30 or int(p.get("workbook_count", "0") or 0) >= 8)[:2]:
        add(p, "multi_panel_or_multi_workbook", "Large file/workbook footprint exercises multi-input review.")

    stale_pool = candidates(lambda p: sheet_risk_counts(sheets_by_project.get(p["project_id"], []))["stale"] > 0 or sheet_risk_counts(sheets_by_project.get(p["project_id"], []))["identity"] > 0)
    for p in stale_pool[:2]:
        add(p, "stale_or_unrelated_sheet_risk", "Worksheet metadata includes stale or insufficient identity risk.")

    hidden_pool = candidates(lambda p: sheet_risk_counts(sheets_by_project.get(p["project_id"], []))["hidden"] > 0)
    for p in hidden_pool[:1]:
        add(p, "hidden_sheet_risk", "Workbook metadata includes hidden or veryHidden sheet risk.")

    revision_pool = candidates(lambda p: file_risks(files_by_project.get(p["project_id"], []))["revision"] > 0)
    for p in revision_pool[:1]:
        add(p, "revision_supersession_risk", "Project files include modification/revision naming.")

    conflict_pool = candidates(lambda p: sheet_risk_counts(sheets_by_project.get(p["project_id"], []))["stale"] > 0)
    for p in conflict_pool[:1]:
        add(p, "conflicting_project_identity_risk", "Worksheet identity conflicts with project path identity.")

    parser_pool = candidates(lambda p: sheet_risk_counts(sheets_by_project.get(p["project_id"], []))["parser"] > 0 or file_risks(files_by_project.get(p["project_id"], []))["parser"] > 0)
    for p in parser_pool[:1]:
        add(p, "parser_required_risk", "Legacy parser-required workbook evidence is present.")

    remaining = [p for p in eligible if p["project_id"] not in used_projects]
    rng.shuffle(remaining)
    for p in remaining:
        if add(p, "seeded_random_family_separated", f"Random seed {seed} among remaining reference-complete projects."):
            break

    if len(selected) < 12:
        for p in sorted(remaining, key=lambda p: p["project_id"]):
            if p["project_id"] not in used_projects:
                selected.append({
                    "project_id": p["project_id"],
                    "family_id": family_id(p.get("project_name", "")),
                    "stratum": "backfill_reference_complete",
                    "rationale": "Backfill because strict strata/family separation produced fewer than 12 projects.",
                    "project": p,
                })
                used_projects.add(p["project_id"])
            if len(selected) == 12:
                break
    return selected[:12]


def html_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    out = ["<table>", "<thead><tr>"]
    for field in fields:
        out.append(f"<th>{html.escape(field)}</th>")
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        for field in fields:
            out.append(f"<td>{html.escape(str(row.get(field, '')))}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def write_packet(packet_dir: Path, project: dict[str, Any], decisions: list[dict[str, Any]]) -> None:
    packet_dir.mkdir(parents=True, exist_ok=True)
    fields = ["decision_id", "relative_path", "worksheet_name", "worksheet_visibility", "proposed_decision", "reason_codes", "parse_status", "worksheet_fingerprint"]
    flat = [flatten_decision(d) for d in decisions]
    csv_write(packet_dir / "candidate_items.csv", flat, fields)
    with (packet_dir / "packet.md").open("w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Source Review Packet {project['project_id']}\n\n")
        f.write(f"Family: `{project['family_id']}`\n\n")
        f.write(f"Stratum: `{project['stratum']}`\n\n")
        f.write(f"Rationale: {project['rationale']}\n\n")
        f.write("No completed-reference content is included. Review only the candidate input rows below.\n\n")
        for row in flat:
            f.write(f"## {row['decision_id']}\n\n")
            f.write(f"- File: `{row['relative_path']}`\n")
            f.write(f"- Worksheet: `{row['worksheet_name']}`\n")
            f.write(f"- Visibility: `{row['worksheet_visibility']}`\n")
            f.write(f"- Proposed: `{row['proposed_decision']}`\n")
            f.write(f"- Reasons: `{row['reason_codes']}`\n")
            f.write(f"- Fingerprint: `{row['worksheet_fingerprint']}`\n\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a 12-project source review batch.")
    parser.add_argument("--file-index", type=Path, default=Path("manifests/all_projects_file_role_index.csv"))
    parser.add_argument("--sheet-index", type=Path, default=Path("manifests/all_projects_workbook_sheet_index.csv"))
    parser.add_argument("--project-manifest", type=Path, default=Path("manifests/all_projects_project_manifest.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/source_review_batches/batch-001"))
    parser.add_argument("--decisions-output", type=Path, default=Path("manifests/source_guard/source_decisions.csv"))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    projects, sheets_by_project, files_by_project = load_project_maps(args.project_manifest, args.sheet_index, args.file_index)
    selected = select_projects(projects, sheets_by_project, files_by_project, args.seed)
    if len(selected) != 12:
        raise SystemExit(f"expected 12 selected projects, got {len(selected)}")

    all_decisions: list[dict[str, Any]] = []
    packet_projects = []
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "project_packets").mkdir(parents=True, exist_ok=True)
    for item in selected:
        decisions = decisions_for_project(item["project_id"], args.file_index, args.sheet_index, compute_fingerprints=True)
        all_decisions.extend(decisions)
        candidate_files = sorted({d["file_id"] for d in decisions})
        candidate_sheets = [d for d in decisions if d.get("sheet_id")]
        packet_projects.append({
            "project_id": item["project_id"],
            "family_id": item["family_id"],
            "stratum": item["stratum"],
            "rationale": item["rationale"],
            "candidate_file_count": len(candidate_files),
            "candidate_worksheet_count": len(candidate_sheets),
        })
        write_packet(args.output_dir / "project_packets" / item["project_id"], item, decisions)

    flat_decisions = [flatten_decision(d) for d in all_decisions]
    csv_write(args.decisions_output, flat_decisions, DECISION_FIELDS)
    csv_write(args.output_dir / "source_review_batch_001.csv", flat_decisions, DECISION_FIELDS)

    blank_fields = ["decision_id", "project_id", "file_id", "sheet_id", "file_sha256", "worksheet_fingerprint", "human_decision", "reviewer", "notes"]
    blanks = []
    for d in all_decisions:
        blanks.append({
            "decision_id": d["decision_id"],
            "project_id": d["project_id"],
            "file_id": d["file_id"],
            "sheet_id": d["sheet_id"],
            "file_sha256": d["file_sha256"],
            "worksheet_fingerprint": d["worksheet_fingerprint"],
            "human_decision": "",
            "reviewer": "",
            "notes": "",
        })
    csv_write(args.output_dir / "blank_human_decisions.csv", blanks, blank_fields)

    counts = Counter(d["proposed_decision"] for d in all_decisions)
    manifest = {
        "batch_id": BATCH_ID,
        "policy_version": POLICY_VERSION,
        "selection_seed": args.seed,
        "selection_algorithm": "reference_complete_projects_stratified_family_separated_seeded_backfill_v1",
        "status": "SOURCE_GUARD_REVIEW_PACK_READY_REAL_GENERATION_BLOCKED",
        "active_year_note": "Active year 115 has no all-three-completed-target projects; selected historical reference-complete calibration projects instead.",
        "projects": packet_projects,
        "counts": {
            "candidate_files": len({d["file_id"] for d in all_decisions}),
            "candidate_worksheets": len([d for d in all_decisions if d.get("sheet_id")]),
            "auto_denied": counts["AUTO_DENIED"],
            "quarantined": counts["QUARANTINED"],
            "parser_required": counts["PARSER_REQUIRED"],
            "awaiting_human_decision": len(all_decisions),
            "allowed": counts["ALLOWED"],
        },
        "outputs": [
            "batch_manifest.json",
            "source_review_batch_001.csv",
            "source_review_batch_001.html",
            "project_packets/",
            "approval_instructions.md",
            "blank_human_decisions.csv",
        ],
    }
    write_json(args.output_dir / "batch_manifest.json", manifest)

    html_fields = ["project_id", "family_id", "stratum", "candidate_file_count", "candidate_worksheet_count", "rationale"]
    html_doc = "<!doctype html><meta charset='utf-8'><title>Source Review Batch 001</title><style>body{font-family:Arial,sans-serif}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px}th{background:#eee}</style><h1>Source Review Batch 001</h1>" + html_table(packet_projects, html_fields)
    (args.output_dir / "source_review_batch_001.html").write_text(html_doc, encoding="utf-8")

    instructions = """# Approval Instructions

This review packet does not approve any item by itself.

For each row in `blank_human_decisions.csv`, fill `human_decision` with exactly
one of:

- HUMAN_APPROVED
- HUMAN_DENIED
- NEEDS_MORE_EVIDENCE

Blank cells are not approvals. Bulk approval is not accepted. Each approval
must retain the exact `decision_id`, `file_sha256`, and `worksheet_fingerprint`
shown in the packet. If a worksheet has no fingerprint, it cannot be approved
for a generator bundle in this calibration phase.
"""
    (args.output_dir / "approval_instructions.md").write_text(instructions, encoding="utf-8", newline="\n")

    coverage = {
        "batch_id": BATCH_ID,
        "selected_project_ids": [p["project_id"] for p in packet_projects],
        "strata": Counter(p["stratum"] for p in packet_projects),
        "decision_counts": dict(counts),
        "candidate_file_count": manifest["counts"]["candidate_files"],
        "candidate_worksheet_count": manifest["counts"]["candidate_worksheets"],
        "batch_manifest_hash": sha256_file(args.output_dir / "batch_manifest.json"),
    }
    write_json(Path("reports/source_guard_coverage_summary.json"), coverage)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
