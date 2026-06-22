from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from harness_lib import detect_forbidden_text, sha256_file, write_json


SOURCE_ROOT_MARKERS = [
    r"C:\Users\alex1\OneDrive\Desktop\All Projects",
    "SRC-ALL-PROJECTS\\",
]


def is_symlink_or_escape(path: Path, bundle_root: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        path.resolve().relative_to(bundle_root.resolve())
        return False
    except Exception:
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify sanitized generator bundle isolation.")
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    required = [
        "bundle_manifest.json",
        "approval_manifest.json",
        "provenance_map.json",
        "visible_file_manifest.json",
        "verification_results.json",
        "bundle_hashes.json",
    ]
    for rel in required:
        if not (args.bundle_dir / rel).exists():
            errors.append(f"MISSING_{rel}")
    bundle_manifest = {}
    approval = {}
    if not errors:
        bundle_manifest = json.loads((args.bundle_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
        approval = json.loads((args.bundle_dir / "approval_manifest.json").read_text(encoding="utf-8"))
        if approval.get("status") != "PASS":
            errors.append("APPROVAL_MANIFEST_NOT_PASS")
        approved_ids = {
            row["decision_id"]
            for row in approval.get("decisions", [])
            if row.get("human_decision") == "HUMAN_APPROVED"
            or row.get("agent_decision") == "AGENT_QUORUM_APPROVED_EVAL"
        }
        for artifact in bundle_manifest.get("artifacts", []):
            if artifact.get("source_decision_id") not in approved_ids:
                errors.append(f"ARTIFACT_WITHOUT_APPROVAL:{artifact.get('path')}")
            path = args.bundle_dir / artifact["path"]
            if not path.exists():
                errors.append(f"MISSING_ARTIFACT:{artifact['path']}")
                continue
            if is_symlink_or_escape(path, args.bundle_dir):
                errors.append(f"SYMLINK_OR_ESCAPE:{artifact['path']}")
            if sha256_file(path).upper() != artifact["sha256"].upper():
                errors.append(f"ARTIFACT_HASH_MISMATCH:{artifact['path']}")

    for path in args.bundle_dir.rglob("*"):
        if is_symlink_or_escape(path, args.bundle_dir):
            errors.append(f"SYMLINK_OR_PATH_ESCAPE:{path}")
        if path.is_file():
            rel = path.relative_to(args.bundle_dir)
            rel_text = str(rel)
            if path.is_file() and path.suffix.lower() in {".xls", ".xlsx", ".xlsm", ".xlsb"}:
                errors.append(f"ORIGINAL_WORKBOOK_EXTENSION:{rel_text}")
            for hit in detect_forbidden_text(rel_text):
                errors.append(f"FORBIDDEN_NAME:{rel_text}:{hit}")
            if ".." in rel.parts:
                errors.append(f"PATH_TRAVERSAL:{rel_text}")
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for marker in SOURCE_ROOT_MARKERS:
                if marker in text:
                    errors.append(f"ABSOLUTE_SOURCE_PATH_LEAK:{rel_text}")
            for hit in detect_forbidden_text(text):
                errors.append(f"FORBIDDEN_CONTENT:{rel_text}:{hit}")

    result = {
        "status": "FAIL" if errors else "PASS",
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "artifact_count": len(bundle_manifest.get("artifacts", [])) if bundle_manifest else 0,
    }
    write_json(args.output, result)
    print(result["status"])
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
