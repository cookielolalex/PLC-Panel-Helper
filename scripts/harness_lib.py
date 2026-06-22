from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FORBIDDEN_TERMS = [
    "生管文件",
    "電機施工圖",
    "生管課用圖",
    "生管用圖",
    "鈑金施工圖",
    "沖孔施工圖",
    "修改",
    "reference_only_sentinel",
    "completed_target",
]

TARGET_OUTPUT_TYPES = {
    "production": "01_生管課用圖_{project_id}.pdf",
    "sheetmetal": "02_鈑金施工圖_{project_id}.pdf",
    "punch": "03_沖孔施工圖_{project_id}.pdf",
}


class HarnessError(Exception):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def sha256_json(data: Any) -> str:
    return sha256_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def classify_path(path_text: str) -> dict[str, Any]:
    name = Path(path_text).name
    normalized = path_text.replace("\\", "/")
    forbidden_hits = [term for term in FORBIDDEN_TERMS if term in normalized]
    ext = Path(name).suffix.lower()
    role = "unclear"
    output_type = None
    eligibility = "HUMAN_REVIEW_REQUIRED"
    confidence = 0.35

    if forbidden_hits:
        eligibility = "FORBIDDEN"
        confidence = 0.95
        if "生管文件" in forbidden_hits:
            role = "forbidden_production_control_file"
        elif "電機施工圖" in forbidden_hits:
            role = "forbidden_electrical_drawing"
        elif "鈑金施工圖" in forbidden_hits:
            role = "completed_sheetmetal_drawing_reference"
            output_type = "sheetmetal"
        elif "沖孔施工圖" in forbidden_hits:
            role = "completed_punch_drawing_reference"
            output_type = "punch"
        elif "生管課用圖" in forbidden_hits or "生管用圖" in forbidden_hits:
            role = "completed_production_drawing_reference"
            output_type = "production"
    elif ext in {".xlsx", ".xlsm", ".xls"}:
        if "合約" in normalized:
            role = "allowed_contract_workbook"
            eligibility = "HUMAN_REVIEW_REQUIRED"
            confidence = 0.7
        elif "材料清單" in normalized or "材料" in normalized:
            role = "allowed_material_list_workbook"
            eligibility = "HUMAN_REVIEW_REQUIRED"
            confidence = 0.65
        else:
            role = "spreadsheet_other"
    elif ext in {".dwg", ".dxf"}:
        role = "cad_block_library"
    elif ext in {".pdf", ".jpg", ".jpeg", ".png"}:
        role = "supporting_document_non_generator"
    return {
        "primary_role": role,
        "drawing_output_type": output_type,
        "generator_eligibility": eligibility,
        "forbidden_signature_match": bool(forbidden_hits),
        "forbidden_hits": forbidden_hits,
        "classification_confidence": confidence,
        "basis": "path_and_label_bootstrap_classifier",
    }


def detect_forbidden_text(text: str) -> list[str]:
    return [term for term in FORBIDDEN_TERMS if term in text]


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Small JSON-Schema subset validator used when jsonschema is unavailable."""
    errors: list[str] = []

    def check_type(value: Any, expected: Any, at: str) -> None:
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "null": type(None),
        }
        choices = expected if isinstance(expected, list) else [expected]
        if "integer" in choices and isinstance(value, bool):
            errors.append(f"{at}: expected integer, got boolean")
            return
        if "number" in choices and isinstance(value, bool):
            errors.append(f"{at}: expected number, got boolean")
            return
        if not any(isinstance(value, type_map[t]) for t in choices if t in type_map):
            errors.append(f"{at}: expected {expected}, got {type(value).__name__}")

    def walk(value: Any, node: dict[str, Any], at: str) -> None:
        if "type" in node:
            check_type(value, node["type"], at)
        if "enum" in node and value not in node["enum"]:
            errors.append(f"{at}: {value!r} not in enum {node['enum']!r}")
        if isinstance(value, dict):
            for key in node.get("required", []):
                if key not in value:
                    errors.append(f"{at}: missing required key {key!r}")
            props = node.get("properties", {})
            for key, sub in props.items():
                if key in value:
                    walk(value[key], sub, f"{at}.{key}")
        if isinstance(value, list):
            if "minItems" in node and len(value) < node["minItems"]:
                errors.append(f"{at}: expected at least {node['minItems']} items")
            item_schema = node.get("items")
            if isinstance(item_schema, dict):
                for i, item in enumerate(value):
                    walk(item, item_schema, f"{at}[{i}]")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in node and value < node["minimum"]:
                errors.append(f"{at}: below minimum {node['minimum']}")
            if "maximum" in node and value > node["maximum"]:
                errors.append(f"{at}: above maximum {node['maximum']}")

    try:
        import jsonschema  # type: ignore

        jsonschema.Draft202012Validator(schema).validate(instance)
        return []
    except ImportError:
        walk(instance, schema, path)
        return errors
    except Exception as exc:
        return [f"{path}: {exc}"]


def validate_file(instance_path: Path, schema_path: Path) -> list[str]:
    return validate(read_json(instance_path), read_json(schema_path))


def manifest_for_paths(paths: list[Path]) -> list[dict[str, str]]:
    rows = []
    for path in paths:
        if path.exists() and path.is_file():
            rows.append({"path": str(path), "sha256": sha256_file(path)})
    return rows


def copy_allowed_file(src: Path, dst_root: Path) -> dict[str, str]:
    dst = dst_root / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {"source": str(src), "bundle_path": str(dst), "sha256": sha256_file(dst)}


def fail(message: str) -> None:
    raise HarnessError(message)


def main_guard(fn):
    try:
        fn()
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
