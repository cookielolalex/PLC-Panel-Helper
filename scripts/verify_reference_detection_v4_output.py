from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from harness_lib import read_json, repo_root, validate


ROOT = repo_root()
LEAK_PATTERNS = [
    "C:\\Users\\alex1",
    "OneDrive\\Desktop\\All Projects",
    "absolute_path",
    "source_root_relative_path",
    "\"raw_text\"",
    "\"ocr_text\"",
    "\"raw_ocr_text\":",
    "\"page_image\"",
    "\"title_crop\"",
    "PUNCH DRAWING",
    "PRODUCTION DRAWING",
    "SHEET METAL DRAWING",
]


def text_contains_leak(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [pattern for pattern in LEAK_PATTERNS if pattern in text]


def validate_items(items: list[dict[str, Any]], schema_path: Path, label: str) -> list[str]:
    schema = read_json(schema_path)
    errors: list[str] = []
    for index, item in enumerate(items):
        errors.extend(f"{label}[{index}]: {err}" for err in validate(item, schema))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify minimized reference detection v4 outputs.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--temp-task-dir", type=Path)
    args = parser.parse_args()
    out = args.output_dir
    errors: list[str] = []

    page_path = out / "reference_page_classifications.json"
    doc_path = out / "reference_document_classifications.json"
    effective_path = out / "effective_reference_set.json"
    audit_path = out / "reference_detection_audit.json"
    required = [page_path, doc_path, effective_path, audit_path]
    for path in required:
        if not path.exists():
            errors.append(f"missing required output: {path}")

    if not errors:
        pages = read_json(page_path).get("page_classifications", [])
        docs = read_json(doc_path).get("document_classifications", [])
        errors.extend(validate_items(pages, ROOT / "schemas" / "reference_page_classification_v4.schema.json", "page"))
        errors.extend(validate_items(docs, ROOT / "schemas" / "reference_document_classification_v4.schema.json", "document"))
        errors.extend(validate(read_json(effective_path), read_json(ROOT / "schemas" / "effective_reference_set_v4.schema.json")))
        errors.extend(validate(read_json(audit_path), read_json(ROOT / "schemas" / "reference_detection_audit_v4.schema.json")))

    for path in required:
        if path.exists():
            leaks = text_contains_leak(path)
            if leaks:
                errors.append(f"{path}: leaked forbidden patterns {leaks}")

    if args.temp_task_dir and args.temp_task_dir.exists():
        errors.append(f"temporary task directory still exists: {args.temp_task_dir}")

    for media in out.rglob("*"):
        if media.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
            errors.append(f"rendered media persisted in output directory: {media}")

    status = "PASS" if not errors else "FAIL"
    print(json.dumps({"status": status, "errors": errors}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
