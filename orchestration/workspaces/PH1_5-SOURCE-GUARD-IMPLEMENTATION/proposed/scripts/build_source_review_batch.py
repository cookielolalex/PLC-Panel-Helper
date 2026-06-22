from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from source_guard import build_review_items, read_csv, sha256_file, write_csv, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a metadata-only source review batch.")
    parser.add_argument("--manual-review-queue", type=Path, required=True)
    parser.add_argument("--file-role-index", type=Path, required=True)
    parser.add_argument("--workbook-sheet-index", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--batch-id", default="source-review-batch")
    parser.add_argument("--max-items", type=int)
    args = parser.parse_args()

    queue_rows = read_csv(args.manual_review_queue)
    file_rows = read_csv(args.file_role_index)
    sheet_rows = read_csv(args.workbook_sheet_index)
    items = build_review_items(queue_rows, file_rows, sheet_rows, args.max_items)
    batch = {
        "review_batch_id": args.batch_id,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "generator_visible": False,
        "source_indices": {
            "file_role_index": {
                "path": str(args.file_role_index),
                "sha256": sha256_file(args.file_role_index),
            },
            "workbook_sheet_index": {
                "path": str(args.workbook_sheet_index),
                "sha256": sha256_file(args.workbook_sheet_index),
            },
            "manual_review_queue": {
                "path": str(args.manual_review_queue),
                "sha256": sha256_file(args.manual_review_queue),
            },
        },
        "items": items,
    }
    write_json(args.output_json, batch)
    if args.output_csv:
        write_csv(args.output_csv, items, [
            "queue_id",
            "item_type",
            "item_id",
            "reason",
            "status",
            "source_root",
            "relative_path",
            "workbook_file_id",
            "sheet_name",
            "primary_role",
            "stale_template_status",
            "visibility",
            "current_generator_eligibility",
            "source_row_sha256",
            "reviewer_instruction",
        ])


if __name__ == "__main__":
    main()

