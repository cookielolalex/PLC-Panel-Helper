from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "reports" / "baseline-024" / "expanded-screening" / "full_project_universe.json"
REFERENCE_SETS = ROOT / "manifests" / "reference_detection" / "effective_reference_sets.json"
OUT_DIR = ROOT / "evals" / "baseline-024"

SEED = "BASELINE024-EXPANDED-DISCOVERY-V2-20260623"


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def seeded_random(project_id: str) -> float:
    digest = hashlib.sha256(f"{SEED}:{project_id}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def score_project(row: dict[str, object], reference: dict[str, object], family_counts: Counter[str]) -> dict[str, object]:
    parser_status = row.get("parser_status", {}) or {}
    parsed_rows = int(parser_status.get("PARSED", 0))
    parser_required_rows = int(parser_status.get("UNSUPPORTED_XLS_PARSER_REQUIRED", 0)) + int(parser_status.get("PARSER_REQUIRED", 0))
    workbook_count = int(row.get("workbook_candidate_count", 0))
    permitted_count = int(row.get("candidate_permitted_input_count", 0))
    reference_status = str(reference.get("reference_availability", "NO_REFERENCE_SET"))
    family = str(row.get("project_family", "UNKNOWN"))

    reference_score = {
        "VERIFIED_ALL_THREE": 40,
        "PROBABLE_ALL_THREE": 32,
        "PARTIAL_REFERENCE_SET": 12,
        "AMBIGUOUS_REFERENCE_SET": 4,
        "NO_REFERENCE_SET": 0,
        "INACCESSIBLE_REFERENCE_SET": -50,
    }.get(reference_status, 0)
    parser_score = min(parsed_rows, 8) * 4 - min(parser_required_rows, 10) * 3
    permitted_score = min(permitted_count, 10) * 3
    identity_score = 10 if row.get("normalized_project_id") and row.get("normalized_project_id") in row.get("source_root_relative_path", "") else 2
    family_uniqueness_score = max(0, 12 - family_counts[family])
    workbook_diversity_score = min(workbook_count, 8)
    revision_complexity_score = 3 if row.get("revision_family") else 0
    source_conflict_score = 4 if row.get("has_forbidden_sources") else 0
    random_tie = seeded_random(str(row.get("normalized_project_id", "")))
    total = (
        reference_score
        + parser_score
        + permitted_score
        + identity_score
        + family_uniqueness_score
        + workbook_diversity_score
        + revision_complexity_score
        + source_conflict_score
        + random_tie
    )
    return {
        "total_score": round(total, 6),
        "reference_score": reference_score,
        "parser_score": parser_score,
        "permitted_score": permitted_score,
        "identity_score": identity_score,
        "family_uniqueness_score": family_uniqueness_score,
        "workbook_diversity_score": workbook_diversity_score,
        "revision_complexity_score": revision_complexity_score,
        "source_conflict_score": source_conflict_score,
        "random_tie_breaker": round(random_tie, 6),
    }


def registry_status(row: dict[str, object], reference: dict[str, object]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    project_id = str(row.get("normalized_project_id", ""))
    reference_status = str(reference.get("reference_availability", "NO_REFERENCE_SET"))
    cohort = str(row.get("current_cohort", ""))

    if row.get("development_eligibility") == "ALREADY_ALLOWED_EVAL":
        return "ALREADY_ALLOWED_EVAL", ["already accepted in the 13-project pool"]
    if cohort == "EXCLUDED_BY_PROTOCOL":
        return "EXCLUDED_PROTECTED_OR_PROTOCOL", list(row.get("exclusion_reasons", []))
    if cohort == "PREVIOUS_BUNDLE_REJECTED":
        return "EXCLUDED_PREVIOUS_REJECTION_RETRY_REQUIRED", ["prior bundle rejection preserved; retry requires defect/fix evidence"]
    if cohort == "PREVIOUS_QUARANTINED_OR_NO_BUNDLE":
        return "EXCLUDED_PREVIOUS_QUARANTINE_REQUIRES_EVIDENCE", ["prior quarantine/no-bundle preserved"]
    if int(row.get("candidate_permitted_input_count", 0)) <= 0:
        reasons.append("no potential permitted source workbook")
    if row.get("onedrive_availability") != "AVAILABLE":
        reasons.append(f"OneDrive availability {row.get('onedrive_availability')}")
    if reference_status in {"VERIFIED_ALL_THREE", "PROBABLE_ALL_THREE"}:
        if reasons:
            return "AUTO_EXCLUDED", reasons
        return "READY_FOR_SOURCE_SCREENING", []
    if reference_status == "PARTIAL_REFERENCE_SET":
        if reasons:
            return "REFERENCE_REVIEW_BLOCKED_BY_SOURCE_METADATA", reasons
        return "REFERENCE_PRESENCE_REVIEW_REQUIRED", ["metadata v2 found only a partial reference set"]
    if reference_status == "AMBIGUOUS_REFERENCE_SET":
        return "REFERENCE_PRESENCE_REVIEW_REQUIRED", ["metadata v2 found an ambiguous reference set"]
    if reference_status == "INACCESSIBLE_REFERENCE_SET":
        return "AUTO_EXCLUDED", ["reference set inaccessible"]
    return "AUTO_EXCLUDED", ["no all-three completed reference set detected by metadata v2"]


def build() -> None:
    universe = read_json(UNIVERSE)
    refs = read_json(REFERENCE_SETS)
    ref_by_project = {row["project_id"]: row for row in refs["effective_reference_sets"]}
    family_counts = Counter(row.get("project_family", "UNKNOWN") for row in universe["projects"])

    records = []
    for row in universe["projects"]:
        project_id = str(row.get("normalized_project_id", ""))
        reference = ref_by_project.get(project_id, {"reference_availability": "NO_REFERENCE_SET", "effective_reference_files": {}})
        status, reasons = registry_status(row, reference)
        scores = score_project(row, reference, family_counts)
        records.append(
            {
                "project_id": project_id,
                "source_root_relative_path": row.get("source_root_relative_path"),
                "project_family": row.get("project_family"),
                "current_cohort": row.get("current_cohort"),
                "candidate_status": status,
                "candidate_status_reasons": reasons,
                "reference_availability": reference.get("reference_availability"),
                "detected_output_types": reference.get("detected_output_types", []),
                "effective_neutral_reference_file_ids": [
                    value.get("neutral_reference_file_id")
                    for value in (reference.get("effective_reference_files") or {}).values()
                ],
                "workbook_candidate_count": row.get("workbook_candidate_count"),
                "candidate_permitted_input_count": row.get("candidate_permitted_input_count"),
                "parser_status": row.get("parser_status"),
                "previous_screening_status": row.get("previous_screening_status"),
                "previous_bundle_status": row.get("previous_bundle_status"),
                "current_source_hash_status": row.get("current_source_hash_status"),
                "ranking": scores,
                "completed_reference_content_inspected_for_selection": False,
            }
        )

    ranked = sorted(
        records,
        key=lambda item: (
            item["candidate_status"] != "READY_FOR_SOURCE_SCREENING",
            item["candidate_status"] != "REFERENCE_PRESENCE_REVIEW_REQUIRED",
            -item["ranking"]["total_score"],
            item["project_id"],
        ),
    )
    for idx, row in enumerate(ranked, start=1):
        row["rank"] = idx

    registry = {
        "registry_id": "expanded_candidate_registry_v2",
        "baseline_id": "baseline-024-cycle-000",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "random_seed": SEED,
        "status_counts": dict(Counter(row["candidate_status"] for row in records)),
        "reference_availability_counts": dict(Counter(row["reference_availability"] for row in records)),
        "records": ranked,
    }
    write_json(OUT_DIR / "expanded_candidate_registry_v2.json", registry)

    ranking = {
        "ranking_id": "expanded_candidate_ranking_v2",
        "random_seed": SEED,
        "ranking_inputs": [
            "likelihood of deterministic parser success",
            "clear project identity",
            "verified/probable three-output reference set",
            "permitted-source availability",
            "family uniqueness",
            "workbook-template diversity",
            "revision complexity",
            "source-conflict diversity",
            "deterministic random tie breaker",
        ],
        "ranked_project_ids": [row["project_id"] for row in ranked],
        "ready_for_source_screening": [
            row["project_id"] for row in ranked if row["candidate_status"] == "READY_FOR_SOURCE_SCREENING"
        ],
        "reference_presence_review_required": [
            row["project_id"] for row in ranked if row["candidate_status"] == "REFERENCE_PRESENCE_REVIEW_REQUIRED"
        ],
    }
    write_json(OUT_DIR / "expanded_candidate_ranking_v2.json", ranking)

    fields = [
        "rank",
        "project_id",
        "candidate_status",
        "candidate_status_reasons",
        "reference_availability",
        "detected_output_types",
        "workbook_candidate_count",
        "candidate_permitted_input_count",
        "current_cohort",
        "previous_screening_status",
        "previous_bundle_status",
        "total_score",
    ]
    with (OUT_DIR / "expanded_candidate_registry_v2.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in ranked:
            writer.writerow(
                {
                    "rank": row["rank"],
                    "project_id": row["project_id"],
                    "candidate_status": row["candidate_status"],
                    "candidate_status_reasons": "|".join(row["candidate_status_reasons"]),
                    "reference_availability": row["reference_availability"],
                    "detected_output_types": "|".join(row["detected_output_types"]),
                    "workbook_candidate_count": row["workbook_candidate_count"],
                    "candidate_permitted_input_count": row["candidate_permitted_input_count"],
                    "current_cohort": row["current_cohort"],
                    "previous_screening_status": row["previous_screening_status"],
                    "previous_bundle_status": row["previous_bundle_status"],
                    "total_score": row["ranking"]["total_score"],
                }
            )

    report = [
        "# Expanded Candidate Selection Report",
        "",
        "- status: `EXPANDED_CANDIDATE_REGISTRY_V2_BUILT`",
        f"- random_seed: `{SEED}`",
        "- completed_reference_content_inspected_for_selection: `false`",
        "",
        "## Candidate Status Counts",
        "",
    ]
    for key, value in sorted(registry["status_counts"].items()):
        report.append(f"- `{key}`: `{value}`")
    report.extend(["", "## Reference Availability Counts", ""])
    for key, value in sorted(registry["reference_availability_counts"].items()):
        report.append(f"- `{key}`: `{value}`")
    report.extend(
        [
            "",
            "## Immediate Screening Readiness",
            "",
            f"- ready_for_source_screening: `{len(ranking['ready_for_source_screening'])}`",
            f"- reference_presence_review_required: `{len(ranking['reference_presence_review_required'])}`",
            "",
            "No prior accepted, rejected, quarantined, or protocol-excluded project was relabeled. Previous results remain preserved.",
        ]
    )
    (OUT_DIR / "expanded_candidate_selection_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
