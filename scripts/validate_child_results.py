from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import sha256_file, validate_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate child result files against schemas/child_result.schema.json.")
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("schemas/child_result.schema.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    failed = False
    for result in args.results:
        errors = validate_file(result, args.schema)
        rows.append({
            "path": str(result),
            "sha256": sha256_file(result),
            "schema_valid": not errors,
            "errors": errors
        })
        failed = failed or bool(errors)
    data = {"status": "FAIL" if failed else "PASS", "results": rows}
    if args.output:
        write_json(args.output, data)
    else:
        print(data)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

