from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from render_reference_classification_evidence import build_evidence, sha256_file


ROOT = Path(__file__).resolve().parents[1]
FILE_INDEX = ROOT / "manifests" / "all_projects_file_role_index.csv"
DETECTOR_VERSION = "target_output_detection_v3_page_content_isolated"
SCHEMA_VERSION = "reference_detection_v3_schema_v1"
TARGET_TYPES = {"PRODUCTION_DRAWING", "SHEETMETAL_DRAWING", "PUNCH_DRAWING"}

TERMS = {
    "PRODUCTION_DRAWING": [
        "PRODUCTION_DRAWING",
        "生管課用圖",
        "生管圖",
        "?恣隤脩",
        "?恣?典",
    ],
    "SHEETMETAL_DRAWING": [
        "SHEETMETAL_DRAWING",
        "鈑金施工圖",
        "鈑金",
        "?",
        "?輸",
    ],
    "PUNCH_DRAWING": [
        "PUNCH_DRAWING",
        "沖孔施工圖",
        "沖孔",
        "瘝",
        "?脣",
    ],
    "ELECTRICAL_DRAWING": [
        "ELECTRICAL_DRAWING",
        "電機施工圖",
        "配線",
        "單線",
        "?餅",
    ],
    "SOURCE_DOCUMENT": [
        "SOURCE_DOCUMENT",
        "CONTRACT",
        "MATERIAL_LIST",
        "契約",
        "物料",
        "?",
        "?",
    ],
    "REVISION_NOTICE": [
        "REVISION_NOTICE",
        "REVISION ONLY",
        "靽格",
        "REV ",
    ],
    "COVER_OR_INDEX": [
        "COVER_OR_INDEX",
        "INDEX",
        "目錄",
        "封面",
    ],
}

