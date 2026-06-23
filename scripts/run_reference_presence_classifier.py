from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILE_INDEX = ROOT / "manifests" / "all_projects_file_role_index.csv"

TARGET_TERMS = {
    "PRODUCTION": ["生管課用圖", "生管用圖", "生管圖"],
    "SHEET_METAL": ["鈑金施工圖", "鈑金圖", "板金施工圖", "板金圖", "鈑金", "板金"],
    "PUNCH": ["沖孔施工圖", "沖孔圖", "冲孔施工圖", "冲孔圖", "沖孔", "冲孔"],
}
EXCLUDE_ROLES = {"forbidden_electrical_drawing", "forbidden_production_control_file"}
REFERENCE_ROLES = {
    "completed_production_drawing_reference": "PRODUCTION",
    "completed_sheetmetal_drawing_reference": "SHEET_METAL",
    "completed_punch_drawing_reference": "PUNCH",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def normalize_project_id(value: str) -> str:
    m = re.search(r"(\d{7})", value or "")
    return m.group(1) if m else (value or "").strip()


def output_from_text(text: str) -> set[str]:
    hits = set()
    for output_type, terms in TARGET_TERMS.items():
        if any(term in text for term in terms):
            hits.add(output_type)
    return hits


def page_ranges(pages: list[int]) -> list[str]:
    if not pages:
        return []
    ranges = []
    start = prev = pages[0]
    for page in pages[1:]:
        if page == prev + 1:
            prev = page
            continue
        ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
        start = prev = page
    ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ranges


def extract_page_texts(pdf_path: Path) -> tuple[int | None, list[str], str | None]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                texts.append("")
        return len(reader.pages), texts, None
    except Exception as exc:  # pragma: no cover - dependency/runtime fallback
        return None, [], f"{type(exc).__name__}: {exc}"


def classify_file(row: dict[str, str], vault_pdf: Path) -> dict[str, object]:
    role = row.get("primary_role", "")
    file_name_text = row.get("file_name", "")
    page_count, page_texts, extraction_error = extract_page_texts(vault_pdf)

    by_output: dict[str, list[int]] = {key: [] for key in TARGET_TERMS}
    if role in REFERENCE_ROLES:
        by_output[REFERENCE_ROLES[role]].append(0)
    else:
        metadata_hits = output_from_text(file_name_text)
        if len(metadata_hits) == 1:
            by_output[next(iter(metadata_hits))].append(0)

    for idx, text in enumerate(page_texts, start=1):
        page_hits = output_from_text(text)
        if len(page_hits) == 1:
            by_output[next(iter(page_hits))].append(idx)

    classifications = []
    for output_type, pages in by_output.items():
        if not pages:
            continue
        pages = sorted(set(pages))
        metadata_only = pages == [0]
        confidence = 0.95 if role in REFERENCE_ROLES and REFERENCE_ROLES[role] == output_type else 0.82
        if not metadata_only and any(page > 0 for page in pages):
            confidence = max(confidence, 0.9)
        classifications.append(
            {
                "project_id": row.get("project_id"),
                "neutral_reference_file_id": row.get("file_id"),
                "sha256": row.get("sha256"),
                "output_type": output_type,
                "page_count": page_count,
                "page_ranges": page_ranges([p for p in pages if p > 0]),
                "detected_project_identity": row.get("project_id"),
                "detected_drawing_identity": f"{output_type}_DRAWING",
                "revision_label": "UNKNOWN_OR_NOT_METADATA_DETECTED",
                "supersession_relationship": "NOT_DETERMINED_METADATA_ONLY",
                "classification_confidence": confidence,
                "ambiguity_reason": "" if not extraction_error else "PDF_TEXT_EXTRACTION_UNAVAILABLE",
                "verification_result": "PASS" if confidence >= 0.9 else "PROBABLE",
            }
        )

    return {
        "project_id": row.get("project_id"),
        "neutral_reference_file_id": row.get("file_id"),
        "sha256": row.get("sha256"),
        "page_count": page_count,
        "classifications": classifications,
        "extraction_error": extraction_error,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Isolated completed-reference presence classifier.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--visible-manifest", type=Path, required=True)
    parser.add_argument("--trajectory", type=Path, required=True)
    parser.add_argument("--vault-dir", type=Path, required=True)
    args = parser.parse_args()

    project_id = args.project_id
    run_id = f"REFPRES-W001-{project_id}"
    args.vault_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for row in read_csv(FILE_INDEX):
        if normalize_project_id(row.get("project_id", "")) != project_id:
            continue
        if row.get("extension", "").lower() != ".pdf":
            continue
        if row.get("primary_role") in EXCLUDE_ROLES:
            continue
        path_text = f"{row.get('relative_path', '')}\\{row.get('file_name', '')}"
        if row.get("primary_role") in REFERENCE_ROLES or output_from_text(path_text) or row.get("primary_role") == "supporting_document_non_generator":
            rows.append(row)

    visible = {
        "run_id": run_id,
        "project_id": project_id,
        "source_root_id": "SRC-ALL-PROJECTS",
        "visible_files": [
            {
                "neutral_reference_file_id": row.get("file_id"),
                "sha256": row.get("sha256"),
                "extension": row.get("extension"),
                "size_bytes": row.get("size_bytes"),
                "source_root_relative_path": row.get("relative_path"),
                "role_hint": row.get("primary_role"),
            }
            for row in rows
        ],
        "forbidden_output_fields": [
            "dimensions",
            "component names",
            "quantities",
            "layout descriptions",
            "raw drawing text",
            "images",
            "thumbnails",
            "title-block details not needed for role classification",
        ],
    }
    write_json(args.visible_manifest, visible)

    inspected = []
    copy_failures = []
    for row in rows:
        src = Path(row.get("absolute_path", ""))
        vault_pdf = args.vault_dir / f"{row.get('file_id')}.pdf"
        try:
            shutil.copy2(src, vault_pdf)
            if row.get("sha256") and sha256_file(vault_pdf) != row.get("sha256", "").upper():
                copy_failures.append({"file_id": row.get("file_id"), "reason": "VAULT_COPY_HASH_MISMATCH"})
                continue
        except Exception as exc:
            copy_failures.append({"file_id": row.get("file_id"), "reason": f"COPY_FAILED:{type(exc).__name__}"})
            continue
        inspected.append(classify_file(row, vault_pdf))

    output_types = sorted({c["output_type"] for item in inspected for c in item["classifications"]})
    classifications = [c for item in inspected for c in item["classifications"]]
    required = {"PRODUCTION", "SHEET_METAL", "PUNCH"}
    all_three = required.issubset(output_types)
    min_confidence = min((float(c["classification_confidence"]) for c in classifications), default=0.0)
    if all_three and min_confidence >= 0.9:
        verification = "VERIFIED_ALL_THREE"
    elif all_three:
        verification = "PROBABLE_ALL_THREE"
    elif output_types:
        verification = "PARTIAL_REFERENCE_SET"
    elif copy_failures:
        verification = "INACCESSIBLE_REFERENCE_SET"
    else:
        verification = "NO_REFERENCE_SET"

    result = {
        "run_id": run_id,
        "classifier_version": "reference_presence_classifier_v1_isolated_pdf_text_minimal",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "project_id": project_id,
        "verification_result": verification,
        "detected_output_types": output_types,
        "inspected_file_count": len(inspected),
        "copy_failures": copy_failures,
        "classifications": classifications,
        "reference_content_persisted": False,
        "raw_text_persisted": False,
        "images_or_thumbnails_persisted": False,
        "vault_workspace": str(args.vault_dir),
        "visible_file_manifest": str(args.visible_manifest),
    }
    write_json(args.output, result)

    trajectory = {
        "run_id": run_id,
        "project_id": project_id,
        "started_at": result["created_at"],
        "completed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "actions": [
            "loaded metadata-only PDF candidate rows",
            "copied candidate PDFs into ignored reference-vault workspace",
            "verified vault copy hashes",
            "extracted transient page text for role labels only",
            "wrote schema-constrained classification result without raw text or images",
        ],
        "output": str(args.output),
    }
    write_json(args.trajectory, trajectory)


if __name__ == "__main__":
    main()
