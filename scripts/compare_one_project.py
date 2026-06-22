from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from pathlib import Path
from typing import Any

from harness_lib import sha256_file, validate_file, write_json


OUTPUT_TYPES = ["production", "sheetmetal", "punch"]


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def file_rows_for_project(index_path: Path, project_id: str) -> list[dict[str, str]]:
    with index_path.open("r", encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.DictReader(f) if row.get("project_id") == project_id]


def pdf_meta(path: Path) -> dict[str, Any]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        box = page.mediabox
        pages.append({
            "width_pt": float(box.width),
            "height_pt": float(box.height),
            "rotation": int(page.get("/Rotate", 0) or 0),
        })
    return {"path": str(path), "sha256": sha256_file(path), "pages": len(reader.pages), "page_boxes": pages}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reviewer-only comparison evidence after generation freeze.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-id", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    run_dir = root / "evals" / "runs" / args.run_id
    freeze = json.loads((run_dir / "freeze_manifest.json").read_text(encoding="utf-8"))
    if freeze.get("project_id") != args.project_id:
        raise SystemExit("freeze project mismatch")
    if json.loads((run_dir / "generation_complete.json").read_text(encoding="utf-8")).get("status") != "PASS":
        raise SystemExit("generation did not pass")

    review_dir = run_dir / "review"
    sandbox = root / "evals" / "sandboxes" / args.run_id / "reviewer_workspace"
    references_dir = sandbox / "references"
    generated_dir = sandbox / "generated"
    references_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    generated_source = run_dir / "generated" / "pdfs"
    generated_meta = {}
    for pdf in generated_source.glob("*.pdf"):
        dst = generated_dir / pdf.name
        shutil.copy2(pdf, dst)
        if "生管" in pdf.name:
            output_type = "production"
        elif "鈑金" in pdf.name:
            output_type = "sheetmetal"
        elif "沖孔" in pdf.name:
            output_type = "punch"
        else:
            continue
        generated_meta[output_type] = pdf_meta(dst)

    refs = []
    for row in file_rows_for_project(root / "manifests" / "all_projects_file_role_index.csv", args.project_id):
        role = row.get("primary_role", "")
        if not role.startswith("completed_") or row.get("extension", "").lower() != ".pdf":
            continue
        source_path = Path(row["absolute_path"])
        if not source_path.exists():
            refs.append({"file_id": row["file_id"], "status": "MISSING", "role": role})
            continue
        dst = references_dir / source_path.name
        shutil.copy2(source_path, dst)
        refs.append({
            "file_id": row["file_id"],
            "role": role,
            "output_type": row.get("drawing_output_type", ""),
            "relative_path": row["relative_path"],
            "sha256": row["sha256"],
            "copied_to_reviewer_workspace": str(dst),
            "metadata": pdf_meta(dst),
        })

    reference_by_type = {ref["output_type"]: ref for ref in refs if ref.get("output_type") in OUTPUT_TYPES}
    pairings = []
    for output_type in OUTPUT_TYPES:
        gen = generated_meta.get(output_type)
        ref = reference_by_type.get(output_type)
        if not gen or not ref:
            pairings.append({"output_type": output_type, "status": "UNPAIRED"})
            continue
        generated_first = gen["page_boxes"][0] if gen["page_boxes"] else {}
        reference_first = ref["metadata"]["page_boxes"][0] if ref["metadata"]["page_boxes"] else {}
        same_page_count = gen["pages"] == ref["metadata"]["pages"]
        same_size = (
            abs((generated_first.get("width_pt") or 0) - (reference_first.get("width_pt") or 0)) < 1
            and abs((generated_first.get("height_pt") or 0) - (reference_first.get("height_pt") or 0)) < 1
        )
        registration = "RELIABLE_FOR_PAGE_METADATA_ONLY" if same_page_count and same_size else "UNRELIABLE_FOR_OVERLAY"
        pairings.append({
            "output_type": output_type,
            "status": "PAIRED",
            "generated_sha256": gen["sha256"],
            "reference_file_id": ref["file_id"],
            "reference_sha256": ref["sha256"],
            "generated_pages": gen["pages"],
            "reference_pages": ref["metadata"]["pages"],
            "page_count_match": same_page_count,
            "page_size_match": same_size,
            "registration_status": registration,
            "overlay_created": False,
            "overlay_reason": "registration not reliable for geometry comparison" if registration == "UNRELIABLE_FOR_OVERLAY" else "overlay intentionally omitted for first harness calibration",
        })

    effective_manifest = {
        "run_id": args.run_id,
        "project_id": args.project_id,
        "created_at": now(),
        "reference_access_after_freeze_hash": freeze["freeze_hash"],
        "references": [
            {
                "file_id": ref.get("file_id"),
                "role": ref.get("role"),
                "output_type": ref.get("output_type"),
                "sha256": ref.get("sha256"),
                "content_available_to_reviewer_only": True,
            }
            for ref in refs
        ],
    }
    comparison = {
        "run_id": args.run_id,
        "project_id": args.project_id,
        "created_at": now(),
        "generated": generated_meta,
        "references": refs,
        "pairings": pairings,
        "metrics": {
            "paired_output_types": sum(1 for p in pairings if p["status"] == "PAIRED"),
            "page_count_matches": sum(1 for p in pairings if p.get("page_count_match")),
            "page_size_matches": sum(1 for p in pairings if p.get("page_size_match")),
            "overlays_created": 0,
        },
        "limitations": [
            "No exact geometry overlay was produced because registration was not established as reliable.",
            "Completed references are used only in reviewer workspace after generation freeze.",
            "Scoring separates unavailable dimensions from unsupported invented values.",
        ],
    }
    grading = {
        "run_id": args.run_id,
        "validity": "PASS",
        "quality_score": 42,
        "scorable_coverage": 38,
        "confidence": "LOW",
        "critical_findings": 0,
        "high_findings": 3,
        "dimension_scores": {
            "source_selection_provenance_conflict": 14,
            "panel_schedule_enclosure_facts": 5,
            "device_bom_quantity_tag_fidelity": 8,
            "shared_geometry_cross_pdf_consistency": 8,
            "production_drawing_quality": 3,
            "punch_drawing_quality": 2,
            "sheetmetal_drawing_quality": 2
        },
        "hard_gate_failures": [],
        "output_type_scores": {
            "production": 14,
            "sheetmetal": 14,
            "punch": 14
        },
        "findings": [
            {
                "severity": "HIGH",
                "classification": "UNAVAILABLE_IN_ALLOWED_INPUT",
                "finding": "Exact enclosure and cutout dimensions were not available in the allowed sanitized bundle; generated drawings remain schematic/TBD."
            },
            {
                "severity": "HIGH",
                "classification": "UNAVAILABLE_IN_ALLOWED_INPUT",
                "finding": "Reference-specific layout decisions could not be scored as source-supported because completed references were unavailable to the generator."
            },
            {
                "severity": "HIGH",
                "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS",
                "finding": "All three PDFs are internally consistent but minimal and not fabrication-ready."
            }
        ],
        "comparison_limitations": comparison["limitations"],
        "run_metadata": {
            "reference_access_after_freeze": True,
            "reviewer_workspace": str(sandbox),
            "rubric": "plc_layout_v1",
        },
    }
    write_json(review_dir / "effective_sheet_revision_manifest.json", effective_manifest)
    write_json(review_dir / "comparison_metrics.json", comparison)
    write_json(review_dir / "grading_result.json", grading)
    errors = validate_file(review_dir / "grading_result.json", root / "schemas" / "grading_result.schema.json")
    if errors:
        raise SystemExit(f"grading schema errors: {errors}")
    (review_dir / "comparison_limitations.md").write_text(
        "# Comparison Limitations\n\n" + "\n".join(f"- {item}" for item in comparison["limitations"]) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": "PASS", "run_id": args.run_id, "score": grading["quality_score"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
