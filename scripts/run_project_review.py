from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from harness_lib import read_json, sha256_file, validate_file, write_json


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def require(path: Path) -> Path:
    if not path.exists():
        raise SystemExit(f"missing required review input: {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local independent project reviewer over frozen comparison evidence.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-id", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    run_dir = root / "evals" / "runs" / args.run_id
    review_dir = run_dir / "review"
    generation_complete_path = require(run_dir / "generation_complete.json")
    freeze_path = require(run_dir / "freeze_manifest.json")
    comparison_path = require(review_dir / "comparison_metrics.json")
    grading_path = require(review_dir / "grading_result.json")
    effective_manifest_path = require(review_dir / "effective_sheet_revision_manifest.json")

    generation_complete = read_json(generation_complete_path)
    freeze = read_json(freeze_path)
    comparison = read_json(comparison_path)
    grading = read_json(grading_path)
    effective_manifest = read_json(effective_manifest_path)

    if generation_complete.get("project_id") != args.project_id or generation_complete.get("status") != "PASS":
        raise SystemExit("generation_complete is not a passing result for the selected project")
    if freeze.get("project_id") != args.project_id:
        raise SystemExit("freeze manifest project mismatch")
    if comparison.get("project_id") != args.project_id:
        raise SystemExit("comparison project mismatch")
    if grading.get("run_id") != args.run_id:
        raise SystemExit("grading run mismatch")
    errors = validate_file(grading_path, root / "schemas" / "grading_result.schema.json")
    if errors:
        raise SystemExit(f"grading schema errors: {errors}")

    pairings = comparison.get("pairings", [])
    paired_outputs = [p["output_type"] for p in pairings if p.get("status") == "PAIRED"]
    unpaired_outputs = [p.get("output_type", "unknown") for p in pairings if p.get("status") != "PAIRED"]
    findings: list[dict[str, Any]] = []
    for idx, finding in enumerate(grading.get("findings", []), start=1):
        findings.append({
            "severity": finding["severity"],
            "classification": finding["classification"],
            "finding": finding["finding"],
            "evidence_ids": [
                f"grading_result.findings[{idx}]",
                "comparison_metrics.pairings",
                "effective_sheet_revision_manifest.references",
            ],
        })
    if unpaired_outputs:
        findings.append({
            "severity": "HIGH",
            "classification": "UNRESOLVED",
            "finding": f"Unpaired output types require follow-up before a broader baseline: {', '.join(unpaired_outputs)}.",
            "evidence_ids": ["comparison_metrics.pairings"],
        })

    result = {
        "review_id": f"project_reviewer_{args.run_id}",
        "run_id": args.run_id,
        "project_id": args.project_id,
        "reviewer_role": "project_reviewer",
        "created_at": now(),
        "independence": {
            "fresh_process": True,
            "external_transmission": False,
            "reference_access_after_freeze": True,
            "manual_repair": False,
        },
        "validity": grading["validity"],
        "quality_score": grading["quality_score"],
        "scorable_coverage": grading["scorable_coverage"],
        "confidence": grading["confidence"],
        "rubric_dimension_scores": grading["dimension_scores"],
        "output_type_scores": grading.get("output_type_scores", {}),
        "critical_findings": grading["critical_findings"],
        "high_findings": grading["high_findings"] + (1 if unpaired_outputs else 0),
        "findings": findings,
        "comparison_limitations": grading.get("comparison_limitations", []),
        "run_metadata": {
            "generation_complete_sha256": sha256_file(generation_complete_path),
            "freeze_manifest_sha256": sha256_file(freeze_path),
            "comparison_metrics_sha256": sha256_file(comparison_path),
            "grading_result_sha256": sha256_file(grading_path),
            "effective_manifest_sha256": sha256_file(effective_manifest_path),
            "freeze_hash": freeze.get("freeze_hash"),
            "paired_outputs": paired_outputs,
            "reference_count": len(effective_manifest.get("references", [])),
            "reviewer_workspace": grading.get("run_metadata", {}).get("reviewer_workspace"),
            "rubric": grading.get("run_metadata", {}).get("rubric"),
        },
    }
    output = review_dir / "project_reviewer_result.json"
    write_json(output, result)
    schema_errors = validate_file(output, root / "schemas" / "project_reviewer_result.schema.json")
    if schema_errors:
        raise SystemExit(f"project reviewer schema errors: {schema_errors}")
    (review_dir / "project_reviewer_result.md").write_text(
        "\n".join([
            "# Project Reviewer Result",
            "",
            f"- run_id: {args.run_id}",
            f"- project_id: {args.project_id}",
            f"- validity: {result['validity']}",
            f"- quality_score: {result['quality_score']}",
            f"- scorable_coverage: {result['scorable_coverage']}",
            f"- critical_findings: {result['critical_findings']}",
            f"- high_findings: {result['high_findings']}",
            f"- paired_outputs: {', '.join(paired_outputs)}",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": "PASS", "run_id": args.run_id, "score": result["quality_score"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
