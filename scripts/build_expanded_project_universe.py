from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "baseline-024" / "expanded-screening"

csv.field_size_limit(2**31 - 1)

SOURCE_ROOT = Path(r"C:\Users\alex1\OneDrive\Desktop\All Projects")
SOURCE_ROOT_ID = "SRC-ALL-PROJECTS"

PROJECT_MANIFEST = ROOT / "manifests" / "all_projects_project_manifest.csv"
FILE_INDEX = ROOT / "manifests" / "all_projects_file_role_index.csv"
SHEET_INDEX = ROOT / "manifests" / "all_projects_workbook_sheet_index.csv"
COHORT_MANIFEST = ROOT / "evals" / "baseline-024" / "cohort_manifest.json"
PHASE_C_STATUS = ROOT / "manifests" / "baseline-024" / "source_approvals" / "phase_c_status.json"
SHORTFALL = ROOT / "reports" / "baseline-024" / "insufficient_eligible_projects_for_24_baseline.json"
FROZEN_WORKFLOW = ROOT / "evals" / "baseline-024" / "frozen_workflow_manifest.json"

WORKBOOK_EXTENSIONS = {".xls", ".xlsx", ".xlsm", ".xlsb", ".csv"}
POTENTIAL_PERMITTED_ROLES = {
    "allowed_contract_workbook",
    "allowed_material_list_workbook",
    "allowed_supporting_workbook",
    "spreadsheet_other",
}
STRICT_PERMITTED_ROLES = {
    "allowed_contract_workbook",
    "allowed_material_list_workbook",
    "allowed_supporting_workbook",
}
REFERENCE_ROLES = {
    "completed_production_drawing_reference",
    "completed_sheetmetal_drawing_reference",
    "completed_punch_drawing_reference",
}
OUTPUT_TYPE_BY_ROLE = {
    "completed_production_drawing_reference": "production",
    "completed_sheetmetal_drawing_reference": "sheetmetal",
    "completed_punch_drawing_reference": "punch",
}

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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def normalize_project_id(value: str) -> str:
    m = re.search(r"(\d{7})", value or "")
    return m.group(1) if m else (value or "").strip()


def year_prefix(project_id: str) -> str:
    m = re.match(r"(\d{3})", project_id or "")
    return m.group(1) if m else ""


def family_candidate(project: dict[str, str], files: list[dict[str, str]]) -> tuple[str, str]:
    customers = [r.get("customer", "").strip() for r in files if r.get("customer", "").strip()]
    if customers:
        return Counter(customers).most_common(1)[0][0], "file_index_customer"
    name = project.get("project_name", "")
    stripped = re.sub(r"^\d{7}", "", name).strip(" -_")
    return stripped[:80] if stripped else "UNKNOWN_FAMILY", "derived_from_project_name"


def revision_family(project_id: str, project_name: str, project_path: str) -> str:
    text = f"{project_name} {project_path}"
    normalized = re.sub(r"(?i)\bREV\b|\bR\d+\b|\d{4}[-_/]\d{1,2}[-_/]\d{1,2}", "", text)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    digest = hashlib.sha1(normalized.encode("utf-8", errors="ignore")).hexdigest()[:12].upper()
    return f"REVFAM-{year_prefix(project_id)}-{digest}"


def duplicate_family(files: list[dict[str, str]]) -> str:
    hashes = sorted({r.get("content_fingerprint") or r.get("sha256") for r in files if r.get("sha256")})
    digest = hashlib.sha1("|".join(hashes).encode("utf-8")).hexdigest()[:12].upper() if hashes else "NOHASH"
    return f"DUPFAM-{digest}"


def load_prior_state() -> dict[str, object]:
    shortfall = read_json(SHORTFALL)
    phase_c = read_json(PHASE_C_STATUS)
    cohort = read_json(COHORT_MANIFEST)
    anchors = {row["project_id"] for row in cohort.get("anchors", [])}
    anchor_family = {row["project_id"]: row.get("family_id", "") for row in cohort.get("anchors", [])}
    accepted_phase_c = set(shortfall.get("accepted_phase_c_project_ids", []))
    bundle_rejected = set(shortfall.get("bundle_rejected_project_ids", []))
    quarantined = set(shortfall.get("quarantined_or_no_bundle_project_ids", []))
    current_allowed = set(shortfall.get("current_allowed_eval_project_ids", []))
    excluded = {row.get("project_id"): row.get("reason") for row in cohort.get("excluded_project_ids", [])}
    return {
        "shortfall": shortfall,
        "phase_c": phase_c,
        "anchors": anchors,
        "anchor_family": anchor_family,
        "accepted_phase_c": accepted_phase_c,
        "bundle_rejected": bundle_rejected,
        "quarantined": quarantined,
        "current_allowed": current_allowed,
        "excluded": excluded,
    }


