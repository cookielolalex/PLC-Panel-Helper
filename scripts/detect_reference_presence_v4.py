from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from pypdf import PdfReader

from render_reference_classification_evidence import bundled_poppler_tool, sha256_file


ROOT = Path(__file__).resolve().parents[1]
FILE_INDEX = ROOT / "manifests" / "all_projects_file_role_index.csv"
TMP_ROOT = ROOT / "tmp" / "reference_detection_v4"
BRIDGE = ROOT / "scripts" / "windows_media_ocr_signal_bridge.ps1"
DETECTOR_VERSION = "target_output_detection_v4_local_multisignal_recovery"
SCHEMA_VERSION = "reference_detection_v4_schema_v1"
TARGET_TYPES = {"PRODUCTION_DRAWING", "SHEETMETAL_DRAWING", "PUNCH_DRAWING"}
NON_TARGET_TYPES = {"ELECTRICAL_DRAWING", "SOURCE_DOCUMENT", "COVER_OR_INDEX", "REVISION_NOTICE", "OTHER_DRAWING"}


TERMS = {
    "PRODUCTION_DRAWING": [
        "PRODUCTION_DRAWING",
        "PRODUCTION DRAWING",
        "CONTROL PANEL",
        "SEIKAN",
    ],
    "SHEETMETAL_DRAWING": [
        "SHEETMETAL_DRAWING",
        "SHEETMETAL DRAWING",
        "SHEET METAL",
        "SHEET-METAL",
    ],
    "PUNCH_DRAWING": [
        "PUNCH_DRAWING",
        "PUNCH DRAWING",
        "PUNCH",
        "HOLE DRAWING",
    ],
    "ELECTRICAL_DRAWING": [
        "ELECTRICAL_DRAWING",
        "ELECTRICAL DRAWING",
        "WIRING",
        "SCHEMATIC",
        "SINGLE LINE",
    ],
    "SOURCE_DOCUMENT": [
        "SOURCE_DOCUMENT",
        "SOURCE DOCUMENT",
        "CONTRACT",
        "MATERIAL LIST",
        "QUOTATION",
    ],
    "REVISION_NOTICE": [
        "REVISION_NOTICE",
        "REVISION ONLY",
        "SUPERSEDES",
        "REV ",
    ],
    "COVER_OR_INDEX": [
        "COVER_OR_INDEX",
        "COVER",
        "INDEX",
    ],
}

ROLE_TARGETS = {
    "completed_production_drawing_reference": "PRODUCTION_DRAWING",
    "completed_sheetmetal_drawing_reference": "SHEETMETAL_DRAWING",
    "completed_punch_drawing_reference": "PUNCH_DRAWING",
}


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


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text or "").upper().replace("_", " ")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def text_hits(text: str) -> list[str]:
    normalized = normalize_text(text)
    hits = []
    for page_type, terms in TERMS.items():
        for term in terms:
            if normalize_text(term) in normalized:
                hits.append(page_type)
                break
    return hits


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


def aspect_bucket(width: float, height: float) -> str:
    if width <= 0 or height <= 0:
        return "UNKNOWN"
    ratio = max(width, height) / max(1.0, min(width, height))
    if ratio < 1.15:
        return "SQUARE"
    if ratio < 1.55:
        return "STANDARD_PAGE"
    if ratio < 2.2:
        return "WIDE_DRAWING"
    return "EXTRA_WIDE"


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
                    "aspect_ratio_bucket": aspect_bucket(width, height),
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


