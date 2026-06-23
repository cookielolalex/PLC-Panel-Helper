from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_lib import read_json, sha256_file


EVALUATOR_VERSION = "plc_layout_evaluator_v2_sensitivity"

DIMENSIONS = [
    "source_selection_provenance_conflict",
    "panel_schedule_enclosure_facts",
    "device_bom_quantity_tag_fidelity",
    "shared_geometry_cross_pdf_consistency",
    "production_drawing_quality",
    "punch_drawing_quality",
    "sheetmetal_drawing_quality",
]


def _round_score(value: float) -> float | int:
    rounded = round(value, 2)
    return int(rounded) if rounded.is_integer() else rounded


def _deduped_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped = []
    for finding in findings:
        key = str(finding.get("dedupe_key") or finding.get("finding_id") or finding.get("finding"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _coverage(record: dict[str, Any]) -> tuple[float, str]:
    coverage = record.get("coverage", {})
    scorable = float(coverage.get("scorable_elements", 0) or 0)
    total = float(coverage.get("total_elements", 0) or 0)
    if total <= 0 or scorable <= 0:
        return 0.0, "INSUFFICIENT_COVERAGE"
    pct = round((scorable / total) * 100, 2)
    if pct >= 85:
        strength = "HIGH_EVIDENCE"
    elif pct >= 65:
        strength = "MEDIUM_EVIDENCE"
    else:
        strength = "LOW_EVIDENCE"
    return pct, strength


def compute_score(record: dict[str, Any]) -> dict[str, Any]:
    validity_inputs = record.get("validity_inputs", {})
    hard_gate_failures = list(validity_inputs.get("hard_gate_failures", []))
    if validity_inputs.get("required_outputs_present") is False:
        hard_gate_failures.append("MISSING_REQUIRED_PDF")

    dimension_scores: dict[str, float | int] = {}
    dimension_details: dict[str, list[dict[str, Any]]] = {}
    for dimension, items in record.get("dimension_items", {}).items():
        raw_score = 0.0
        normalized_items = []
        for item in items:
            max_score = float(item.get("max_score", 0) or 0)
            score = min(max(float(item.get("score", 0) or 0), 0.0), max_score)
            raw_score += score
            normalized_items.append({**item, "score": _round_score(score), "max_score": _round_score(max_score)})
        dimension_scores[dimension] = _round_score(raw_score)
        dimension_details[dimension] = normalized_items

    for dimension in DIMENSIONS:
        dimension_scores.setdefault(dimension, 0)
        dimension_details.setdefault(dimension, [])

    coverage, evidence_strength = _coverage(record)
    findings = _deduped_findings(list(record.get("findings", [])))
    validity = "FAIL" if hard_gate_failures else "PASS"
    quality_score = _round_score(sum(float(dimension_scores[d]) for d in DIMENSIONS))
    if validity == "FAIL":
        quality_score = 0
    confidence = record.get("confidence")
    if not confidence:
        confidence = "LOW" if evidence_strength in {"LOW_EVIDENCE", "INSUFFICIENT_COVERAGE"} else "MEDIUM"

    output_type_scores = record.get("output_type_scores")
    if not output_type_scores:
        output_type_scores = {
            "production": dimension_scores["production_drawing_quality"],
            "sheetmetal": dimension_scores["sheetmetal_drawing_quality"],
            "punch": dimension_scores["punch_drawing_quality"],
        }

    return {
        "run_id": record.get("run_id", ""),
        "validity": validity,
        "quality_score": quality_score,
        "scorable_coverage": _round_score(coverage),
        "confidence": confidence,
        "critical_findings": sum(1 for f in findings if f.get("severity") == "CRITICAL"),
        "high_findings": sum(1 for f in findings if f.get("severity") == "HIGH"),
        "dimension_scores": dimension_scores,
        "hard_gate_failures": hard_gate_failures,
        "output_type_scores": output_type_scores,
        "findings": [
            {
                "severity": f.get("severity", "INFO"),
                "classification": f.get("classification", "UNRESOLVED"),
                "finding": f.get("finding", ""),
            }
            for f in findings
        ],
        "comparison_limitations": list(record.get("comparison_limitations", [])),
        "run_metadata": {
            **record.get("run_metadata", {}),
            "evaluator_version": EVALUATOR_VERSION,
            "scoring_record_sha256": record.get("scoring_record_sha256"),
            "evidence_strength": evidence_strength,
        },
        "scoring_evidence": {
            "evaluator_version": EVALUATOR_VERSION,
            "coverage": record.get("coverage", {}),
            "dimension_items": dimension_details,
            "deduped_finding_count": len(findings),
        },
        "evidence_strength": evidence_strength,
    }


def _read_generated_json(run_dir: Path, prefix: str, project_id: str) -> dict[str, Any]:
    path = run_dir / "generated" / f"{prefix}_{project_id}.json"
    if path.exists():
        return read_json(path)
    matches = sorted((run_dir / "generated").glob(f"{prefix}_*.json"))
    return read_json(matches[0]) if matches else {}


def build_calibration_scoring_record(run_dir: Path, project_id: str, comparison: dict[str, Any]) -> dict[str, Any]:
    run_id = run_dir.name
    job_spec = _read_generated_json(run_dir, "job_spec", project_id)
    drawing_model = _read_generated_json(run_dir, "drawing_model", project_id)
    pdf_validation = read_json(run_dir / "generated" / "pdf_validation.json")
    generation_complete = read_json(run_dir / "generation_complete.json")
    freeze = read_json(run_dir / "freeze_manifest.json")

    source_refs = job_spec.get("source_references", [])
    unresolved_fields = job_spec.get("unresolved_fields", [])
    panels = drawing_model.get("panels", [])
    required_pdf_count = sum(1 for check in pdf_validation.get("checks", []) if check.get("exists") and check.get("pages", 0) > 0)
    paired_outputs = sum(1 for pairing in comparison.get("pairings", []) if pairing.get("status") == "PAIRED")
    reliable_overlay = any(pairing.get("overlay_created") for pairing in comparison.get("pairings", []))
    hard_gates = list(pdf_validation.get("hard_gate_failures", []))
    if generation_complete.get("status") != "PASS":
        hard_gates.append("GENERATION_NOT_PASSING")

    source_score = 14 if source_refs else 0
    panel_score = 5 if panels and unresolved_fields else (12 if panels else 0)
    device_score = 8 if panels and not any(panel.get("devices") for panel in panels) else (14 if panels else 0)
    cross_pdf_score = 8 if required_pdf_count == 3 and paired_outputs == 3 else 0
    production_score = 3 if required_pdf_count >= 1 else 0
    punch_score = 2 if required_pdf_count >= 3 else 0
    sheetmetal_score = 2 if required_pdf_count >= 2 else 0
    if reliable_overlay:
        cross_pdf_score = max(cross_pdf_score, 12)

    coverage_items = [
        {"item_id": "verified_source_provenance", "scorable": 20 if source_refs else 0, "denominator": 20},
        {"item_id": "required_pdf_readability", "scorable": required_pdf_count * 3, "denominator": 9},
        {"item_id": "canonical_model_panel_structure", "scorable": 9 if panels and drawing_model.get("job_spec_hash") else 0, "denominator": 9},
        {"item_id": "exact_reference_geometry", "scorable": 0, "denominator": 34},
        {"item_id": "device_and_material_specifics", "scorable": 0, "denominator": 28},
    ]
    scorable = sum(item["scorable"] for item in coverage_items)
    denominator = sum(item["denominator"] for item in coverage_items)

    findings = [
        {
            "finding_id": f"{run_id}:missing_exact_dimensions",
            "dedupe_key": "missing_exact_dimensions",
            "severity": "HIGH",
            "classification": "UNAVAILABLE_IN_ALLOWED_INPUT",
            "finding": "Exact enclosure and cutout dimensions were not available in the allowed sanitized bundle; generated drawings remain schematic/TBD.",
        },
        {
            "finding_id": f"{run_id}:reference_layout_unavailable",
            "dedupe_key": "reference_layout_unavailable",
            "severity": "HIGH",
            "classification": "UNAVAILABLE_IN_ALLOWED_INPUT",
            "finding": "Reference-specific layout decisions could not be scored as source-supported because completed references were unavailable to the generator.",
        },
        {
            "finding_id": f"{run_id}:schematic_minimal",
            "dedupe_key": "schematic_minimal",
            "severity": "HIGH",
            "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS",
            "finding": "All three PDFs are internally consistent but minimal and not fabrication-ready.",
        },
    ]

    return {
        "record_version": "calibration_scoring_record_v2",
        "evaluator_version": EVALUATOR_VERSION,
        "run_id": run_id,
        "project_id": project_id,
        "validity_inputs": {
            "required_outputs_present": required_pdf_count == 3,
            "hard_gate_failures": hard_gates,
        },
        "coverage": {
            "scorable_elements": scorable,
            "total_elements": denominator,
            "items": coverage_items,
        },
        "dimension_items": {
            "source_selection_provenance_conflict": [
                {"item_id": "verified_source_bundle_and_provenance", "score": source_score, "max_score": 20, "classification": "EXPLICIT_IN_ALLOWED_INPUT"}
            ],
            "panel_schedule_enclosure_facts": [
                {"item_id": "panel_schedule_with_unresolved_fabrication_facts", "score": panel_score, "max_score": 15, "classification": "UNAVAILABLE_IN_ALLOWED_INPUT"}
            ],
            "device_bom_quantity_tag_fidelity": [
                {"item_id": "device_bom_not_extracted_from_allowed_bundle", "score": device_score, "max_score": 20, "classification": "UNAVAILABLE_IN_ALLOWED_INPUT"}
            ],
            "shared_geometry_cross_pdf_consistency": [
                {"item_id": "canonical_model_cross_pdf_consistency_metadata_only", "score": cross_pdf_score, "max_score": 15, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
            "production_drawing_quality": [
                {"item_id": "production_pdf_schematic_readable", "score": production_score, "max_score": 10, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
            "punch_drawing_quality": [
                {"item_id": "punch_pdf_schematic_readable", "score": punch_score, "max_score": 10, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
            "sheetmetal_drawing_quality": [
                {"item_id": "sheetmetal_pdf_schematic_readable", "score": sheetmetal_score, "max_score": 10, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
        },
        "output_type_scores": {"production": 14, "sheetmetal": 14, "punch": 14},
        "findings": findings,
        "comparison_limitations": list(comparison.get("limitations", [])),
        "run_metadata": {
            "reference_access_after_freeze": True,
            "reviewer_workspace": str(Path("evals") / "sandboxes" / run_id / "reviewer_workspace"),
            "rubric": "plc_layout_v2",
            "freeze_hash": freeze.get("freeze_hash"),
            "generation_complete_sha256": sha256_file(run_dir / "generation_complete.json"),
            "freeze_manifest_sha256": sha256_file(run_dir / "freeze_manifest.json"),
            "pdf_validation_sha256": sha256_file(run_dir / "generated" / "pdf_validation.json"),
        },
    }