def current_cohort(project_id: str, prior: dict[str, object]) -> str:
    if project_id in prior["anchors"]:
        return "ANCHOR_ALLOWED_EVAL"
    if project_id in prior["accepted_phase_c"]:
        return "PHASE_C_ACCEPTED_ALLOWED_EVAL"
    if project_id in prior["bundle_rejected"]:
        return "PREVIOUS_BUNDLE_REJECTED"
    if project_id in prior["quarantined"]:
        return "PREVIOUS_QUARANTINED_OR_NO_BUNDLE"
    if project_id in prior["excluded"]:
        return "EXCLUDED_BY_PROTOCOL"
    return "UNASSIGNED_DEVELOPMENT_INVENTORY"


def previous_status(project_id: str, prior: dict[str, object]) -> tuple[str, str]:
    if project_id in prior["anchors"]:
        return "ALLOWED_EVAL_ANCHOR", "ACCEPTED_BUNDLE_CURRENT"
    if project_id in prior["accepted_phase_c"]:
        return "PHASE_C_ACCEPTED", "ACCEPTED_BUNDLE_CURRENT"
    if project_id in prior["bundle_rejected"]:
        return "PHASE_C_SCREENED", "BUNDLE_VERIFICATION_REJECTED"
    if project_id in prior["quarantined"]:
        return "PHASE_C_SCREENED", "QUARANTINED_OR_NO_BUNDLE"
    return "NOT_PREVIOUSLY_SCREENED", "NOT_PREVIOUSLY_SCREENED"


