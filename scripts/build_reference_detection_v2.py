from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILE_INDEX = ROOT / "manifests" / "all_projects_file_role_index.csv"
PROJECT_MANIFEST = ROOT / "manifests" / "all_projects_project_manifest.csv"
OUT_MANIFEST_DIR = ROOT / "manifests" / "reference_detection"
OUT_REPORT_DIR = ROOT / "reports" / "baseline-024" / "expanded-screening"

REFERENCE_ROLES = {
    "completed_production_drawing_reference": "PRODUCTION",
    "completed_sheetmetal_drawing_reference": "SHEET_METAL",
    "completed_punch_drawing_reference": "PUNCH",
}

ALIASES = {
    "PRODUCTION": {
        "verified_aliases": ["生管課用圖", "生管用圖", "生管圖"],
        "probable_aliases": ["生產圖", "生產用圖"],
        "exclude_if_present": ["生管文件", "電機施工圖", "估價", "報價", "合約", "工作記錄", "材料", "訂單"],
    },
    "SHEET_METAL": {
        "verified_aliases": ["鈑金施工圖", "鈑金圖", "板金施工圖", "板金圖"],
        "probable_aliases": ["鈑金", "板金"],
        "exclude_if_present": ["電機施工圖", "估價", "報價", "合約", "工作記錄", "材料", "訂單"],
    },
    "PUNCH": {
        "verified_aliases": ["沖孔施工圖", "沖孔圖", "冲孔施工圖", "冲孔圖"],
        "probable_aliases": ["沖孔", "冲孔"],
        "exclude_if_present": ["電機施工圖", "估價", "報價", "合約", "工作記錄", "材料", "訂單"],
    },
}