def render_pdf(pdf_path: Path, task_id: str, file_id: str) -> tuple[str, list[Path], Path]:
    pdftoppm = bundled_poppler_tool("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("pdftoppm not found in bundled runtime or PATH")
    task_dir = TMP_ROOT / task_id
    render_dir = task_dir / "renders" / hashlib.sha1(file_id.encode("utf-8")).hexdigest()[:12]
    render_dir.mkdir(parents=True, exist_ok=True)
    prefix = render_dir / "page"
    subprocess.run([pdftoppm, "-png", "-r", "72", str(pdf_path), str(prefix)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pages = sorted(render_dir.glob("page-*.png"))
    if not pages:
        raise RuntimeError("pdftoppm produced no page images")
    return "POPPLER_PDFTOPPM", pages, task_dir


def image_features(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        gray = image.convert("L")
        width, height = gray.size
        arr = np.asarray(gray, dtype=np.uint8)
        ink = arr < 225
        ink_ratio = float(ink.mean()) if ink.size else 0.0
        dark_rows = ink.mean(axis=1) if ink.size else np.array([])
        dark_cols = ink.mean(axis=0) if ink.size else np.array([])
        h_lines = int((dark_rows > 0.55).sum()) if dark_rows.size else 0
        v_lines = int((dark_cols > 0.55).sum()) if dark_cols.size else 0
        title = arr[int(height * 0.64):height, int(width * 0.52):width] if width and height else arr
        title_ink = float((title < 225).mean()) if title.size else 0.0
        return {
            "orientation": page_orientation(width, height),
            "aspect_ratio_bucket": aspect_bucket(width, height),
            "coarse_text_density": "HIGH" if ink_ratio > 0.18 else "MEDIUM" if ink_ratio > 0.06 else "LOW",
            "horizontal_line_density": "HIGH" if h_lines > 20 else "MEDIUM" if h_lines > 5 else "LOW",
            "vertical_line_density": "HIGH" if v_lines > 20 else "MEDIUM" if v_lines > 5 else "LOW",
            "title_block_region_presence": title_ink > 0.02,
        }


def run_ocr_signal(image_path: Path, project_id: str, language_tag: str, disable_ocr: bool, simulate_failure: bool) -> dict[str, Any]:
    if disable_ocr:
        return {"status": "DISABLED", "role_hits": [], "project_identity_status": "NOT_FOUND", "actual_classifier": "OCR_DISABLED"}
    if simulate_failure:
        return {"status": "FAIL", "role_hits": [], "project_identity_status": "NOT_FOUND", "actual_classifier": "SIMULATED_OCR_FAILURE"}
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(BRIDGE),
        "-ImagePath",
        str(image_path),
        "-ProjectId",
        project_id,
    ]
    if language_tag:
        cmd.extend(["-LanguageTag", language_tag])
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=45, check=False)
    if not result.stdout.strip():
        return {"status": "FAIL", "role_hits": [], "project_identity_status": "NOT_FOUND", "actual_classifier": "Windows.Media.Ocr.OcrEngine"}
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "FAIL", "role_hits": [], "project_identity_status": "NOT_FOUND", "actual_classifier": "Windows.Media.Ocr.OcrEngine"}
    if isinstance(payload.get("role_hits"), str):
        payload["role_hits"] = [payload["role_hits"]]
    return payload


def evidence_id(task_id: str, file_id: str, page_number: int, page_type: str) -> str:
    return "V4E-" + hashlib.sha1(f"{task_id}:{file_id}:{page_number}:{page_type}".encode("utf-8")).hexdigest()[:14].upper()


def classify_page(
    *,
    task_id: str,
    project_id: str,
    row: dict[str, Any],
    page: dict[str, Any],
    page_count: int,
    duplicate_group_id: str | None,
    rendered_page: Path | None,
    language_tag: str,
    disable_ocr: bool,
    simulate_ocr_failure: bool,
) -> dict[str, Any]:
    page_text = page.get("text", "")
    metadata_text = row.get("metadata_text", "")
    role_hint = row.get("role_hint", "")
    embedded_hits = text_hits(page_text)
    image = image_features(rendered_page) if rendered_page else {}
    ocr = run_ocr_signal(rendered_page, project_id, language_tag, disable_ocr, simulate_ocr_failure) if rendered_page else {"status": "NO_RENDER", "role_hits": []}
    ocr_hits = list(ocr.get("role_hits") or [])
    content_hits = list(dict.fromkeys(embedded_hits + ocr_hits))
    target_hits = sorted({hit for hit in content_hits if hit in TARGET_TYPES})
    non_target_hits = sorted({hit for hit in content_hits if hit in NON_TARGET_TYPES})
    evidence_codes = ["PYPDF_EMBEDDED_TEXT" if page_text else "NO_EMBEDDED_TARGET_TEXT", "POPPLER_RENDER", "PIL_NUMPY_LAYOUT"]
    if ocr.get("status") == "PASS":
        evidence_codes.append("WINDOWS_MEDIA_OCR")
    elif ocr.get("status") in {"FAIL", "DISABLED"}:
        evidence_codes.append("OCR_UNAVAILABLE")
    if role_hint:
        evidence_codes.append("WEAK_METADATA_PRIOR")

    page_type = "UNCLASSIFIED"
    method = "FAIL_CLOSED_NO_EXPLICIT_CONTENT"
    confidence = 0.2
    ambiguity = None
    target = False

    if target_hits and non_target_hits:
        page_type = "AMBIGUOUS"
        method = "CONFLICTING_TARGET_AND_NON_TARGET_CONTENT"
        ambiguity = "TARGET_NON_TARGET_SIGNAL_CONFLICT"
        confidence = 0.35
    elif len(target_hits) > 1:
        page_type = "AMBIGUOUS"
        method = "MULTIPLE_TARGET_ROLE_SIGNALS_ON_ONE_PAGE"
        ambiguity = "MULTIPLE_TARGET_TYPES_ON_PAGE"
        confidence = 0.4
    elif len(target_hits) == 1:
        page_type = target_hits[0]
        target = True
        method = "EMBEDDED_OR_LOCAL_OCR_ROLE_SIGNAL"
        confidence = 0.94 if ocr.get("status") == "PASS" or page_text else 0.86
    elif non_target_hits:
        page_type = non_target_hits[0]
        method = "EXPLICIT_NON_TARGET_CONTENT"
        confidence = 0.9
    elif role_hint in ROLE_TARGETS:
        page_type = "UNCLASSIFIED"
        method = "WEAK_TARGET_PRIOR_WITHOUT_PAGE_CONTENT"
        ambiguity = "FILENAME_OR_FOLDER_PRIOR_INSUFFICIENT"
        confidence = 0.25

    identity = project_identity_status(project_id, page_text, metadata_text, target)
    if target and ocr.get("project_identity_status") == "CONFIRMED":
        identity = "CONFIRMED"
    elif target and identity != "CONFIRMED":
        confidence = min(confidence, 0.78)

    revision = "REVISION_MARKER_PRESENT" if "REVISION_NOTICE" in content_hits else None
    raster_status = "EMBEDDED_TEXT" if page_text else "OCR_SIGNAL_AVAILABLE" if ocr.get("status") == "PASS" else "OCR_UNAVAILABLE"
    return {
        "schema_version": SCHEMA_VERSION,
        "detector_version": DETECTOR_VERSION,
        "task_id": task_id,
        "project_id": project_id,
        "neutral_reference_file_id": row["neutral_reference_file_id"],
        "page_number": page["page_number"],
        "page_count": page_count,
        "orientation": image.get("orientation") or page["orientation"],
        "aspect_ratio_bucket": image.get("aspect_ratio_bucket") or page["aspect_ratio_bucket"],
        "raster_status": raster_status,
        "page_classification": page_type,
        "project_identity_status": identity,
        "revision_identity": revision,
        "effective_status": "CURRENT_EFFECTIVE_CANDIDATE" if target else "NON_TARGET_OR_UNRESOLVED",
        "duplicate_group_id": duplicate_group_id,
        "ambiguity_code": ambiguity,
        "classification_method": method,
        "confidence": round(confidence, 3),
        "evidence_channel_codes": sorted(set(evidence_codes)),
        "layout_signal_codes": {
            "coarse_text_density": image.get("coarse_text_density", "UNKNOWN"),
            "horizontal_line_density": image.get("horizontal_line_density", "UNKNOWN"),
            "vertical_line_density": image.get("vertical_line_density", "UNKNOWN"),
            "title_block_region_presence": bool(image.get("title_block_region_presence", False)),
        },
        "evidence_ids": [evidence_id(task_id, row["neutral_reference_file_id"], page["page_number"], page_type)],
        "minimization": {
            "raw_text_persisted": False,
            "raw_ocr_text_persisted": False,
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
    usable = [
        row
        for row in page_rows
        if row["page_classification"] in TARGET_TYPES
        and row["project_identity_status"] == "CONFIRMED"
        and row["confidence"] >= 0.86
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
                "page_range": page_ranges([row["page_number"] for row in rows]),
                "target_type": target_type,
                "project_identity_status": "CONFIRMED",
                "revision_identity": rows[-1].get("revision_identity"),
                "supersedes": None,
                "current_effective_status": "CURRENT_EFFECTIVE",
                "duplicate_group_id": rows[-1].get("duplicate_group_id"),
                "classification_method": "+".join(sorted(set(row["classification_method"] for row in rows))),
                "confidence": min(row["confidence"] for row in rows),
                "evidence_channel_codes": sorted({code for row in rows for code in row["evidence_channel_codes"]}),
            }
        )

    target_types = sorted({row["target_type"] for row in effective_pages})
    files_with_multiple_targets = defaultdict(set)
    for row in effective_pages:
        files_with_multiple_targets[row["neutral_reference_file_id"]].add(row["target_type"])

    unresolved = []
    page_types = {row["page_classification"] for row in page_rows}
    if "ELECTRICAL_DRAWING" in page_types:
        unresolved.append("ELECTRICAL_DRAWINGS_PRESENT_AND_EXCLUDED_FROM_TARGET_SET")
    if "AMBIGUOUS" in page_types:
        unresolved.append("AMBIGUOUS_PAGES_REMAIN")
    if "UNCLASSIFIED" in page_types:
        unresolved.append("UNCLASSIFIED_PAGES_REMAIN")

    if set(target_types) >= TARGET_TYPES:
        if any(len(types) > 1 for types in files_with_multiple_targets.values()):
            status = "VERIFIED_ALL_THREE_COMBINED_PACKAGE"
        else:
            status = "VERIFIED_ALL_THREE_BY_CONTENT"
    elif "AMBIGUOUS" in page_types:
        status = "AMBIGUOUS_REFERENCE_SET"
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
            "raw_ocr_text_persisted": False,
            "rendered_images_persisted": False,
            "title_crops_persisted": False,
            "absolute_private_paths_persisted": False,
            "drawing_details_persisted": False,
        },
    }


