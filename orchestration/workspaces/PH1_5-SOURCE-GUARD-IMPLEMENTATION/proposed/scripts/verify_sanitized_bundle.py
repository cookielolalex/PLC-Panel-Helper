from __future__ import annotations

import argparse
from pathlib import Path

from source_guard import read_json, verify_bundle_manifest, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a sanitized generator bundle manifest and copied files.")
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = read_json(args.manifest)
    errors = verify_bundle_manifest(manifest, args.bundle_dir)
    result = {
        "manifest_id": manifest.get("manifest_id", ""),
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
    }
    write_json(args.output, result)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