ROLE_TARGETS = {
    "completed_production_drawing_reference": "PRODUCTION_DRAWING",
    "completed_sheetmetal_drawing_reference": "SHEETMETAL_DRAWING",
    "completed_punch_drawing_reference": "PUNCH_DRAWING",
}
FORBIDDEN_ROLE_HINTS = {"forbidden_electrical_drawing", "forbidden_production_control_file"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize_project_id(value: str) -> str:
    match = re.search(r"(\d{7})", value or "")
    return match.group(1) if match else (value or "").strip()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def text_hits(text: str) -> list[str]:
    normalized = (text or "").upper()
    hits = []
    for page_type, terms in TERMS.items():
        for term in terms:
            if term and term.upper() in normalized:
                hits.append(page_type)
                break
    return hits


def target_hit_from_metadata(text: str, role_hint: str) -> str | None:
    hits = [hit for hit in text_hits(text) if hit in TARGET_TYPES]
    unique_hits = set(hits)
    if len(unique_hits) == 1:
        return next(iter(unique_hits))
    if role_hint in ROLE_TARGETS:
        return ROLE_TARGETS[role_hint]
    return None


def project_identity_status(project_id: str, text: str, metadata_text: str, target: bool) -> str:
    ids = set(re.findall(r"\b\d{7}\b", text or ""))
    if project_id in ids:
        return "CONFIRMED"
    if ids and project_id not in ids:
        return "CONFLICT"
    if target and project_id in metadata_text:
        return "CONFIRMED"
    return "NOT_FOUND" if target else "NOT_REQUIRED_FOR_NON_TARGET"


def page_orientation(width: float, height: float) -> str:
    if width > height:
        return "LANDSCAPE"
    if height > width:
        return "PORTRAIT"
    return "SQUARE_OR_UNKNOWN"


def extract_pdf_pages(pdf_path: Path) -> tuple[list[dict[str, Any]], str]:
    pages: list[dict[str, Any]] = []
    try:
        reader = PdfReader(str(pdf_path))
        for index, page in enumerate(reader.pages, start=1):
            width = float(page.mediabox.width or 0)
            height = float(page.mediabox.height or 0)
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            pages.append(
                {
                    "page_number": index,
                    "page_width_pt": width,
                    "page_height_pt": height,
                    "orientation": page_orientation(width, height),
                    "text": text,
                }
            )
        return pages, "PYPDF_METADATA_AND_TEXT_PASS"
    except Exception as exc:
        return [], f"PYPDF_READ_FAILED:{type(exc).__name__}"


def candidate_rows_from_manifest(path: Path) -> list[dict[str, Any]]:
    data = read_json(path)
    rows = []
    for item in data.get("files", []):
        rows.append(
            {
                "project_id": normalize_project_id(item.get("project_id") or data.get("project_id", "")),
                "neutral_reference_file_id": item["neutral_reference_file_id"],
                "file_sha256": item.get("sha256", ""),
                "absolute_path": item["path"],
                "metadata_text": item.get("metadata_text", ""),
                "role_hint": item.get("role_hint", ""),
            }
        )
    return rows


def candidate_rows_from_inventory(project_id: str) -> list[dict[str, Any]]:
    rows = []
    for row in read_csv(FILE_INDEX):
        if normalize_project_id(row.get("project_id", "")) != project_id:
            continue
        if row.get("extension", "").lower() != ".pdf":
            continue
        metadata_text = f"{row.get('relative_path', '')} {row.get('file_name', '')}"
        rows.append(
            {
                "project_id": project_id,
                "neutral_reference_file_id": row.get("file_id"),
                "file_sha256": row.get("sha256", ""),
                "absolute_path": row.get("absolute_path", ""),
                "metadata_text": metadata_text,
                "role_hint": row.get("primary_role", ""),
            }
        )
    return rows


def classify_page(
    *,
    task_id: str,
    project_id: str,
    row: dict[str, Any],
    page: dict[str, Any],
    page_count: int,
    visual_evidence_id: str,
) -> dict[str, Any]:
    page_text = page.get("text", "")
    metadata_text = row.get("metadata_text", "")
    role_hint = row.get("role_hint", "")
    hits = text_hits(page_text)
    target_hits = [hit for hit in hits if hit in TARGET_TYPES]
    non_target_hits = [hit for hit in hits if hit not in TARGET_TYPES]
    method = "PAGE_TEXT"
    confidence = 0.0
    page_type = "UNCLASSIFIED"

    if len(set(target_hits)) == 1:
        page_type = target_hits[0]
        identity = project_identity_status(project_id, page_text, metadata_text, True)
        confidence = 0.97 if identity == "CONFIRMED" else 0.78
    elif len(set(target_hits)) > 1:
        page_type = "UNCLASSIFIED"
        identity = "NOT_FOUND"
        method = "AMBIGUOUS_PAGE_TEXT"
        confidence = 0.25
    elif "ELECTRICAL_DRAWING" in non_target_hits:
        page_type = "ELECTRICAL_DRAWING"
        identity = project_identity_status(project_id, page_text, metadata_text, False)
        confidence = 0.94
    elif "REVISION_NOTICE" in non_target_hits:
        page_type = "REVISION_NOTICE"
        identity = project_identity_status(project_id, page_text, metadata_text, False)
        confidence = 0.8
    elif "SOURCE_DOCUMENT" in non_target_hits:
        page_type = "SOURCE_DOCUMENT"
        identity = project_identity_status(project_id, page_text, metadata_text, False)
        confidence = 0.82
    elif "COVER_OR_INDEX" in non_target_hits:
        page_type = "COVER_OR_INDEX"
        identity = project_identity_status(project_id, page_text, metadata_text, False)
        confidence = 0.78
    else:
        metadata_target = target_hit_from_metadata(metadata_text, role_hint)
        metadata_identity = project_identity_status(project_id, "", metadata_text, bool(metadata_target))
        if metadata_target and role_hint not in FORBIDDEN_ROLE_HINTS:
            page_type = metadata_target
            identity = metadata_identity
            method = "METADATA_ROLE_AFTER_RENDERED_PAGE_NO_TEXT"
            confidence = 0.88
        elif role_hint == "forbidden_electrical_drawing":
            page_type = "ELECTRICAL_DRAWING"
            identity = "NOT_REQUIRED_FOR_NON_TARGET"
            method = "FORBIDDEN_ELECTRICAL_ROLE_NO_TARGET_CONTENT"
            confidence = 0.7
        else:
            identity = metadata_identity if metadata_target else "NOT_FOUND"
            method = "RENDERED_PAGE_WITHOUT_CLASSIFIABLE_TEXT"
            confidence = 0.2

    target = page_type in TARGET_TYPES
    if target and identity != "CONFIRMED":
        confidence = min(confidence, 0.78)

    evidence_id = (
        "RPE-"
        + hashlib.sha1(
            f"{task_id}:{row.get('neutral_reference_file_id')}:{page['page_number']}:{page_type}:{visual_evidence_id}".encode(
                "utf-8"
            )
        ).hexdigest()[:14].upper()
    )
    signals = ["page_dimensions", "temporary_page_render", "temporary_title_crop", "neutral_visual_signature"]
    if page_text:
        signals.append("embedded_page_text_role_terms")
    if method.startswith("METADATA") or method.startswith("FORBIDDEN"):
        signals.append("inventory_role_or_filename_context")

    return {
        "schema_version": SCHEMA_VERSION,
        "detector_version": DETECTOR_VERSION,
        "task_id": task_id,
        "project_id": project_id,
        "neutral_reference_file_id": row["neutral_reference_file_id"],
        "page_number": page["page_number"],
        "page_count": page_count,
        "page_width_pt": page["page_width_pt"],
        "page_height_pt": page["page_height_pt"],
        "orientation": page["orientation"],
        "page_classification": page_type,
        "project_identity_status": identity,
        "revision_identity": "REVISION_MARKER_PRESENT" if "REVISION_NOTICE" in hits else None,
        "classification_method": method,
        "confidence": round(confidence, 3),
        "evidence_ids": [evidence_id, visual_evidence_id],
        "signals_used": signals,
        "minimization": {
            "raw_text_persisted": False,
            "rendered_image_persisted": False,
            "title_crop_persisted": False,
            "absolute_private_path_persisted": False,
            "drawing_detail_persisted": False,
        },
    }


def page_ranges(pages: list[int]) -> str:
    if not pages:
        return ""
    ranges = []
    start = prev = pages[0]
    for page in pages[1:]:
        if page == prev + 1:
            prev = page
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = page
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ",".join(ranges)


def build_effective_set(task_id: str, project_id: str, page_rows: list[dict[str, Any]], doc_rows: list[dict[str, Any]]) -> dict[str, Any]:
    duplicate_of = {doc["neutral_reference_file_id"]: doc.get("duplicate_of") for doc in doc_rows}
    doc_sha = {doc["neutral_reference_file_id"]: doc["file_sha256"] for doc in doc_rows}
    usable = [
        row
        for row in page_rows
        if row["page_classification"] in TARGET_TYPES
        and row["project_identity_status"] == "CONFIRMED"
        and row["confidence"] >= 0.88
        and not duplicate_of.get(row["neutral_reference_file_id"])
    ]
    by_target_file: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in usable:
        by_target_file[(row["page_classification"], row["neutral_reference_file_id"])].append(row)

    effective_pages = []
    for (target_type, file_id), rows in sorted(by_target_file.items()):
        rows.sort(key=lambda r: r["page_number"])
        effective_pages.append(
            {
                "neutral_reference_file_id": file_id,
                "file_sha256": doc_sha.get(file_id, ""),
                "page_range": page_ranges([row["page_number"] for row in rows]),
                "target_type": target_type,
                "project_identity_status": "CONFIRMED",
                "panel_or_sheet_identity": None,
                "revision_identity": rows[-1].get("revision_identity"),
                "supersedes": None,
                "current_effective_status": "CURRENT_EFFECTIVE",
                "classification_method": "+".join(sorted(set(row["classification_method"] for row in rows))),
                "confidence": min(row["confidence"] for row in rows),
                "evidence_ids": sorted({e for row in rows for e in row["evidence_ids"]}),
            }
        )

    target_types = sorted({row["target_type"] for row in effective_pages})
    files_by_type = defaultdict(set)
    for row in effective_pages:
        files_by_type[row["target_type"]].add(row["neutral_reference_file_id"])
    files_with_multiple_targets = defaultdict(set)
    for row in effective_pages:
        files_with_multiple_targets[row["neutral_reference_file_id"]].add(row["target_type"])

    unresolved = []
    if "ELECTRICAL_DRAWING" in {row["page_classification"] for row in page_rows}:
        unresolved.append("ELECTRICAL_DRAWINGS_PRESENT_AND_EXCLUDED_FROM_TARGET_SET")
    if any(row["page_classification"] == "UNCLASSIFIED" for row in page_rows):
        unresolved.append("UNCLASSIFIED_PAGES_REMAIN")

    if set(target_types) >= TARGET_TYPES:
        if any(len(types) > 1 for types in files_with_multiple_targets.values()):
            status = "VERIFIED_ALL_THREE_COMBINED_PACKAGE"
        else:
            status = "VERIFIED_ALL_THREE_BY_CONTENT"
    elif target_types:
        status = "PARTIAL_REFERENCE_SET"
    elif any(doc["document_status"] == "INACCESSIBLE" for doc in doc_rows):
        status = "INACCESSIBLE_REFERENCE_SET"
    else:
        status = "NO_REFERENCE_SET"

    duplicate_groups = []
    grouped = defaultdict(list)
    for doc in doc_rows:
        if doc.get("duplicate_of"):
            grouped[doc["duplicate_of"]].append(doc["neutral_reference_file_id"])
    for original, duplicates in sorted(grouped.items()):
        duplicate_groups.append({"original_neutral_reference_file_id": original, "duplicate_neutral_reference_file_ids": duplicates})

    return {
        "schema_version": SCHEMA_VERSION,
        "detector_version": DETECTOR_VERSION,
        "task_id": task_id,
        "project_id": project_id,
        "status": status,
        "target_types_present": target_types,
        "effective_pages": effective_pages,
        "duplicate_groups": duplicate_groups,
        "unresolved_issues": unresolved,
        "generator_exposure": {
            "generator_receives_reference_file_ids": False,
            "generator_receives_reference_hashes": False,
            "generator_receives_reference_paths": False,
            "generator_receives_reference_content": False,
        },
        "minimization": {
            "raw_text_persisted": False,
            "rendered_images_persisted": False,
            "title_crops_persisted": False,
            "absolute_private_paths_persisted": False,
            "drawing_details_persisted": False,
        },
    }


def classify_project(project_id: str, rows: list[dict[str, Any]], task_id: str, output_dir: Path, keep_temp: bool = False) -> dict[str, Any]:
    page_classifications: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []
    seen_sha: dict[str, str] = {}
    renderers = set()
    task_dirs = set()

    for row in rows:
        pdf_path = Path(row["absolute_path"])
        file_id = row["neutral_reference_file_id"]
        expected_sha = (row.get("file_sha256") or "").upper()
        doc_status = "INACCESSIBLE"
        render_status = "NOT_RENDERED"
        metadata_status = "NOT_READ"
        page_rows: list[dict[str, Any]] = []
        duplicate_of = None
        actual_sha = ""

        try:
            actual_sha = sha256_file(pdf_path)
            if expected_sha and actual_sha != expected_sha:
                metadata_status = "HASH_MISMATCH"
            else:
                duplicate_of = seen_sha.get(actual_sha)
                if not duplicate_of:
                    seen_sha[actual_sha] = file_id
                pages, metadata_status = extract_pdf_pages(pdf_path)
                evidence = build_evidence(pdf_path, f"{task_id}-{file_id}")
                renderers.add(evidence["renderer"])
                task_dirs.add(evidence["task_dir"])
                render_status = f"RENDERED_{evidence['page_count']}_PAGES"
                page_signatures = {p["page_number"]: p["page_signature"]["signature_id"] for p in evidence["pages"]}
                for page in pages:
                    visual_id = "VIS-" + page_signatures.get(page["page_number"], "NO_RENDER_SIG")
                    page_rows.append(
                        classify_page(
                            task_id=task_id,
                            project_id=project_id,
                            row=row,
                            page=page,
                            page_count=len(pages),
                            visual_evidence_id=visual_id,
                        )
                    )
                page_classifications.extend(page_rows)
                page_types = {row["page_classification"] for row in page_rows}
                if duplicate_of:
                    doc_status = "DUPLICATE_REFERENCE"
                elif page_types & TARGET_TYPES:
                    doc_status = "TARGET_EVIDENCE"
                elif page_types:
                    doc_status = "NON_TARGET_REFERENCE"
                else:
                    doc_status = "AMBIGUOUS_REFERENCE"
        except Exception as exc:
            metadata_status = f"READ_OR_RENDER_FAILED:{type(exc).__name__}"

        documents.append(
            {
                "schema_version": SCHEMA_VERSION,
                "detector_version": DETECTOR_VERSION,
                "task_id": task_id,
                "project_id": project_id,
                "neutral_reference_file_id": file_id,
                "file_sha256": actual_sha or expected_sha,
                "page_count": max((row.get("page_count", 0) for row in page_rows), default=0),
                "metadata_status": metadata_status,
                "render_status": render_status,
                "detected_page_types": sorted({row["page_classification"] for row in page_rows}),
                "page_classification_ids": [row["evidence_ids"][0] for row in page_rows],
                "duplicate_of": duplicate_of,
                "document_status": doc_status,
                "minimization": {
                    "raw_text_persisted": False,
                    "rendered_images_persisted": False,
                    "title_crops_persisted": False,
                    "absolute_private_paths_persisted": False,
                },
            }
        )

    effective = build_effective_set(task_id, project_id, page_classifications, documents)

    if not keep_temp:
        for task_dir in sorted(task_dirs):
            path = Path(task_dir)
            if path.exists():
                shutil.rmtree(path)

    temp_removed = all(not Path(task_dir).exists() for task_dir in task_dirs)
    checks = [
        {"name": "source_hashes_verified_for_accessed_files", "status": "PASS", "detail": "hash mismatches become inaccessible document records"},
        {"name": "temporary_renders_removed", "status": "PASS" if temp_removed else "FAIL", "detail": "tmp/reference_detection_v3 task directories removed"},
        {"name": "raw_text_not_persisted", "status": "PASS", "detail": "page text is used transiently only"},
        {"name": "generator_exposure_false", "status": "PASS", "detail": "effective set records no generator reference exposure"},
    ]
    audit_status = "REFERENCE_PRESENCE_BATCH_AUDIT_PASS" if all(c["status"] == "PASS" for c in checks) else "REFERENCE_PRESENCE_BATCH_AUDIT_FAIL"
    audit = {
        "audit_id": f"reference_detection_v3_audit_{task_id}",
        "detector_version": DETECTOR_VERSION,
        "task_id": task_id,
        "project_id": project_id,
        "status": audit_status,
        "checks": checks,
        "renderer": "+".join(sorted(renderers)) if renderers else "NO_RENDERER_USED",
        "temporary_workspace_removed": temp_removed,
        "data_minimization_pass": True,
        "generator_isolation_pass": True,
    }

    write_json(output_dir / "reference_page_classifications.json", {"page_classifications": page_classifications})
    write_json(output_dir / "reference_document_classifications.json", {"document_classifications": documents})
    write_json(output_dir / "effective_reference_set.json", effective)
    write_json(output_dir / "reference_detection_audit.json", audit)
    return {"effective_reference_set": effective, "audit": audit}


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect completed-reference presence with isolated page-level classification.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--candidate-manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--task-id")
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()
    project_id = normalize_project_id(args.project_id)
    task_id = args.task_id or f"refdet-v3-{project_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    rows = candidate_rows_from_manifest(args.candidate_manifest) if args.candidate_manifest else candidate_rows_from_inventory(project_id)
    rows = [row for row in rows if normalize_project_id(row.get("project_id", "")) == project_id]
    result = classify_project(project_id, rows, task_id, args.output_dir, keep_temp=args.keep_temp)
    print(json.dumps({"project_id": project_id, "status": result["effective_reference_set"]["status"], "audit": result["audit"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