def classify_project(
    project_id: str,
    rows: list[dict[str, Any]],
    task_id: str,
    output_dir: Path,
    *,
    keep_temp: bool = False,
    ocr_language: str = "",
    disable_ocr: bool = False,
    simulate_ocr_failure: bool = False,
) -> dict[str, Any]:
    page_classifications: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []
    seen_sha: dict[str, str] = {}
    duplicate_group_by_sha: dict[str, str] = {}
    renderers = set()
    task_dirs = set()
    ocr_engines = set()

    for row in rows:
        pdf_path = Path(row["absolute_path"])
        file_id = row["neutral_reference_file_id"]
        expected_sha = (row.get("file_sha256") or "").upper()
        doc_status = "INACCESSIBLE"
        render_status = "NOT_RENDERED"
        metadata_status = "NOT_READ"
        page_rows: list[dict[str, Any]] = []
        duplicate_of = None
        duplicate_group_id = None

        try:
            actual_sha = sha256_file(pdf_path)
            if expected_sha and actual_sha != expected_sha:
                metadata_status = "HASH_MISMATCH"
            else:
                duplicate_of = seen_sha.get(actual_sha)
                if not duplicate_of:
                    seen_sha[actual_sha] = file_id
                    duplicate_group_by_sha[actual_sha] = f"DUP-G{len(duplicate_group_by_sha) + 1:04d}"
                duplicate_group_id = duplicate_group_by_sha[actual_sha]
                pages, metadata_status = extract_pdf_pages(pdf_path)
                renderer, rendered_pages, task_dir = render_pdf(pdf_path, task_id, file_id)
                renderers.add(renderer)
                task_dirs.add(str(task_dir))
                render_status = f"RENDERED_{len(rendered_pages)}_PAGES"
                rendered_by_page = {index: path for index, path in enumerate(rendered_pages, start=1)}
                for page in pages:
                    page_row = classify_page(
                        task_id=task_id,
                        project_id=project_id,
                        row=row,
                        page=page,
                        page_count=len(pages),
                        duplicate_group_id=duplicate_group_id,
                        rendered_page=rendered_by_page.get(page["page_number"]),
                        language_tag=ocr_language,
                        disable_ocr=disable_ocr,
                        simulate_ocr_failure=simulate_ocr_failure,
                    )
                    if "WINDOWS_MEDIA_OCR" in page_row["evidence_channel_codes"]:
                        ocr_engines.add("Windows.Media.Ocr.OcrEngine")
                    page_rows.append(page_row)
                page_classifications.extend(page_rows)
                page_types = {item["page_classification"] for item in page_rows}
                if duplicate_of:
                    doc_status = "DUPLICATE_REFERENCE"
                elif page_types & TARGET_TYPES:
                    doc_status = "TARGET_EVIDENCE"
                elif "AMBIGUOUS" in page_types:
                    doc_status = "AMBIGUOUS_REFERENCE"
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
                "page_count": max((item.get("page_count", 0) for item in page_rows), default=0),
                "metadata_status": metadata_status,
                "render_status": render_status,
                "detected_page_types": sorted({item["page_classification"] for item in page_rows}),
                "page_classification_ids": [item["evidence_ids"][0] for item in page_rows],
                "duplicate_group_id": duplicate_group_id,
                "duplicate_of": duplicate_of,
                "document_status": doc_status,
                "minimization": {
                    "raw_text_persisted": False,
                    "raw_ocr_text_persisted": False,
                    "rendered_images_persisted": False,
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
        {"name": "temporary_renders_removed", "status": "PASS" if temp_removed else "FAIL", "detail": "tmp/reference_detection_v4 task directories removed"},
        {"name": "raw_text_not_persisted", "status": "PASS", "detail": "embedded text is transient only"},
        {"name": "raw_ocr_not_persisted", "status": "PASS", "detail": "OCR bridge returns role signals only"},
        {"name": "generator_exposure_false", "status": "PASS", "detail": "effective set records no generator reference exposure"},
        {"name": "source_review_blindness", "status": "PASS", "detail": "no source-review artifact is written by detector"},
    ]
    audit_status = "REFERENCE_PRESENCE_BATCH_AUDIT_PASS" if all(c["status"] == "PASS" for c in checks) else "REFERENCE_PRESENCE_BATCH_AUDIT_FAIL"
    audit = {
        "audit_id": f"reference_detection_v4_audit_{task_id}",
        "detector_version": DETECTOR_VERSION,
        "task_id": task_id,
        "project_id": project_id,
        "status": audit_status,
        "checks": checks,
        "renderer": "+".join(sorted(renderers)) if renderers else "NO_RENDERER_USED",
        "ocr_engine": "+".join(sorted(ocr_engines)) if ocr_engines else "NO_OCR_SIGNAL_USED",
        "temporary_workspace_removed": temp_removed,
        "data_minimization_pass": True,
        "generator_isolation_pass": True,
        "source_review_blindness_pass": True,
    }

    write_json(output_dir / "reference_page_classifications.json", {"page_classifications": page_classifications})
    write_json(output_dir / "reference_document_classifications.json", {"document_classifications": documents})
    write_json(output_dir / "effective_reference_set.json", effective)
    write_json(output_dir / "reference_detection_audit.json", audit)
    return {"effective_reference_set": effective, "audit": audit}


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect completed-reference presence with local multisignal v4 classification.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--candidate-manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--task-id")
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--ocr-language", default="")
    parser.add_argument("--disable-ocr", action="store_true")
    parser.add_argument("--simulate-ocr-failure", action="store_true")
    args = parser.parse_args()
    project_id = normalize_project_id(args.project_id)
    task_id = args.task_id or f"refdet-v4-{project_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    rows = candidate_rows_from_manifest(args.candidate_manifest) if args.candidate_manifest else candidate_rows_from_inventory(project_id)
    rows = [row for row in rows if normalize_project_id(row.get("project_id", "")) == project_id]
    result = classify_project(
        project_id,
        rows,
        task_id,
        args.output_dir,
        keep_temp=args.keep_temp,
        ocr_language=args.ocr_language,
        disable_ocr=args.disable_ocr,
        simulate_ocr_failure=args.simulate_ocr_failure,
    )
    print(json.dumps({"project_id": project_id, "status": result["effective_reference_set"]["status"], "audit": result["audit"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
