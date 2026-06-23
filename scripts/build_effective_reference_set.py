from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from detect_reference_presence_v3 import build_effective_set, write_json


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an effective reference set from frozen v3 page/document classifications.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--page-classifications", type=Path, required=True)
    parser.add_argument("--document-classifications", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    page_rows = read_json(args.page_classifications).get("page_classifications", [])
    doc_rows = read_json(args.document_classifications).get("document_classifications", [])
    write_json(args.output, build_effective_set(args.task_id, args.project_id, page_rows, doc_rows))


if __name__ == "__main__":
    main()
