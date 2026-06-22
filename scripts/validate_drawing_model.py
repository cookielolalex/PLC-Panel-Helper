from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import validate_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("drawing_model", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("schemas/drawing_model.schema.json"))
    args = parser.parse_args()
    errors = validate_file(args.drawing_model, args.schema)
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("drawing_model schema: PASS")


if __name__ == "__main__":
    main()