REVISION_PATTERNS = [
    r"(?i)\bREV\b",
    r"(?i)\bR\d+\b",
    r"\d{4}[-_/]\d{1,2}[-_/]\d{1,2}",
    "修正",
    "變更",
    "更新",
    "新版",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_project_id(value: str) -> str:
    m = re.search(r"(\d{7})", value or "")
    return m.group(1) if m else (value or "").strip()


def has_any(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term and term in text]


def detect_revision(text: str) -> list[str]:
    hits = []
    for pattern in REVISION_PATTERNS:
        if pattern.startswith("(?i)") or "\\" in pattern:
            if re.search(pattern, text):
                hits.append(pattern)
        elif pattern in text:
            hits.append(pattern)
    return hits


def classify_pdf(row: dict[str, str]) -> list[dict[str, object]]:
    if row.get("extension", "").lower() != ".pdf":
        return []

    text = f"{row.get('relative_path', '')}\\{row.get('file_name', '')}"
    role = row.get("primary_role", "")
    classifications: list[dict[str, object]] = []

    if role in REFERENCE_ROLES:
        return [
            {
                "output_type": REFERENCE_ROLES[role],
                "detection_basis": "existing_inventory_role",
                "confidence": 0.95,
                "alias_hits": [role],
                "excluded_alias_hits": [],
            }
        ]

    for output_type, rules in ALIASES.items():
        excluded = has_any(text, rules["exclude_if_present"])
        verified_hits = has_any(text, rules["verified_aliases"])
        probable_hits = has_any(text, rules["probable_aliases"])
        if verified_hits and not excluded:
            classifications.append(
                {
                    "output_type": output_type,
                    "detection_basis": "verified_alias",
                    "confidence": 0.9,
                    "alias_hits": verified_hits,
                    "excluded_alias_hits": [],
                }
            )
        elif probable_hits and not excluded:
            classifications.append(
                {
                    "output_type": output_type,
                    "detection_basis": "probable_alias",
                    "confidence": 0.72,
                    "alias_hits": probable_hits,
                    "excluded_alias_hits": [],
                }
            )
        elif verified_hits or probable_hits:
            classifications.append(
                {
                    "output_type": output_type,
                    "detection_basis": "alias_excluded_by_policy",
                    "confidence": 0.0,
                    "alias_hits": verified_hits + probable_hits,
                    "excluded_alias_hits": excluded,
                }
            )

    positive_output_types = {item["output_type"] for item in classifications if item["confidence"] > 0}
    if len(positive_output_types) > 1:
        return []

    deduped: dict[str, dict[str, object]] = {}
    for item in classifications:
        output_type = item["output_type"]
        if output_type not in deduped or item["confidence"] > deduped[output_type]["confidence"]:
            deduped[output_type] = item
    return [item for item in deduped.values() if item["confidence"] > 0]


def availability_for(types: set[str], has_probable: bool, ambiguous: bool, inaccessible: bool = False) -> str:
    if inaccessible:
        return "INACCESSIBLE_REFERENCE_SET"
    if ambiguous:
        return "AMBIGUOUS_REFERENCE_SET"
    required = {"PRODUCTION", "SHEET_METAL", "PUNCH"}
    if required.issubset(types):
        return "PROBABLE_ALL_THREE" if has_probable else "VERIFIED_ALL_THREE"
    if types:
        return "PARTIAL_REFERENCE_SET"
    return "NO_REFERENCE_SET"


def build() -> None:
    OUT_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    files = read_csv(FILE_INDEX)
    projects = {
        normalize_project_id(row.get("project_id", "")): row
        for row in read_csv(PROJECT_MANIFEST)
        if re.fullmatch(r"\d{7}", normalize_project_id(row.get("project_id", "")))
    }

    candidates: list[dict[str, object]] = []
    by_project: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in files:
        project_id = normalize_project_id(row.get("project_id", ""))
        if not re.fullmatch(r"\d{7}", project_id):
            continue
        classifications = classify_pdf(row)
        if not classifications:
            continue
        for classification in classifications:
            candidate = {
                "project_id": project_id,
                "neutral_reference_file_id": row.get("file_id"),
                "sha256": row.get("sha256"),
                "extension": row.get("extension"),
                "size_bytes": int(float(row.get("size_bytes") or 0)),
                "relative_path": row.get("relative_path"),
                "existing_inventory_role": row.get("primary_role"),
                "existing_inventory_output_type": row.get("drawing_output_type"),
                "detected_output_type": classification["output_type"],
                "detection_basis": classification["detection_basis"],
                "alias_hits": classification["alias_hits"],
                "classification_confidence": classification["confidence"],
                "revision_indicators": detect_revision(row.get("relative_path", "")),
                "page_count": None,
                "pdf_metadata_status": "NOT_OPENED_METADATA_ONLY_PASS",
            }
            candidates.append(candidate)
            by_project[project_id].append(candidate)

    effective_sets = []
    false_negative_rows = []
    for project_id, project in sorted(projects.items()):
        items = by_project.get(project_id, [])
        types = {str(item["detected_output_type"]) for item in items}
        has_probable = any(item.get("detection_basis") == "probable_alias" for item in items)
        duplicate_types = [t for t, c in Counter(item["detected_output_type"] for item in items).items() if c > 1]
        ambiguous = False
        status = availability_for(types, has_probable, ambiguous)
        v1_all_three = str(project.get("has_all_three_completed_targets", "")).lower() == "true"
        selected = {}
        for output_type in ["PRODUCTION", "SHEET_METAL", "PUNCH"]:
            typed = [item for item in items if item["detected_output_type"] == output_type]
            typed.sort(key=lambda item: (item["classification_confidence"], -int(item["size_bytes"])), reverse=True)
            if typed:
                selected[output_type] = {
                    "neutral_reference_file_id": typed[0]["neutral_reference_file_id"],
                    "sha256": typed[0]["sha256"],
                    "detection_basis": typed[0]["detection_basis"],
                    "classification_confidence": typed[0]["classification_confidence"],
                }
        effective = {
            "project_id": project_id,
            "inventory_v1_has_all_three_completed_targets": v1_all_three,
            "reference_availability": status,
            "detected_output_types": sorted(types),
            "candidate_count": len(items),
            "duplicate_output_type_candidates": duplicate_types,
            "effective_reference_files": selected,
            "source_for_generators": {
                "completed_reference_set_exists": status in {"VERIFIED_ALL_THREE", "PROBABLE_ALL_THREE"},
                "three_output_types_verified": status == "VERIFIED_ALL_THREE",
                "neutral_file_ids": [v["neutral_reference_file_id"] for v in selected.values()],
                "reference_manifest_hash": None,
            },
            "reference_content_inspected": False,
        }
        effective_sets.append(effective)
        if not v1_all_three and status in {"VERIFIED_ALL_THREE", "PROBABLE_ALL_THREE"}:
            false_negative_rows.append(effective)

    alias_registry = {
        "registry_id": "target_output_alias_registry_v2",
        "version": "target_output_detection_v2_metadata_aliases",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "output_types": ALIASES,
        "revision_indicator_patterns": REVISION_PATTERNS,
        "forbidden_loose_matches": ["電機施工圖", "生管文件"],
    }
    policy = {
        "policy_id": "target_output_detection_policy_v2",
        "version": "target_output_detection_v2_metadata_first",
        "metadata_inspection_order": [
            "filename",
            "relative_path",
            "extension",
            "hash",
            "size",
            "page_count",
            "pdf_metadata",
            "existing_inventory_classification",
        ],
        "root_metadata_pass": "Does not open completed PDFs; page_count and PDF metadata remain null unless an isolated reference_presence_classifier is required.",
        "classification_values": [
            "VERIFIED_ALL_THREE",
            "PROBABLE_ALL_THREE",
            "PARTIAL_REFERENCE_SET",
            "AMBIGUOUS_REFERENCE_SET",
            "NO_REFERENCE_SET",
            "INACCESSIBLE_REFERENCE_SET",
        ],
        "reference_content_isolation": {
            "source_review_agents_receive": [
                "completed reference set exists",
                "three output types verified",
                "neutral file IDs",
                "reference manifest hash",
            ],
            "generators_receive": [
                "completed reference set exists",
                "three output types verified",
                "neutral file IDs",
                "reference manifest hash",
            ],
            "forbidden_to_source_reviewers_and_generators": [
                "reference dimensions",
                "component names",
                "quantities",
                "layout descriptions",
                "drawing text",
                "images",
                "thumbnails",
                "title block details beyond role classification",
                "reference-derived design decisions",
            ],
        },
    }

    completed_candidates = {
        "version": "target_output_detection_v2_metadata_aliases",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    effective = {
        "version": "target_output_detection_v2_metadata_aliases",
        "project_count": len(effective_sets),
        "reference_availability_counts": dict(Counter(row["reference_availability"] for row in effective_sets)),
        "effective_reference_sets": effective_sets,
    }

    write_json(OUT_MANIFEST_DIR / "target_output_alias_registry.json", alias_registry)
    write_json(OUT_MANIFEST_DIR / "target_output_detection_policy.json", policy)
    write_json(OUT_MANIFEST_DIR / "completed_reference_candidates.json", completed_candidates)
    write_json(OUT_MANIFEST_DIR / "effective_reference_sets.json", effective)

    with (OUT_REPORT_DIR / "target_detection_false_negative_candidates.csv").open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "project_id",
            "reference_availability",
            "detected_output_types",
            "candidate_count",
            "effective_neutral_file_ids",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in false_negative_rows:
            writer.writerow(
                {
                    "project_id": row["project_id"],
                    "reference_availability": row["reference_availability"],
                    "detected_output_types": "|".join(row["detected_output_types"]),
                    "candidate_count": row["candidate_count"],
                    "effective_neutral_file_ids": "|".join(v["neutral_reference_file_id"] for v in row["effective_reference_files"].values()),
                }
            )

    report = [
        "# Target Detection V2 Report",
        "",
        "- status: `TARGET_DETECTION_V2_METADATA_ALIAS_PASS`",
        "- completed PDF contents opened: `false`",
        "- page rendering/OCR/text extraction: `false`",
        f"- completed-reference candidate rows: `{len(candidates)}`",
        "",
        "## Reference Availability Counts",
        "",
    ]
    for key, value in sorted(effective["reference_availability_counts"].items()):
        report.append(f"- `{key}`: `{value}`")
    report.extend(
        [
            "",
            "## V1 False Negative Candidates",
            "",
            f"- projects promoted from v1 not-all-three to v2 all-three/probable-all-three: `{len(false_negative_rows)}`",
            "",
            "## Isolation Notes",
            "",
            "This pass used filename, relative path, extension, recorded hash, recorded size, and existing inventory role only.",
            "Reference page content, dimensions, component names, quantities, layout descriptions, images, thumbnails, and title-block details were not extracted.",
        ]
    )
    (OUT_REPORT_DIR / "target_detection_v2_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
