from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a conservative reference adjudication shell.")
    parser.add_argument("--reference-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = read_json(args.reference_manifest)
    items = []
    for sheet in manifest.get("sheets", []):
        items.append({
            "reference_item_id": f"{sheet['sheet_id']}-PENDING",
            "output_type": sheet.get("output_type"),
            "sheet_id": sheet.get("sheet_id"),
            "object_value_category": "pending_manual_adjudication",
            "source_availability": "UNRESOLVED",
            "criticality_weight": 0,
            "scored": False,
            "exclusion_reason": "Phase 0 shell; no completed reference adjudication."
        })
    write_json(args.output, {
        "adjudication_id": "reference-adjudication",
        "project_id": manifest["project_id"],
        "status": "PENDING_MANUAL_ADJUDICATION",
        "items": items
    })


if __name__ == "__main__":
    main()

