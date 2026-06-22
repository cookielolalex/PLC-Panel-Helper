from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import classify_path, sha256_file, write_json, read_json


def inventory_path(path: Path, source_root_id: str, max_files: int, hash_files: bool) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    candidates = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
    for index, file_path in enumerate(candidates[:max_files], start=1):
        info = classify_path(str(file_path))
        rows.append({
            "file_id": f"{source_root_id}-FILE-{index:06d}",
            "source_root": source_root_id,
            "relative_path": file_path.name if path.is_file() else str(file_path.relative_to(path)),
            "archive_member_path": None,
            "project_id": None,
            "project_name": None,
            "customer": None,
            "file_name": file_path.name,
            "extension": file_path.suffix.lower(),
            "size_bytes": file_path.stat().st_size,
            "modified_time": None,
            "sha256": sha256_file(file_path) if hash_files else "NOT_HASHED_PHASE0",
            "content_fingerprint": None,
            "duplicate_of": None,
            "primary_role": info["primary_role"],
            "secondary_tags": info["forbidden_hits"],
            "drawing_output_type": info["drawing_output_type"],
            "generator_eligibility": info["generator_eligibility"],
            "forbidden_signature_match": info["forbidden_signature_match"],
            "classification_confidence": info["classification_confidence"],
            "basis": info["basis"],
            "parse_status": "NOT_PARSED",
            "review_status": "BOOTSTRAP",
            "notes": "Phase 0 inventory; no workbook parsing."
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a read-only source manifest.")
    parser.add_argument("--source-roots", type=Path, default=Path("manifests/source_roots_probe.json"))
    parser.add_argument("--output", type=Path, default=Path("manifests/source_manifest_initial.json"))
    parser.add_argument("--max-files", type=int, default=500)
    parser.add_argument("--hash-files", action="store_true")
    args = parser.parse_args()

    roots = read_json(args.source_roots)["declared_roots"]
    files = []
    blockers = []
    for root in roots:
        p = Path(root["path"])
        if not p.exists():
            blockers.append(f"{root['id']} missing: {root['path']}")
            continue
        files.extend(inventory_path(p, root["id"], args.max_files, args.hash_files))
    write_json(args.output, {
        "manifest_id": "source-manifest-generated",
        "created_at": "LOCAL",
        "status": "SOURCE_ROOTS_MISSING" if blockers else "INVENTORY_PARTIAL",
        "files": files,
        "worksheets": [],
        "blockers": blockers
    })


if __name__ == "__main__":
    main()

