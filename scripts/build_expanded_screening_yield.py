from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "baseline-024" / "expanded-screening"
REGISTRY = ROOT / "evals" / "baseline-024" / "expanded_candidate_registry_v2.json"
REVIEWS = ROOT / "manifests" / "reference_detection" / "reviews"


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    registry = read_json(REGISTRY)
    wave_rows = []
    cumulative_promoted = 0
    cumulative_screened = 0
    for wave_dir in sorted(REVIEWS.glob("wave-*")):
        result_files = sorted(wave_dir.glob("*_reference_presence.json"))
        if not result_files:
            continue
        results = [read_json(path) for path in result_files]
        counts = Counter(row["verification_result"] for row in results)
        promoted = counts.get("VERIFIED_ALL_THREE", 0) + counts.get("PROBABLE_ALL_THREE", 0)
        cumulative_promoted += promoted
        cumulative_screened += len(results)
        wave_rows.append(
            {
                "batch_id": wave_dir.name,
                "batch_type": "reference_presence_pre_screen",
                "candidates_screened": len(results),
                "deterministic_denials": 0,
                "parser_required_count": 0,
                "quarantined_count": 0,
                "quorum_approved_count": 0,
                "bundle_verification_pass_count": 0,
                "bundle_verification_failure_count": 0,
                "independent_audit_pass_count": 0,
                "reference_promoted_all_three_count": promoted,
                "reference_partial_count": counts.get("PARTIAL_REFERENCE_SET", 0),
                "cumulative_allowed_eval_count": 13,
                "cumulative_reference_promoted_count": cumulative_promoted,
            }
        )

    with (OUT_DIR / "screening_yield_by_batch.csv").open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "batch_id",
            "batch_type",
            "candidates_screened",
            "deterministic_denials",
            "parser_required_count",
            "quarantined_count",
            "quorum_approved_count",
            "bundle_verification_pass_count",
            "bundle_verification_failure_count",
            "independent_audit_pass_count",
            "reference_promoted_all_three_count",
            "reference_partial_count",
            "cumulative_allowed_eval_count",
            "cumulative_reference_promoted_count",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(wave_rows)

    blockers = {
        "status": "BLOCKER_ANALYSIS_AFTER_THREE_LOW_YIELD_REFERENCE_WAVES",
        "source_screening_started": False,
        "reason_source_screening_not_started": "expanded candidate registry has zero READY_FOR_SOURCE_SCREENING projects",
        "ready_for_source_screening_count": registry["status_counts"].get("READY_FOR_SOURCE_SCREENING", 0),
        "reference_presence_review_required_count": registry["status_counts"].get("REFERENCE_PRESENCE_REVIEW_REQUIRED", 0),
        "reference_presence_waves_completed": len(wave_rows),
        "reference_presence_projects_screened": cumulative_screened,
        "reference_presence_promoted_all_three": cumulative_promoted,
        "dominant_blockers": [
            {
                "blocker_id": "NO_NEW_VERIFIED_ALL_THREE_REFERENCE_SETS",
                "count": registry["status_counts"].get("REFERENCE_PRESENCE_REVIEW_REQUIRED", 0),
                "evidence": "metadata v2 found zero new ready candidates; first 18 isolated reference-presence reviews remained PARTIAL_REFERENCE_SET",
                "recommended_layer": "reference_detection_policy_and_source_inventory",
                "action": "Do not weaken all-three requirement. Continue reference-presence review only if improved isolated classifier can distinguish target production/punch drawings without using forbidden production-control or electrical PDFs.",
            },
            {
                "blocker_id": "PARTIAL_SETS_ARE_SHEET_METAL_ONLY_IN_TOP_RANKS",
                "count": cumulative_screened,
                "evidence": "waves 001-003 detected only SHEET_METAL output type for all reviewed projects",
                "recommended_layer": "inventory_reconciliation",
                "action": "Treat as source availability blocker unless later metadata or isolated classification finds separate production and punch target PDFs.",
            },
        ],
        "forbidden_boundary_preserved": True,
        "generation_authorized": False,
    }
    write_json(OUT_DIR / "dominant_blockers.json", blockers)

    report = [
        "# Expanded Screening Yield Summary",
        "",
        "- status: `PRE_SOURCE_SCREENING_BLOCKED_BY_REFERENCE_PRESENCE`",
        "- source-screening batches completed: `0`",
        f"- reference-presence waves completed: `{len(wave_rows)}`",
        f"- reference-presence projects screened: `{cumulative_screened}`",
        f"- projects promoted to all-three reference availability: `{cumulative_promoted}`",
        "- cumulative ALLOWED_EVAL count: `13`",
        "- baseline generation attempts: `0`",
        "",
        "The expanded candidate registry contains no immediate `READY_FOR_SOURCE_SCREENING` projects. Three isolated reference-presence waves were run against the highest-ranked partial-reference projects; all remained `PARTIAL_REFERENCE_SET` with only sheet-metal target evidence.",
        "",
        "No eligibility requirement was lowered. Source screening and generation remain blocked.",
    ]
    (OUT_DIR / "screening_yield_summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