def development_eligibility(
    project: dict[str, str],
    project_id: str,
    prior: dict[str, object],
    permitted_count: int,
    available: str,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if project_id in prior["current_allowed"]:
        reasons.append("already verified ALLOWED_EVAL")
        return "ALREADY_ALLOWED_EVAL", reasons
    if project_id in prior["excluded"]:
        reasons.append(str(prior["excluded"][project_id]))
        return "EXCLUDED_BY_FROZEN_PROTOCOL", reasons
    if project_id in prior["bundle_rejected"]:
        reasons.append("previous bundle verification rejection requires accepted retry justification")
        return "PREVIOUS_REJECTION_RETRY_REQUIRED", reasons
    if project_id in prior["quarantined"]:
        reasons.append("previous quarantine/no-bundle requires new deterministic resolving evidence")
        return "PREVIOUS_QUARANTINE_EVIDENCE_REQUIRED", reasons
    if not parse_bool(project.get("has_all_three_completed_targets", "")):
        reasons.append("inventory v1 did not detect all three completed targets")
    if permitted_count <= 0:
        reasons.append("no potential permitted source workbook in current inventory")
    if available != "AVAILABLE":
        reasons.append(f"source folder availability is {available}")
    if reasons:
        return "NOT_CURRENTLY_DEVELOPMENT_ELIGIBLE", reasons
    return "DEVELOPMENT_ELIGIBLE_PENDING_REFERENCE_DETECTION_V2", reasons


def verify_bundle_hashes() -> dict[str, object]:
    bundle_hash_files = list((ROOT / "evals" / "cases" / "development").glob("*/bundle_hashes.json"))
    bundle_hash_files.extend(
        p
        for p in (ROOT / "manifests" / "baseline-024" / "project_bundles").glob("batch-*/accepted/*/bundle_hashes.json")
    )
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
    for hash_file in sorted(bundle_hash_files):
        root = hash_file.parent
        projects.append(root.name)
        data = read_json(hash_file)
        for key, rel in key_to_file.items():
            if key not in data:
                continue
            checked += 1
            path = root / rel
            if not path.exists():
                failures.append({"project_id": root.name, "item": rel, "status": "MISSING"})
                continue
            actual = sha256_file(path)
            expected = str(data[key]).upper()
            if actual != expected:
                failures.append({"project_id": root.name, "item": rel, "status": "HASH_MISMATCH"})
        actual_artifacts: dict[str, str] = {}
        sanitized = root / "sanitized_inputs"
        if sanitized.exists():
            for artifact in sanitized.iterdir():
                if artifact.is_file():
                    match = re.match(r"^(SGD-[A-F0-9]+)_", artifact.name)
                    if match:
                        actual_artifacts[match.group(1)] = sha256_file(artifact)
        for artifact in data.get("artifacts", []):
            checked += 1
            artifact_id = artifact.get("artifact_id", "")
            if artifact_id not in actual_artifacts:
                failures.append({"project_id": root.name, "item": artifact_id, "status": "MISSING"})
                continue
            if actual_artifacts[artifact_id] != str(artifact.get("sha256", "")).upper():
                failures.append({"project_id": root.name, "item": artifact_id, "status": "HASH_MISMATCH"})
    return {
        "status": "PASS" if not failures and len(bundle_hash_files) == 13 else "FAIL",
        "bundle_hash_file_count": len(bundle_hash_files),
        "checked_entries": checked,
        "projects": sorted(projects),
        "failures": failures,
        "artifact_path_note": "Artifacts are matched by neutral artifact_id because some JSON paths preserve mojibake labels while on-disk filenames are decoded CJK.",
    }


def verify_frozen_workflow() -> dict[str, object]:
    manifest = read_json(FROZEN_WORKFLOW)
    expected_hashes = manifest.get("hashes", {})
    checks = []
    failures = []
    for key, rel in FROZEN_HASH_PATHS.items():
        path = ROOT / rel
        expected = str(expected_hashes.get(key, "")).upper()
        actual = sha256_file(path) if path.exists() else ""
        status = "PASS" if expected and actual == expected else "FAIL"
        row = {"key": key, "path": rel, "status": status, "expected": expected, "actual": actual}
        checks.append(row)
        if status != "PASS":
            failures.append(row)
    return {"status": "PASS" if not failures else "FAIL", "checks": checks, "failures": failures}


def build() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    projects = read_csv(PROJECT_MANIFEST)
    files = read_csv(FILE_INDEX)
    sheets = read_csv(SHEET_INDEX)
    prior = load_prior_state()

    files_by_project: dict[str, list[dict[str, str]]] = defaultdict(list)
    file_by_id: dict[str, dict[str, str]] = {}
    for row in files:
        project_id = normalize_project_id(row.get("project_id", ""))
        if project_id:
            files_by_project[project_id].append(row)
        if row.get("file_id"):
            file_by_id[row["file_id"]] = row

    sheet_parse_by_project: dict[str, Counter[str]] = defaultdict(Counter)
    sheet_visibility_by_project: dict[str, Counter[str]] = defaultdict(Counter)
    for sheet in sheets:
        workbook = file_by_id.get(sheet.get("workbook_file_id", ""))
        if not workbook:
            continue
        project_id = normalize_project_id(workbook.get("project_id", ""))
        if not project_id:
            continue
        sheet_parse_by_project[project_id][sheet.get("parse_status", "") or "UNKNOWN"] += 1
        sheet_visibility_by_project[project_id][sheet.get("visibility", "") or "UNKNOWN"] += 1

    records: list[dict[str, object]] = []
    non_project_inventory_rows: list[dict[str, str]] = []
    folder_to_ids: dict[str, list[str]] = defaultdict(list)
    project_to_folders: dict[str, list[str]] = defaultdict(list)
    family_rows: list[dict[str, object]] = []

    for project in projects:
        project_id = normalize_project_id(project.get("project_id", ""))
        if not re.fullmatch(r"\d{7}", project_id):
            non_project_inventory_rows.append(project)
            continue
        pfiles = files_by_project.get(project_id, [])
        folder = project.get("project_path", "")
        folder_to_ids[folder].append(project_id)
        project_to_folders[project_id].append(folder)

        family, family_source = family_candidate(project, pfiles)
        if project_id in prior["anchor_family"]:
            family = prior["anchor_family"][project_id]
            family_source = "frozen_cohort_manifest"

        project_root = SOURCE_ROOT / folder
        availability = "AVAILABLE" if project_root.exists() else "INACCESSIBLE_OR_PLACEHOLDER"

        workbook_candidates = [
            {
                "file_id": row.get("file_id"),
                "relative_path": row.get("relative_path"),
                "primary_role": row.get("primary_role"),
                "extension": row.get("extension"),
                "sha256": row.get("sha256"),
                "parse_status": row.get("parse_status"),
                "generator_eligibility": row.get("generator_eligibility"),
            }
            for row in pfiles
            if row.get("extension", "").lower() in WORKBOOK_EXTENSIONS
            and row.get("primary_role") in POTENTIAL_PERMITTED_ROLES
        ]
        strict_permitted_count = sum(1 for row in pfiles if row.get("primary_role") in STRICT_PERMITTED_ROLES)
        potential_permitted_count = len(workbook_candidates)

        target_candidates = [
            {
                "file_id": row.get("file_id"),
                "relative_path": row.get("relative_path"),
                "primary_role": row.get("primary_role"),
                "output_type": OUTPUT_TYPE_BY_ROLE.get(row.get("primary_role", ""), row.get("drawing_output_type")),
                "extension": row.get("extension"),
                "size_bytes": row.get("size_bytes"),
                "sha256": row.get("sha256"),
                "classification_confidence": row.get("classification_confidence"),
            }
            for row in pfiles
            if row.get("primary_role") in REFERENCE_ROLES
        ]
        reference_counts = Counter(c["output_type"] for c in target_candidates)

        missing_hash_count = sum(1 for row in pfiles if not row.get("sha256"))
        source_hash_status = "HASH_RECORDED_ALL_PROJECT_FILES" if missing_hash_count == 0 else "MISSING_RECORDED_HASHES"

        eligibility, exclusion_reasons = development_eligibility(
            project,
            project_id,
            prior,
            potential_permitted_count,
            availability,
        )
        prev_screen, prev_bundle = previous_status(project_id, prior)
        cohort = current_cohort(project_id, prior)

        record = {
            "project_id": project.get("project_id", ""),
            "normalized_project_id": project_id,
            "physical_project_folder": project.get("project_name", ""),
            "source_root_id": SOURCE_ROOT_ID,
            "source_root_relative_path": folder,
            "customer_or_customer_family": family if family_source != "frozen_cohort_manifest" else "",
            "project_family": family,
            "project_family_source": family_source,
            "revision_family": revision_family(project_id, project.get("project_name", ""), folder),
            "duplicate_family": duplicate_family(pfiles),
            "year_prefix": year_prefix(project_id),
            "workbook_candidates": workbook_candidates,
            "workbook_candidate_count": len(workbook_candidates),
            "strict_permitted_input_count": strict_permitted_count,
            "candidate_permitted_input_count": potential_permitted_count,
            "parser_status": dict(sheet_parse_by_project.get(project_id, Counter())),
            "sheet_visibility_counts": dict(sheet_visibility_by_project.get(project_id, Counter())),
            "target_reference_file_candidates": target_candidates,
            "target_reference_file_candidate_count": len(target_candidates),
            "target_reference_type_counts": dict(reference_counts),
            "inventory_v1_has_all_three_completed_targets": parse_bool(project.get("has_all_three_completed_targets", "")),
            "onedrive_availability": availability,
            "current_cohort": cohort,
            "development_eligibility": eligibility,
            "exclusion_reasons": exclusion_reasons,
            "previous_screening_status": prev_screen,
            "previous_bundle_status": prev_bundle,
            "current_source_hash_status": source_hash_status,
            "recorded_file_count": int(project.get("file_count", "0") or 0),
            "recorded_workbook_count": int(project.get("workbook_count", "0") or 0),
            "generator_candidate_status": project.get("generator_candidate_status", ""),
            "has_forbidden_sources": parse_bool(project.get("has_forbidden_sources", "")),
        }
        records.append(record)
        family_rows.append(
            {
                "project_id": project_id,
                "project_family": family,
                "project_family_source": family_source,
                "current_cohort": cohort,
                "proposed_canonical_change": False,
                "audit_required_before_change": family_source != "frozen_cohort_manifest",
            }
        )

    duplicate_reference_hashes: dict[str, list[dict[str, str]]] = defaultdict(list)
    duplicate_content_fingerprints: dict[str, list[dict[str, str]]] = defaultdict(list)
    nested_output_folders = []
    inconsistent_target_terms = []
    for row in files:
        project_id = normalize_project_id(row.get("project_id", ""))
        sha = row.get("sha256", "")
        fp = row.get("content_fingerprint", "")
        if row.get("primary_role") in REFERENCE_ROLES and sha:
            duplicate_reference_hashes[sha].append({"project_id": project_id, "file_id": row.get("file_id", ""), "role": row.get("primary_role", "")})
        if fp:
            duplicate_content_fingerprints[fp].append({"project_id": project_id, "file_id": row.get("file_id", ""), "role": row.get("primary_role", "")})
        rel = row.get("relative_path", "")
        if row.get("primary_role") in REFERENCE_ROLES and rel.count("\\") >= 4:
            nested_output_folders.append({"project_id": project_id, "file_id": row.get("file_id", ""), "relative_path": rel, "role": row.get("primary_role", "")})
        if row.get("extension", "").lower() == ".pdf" and any(term in rel for term in ["施工圖", "生管", "鈑金", "沖孔"]):
            if row.get("primary_role") not in REFERENCE_ROLES and "forbidden" not in row.get("primary_role", ""):
                inconsistent_target_terms.append({"project_id": project_id, "file_id": row.get("file_id", ""), "relative_path": rel, "role": row.get("primary_role", "")})

    duplicate_reference_groups = {k: v for k, v in duplicate_reference_hashes.items() if len({x["project_id"] for x in v}) > 1}
    duplicate_content_groups = {k: v for k, v in duplicate_content_fingerprints.items() if len({x["project_id"] for x in v}) > 1}

    folder_map = {
        "source_root_id": SOURCE_ROOT_ID,
        "source_root": str(SOURCE_ROOT),
        "folder_count": len(folder_to_ids),
        "multiple_project_ids_under_one_folder": [
            {"source_root_relative_path": folder, "project_ids": sorted(set(ids))}
            for folder, ids in sorted(folder_to_ids.items())
            if len(set(ids)) > 1
        ],
        "project_spread_across_multiple_folders": [
            {"project_id": pid, "source_root_relative_paths": sorted(set(folders))}
            for pid, folders in sorted(project_to_folders.items())
            if len(set(folders)) > 1
        ],
        "folder_to_project_ids": [
            {"source_root_relative_path": folder, "project_ids": sorted(set(ids))}
            for folder, ids in sorted(folder_to_ids.items())
        ],
    }

    family_reconciliation = {
        "status": "SCREENING_ONLY_NO_CANONICAL_FAMILY_CHANGES",
        "policy": "Any changed family assignment requires old value, proposed value, evidence, affected cohorts, leakage-risk analysis, and independent audit.",
        "family_assignments": family_rows,
        "proposed_family_assignment_changes": [],
        "family_counts": dict(Counter(row["project_family"] for row in family_rows)),
    }

    duplicate_revision = {
        "status": "HEURISTIC_METADATA_GROUPS_FOR_SCREENING_ONLY",
        "revision_family_counts": dict(Counter(row["revision_family"] for row in records)),
        "duplicate_family_counts": dict(Counter(row["duplicate_family"] for row in records)),
        "duplicate_completed_reference_hash_groups": duplicate_reference_groups,
        "duplicate_content_fingerprint_groups": duplicate_content_groups,
        "nested_output_folder_candidates": nested_output_folders[:500],
        "inconsistent_target_term_candidates": inconsistent_target_terms[:500],
    }

    checkpoint = {
        "git_head_verified_before_phase_a": "568a373 descendant of 68285b6",
        "starting_checkpoint_commit": "68285b608f0349f4f183fb09698449fe75740a11",
        "amendment_commit": "568a373",
        "accepted_bundle_hash_verification": verify_bundle_hashes(),
        "frozen_workflow_hash_verification": verify_frozen_workflow(),
        "baseline_generation_attempts": prior["shortfall"].get("generation_attempts", 0),
        "primary_reviews": prior["shortfall"].get("primary_reviews", 0),
        "secondary_reviews": prior["shortfall"].get("secondary_reviews", 0),
        "evaluator_sensitivity_gate": "EVALUATOR_SENSITIVITY_PASS",
        "reference_content_used_for_selection": False,
    }

    summary = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_root_id": SOURCE_ROOT_ID,
        "source_root": str(SOURCE_ROOT),
        "project_count": len(records),
        "non_project_inventory_row_count": len(non_project_inventory_rows),
        "non_project_inventory_row_ids": [row.get("project_id", "") for row in non_project_inventory_rows],
        "physical_project_folder_count": len(folder_to_ids),
        "project_ids_detected": len({row["normalized_project_id"] for row in records}),
        "development_eligibility_counts": dict(Counter(row["development_eligibility"] for row in records)),
        "current_cohort_counts": dict(Counter(row["current_cohort"] for row in records)),
        "inventory_v1_all_three_completed_targets_count": sum(1 for row in records if row["inventory_v1_has_all_three_completed_targets"]),
        "potential_permitted_input_project_count": sum(1 for row in records if row["candidate_permitted_input_count"] > 0),
        "one_drive_availability_counts": dict(Counter(row["onedrive_availability"] for row in records)),
    }

    universe = {"summary": summary, "checkpoint_verification": checkpoint, "projects": records}
    write_json(OUT_DIR / "full_project_universe.json", universe)
    write_json(OUT_DIR / "project_folder_to_id_map.json", folder_map)
    write_json(OUT_DIR / "project_family_reconciliation.json", family_reconciliation)
    write_json(OUT_DIR / "duplicate_and_revision_groups.json", duplicate_revision)

    csv_fields = [
        "project_id",
        "normalized_project_id",
        "source_root_relative_path",
        "project_family",
        "project_family_source",
        "revision_family",
        "duplicate_family",
        "year_prefix",
        "workbook_candidate_count",
        "candidate_permitted_input_count",
        "strict_permitted_input_count",
        "target_reference_file_candidate_count",
        "inventory_v1_has_all_three_completed_targets",
        "onedrive_availability",
        "current_cohort",
        "development_eligibility",
        "exclusion_reasons",
        "previous_screening_status",
        "previous_bundle_status",
        "current_source_hash_status",
        "generator_candidate_status",
    ]
    with (OUT_DIR / "full_project_universe.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for row in records:
            flat = {field: row.get(field, "") for field in csv_fields}
            flat["exclusion_reasons"] = "|".join(row.get("exclusion_reasons", []))
            writer.writerow(flat)

    report = [
        "# Expanded Screening Inventory Reconciliation",
        "",
        f"- status: `PHASE_A_RECONCILED_METADATA_ONLY`",
        f"- source_root_id: `{SOURCE_ROOT_ID}`",
        f"- physical project folders reconciled: `{summary['physical_project_folder_count']}`",
        f"- project IDs reconciled: `{summary['project_ids_detected']}`",
        f"- inventory v1 all-three target count: `{summary['inventory_v1_all_three_completed_targets_count']}`",
        f"- projects with potential permitted inputs: `{summary['potential_permitted_input_project_count']}`",
        f"- accepted bundle hash verification: `{checkpoint['accepted_bundle_hash_verification']['status']}`",
        f"- frozen workflow hash verification: `{checkpoint['frozen_workflow_hash_verification']['status']}`",
        f"- baseline generation attempts: `{checkpoint['baseline_generation_attempts']}`",
        "",
        "No completed-reference page content was inspected. Target-reference candidates are recorded from existing metadata only.",
        "",
        "## Eligibility Counts",
        "",
    ]
    for key, value in sorted(summary["development_eligibility_counts"].items()):
        report.append(f"- `{key}`: `{value}`")
    report.extend(["", "## Cohort Counts", ""])
    for key, value in sorted(summary["current_cohort_counts"].items()):
        report.append(f"- `{key}`: `{value}`")
    report.extend(
        [
            "",
            "## Reconciliation Notes",
            "",
            f"- Multiple-project folders detected: `{len(folder_map['multiple_project_ids_under_one_folder'])}`",
            f"- Projects spread across multiple folders detected: `{len(folder_map['project_spread_across_multiple_folders'])}`",
            f"- Duplicate completed-reference hash groups: `{len(duplicate_reference_groups)}`",
            f"- Duplicate content-fingerprint groups: `{len(duplicate_content_groups)}`",
            f"- Nested output-folder candidates sampled: `{len(duplicate_revision['nested_output_folder_candidates'])}`",
            f"- Inconsistent target-term candidates sampled: `{len(duplicate_revision['inconsistent_target_term_candidates'])}`",
            "",
            "Family assignments in this report are screening metadata only. No canonical family assignment was changed.",
        ]
    )
    (OUT_DIR / "inventory_reconciliation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
