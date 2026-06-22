from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import validate_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("job_spec", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("schemas/job_spec.schema.json"))
    args = parser.parse_args()
    errors = validate_file(args.job_spec, args.schema)
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("job_spec schema: PASS")


if __name__ == "__main__":
    main()

