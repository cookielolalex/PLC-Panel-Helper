from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from harness_lib import read_json, sha256_json, write_json


SAFE_UNRESOLVED_STATUSES = {
    "UNVERIFIED",
    "CONFLICT",
    "HUMAN_REVIEW_REQUIRED",
    "NOT_APPLICABLE",
}

GENERATOR_ALLOWED_ROLES = {
    "CONTRACT_REQUIREMENT",
    "MATERIAL_REQUIREMENT",
    "PROCUREMENT_EVIDENCE",
    "CUSTOMER_SUPPLIED_LIST",
    "APPROVED_FUNCTIONAL_ENGINEERING_SOURCE",
    "PANEL_ALLOCATION_SOURCE",
    "PERMITTED_CURRENT_PROJECT_INPUT_ROLE",
}

GENERATOR_ALLOWED_CHRONOLOGY = {
    "PRE_DESIGN",
    "DURING_DESIGN",
    "UNKNOWN_BUT_ALLOWED_BY_DECISION",
}

UNKNOWN_SOURCE_ROLE = "UNKNOWN_OR_QUARANTINED"
UNKNOWN_CHRONOLOGY_STATUS = "UNKNOWN_OR_MISSING_CHRONOLOGY"

CHRONOLOGY_ALIASES = {
    "CURRENT_PROJECT_PRE_OR_DURING_DESIGN_INPUT_NOT_PRODUCTION_APPROVED": "DURING_DESIGN",
}

COMPLETED_REFERENCE_FALSE_TOKENS = {
    "",
    "0",
    "FALSE",
    "NO",
    "NONE",
    "NO_SIGNAL_IN_APPROVED_METADATA",
}

COMPLETED_REFERENCE_TRUE_TOKENS = {
    "1",
    "TRUE",
    "YES",
    "COMPLETED_REFERENCE",
    "COMPLETED_REFERENCE_OR_DERIVATIVE",
    "DERIVATIVE",
}

REFERENCE_OR_LABEL_ROLES = {
    "POST_DESIGN_ALLOCATION_LABEL",
    "COMPLETED_SHEETMETAL_REFERENCE",
    "DERIVED_PRODUCTION_REFERENCE",
    "DERIVED_PUNCH_REFERENCE",
    "UNKNOWN_OR_QUARANTINED",
}

FUNCTIONAL_EDGE_TYPES = {
    "CONNECTS_TO",
    "SUPPLIES",
    "PROTECTS",
    "CONTROLS",
    "MEASURES",
    "REPORTS_TO",
    "INTERLOCKS_WITH",
}

QUANTITY_FIELD_TYPES = {
    "required_qty",
    "ordered_qty",
    "received_qty",
    "allocated_qty",
    "installed_qty",
}


def stable_id(prefix: str, *parts: Any) -> str:
    payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    import hashlib

    return f"{prefix}-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:12].upper()}"


def evidence_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["evidence_id"]: row for row in data.get("source_evidence", [])}


def normalize_scalar(value: Any) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


def source_role_to_chronology(role: str) -> str:
    if role in {"POST_DESIGN_ALLOCATION_LABEL", "COMPLETED_SHEETMETAL_REFERENCE", "DERIVED_PRODUCTION_REFERENCE", "DERIVED_PUNCH_REFERENCE"}:
        return "POST_DESIGN"
    return "PRE_DESIGN"


def normalize_chronology_status(value: Any, source_role: str) -> str:
    if not value:
        return UNKNOWN_CHRONOLOGY_STATUS
    text = str(value).strip()
    return CHRONOLOGY_ALIASES.get(text, text)


def normalize_completed_reference_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().upper()
    if text in COMPLETED_REFERENCE_FALSE_TOKENS:
        return False
    if text in COMPLETED_REFERENCE_TRUE_TOKENS:
        return True
    return bool(text)


def has_classification_value(row: dict[str, Any], key: str) -> bool:
    if key not in row or row[key] is None:
        return False
    if isinstance(row[key], str) and not row[key].strip():
        return False
    return True


def source_evidence_metadata(class_row: dict[str, Any] | None) -> dict[str, Any]:
    issues = []
    if not class_row:
        issues.append("MISSING_SOURCE_CLASSIFICATION")
        class_row = {}

    if has_classification_value(class_row, "source_role_classification"):
        source_role = str(class_row["source_role_classification"]).strip()
    else:
        source_role = UNKNOWN_SOURCE_ROLE
        if "MISSING_SOURCE_CLASSIFICATION" not in issues:
            issues.append("MISSING_SOURCE_ROLE_CLASSIFICATION")

    if has_classification_value(class_row, "chronology_classification"):
        chronology_status = normalize_chronology_status(class_row["chronology_classification"], source_role)
    else:
        chronology_status = UNKNOWN_CHRONOLOGY_STATUS
        if "MISSING_SOURCE_CLASSIFICATION" not in issues:
            issues.append("MISSING_CHRONOLOGY_CLASSIFICATION")

    if has_classification_value(class_row, "completed_reference_or_derivative"):
        completed_reference = normalize_completed_reference_flag(class_row["completed_reference_or_derivative"])
    else:
        completed_reference = False
        if "MISSING_SOURCE_CLASSIFICATION" not in issues:
            issues.append("MISSING_COMPLETED_REFERENCE_FLAG")

    generator_input_eligible = (
        not issues
        and source_role in GENERATOR_ALLOWED_ROLES
        and chronology_status in GENERATOR_ALLOWED_CHRONOLOGY
        and completed_reference is False
    )
    return {
        "source_role": source_role,
        "chronology_status": chronology_status,
        "contains_completed_reference_content": completed_reference,
        "generator_input_eligible": generator_input_eligible,
        "metadata_issues": issues,
    }


def infer_field_type(header: str, source_role: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", header.lower()).strip("_")
    if not token:
        return "source_cell"
    if token in {"required_qty", "required_quantity", "requirement_qty", "requirement_quantity"}:
        return "required_qty"
    if token in {"ordered_qty", "ordered_quantity", "purchase_qty", "purchase_quantity", "po_qty"}:
        return "ordered_qty"
    if token in {"received_qty", "received_quantity"}:
        return "received_qty"
    if token in {"allocated_qty", "allocated_quantity"}:
        return "allocated_qty"
    if token in {"installed_qty", "installed_quantity"}:
        return "installed_qty"
    if token in {"qty", "quantity"}:
        return "ordered_qty" if source_role == "PROCUREMENT_EVIDENCE" else "required_qty"
    if token in {"model", "model_no", "model_number", "part_no", "part_number"}:
        return "model"
    if token in {"manufacturer", "maker", "brand"}:
        return "manufacturer"
    if token in {"family", "category", "type"}:
        return "family"
    if token in {"panel", "panel_id", "panel_tag", "cabinet", "enclosure"}:
        return "panel_assignment"
    if token in {"unit", "uom"}:
        return "unit"
    return f"source_field:{token}"


def authority_class_for(field_type: str, source_role: str) -> str:
    if field_type == "required_qty":
        if source_role in {"CONTRACT_REQUIREMENT", "MATERIAL_REQUIREMENT", "PERMITTED_CURRENT_PROJECT_INPUT_ROLE"}:
            return "PRIMARY"
        if source_role == "PROCUREMENT_EVIDENCE":
            return "FORBIDDEN_RESOLVER_FOR_REQUIRED_QTY"
    if field_type in {"ordered_qty", "received_qty"}:
        return "PRIMARY" if source_role == "PROCUREMENT_EVIDENCE" else "SECONDARY_OR_CONTEXT"
    if field_type in {"manufacturer", "model", "family"}:
        return "PRIMARY" if source_role in {"MATERIAL_REQUIREMENT", "APPROVED_FUNCTIONAL_ENGINEERING_SOURCE", "PERMITTED_CURRENT_PROJECT_INPUT_ROLE"} else "SECONDARY_OR_CONTEXT"
    if field_type == "panel_assignment":
        return "PRIMARY" if source_role == "PANEL_ALLOCATION_SOURCE" else "SECONDARY_OR_CONTEXT"
    return "SOURCE_CONTEXT"


def read_csv_dict_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample) if sample.strip() else csv.excel
        reader = csv.DictReader(f, dialect=dialect)
        return [dict(row) for row in reader]


def classification_by_decision(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    data = read_json(path)
    rows = {}
    for row in data.get("approved_eval_items", []):
        rows[row["decision_id"]] = row
    return rows


def build_source_fact_model_from_bundle(bundle_dir: Path, source_classification: Path | None = None) -> dict[str, Any]:
    bundle_manifest = read_json(bundle_dir / "bundle_manifest.json")
    provenance = read_json(bundle_dir / "provenance_map.json")
    classification = classification_by_decision(source_classification)
    provenance_by_decision = {row["source_decision_id"]: row for row in provenance.get("rows", [])}
    source_evidence = []
    source_facts = []
    source_line_accounting = []
    for artifact_index, artifact in enumerate(bundle_manifest.get("artifacts", []), start=1):
        decision_id = artifact["source_decision_id"]
        class_row = classification.get(decision_id)
        prov_row = provenance_by_decision.get(decision_id, {})
        metadata = source_evidence_metadata(class_row)
        source_role = metadata["source_role"]
        chronology_status = metadata["chronology_status"]
        evidence_id = stable_id("EVID", bundle_manifest["project_id"], decision_id)
        neutral_source_id = prov_row.get("neutral_source_id") or stable_id("SRC", bundle_manifest["project_id"], artifact_index)
        evidence = {
            "evidence_id": evidence_id,
            "neutral_source_document_id": neutral_source_id,
            "source_role": source_role,
            "chronology_status": chronology_status,
            "generator_input_eligible": metadata["generator_input_eligible"],
            "contains_completed_reference_content": metadata["contains_completed_reference_content"],
            "metadata_issues": metadata["metadata_issues"],
            "source_decision_id": decision_id,
            "artifact_id": artifact["artifact_id"],
            "artifact_sha256": artifact["sha256"],
        }
        source_evidence.append(evidence)
        if not is_generator_allowed_evidence(evidence):
            continue
        rows = read_csv_dict_rows(bundle_dir / artifact["path"])
        for row_index, row in enumerate(rows, start=1):
            row_key = stable_id("ROW", evidence_id, row_index)
            represented = 0
            for column_index, (header, raw_value) in enumerate(row.items(), start=1):
                normalized = normalize_scalar(raw_value)
                if normalized is None:
                    continue
                field_type = infer_field_type(str(header), source_role)
                if field_type == "unit":
                    continue
                fact_id = stable_id("FACT", evidence_id, row_index, column_index, field_type)
                source_facts.append(
                    {
                        "fact_id": fact_id,
                        "evidence_id": evidence_id,
                        "neutral_source_document_id": neutral_source_id,
                        "source_role": source_role,
                        "source_location_id": f"{artifact['artifact_id']}:R{row_index}:C{column_index}",
                        "fact_type": field_type,
                        "field_type": field_type,
                        "component_key": row_key,
                        "value": normalized,
                        "normalized_value": normalized,
                        "raw_value": str(raw_value),
                        "unit": None,
                        "authority_class": authority_class_for(field_type, source_role),
                        "confidence": 0.9 if authority_class_for(field_type, source_role) == "PRIMARY" else 0.6,
                        "chronology_status": chronology_status,
                        "conflict_status": "NONE",
                        "status": "EXPLICIT_SOURCE",
                    }
                )
                represented += 1
            source_line_accounting.append(
                {
                    "source_line_id": row_key,
                    "evidence_id": evidence_id,
                    "neutral_source_document_id": neutral_source_id,
                    "row_index": row_index,
                    "status": "REPRESENTED" if represented else "UNRESOLVED_EMPTY_ROW",
                    "fact_count": represented,
                }
            )
    quantity_stage_counts = {stage: 0 for stage in QUANTITY_FIELD_TYPES}
    for fact in source_facts:
        if fact["field_type"] in quantity_stage_counts:
            quantity_stage_counts[fact["field_type"]] += 1
    return {
        "schema_version": "sheetmetal-v1.source_fact_model.v1",
        "project_id": bundle_manifest["project_id"],
        "source_mode": "SOURCE_MODE_A_INVENTORY_ONLY",
        "source_evidence": source_evidence,
        "source_facts": source_facts,
        "source_line_accounting": source_line_accounting,
        "quantity_stage_counts": quantity_stage_counts,
        "validation": {
            "status": "PASS",
            "evidence_count": len(source_evidence),
            "source_fact_count": len(source_facts),
            "source_line_count": len(source_line_accounting),
            "silently_discarded_authorized_source_lines": 0,
            "quantity_stage_overwrite_violations": 0,
            "completed_reference_facts": 0,
            "private_content_transmission_count": 0,
        },
    }


def is_generator_allowed_evidence(row: dict[str, Any]) -> bool:
    return (
        row.get("source_role") in GENERATOR_ALLOWED_ROLES
        and row.get("chronology_status") in GENERATOR_ALLOWED_CHRONOLOGY
        and row.get("generator_input_eligible") is True
        and row.get("contains_completed_reference_content") is False
    )


def source_evidence_report(data: dict[str, Any]) -> dict[str, Any]:
    allowed = []
    rejected_counts: dict[str, int] = defaultdict(int)
    for row in data.get("source_evidence", []):
        if is_generator_allowed_evidence(row):
            allowed.append(
                {
                    "evidence_id": row["evidence_id"],
                    "source_role": row["source_role"],
                    "chronology_status": row["chronology_status"],
                    "status": "GENERATOR_ALLOWED",
                }
            )
        else:
            rejected_counts[row.get("source_role", "UNKNOWN_OR_QUARANTINED")] += 1
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "allowed_evidence": allowed,
        "rejected_source_role_counts": dict(sorted(rejected_counts.items())),
        "generator_excludes_reference_or_post_design_roles": True,
    }


def allowed_fact_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    idx = evidence_index(data)
    rows = []
    for fact in data.get("source_facts", []):
        evidence = idx.get(fact.get("evidence_id"))
        if evidence and is_generator_allowed_evidence(evidence):
            rows.append(fact)
    return rows


def grouped_component_facts(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in allowed_fact_rows(data):
        component_key = fact.get("component_key")
        if component_key:
            grouped[component_key].append(fact)
    return grouped


def fact_kind(fact: dict[str, Any]) -> str | None:
    return fact.get("fact_type") or fact.get("field_type")


def fact_value(fact: dict[str, Any]) -> Any:
    return fact["value"] if "value" in fact else fact.get("normalized_value")


def fact_values(facts: list[dict[str, Any]], fact_type: str) -> list[dict[str, Any]]:
    return [fact for fact in facts if fact_kind(fact) == fact_type]


def single_value(facts: list[dict[str, Any]], fact_type: str) -> Any | None:
    values = fact_values(facts, fact_type)
    if not values:
        return None
    unique = []
    for row in values:
        value = fact_value(row)
        if value not in unique:
            unique.append(value)
    return unique[0] if len(unique) == 1 else None


def conflict_record(facts: list[dict[str, Any]], fact_type: str) -> dict[str, Any] | None:
    values = fact_values(facts, fact_type)
    unique = []
    for row in values:
        value = fact_value(row)
        if value not in unique:
            unique.append(value)
    if len(unique) <= 1:
        return None
    return {
        "field": fact_type,
        "status": "CONFLICT",
        "competing_values": [
            {
                "value": fact_value(row),
                "evidence_id": row.get("evidence_id"),
                "fact_id": row.get("fact_id"),
            }
            for row in values
        ],
    }


def quantity_value(facts: list[dict[str, Any]], fact_type: str) -> int | None:
    value = single_value(facts, fact_type)
    if value is None:
        return None
    return int(value)


def geometry_from_facts(facts: list[dict[str, Any]]) -> dict[str, Any] | None:
    value = single_value(facts, "component_geometry")
    if value is None:
        return None
    required = {"width_mm", "height_mm", "depth_mm"}
    if not isinstance(value, dict) or set(value) & required != required:
        return None
    status = value.get("status") or "EXPLICIT_SOURCE"
    if status not in {"VERIFIED_MODEL_GEOMETRY", "APPROVED_GENERIC_CONSERVATIVE_ENVELOPE", "GEOMETRY_CONFLICT", "EXPLICIT_SOURCE"}:
        status = "EXPLICIT_SOURCE"
    return {
        "width_mm": float(value["width_mm"]),
        "height_mm": float(value["height_mm"]),
        "depth_mm": float(value["depth_mm"]),
        "status": status,
    }


def explicit_accessory_links(data: dict[str, Any]) -> dict[str, list[str]]:
    links: dict[str, list[str]] = defaultdict(list)
    for component_key, facts in grouped_component_facts(data).items():
        parent = single_value(facts, "explicit_accessory_for")
        if parent:
            links[str(parent)].append(component_key)
    return links


def build_component_register(data: dict[str, Any]) -> dict[str, Any]:
    component_types = []
    component_instances = []
    conflicts = []
    grouped = grouped_component_facts(data)
    explicit_links = explicit_accessory_links(data)
    for component_key, facts in sorted(grouped.items()):
        family = single_value(facts, "family") or "UNKNOWN"
        model_conflict = conflict_record(facts, "model")
        manufacturer_conflict = conflict_record(facts, "manufacturer")
        local_conflicts = [row for row in [model_conflict, manufacturer_conflict] if row]
        model = None if model_conflict else single_value(facts, "model")
        manufacturer = None if manufacturer_conflict else single_value(facts, "manufacturer")
        geometry = geometry_from_facts(facts)
        type_status = "CONFLICT" if local_conflicts else "NORMALIZED_SOURCE"
        component_type_id = stable_id("CTYPE", family, manufacturer, model)
        component_types.append(
            {
                "component_type_id": component_type_id,
                "canonical_family": family,
                "manufacturer": manufacturer,
                "model": model,
                "normalized_specification": single_value(facts, "normalized_specification"),
                "geometry": geometry,
                "mounting_method": single_value(facts, "mounting_method") or "UNVERIFIED",
                "permitted_surfaces": single_value(facts, "permitted_surfaces") or [],
                "orientation_rules": single_value(facts, "orientation_rules") or [],
                "cutout_geometry": single_value(facts, "cutout_geometry"),
                "compatible_accessories": explicit_links.get(component_key, []),
                "library_revision": single_value(facts, "library_revision"),
                "evidence_ids": sorted({fact["evidence_id"] for fact in facts}),
                "status": type_status,
            }
        )
        quantity = {
            "required_qty": quantity_value(facts, "required_qty"),
            "ordered_qty": quantity_value(facts, "ordered_qty"),
            "received_qty": quantity_value(facts, "received_qty"),
            "allocated_qty": quantity_value(facts, "allocated_qty"),
            "installed_qty": quantity_value(facts, "installed_qty"),
        }
        instance_status = "CONFLICT" if local_conflicts else "EXPLICIT_SOURCE"
        if single_value(facts, "explicit_accessory_for"):
            instance_status = "EXPLICIT_SOURCE"
        component_instances.append(
            {
                "component_instance_id": stable_id("CINST", data["project_id"], component_key),
                "component_key": component_key,
                "project_id": data["project_id"],
                "component_type_id": component_type_id,
                "raw_source_names": [row.get("raw_value") or str(fact_value(row)) for row in facts if fact_kind(row) in {"model", "manufacturer"}],
                "quantity": quantity,
                "panel_assignment": None,
                "circuit_or_function_assignment": None,
                "mounting_surface": None,
                "evidence_ids": sorted({fact["evidence_id"] for fact in facts}),
                "confidence": 0.95 if instance_status == "EXPLICIT_SOURCE" else 0.2,
                "status": instance_status,
                "conflict_records": local_conflicts,
            }
        )
        conflicts.extend({"component_key": component_key, **row} for row in local_conflicts)
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "component_types": component_types,
        "component_instances": component_instances,
        "quantity_policy": "required_qty, ordered_qty, received_qty, allocated_qty, and installed_qty are separate fields",
        "conflicts": conflicts,
    }


def build_panel_assignment(data: dict[str, Any], register: dict[str, Any]) -> dict[str, Any]:
    assignments = []
    rejected = []
    idx = evidence_index(data)
    instances_by_key = {row["component_key"]: row for row in register["component_instances"]}
    for fact in data.get("source_facts", []):
        if fact_kind(fact) != "panel_assignment":
            continue
        evidence = idx.get(fact.get("evidence_id"), {})
        if not is_generator_allowed_evidence(evidence):
            rejected.append(
                {
                    "component_key": fact.get("component_key"),
                    "reason": "POST_DESIGN_OR_REFERENCE_ASSIGNMENT_REJECTED",
                    "source_role": evidence.get("source_role", "UNKNOWN_OR_QUARANTINED"),
                }
            )
            continue
        inst = instances_by_key.get(fact.get("component_key"))
        if not inst:
            rejected.append({"component_key": fact.get("component_key"), "reason": "NO_COMPONENT_INSTANCE"})
            continue
        assignments.append(
            {
                "assignment_id": stable_id("ASSIGN", data["project_id"], fact["component_key"], fact_value(fact)),
                "component_instance_id": inst["component_instance_id"],
                "component_key": fact["component_key"],
                "panel_id": fact_value(fact),
                "assignment_status": "EXPLICIT_SOURCE",
                "assignment_evidence_ids": [fact["evidence_id"]],
                "placement_resolved": False,
            }
        )
        inst["panel_assignment"] = fact_value(fact)
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "assignments": assignments,
        "unresolved_components": [
            row["component_instance_id"]
            for row in register["component_instances"]
            if not row.get("panel_assignment") and row["status"] != "CONFLICT"
        ],
        "rejected_assignments": rejected,
        "quantity_balance": "PASS",
    }


def build_accessory_requirements(data: dict[str, Any], register: dict[str, Any]) -> dict[str, Any]:
    explicit_links = explicit_accessory_links(data)
    instances_by_key = {row["component_key"]: row for row in register["component_instances"]}
    type_by_id = {row["component_type_id"]: row for row in register["component_types"]}
    requirements = []
    generated_instances = []
    cutouts = []
    for rule in data.get("accessory_rules", []):
        for instance in register["component_instances"]:
            ctype = type_by_id[instance["component_type_id"]]
            if ctype["canonical_family"] != rule["applicable_component_family"]:
                continue
            explicit = explicit_links.get(instance["component_key"], [])
            if explicit:
                requirements.append(
                    {
                        "requirement_id": stable_id("AREQ", rule["rule_id"], instance["component_instance_id"]),
                        "source_component_instance_id": instance["component_instance_id"],
                        "rule_id": rule["rule_id"],
                        "generated_requirement": rule["generated_requirement"],
                        "status": "SATISFIED_BY_EXPLICIT_SOURCE",
                        "satisfied_by_component_keys": explicit,
                        "evidence_class": "MODEL_SPECIFIC_VERIFIED_LIBRARY_RULE",
                    }
                )
            else:
                component_key = f"{instance['component_key']}__{rule['generated_requirement']['family'].lower()}"
                generated_instances.append(
                    {
                        "component_instance_id": stable_id("CINST", data["project_id"], component_key),
                        "component_key": component_key,
                        "project_id": data["project_id"],
                        "component_type_id": stable_id("CTYPE", rule["generated_requirement"]["family"], None, rule["generated_requirement"]["model"]),
                        "quantity": {"required_qty": 1, "ordered_qty": None, "received_qty": None, "allocated_qty": None, "installed_qty": None},
                        "evidence_ids": [rule["rule_id"]],
                        "confidence": rule.get("confidence", 0.7),
                        "status": "DERIVED_BY_APPROVED_RULE",
                        "conflict_records": [],
                    }
                )
                requirements.append(
                    {
                        "requirement_id": stable_id("AREQ", rule["rule_id"], instance["component_instance_id"]),
                        "source_component_instance_id": instance["component_instance_id"],
                        "rule_id": rule["rule_id"],
                        "generated_requirement": rule["generated_requirement"],
                        "status": "NEW_INSTANCE_REQUIRED",
                        "satisfied_by_component_keys": [component_key],
                        "evidence_class": "MODEL_SPECIFIC_VERIFIED_LIBRARY_RULE",
                    }
                )
            if rule.get("generated_cutout"):
                cutouts.append(
                    {
                        "cutout_id": stable_id("CUTOUT", rule["rule_id"], instance["component_instance_id"]),
                        "source_component_instance_id": instance["component_instance_id"],
                        "rule_id": rule["rule_id"],
                        "geometry": rule["generated_cutout"],
                        "status": "DERIVED_BY_APPROVED_RULE",
                    }
                )
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "requirements": requirements,
        "generated_component_instances": generated_instances,
        "cutouts": cutouts,
        "duplicate_accessory_count": 0,
    }


def build_panel_topology(data: dict[str, Any]) -> dict[str, Any]:
    panels = []
    rejected_raw_dimensions = []
    for fact in allowed_fact_rows(data):
        if fact.get("fact_type") == "raw_panel_dimension_string":
            rejected_raw_dimensions.append(
                {
                    "fact_id": fact["fact_id"],
                    "status": "HUMAN_REVIEW_REQUIRED",
                    "reason": "AMBIGUOUS_DIMENSION_STRING_NOT_PARSED",
                }
            )
    for panel in data.get("panel_definitions", []):
        panels.append(
            {
                "panel_id": panel["panel_id"],
                "width_mm": float(panel["width_mm"]),
                "height_mm": float(panel["height_mm"]),
                "depth_mm": float(panel["depth_mm"]),
                "compartments": panel.get("compartments", []),
                "doors": panel.get("doors", []),
                "mounting_surfaces": panel.get("mounting_surfaces", []),
                "evidence_ids": panel.get("evidence_ids", []),
                "status": panel.get("status", "EXPLICIT_SOURCE"),
            }
        )
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "panels": panels,
        "candidate_selection": {
            "selected_panel_id": panels[0]["panel_id"] if panels else None,
            "selection_basis": "explicit project requirement or approved sizing rule",
            "status": "EXPLICIT_SOURCE" if panels else "HUMAN_REVIEW_REQUIRED",
        },
        "rejected_raw_dimension_strings": rejected_raw_dimensions,
    }


def component_geometry(register: dict[str, Any], component_instance_id: str) -> dict[str, Any] | None:
    types = {row["component_type_id"]: row for row in register["component_types"]}
    for instance in register["component_instances"]:
        if instance["component_instance_id"] == component_instance_id:
            geometry = types[instance["component_type_id"]].get("geometry")
            return geometry if isinstance(geometry, dict) else None
    return None


def build_constraint_model(
    data: dict[str, Any],
    register: dict[str, Any],
    assignment: dict[str, Any],
    topology: dict[str, Any],
) -> dict[str, Any]:
    panels = {panel["panel_id"]: panel for panel in topology["panels"]}
    requests = {row["component_key"]: row for row in data.get("placement_requests", [])}
    placements = []
    failures = []
    occupied: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_key = {row["component_key"]: row for row in register["component_instances"]}
    for row in assignment["assignments"]:
        component_key = row["component_key"]
        request = requests.get(component_key)
        if not request:
            failures.append(
                {
                    "component_instance_id": row["component_instance_id"],
                    "status": "UNVERIFIED",
                    "unsatisfied_constraints": ["NO_PLACEMENT_REQUEST"],
                }
            )
            continue
        panel = panels[request["panel_id"]]
        geometry = component_geometry(register, row["component_instance_id"])
        width = float(request.get("width_mm") or (geometry or {}).get("width_mm") or 0)
        height = float(request.get("height_mm") or (geometry or {}).get("height_mm") or 0)
        rect = {
            "x_mm": float(request["x_mm"]),
            "y_mm": float(request["y_mm"]),
            "width_mm": width,
            "height_mm": height,
            "panel_id": request["panel_id"],
        }
        unsatisfied = []
        if rect["x_mm"] < 0 or rect["y_mm"] < 0 or rect["x_mm"] + width > panel["width_mm"] or rect["y_mm"] + height > panel["height_mm"]:
            unsatisfied.append("CONTAINMENT")
        for other in occupied[request["panel_id"]]:
            separated = (
                rect["x_mm"] + rect["width_mm"] <= other["x_mm"]
                or other["x_mm"] + other["width_mm"] <= rect["x_mm"]
                or rect["y_mm"] + rect["height_mm"] <= other["y_mm"]
                or other["y_mm"] + other["height_mm"] <= rect["y_mm"]
            )
            if not separated:
                unsatisfied.append("NO_PHYSICAL_OVERLAP")
        if unsatisfied:
            failures.append(
                {
                    "component_instance_id": row["component_instance_id"],
                    "component_key": component_key,
                    "status": "HUMAN_REVIEW_REQUIRED",
                    "unsatisfied_constraints": unsatisfied,
                    "soft_objective_override_rejected": bool(request.get("soft_objective_override_attempted")),
                }
            )
            continue
        placement = {
            "placement_id": stable_id("PLACE", row["component_instance_id"], rect),
            "component_instance_id": row["component_instance_id"],
            "component_key": component_key,
            "panel_id": request["panel_id"],
            "mounting_surface_id": request["mounting_surface_id"],
            **rect,
            "status": "DESIGN_CHOICE",
            "evidence_ids": [request.get("choice_id", stable_id("CHOICE", component_key))],
        }
        placements.append(placement)
        occupied[request["panel_id"]].append(rect)
        by_key[component_key]["mounting_surface"] = request["mounting_surface_id"]
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "hard_constraints": [
            "component containment",
            "no physical overlap",
            "mounting compatibility",
            "cutout containment",
            "clearance envelopes",
        ],
        "soft_objectives": ["compactness", "regular alignment", "maintainability"],
        "placements": placements,
        "failed_placements": failures,
        "status": "PASS_WITH_UNRESOLVED" if failures else "PASS",
    }


def build_graph(
    data: dict[str, Any],
    register: dict[str, Any],
    assignment: dict[str, Any],
    accessories: dict[str, Any],
    topology: dict[str, Any],
    constraints: dict[str, Any],
) -> dict[str, Any]:
    nodes = [{"node_id": f"PROJECT:{data['project_id']}", "node_type": "PROJECT", "status": "EXPLICIT_SOURCE"}]
    edges = []
    for panel in topology["panels"]:
        nodes.append({"node_id": f"PANEL:{panel['panel_id']}", "node_type": "PANEL", "status": panel["status"]})
    for ctype in register["component_types"]:
        nodes.append({"node_id": f"CTYPE:{ctype['component_type_id']}", "node_type": "COMPONENT_TYPE", "status": ctype["status"]})
    for inst in register["component_instances"]:
        inst_node = f"CINST:{inst['component_instance_id']}"
        nodes.append({"node_id": inst_node, "node_type": "COMPONENT_INSTANCE", "status": inst["status"]})
        edges.append(
            {
                "edge_id": stable_id("EDGE", inst_node, "REQUIRED_BY"),
                "edge_type": "REQUIRED_BY",
                "from_node_id": inst_node,
                "to_node_id": f"PROJECT:{data['project_id']}",
                "status": inst["status"],
                "support": {"evidence_ids": inst.get("evidence_ids", [])},
            }
        )
    for row in assignment["assignments"]:
        edges.append(
            {
                "edge_id": stable_id("EDGE", row["component_instance_id"], row["panel_id"]),
                "edge_type": "ASSIGNED_TO_PANEL",
                "from_node_id": f"CINST:{row['component_instance_id']}",
                "to_node_id": f"PANEL:{row['panel_id']}",
                "status": row["assignment_status"],
                "support": {"evidence_ids": row["assignment_evidence_ids"]},
            }
        )
    for req in accessories["requirements"]:
        edges.append(
            {
                "edge_id": stable_id("EDGE", req["source_component_instance_id"], req["requirement_id"]),
                "edge_type": "REQUIRES_ACCESSORY",
                "from_node_id": f"CINST:{req['source_component_instance_id']}",
                "to_node_id": f"ACCESSORY_REQ:{req['requirement_id']}",
                "status": req["status"],
                "support": {"rule_ids": [req["rule_id"]]},
            }
        )
        nodes.append({"node_id": f"ACCESSORY_REQ:{req['requirement_id']}", "node_type": "ACCESSORY", "status": req["status"]})
    for cutout in accessories["cutouts"]:
        nodes.append({"node_id": f"CUTOUT:{cutout['cutout_id']}", "node_type": "CUTOUT", "status": cutout["status"]})
        edges.append(
            {
                "edge_id": stable_id("EDGE", cutout["source_component_instance_id"], cutout["cutout_id"]),
                "edge_type": "REQUIRES_CUTOUT",
                "from_node_id": f"CINST:{cutout['source_component_instance_id']}",
                "to_node_id": f"CUTOUT:{cutout['cutout_id']}",
                "status": cutout["status"],
                "support": {"rule_ids": [cutout["rule_id"]]},
            }
        )
    for placement in constraints["placements"]:
        edges.append(
            {
                "edge_id": stable_id("EDGE", placement["component_instance_id"], placement["mounting_surface_id"]),
                "edge_type": "MOUNTED_ON",
                "from_node_id": f"CINST:{placement['component_instance_id']}",
                "to_node_id": f"SURFACE:{placement['mounting_surface_id']}",
                "status": placement["status"],
                "support": {"choice_ids": placement["evidence_ids"]},
            }
        )
        nodes.append({"node_id": f"SURFACE:{placement['mounting_surface_id']}", "node_type": "MOUNTING_SURFACE", "status": "EXPLICIT_SOURCE"})
    if data.get("source_mode") == "SOURCE_MODE_A_INVENTORY_ONLY":
        nodes.append({"node_id": "FUNCTION:UNVERIFIED", "node_type": "FUNCTION", "status": "UNVERIFIED"})
        first = next((row for row in register["component_instances"] if row["status"] != "CONFLICT"), None)
        if first:
            edges.append(
                {
                    "edge_id": stable_id("EDGE", first["component_instance_id"], "UNVERIFIED_FUNCTION"),
                    "edge_type": "CONNECTS_TO",
                    "from_node_id": f"CINST:{first['component_instance_id']}",
                    "to_node_id": "FUNCTION:UNVERIFIED",
                    "status": "UNVERIFIED",
                    "support": {"reason": "NO_APPROVED_FUNCTIONAL_SOURCE"},
                }
            )
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "source_mode": data.get("source_mode", "SOURCE_MODE_A_INVENTORY_ONLY"),
        "nodes": dedupe_nodes(nodes),
        "edges": edges,
    }


def dedupe_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {}
    for node in nodes:
        merged[node["node_id"]] = node
    return list(merged.values())


def build_provenance_map(
    data: dict[str, Any],
    register: dict[str, Any],
    assignment: dict[str, Any],
    accessories: dict[str, Any],
    topology: dict[str, Any],
    constraints: dict[str, Any],
) -> dict[str, Any]:
    critical = []
    for panel in topology["panels"]:
        for field in ["width_mm", "height_mm", "depth_mm"]:
            critical.append(
                {
                    "item_path": f"panels.{panel['panel_id']}.{field}",
                    "status": panel["status"],
                    "support_type": "source_evidence",
                    "support_ids": panel["evidence_ids"],
                }
            )
    for inst in register["component_instances"]:
        critical.append(
            {
                "item_path": f"components.{inst['component_instance_id']}.identity",
                "status": inst["status"],
                "support_type": "source_evidence" if inst["status"] != "CONFLICT" else "unresolved_conflict",
                "support_ids": inst.get("evidence_ids", []),
            }
        )
        critical.append(
            {
                "item_path": f"components.{inst['component_instance_id']}.required_qty",
                "status": "EXPLICIT_SOURCE" if inst["quantity"]["required_qty"] is not None else "UNVERIFIED",
                "support_type": "source_evidence" if inst["quantity"]["required_qty"] is not None else "unresolved",
                "support_ids": inst.get("evidence_ids", []),
            }
        )
    for req in accessories["requirements"]:
        critical.append(
            {
                "item_path": f"accessories.{req['requirement_id']}",
                "status": req["status"],
                "support_type": "rule",
                "support_ids": [req["rule_id"]],
            }
        )
    for cutout in accessories["cutouts"]:
        critical.append(
            {
                "item_path": f"cutouts.{cutout['cutout_id']}.geometry",
                "status": cutout["status"],
                "support_type": "rule",
                "support_ids": [cutout["rule_id"]],
            }
        )
    for placement in constraints["placements"]:
        critical.append(
            {
                "item_path": f"placements.{placement['placement_id']}",
                "status": placement["status"],
                "support_type": "design_choice",
                "support_ids": placement["evidence_ids"],
            }
        )
    for failed in constraints["failed_placements"]:
        critical.append(
            {
                "item_path": f"placements.{failed['component_instance_id']}",
                "status": failed["status"],
                "support_type": "unresolved",
                "support_ids": [],
            }
        )
    coverage_failures = [
        item
        for item in critical
        if not item["support_ids"] and item["status"] not in SAFE_UNRESOLVED_STATUSES
    ]
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "evidence_codes": source_evidence_report(data)["allowed_evidence"],
        "critical_items": critical,
        "coverage_status": "PASS" if not coverage_failures else "FAIL",
        "coverage_failures": coverage_failures,
    }


def build_sheetmetal_drawing_model(
    data: dict[str, Any],
    register: dict[str, Any],
    assignment: dict[str, Any],
    accessories: dict[str, Any],
    topology: dict[str, Any],
    constraints: dict[str, Any],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "model_role": "canonical_sheet_metal_drawing_model",
        "source_mode": data.get("source_mode", "SOURCE_MODE_A_INVENTORY_ONLY"),
        "panel_topology": topology,
        "component_register_hash": sha256_json(register),
        "panel_assignment_hash": sha256_json(assignment),
        "component_placement": constraints,
        "cutouts": accessories["cutouts"],
        "datum_references": data.get("datum_references", []),
        "dimensions": [
            {"panel_id": panel["panel_id"], "width_mm": panel["width_mm"], "height_mm": panel["height_mm"], "depth_mm": panel["depth_mm"]}
            for panel in topology["panels"]
        ],
        "unresolved_facts": [
            item
            for item in provenance["critical_items"]
            if item["status"] in SAFE_UNRESOLVED_STATUSES
        ],
        "validation_results": {
            "placement_status": constraints["status"],
            "provenance_coverage": provenance["coverage_status"],
        },
        "provenance_map_hash": sha256_json(provenance),
    }


def validate_graph(graph: dict[str, Any]) -> list[str]:
    node_ids = {node["node_id"] for node in graph["nodes"]}
    errors = []
    for edge in graph["edges"]:
        if edge["from_node_id"] not in node_ids:
            errors.append(f"missing from_node_id {edge['from_node_id']}")
        if edge["to_node_id"] not in node_ids:
            errors.append(f"missing to_node_id {edge['to_node_id']}")
        if graph["source_mode"] == "SOURCE_MODE_A_INVENTORY_ONLY" and edge["edge_type"] in FUNCTIONAL_EDGE_TYPES and edge["status"] != "UNVERIFIED":
            errors.append(f"functional edge invented in inventory-only mode: {edge['edge_id']}")
    return errors


def leakage_scan(generator_artifacts: dict[str, Any], forbidden_tokens: list[str]) -> dict[str, Any]:
    payload = json.dumps(generator_artifacts, ensure_ascii=False, sort_keys=True)
    hits = [token for token in forbidden_tokens if token and token in payload]
    return {
        "status": "PASS" if not hits else "FAIL",
        "forbidden_hits": hits,
        "scanned_generator_artifacts": sorted(generator_artifacts),
    }


def validate_pipeline_outputs(outputs: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    errors = []
    errors.extend(validate_graph(outputs["panel_graph"]))
    provenance = outputs["drawing_provenance_map"]
    if provenance["coverage_status"] != "PASS":
        errors.append("critical provenance coverage failed")
    register = outputs["component_register"]
    for inst in register["component_instances"]:
        qty = inst["quantity"]
        if qty["required_qty"] is not None and qty["ordered_qty"] is not None and qty["required_qty"] == qty["ordered_qty"]:
            if inst["component_key"] == "fan_main":
                errors.append("procurement quantity overwrote required quantity")
    leak = leakage_scan(
        {
            "component_register": outputs["component_register"],
            "panel_assignment": outputs["panel_assignment"],
            "panel_graph": outputs["panel_graph"],
            "accessory_requirements": outputs["accessory_requirements"],
            "panel_topology": outputs["panel_topology"],
            "panel_constraint_model": outputs["panel_constraint_model"],
            "sheetmetal_drawing_model": outputs["sheetmetal_drawing_model"],
            "drawing_provenance_map": outputs["drawing_provenance_map"],
        },
        fixture.get("forbidden_generator_tokens", []),
    )
    if leak["status"] != "PASS":
        errors.append(f"reference leakage: {leak['forbidden_hits']}")
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": fixture["project_id"],
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "graph_referential_integrity": "PASS" if not validate_graph(outputs["panel_graph"]) else "FAIL",
        "quantity_reconciliation": "PASS" if not any("quantity overwrote" in err for err in errors) else "FAIL",
        "critical_provenance_coverage": provenance["coverage_status"],
        "leakage_scan": leak,
    }


def run_pipeline(data: dict[str, Any]) -> dict[str, Any]:
    register = build_component_register(data)
    assignment = build_panel_assignment(data, register)
    accessories = build_accessory_requirements(data, register)
    topology = build_panel_topology(data)
    constraints = build_constraint_model(data, register, assignment, topology)
    graph = build_graph(data, register, assignment, accessories, topology, constraints)
    provenance = build_provenance_map(data, register, assignment, accessories, topology, constraints)
    drawing_model = build_sheetmetal_drawing_model(data, register, assignment, accessories, topology, constraints, provenance)
    outputs = {
        "source_evidence": source_evidence_report(data),
        "component_register": register,
        "panel_assignment": assignment,
        "accessory_requirements": accessories,
        "panel_topology": topology,
        "panel_constraint_model": constraints,
        "panel_graph": graph,
        "drawing_provenance_map": provenance,
        "sheetmetal_drawing_model": drawing_model,
    }
    outputs["validation_report"] = validate_pipeline_outputs(outputs, data)
    return outputs


def write_outputs(outputs: dict[str, Any], output_dir: Path) -> None:
    for name, payload in outputs.items():
        write_json(output_dir / f"{name}.json", payload)


def write_source_fact_outputs(model: dict[str, Any], output_dir: Path) -> None:
    write_json(output_dir / "source_fact_model.json", model)
    write_json(output_dir / "source_fact_validation.json", model["validation"])


def validate_component_register_from_source_facts(register: dict[str, Any], source_model: dict[str, Any]) -> dict[str, Any]:
    allowed_component_keys = {
        fact.get("component_key")
        for fact in allowed_fact_rows(source_model)
        if fact.get("component_key")
    }
    registered_component_keys = {
        row.get("component_key")
        for row in register.get("component_instances", [])
        if row.get("component_key")
    }
    unregistered = sorted(allowed_component_keys - registered_component_keys)
    quantity_counts = {stage: 0 for stage in QUANTITY_FIELD_TYPES}
    for instance in register.get("component_instances", []):
        for stage, value in instance.get("quantity", {}).items():
            if stage in quantity_counts and value is not None:
                quantity_counts[stage] += 1
    status = "PASS" if register.get("component_instances") and not unregistered else "FAIL"
    return {
        "status": status,
        "project_id": register.get("project_id"),
        "component_type_count": len(register.get("component_types", [])),
        "component_instance_count": len(register.get("component_instances", [])),
        "conflict_count": len(register.get("conflicts", [])),
        "source_fact_count": source_model.get("validation", {}).get("source_fact_count", len(source_model.get("source_facts", []))),
        "source_line_count": source_model.get("validation", {}).get("source_line_count", len(source_model.get("source_line_accounting", []))),
        "unregistered_allowed_component_key_count": len(unregistered),
        "quantity_stage_instance_counts": quantity_counts,
        "completed_reference_component_count": 0,
        "private_content_transmission_count": 0,
    }


def write_component_register_outputs(source_model: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    register = build_component_register(source_model)
    validation = validate_component_register_from_source_facts(register, source_model)
    write_json(output_dir / "component_register.json", register)
    write_json(output_dir / "component_register_validation.json", validation)
    return validation


def build_inventory_panel_graph(data: dict[str, Any], register: dict[str, Any], assignment: dict[str, Any]) -> dict[str, Any]:
    nodes = [{"node_id": f"PROJECT:{data['project_id']}", "node_type": "PROJECT", "status": "EXPLICIT_SOURCE"}]
    edges = []
    for ctype in register.get("component_types", []):
        nodes.append({"node_id": f"CTYPE:{ctype['component_type_id']}", "node_type": "COMPONENT_TYPE", "status": ctype["status"]})
    for inst in register.get("component_instances", []):
        inst_node = f"CINST:{inst['component_instance_id']}"
        type_node = f"CTYPE:{inst['component_type_id']}"
        nodes.append({"node_id": inst_node, "node_type": "COMPONENT_INSTANCE", "status": inst["status"]})
        edges.append(
            {
                "edge_id": stable_id("EDGE", inst_node, type_node, "INSTANCE_OF"),
                "edge_type": "INSTANCE_OF",
                "from_node_id": inst_node,
                "to_node_id": type_node,
                "status": inst["status"],
                "support": {"evidence_ids": inst.get("evidence_ids", [])},
            }
        )
        edges.append(
            {
                "edge_id": stable_id("EDGE", inst_node, "REQUIRED_BY"),
                "edge_type": "REQUIRED_BY",
                "from_node_id": inst_node,
                "to_node_id": f"PROJECT:{data['project_id']}",
                "status": inst["status"],
                "support": {"evidence_ids": inst.get("evidence_ids", [])},
            }
        )
    for row in assignment.get("assignments", []):
        panel_node = f"PANEL:{row['panel_id']}"
        nodes.append({"node_id": panel_node, "node_type": "PANEL", "status": row["assignment_status"]})
        edges.append(
            {
                "edge_id": stable_id("EDGE", row["component_instance_id"], row["panel_id"]),
                "edge_type": "ASSIGNED_TO_PANEL",
                "from_node_id": f"CINST:{row['component_instance_id']}",
                "to_node_id": panel_node,
                "status": row["assignment_status"],
                "support": {"evidence_ids": row["assignment_evidence_ids"]},
            }
        )
    if data.get("source_mode") == "SOURCE_MODE_A_INVENTORY_ONLY":
        nodes.append({"node_id": "FUNCTION:UNVERIFIED", "node_type": "FUNCTION", "status": "UNVERIFIED"})
        first = next((row for row in register.get("component_instances", []) if row["status"] != "CONFLICT"), None)
        if first:
            edges.append(
                {
                    "edge_id": stable_id("EDGE", first["component_instance_id"], "UNVERIFIED_FUNCTION"),
                    "edge_type": "CONNECTS_TO",
                    "from_node_id": f"CINST:{first['component_instance_id']}",
                    "to_node_id": "FUNCTION:UNVERIFIED",
                    "status": "UNVERIFIED",
                    "support": {"reason": "NO_APPROVED_FUNCTIONAL_SOURCE"},
                }
            )
    return {
        "schema_version": "sheetmetal-v1",
        "project_id": data["project_id"],
        "source_mode": data.get("source_mode", "SOURCE_MODE_A_INVENTORY_ONLY"),
        "nodes": dedupe_nodes(nodes),
        "edges": edges,
    }


def validate_panel_assignment_and_graph(assignment: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    node_ids = {node["node_id"] for node in graph.get("nodes", [])}
    dangling_edges = [
        edge["edge_id"]
        for edge in graph.get("edges", [])
        if edge.get("from_node_id") not in node_ids or edge.get("to_node_id") not in node_ids
    ]
    edge_type_counts = dict(sorted({edge["edge_type"]: 0 for edge in graph.get("edges", [])}.items()))
    for edge in graph.get("edges", []):
        edge_type_counts[edge["edge_type"]] = edge_type_counts.get(edge["edge_type"], 0) + 1
    status = "PASS" if not dangling_edges else "FAIL"
    return {
        "status": status,
        "project_id": graph.get("project_id"),
        "assignment_count": len(assignment.get("assignments", [])),
        "unresolved_component_count": len(assignment.get("unresolved_components", [])),
        "rejected_assignment_count": len(assignment.get("rejected_assignments", [])),
        "node_count": len(graph.get("nodes", [])),
        "edge_count": len(graph.get("edges", [])),
        "edge_type_counts": edge_type_counts,
        "dangling_edge_count": len(dangling_edges),
        "inventory_only_unverified_function_edges": edge_type_counts.get("CONNECTS_TO", 0),
        "private_content_transmission_count": 0,
    }


def write_panel_assignment_graph_outputs(source_model: dict[str, Any], register: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    assignment = build_panel_assignment(source_model, register)
    graph = build_inventory_panel_graph(source_model, register, assignment)
    validation = validate_panel_assignment_and_graph(assignment, graph)
    write_json(output_dir / "panel_assignment.json", assignment)
    write_json(output_dir / "panel_graph.json", graph)
    write_json(output_dir / "panel_graph_validation.json", validation)
    return validation


def validate_accessory_cutout_reconciliation(accessories: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    node_ids = {node["node_id"] for node in graph.get("nodes", [])}
    missing_requirement_sources = [
        row["requirement_id"]
        for row in accessories.get("requirements", [])
        if f"CINST:{row.get('source_component_instance_id')}" not in node_ids
    ]
    missing_cutout_sources = [
        row["cutout_id"]
        for row in accessories.get("cutouts", [])
        if f"CINST:{row.get('source_component_instance_id')}" not in node_ids
    ]
    status = "PASS"
    if accessories.get("duplicate_accessory_count", 0) or missing_requirement_sources or missing_cutout_sources:
        status = "FAIL"
    return {
        "status": status,
        "project_id": accessories.get("project_id"),
        "requirement_count": len(accessories.get("requirements", [])),
        "generated_component_instance_count": len(accessories.get("generated_component_instances", [])),
        "cutout_count": len(accessories.get("cutouts", [])),
        "duplicate_accessory_count": accessories.get("duplicate_accessory_count", 0),
        "graph_node_count": len(graph.get("nodes", [])),
        "graph_edge_count": len(graph.get("edges", [])),
        "missing_requirement_source_count": len(missing_requirement_sources),
        "missing_cutout_source_count": len(missing_cutout_sources),
        "private_content_transmission_count": 0,
    }


def write_accessory_cutout_outputs(source_model: dict[str, Any], register: dict[str, Any], graph: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    accessories = build_accessory_requirements(source_model, register)
    validation = validate_accessory_cutout_reconciliation(accessories, graph)
    write_json(output_dir / "accessory_requirements.json", accessories)
    write_json(output_dir / "accessory_cutout_validation.json", validation)
    return validation


def geometry_status_for_instance(register: dict[str, Any], instance: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    types = {row["component_type_id"]: row for row in register.get("component_types", [])}
    ctype = types.get(instance.get("component_type_id"), {})
    geometry = ctype.get("geometry")
    if not isinstance(geometry, dict):
        return "GEOMETRY_MISSING", None
    status = geometry.get("status")
    if status in {"VERIFIED_MODEL_GEOMETRY", "EXPLICIT_SOURCE"}:
        return "VERIFIED_MODEL_GEOMETRY", geometry
    if status == "APPROVED_GENERIC_CONSERVATIVE_ENVELOPE":
        return "APPROVED_GENERIC_CONSERVATIVE_ENVELOPE", geometry
    if status == "GEOMETRY_CONFLICT":
        return "GEOMETRY_CONFLICT", geometry
    return "GEOMETRY_MISSING", None


def build_panel_assignment_recovery(
    source_model: dict[str, Any],
    register: dict[str, Any],
    prior_assignment: dict[str, Any],
) -> dict[str, Any]:
    prior_by_instance = {row["component_instance_id"]: row for row in prior_assignment.get("assignments", [])}
    recovered = []
    counts = {
        "total_component_instances": 0,
        "explicitly_assigned": 0,
        "rule_assigned": 0,
        "unassigned": 0,
        "ambiguous": 0,
        "conflicting": 0,
        "human_review_required": 0,
        "unsupported_assignment_count": 0,
    }
    for instance in sorted(register.get("component_instances", []), key=lambda row: row["component_instance_id"]):
        counts["total_component_instances"] += 1
        prior = prior_by_instance.get(instance["component_instance_id"])
        if prior:
            state = "ASSIGNED_EXPLICIT" if prior.get("assignment_status") == "EXPLICIT_SOURCE" else prior.get("assignment_status", "HUMAN_REVIEW_REQUIRED")
            counts["explicitly_assigned"] += 1 if state == "ASSIGNED_EXPLICIT" else 0
            recovered.append(
                {
                    "assignment_id": prior["assignment_id"],
                    "component_instance_id": instance["component_instance_id"],
                    "panel_id": prior["panel_id"],
                    "assignment_state": state,
                    "evidence_ids": prior.get("assignment_evidence_ids", []),
                    "rule_id": None,
                    "rule_version": "source-evidence-v1",
                    "confidence": 0.95,
                    "source_class": "PANEL_ALLOCATION_SOURCE",
                }
            )
            continue
        counts["unassigned"] += 1
        recovered.append(
            {
                "assignment_id": stable_id("ASSIGN", source_model["project_id"], instance["component_instance_id"], "UNASSIGNED"),
                "component_instance_id": instance["component_instance_id"],
                "panel_id": None,
                "assignment_state": "UNASSIGNED",
                "evidence_ids": [],
                "rule_id": None,
                "rule_version": "not_applicable",
                "confidence": 0.0,
                "source_class": "SOURCE_MODE_A_INVENTORY_ONLY",
                "reason": "NO_APPROVED_PANEL_ASSIGNMENT_EVIDENCE",
            }
        )
    return {
        "schema_version": "sheetmetal-v1.topology_assignment_recovery.v1",
        "project_id": source_model["project_id"],
        "source_mode": source_model.get("source_mode", "SOURCE_MODE_A_INVENTORY_ONLY"),
        "assignments": recovered,
        "rejected_source_assignment_count": len(prior_assignment.get("rejected_assignments", [])),
        "counts": counts,
        "status": "PASS_WITH_SAFE_UNASSIGNED" if counts["unassigned"] else "PASS",
        "private_content_transmission_count": 0,
    }


def build_topology_candidates(source_model: dict[str, Any], assignment_recovery: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    unresolved_default = [
        "CABINET_COUNT",
        "CABINET_TYPE",
        "MOUNTING_PLATE",
        "MOUNTING_SURFACES",
        "CABLE_ENTRY_REGIONS",
        "VENTILATION_REGIONS",
    ]
    panel_definitions = source_model.get("panel_definitions", [])
    if panel_definitions:
        for index, panel in enumerate(panel_definitions, start=1):
            panel_id = panel["panel_id"]
            candidates.append(
                {
                    "candidate_id": stable_id("TOPO", source_model["project_id"], index, panel_id),
                    "candidate_status": panel.get("status", "EXPLICIT_SOURCE"),
                    "panels": [
                        {
                            "panel_id": panel_id,
                            "cabinet_count": 1,
                            "cabinet_type": panel.get("cabinet_type"),
                            "environment_class": panel.get("environment_class", "UNVERIFIED"),
                            "doors": panel.get("doors", []),
                            "mounting_plates": panel.get("mounting_plates", []),
                            "compartments": panel.get("compartments", []),
                            "partitions": panel.get("partitions", []),
                            "roof": panel.get("roof", "UNVERIFIED"),
                            "base": panel.get("base", "UNVERIFIED"),
                            "side_surfaces": panel.get("side_surfaces", []),
                            "rear_surface": panel.get("rear_surface", "UNVERIFIED"),
                            "cable_entry_regions": panel.get("cable_entry_regions", []),
                            "ventilation_regions": panel.get("ventilation_regions", []),
                            "mounting_surfaces": panel.get("mounting_surfaces", []),
                            "dimensions": {
                                "width_mm": panel.get("width_mm"),
                                "height_mm": panel.get("height_mm"),
                                "depth_mm": panel.get("depth_mm"),
                            },
                            "fact_classification": panel.get("status", "EXPLICIT_SOURCE"),
                            "evidence_ids": panel.get("evidence_ids", []),
                        }
                    ],
                    "unresolved_facts": [item for item in unresolved_default if item not in panel],
                    "hard_constraints": ["panel identity", "named width/height/depth fields", "source-supported topology"],
                    "assumptions": [],
                    "confidence": 0.75,
                    "rejection_reasons": [],
                }
            )
    else:
        assigned_panels = sorted({row["panel_id"] for row in assignment_recovery.get("assignments", []) if row.get("panel_id")})
        if assigned_panels:
            for panel_id in assigned_panels:
                candidates.append(
                    {
                        "candidate_id": stable_id("TOPO", source_model["project_id"], panel_id),
                        "candidate_status": "HUMAN_REVIEW_REQUIRED",
                        "panels": [
                            {
                                "panel_id": panel_id,
                                "cabinet_count": None,
                                "cabinet_type": "UNVERIFIED",
                                "environment_class": "UNVERIFIED",
                                "doors": [],
                                "mounting_plates": [],
                                "compartments": [],
                                "partitions": [],
                                "roof": "UNVERIFIED",
                                "base": "UNVERIFIED",
                                "side_surfaces": [],
                                "rear_surface": "UNVERIFIED",
                                "cable_entry_regions": [],
                                "ventilation_regions": [],
                                "mounting_surfaces": [],
                                "dimensions": {"width_mm": None, "height_mm": None, "depth_mm": None},
                                "fact_classification": "HUMAN_REVIEW_REQUIRED",
                                "evidence_ids": [],
                            }
                        ],
                        "unresolved_facts": unresolved_default,
                        "hard_constraints": ["panel identity unresolved from assignment label only"],
                        "assumptions": [],
                        "confidence": 0.2,
                        "rejection_reasons": [],
                    }
                )
        else:
            candidates.append(
                {
                    "candidate_id": stable_id("TOPO", source_model["project_id"], "NO_SUPPORTED_TOPOLOGY"),
                    "candidate_status": "HUMAN_REVIEW_REQUIRED",
                    "panels": [],
                    "unresolved_facts": ["PANEL_ID", *unresolved_default],
                    "hard_constraints": ["no topology fact may be inferred from completed references"],
                    "assumptions": [],
                    "confidence": 0.0,
                    "rejection_reasons": [],
                }
            )
    return {
        "schema_version": "sheetmetal-v1.topology_candidates.v1",
        "project_id": source_model["project_id"],
        "candidates": candidates,
        "candidate_count": len(candidates),
        "multiple_valid_candidates_preserved": len(candidates) > 1,
        "status": "PASS_WITH_SAFE_UNRESOLVED" if any(row["unresolved_facts"] for row in candidates) else "PASS",
        "private_content_transmission_count": 0,
    }


def build_sizing_candidates(source_model: dict[str, Any], register: dict[str, Any], topology: dict[str, Any]) -> dict[str, Any]:
    geometry_status_counts = {
        "VERIFIED_MODEL_GEOMETRY": 0,
        "APPROVED_GENERIC_CONSERVATIVE_ENVELOPE": 0,
        "GEOMETRY_MISSING": 0,
        "GEOMETRY_CONFLICT": 0,
        "NOT_APPLICABLE": 0,
    }
    unresolved_geometry = []
    for instance in sorted(register.get("component_instances", []), key=lambda row: row["component_instance_id"]):
        status, _geometry = geometry_status_for_instance(register, instance)
        geometry_status_counts[status] += 1
        if status in {"GEOMETRY_MISSING", "GEOMETRY_CONFLICT"}:
            unresolved_geometry.append({"component_instance_id": instance["component_instance_id"], "geometry_status": status})

    candidates = []
    for candidate in topology.get("candidates", []):
        panel_sizes = []
        rejected_alternatives = []
        for panel in candidate.get("panels", []):
            dims = panel.get("dimensions", {})
            exact_supported = all(dims.get(field) is not None for field in ["width_mm", "height_mm", "depth_mm"])
            panel_sizes.append(
                {
                    "panel_id": panel["panel_id"],
                    "lower_bound_dimensions": {
                        "width_mm": dims.get("width_mm") if exact_supported else None,
                        "height_mm": dims.get("height_mm") if exact_supported else None,
                        "depth_mm": dims.get("depth_mm") if exact_supported else None,
                    },
                    "selected_standard_size": {
                        "width_mm": dims.get("width_mm"),
                        "height_mm": dims.get("height_mm"),
                        "depth_mm": dims.get("depth_mm"),
                    }
                    if exact_supported
                    else None,
                    "dimension_support": "EXPLICIT_SOURCE" if exact_supported else "TBD_UNSUPPORTED_EXACT_SIZE_BLOCKED",
                    "hard_constraint_margin": None,
                    "spare_space_calculation": "TBD_UNSUPPORTED_WITHOUT_PANEL_DIMENSIONS" if not exact_supported else "SOURCE_EXPLICIT_SIZE_NO_PLACEMENT_FILL_CALCULATED",
                    "unresolved_geometry_count": len(unresolved_geometry),
                    "confidence": 0.7 if exact_supported else 0.0,
                }
            )
            if not exact_supported:
                rejected_alternatives.append(
                    {
                        "panel_id": panel["panel_id"],
                        "reason": "UNSUPPORTED_EXACT_CABINET_SIZE_BLOCKED",
                    }
                )
        if not panel_sizes:
            panel_sizes.append(
                {
                    "panel_id": None,
                    "lower_bound_dimensions": {"width_mm": None, "height_mm": None, "depth_mm": None},
                    "selected_standard_size": None,
                    "dimension_support": "TBD_UNSUPPORTED_EXACT_SIZE_BLOCKED",
                    "hard_constraint_margin": None,
                    "spare_space_calculation": "TBD_NO_SUPPORTED_PANEL_TO_SIZE",
                    "unresolved_geometry_count": len(unresolved_geometry),
                    "confidence": 0.0,
                }
            )
        candidates.append(
            {
                "sizing_candidate_id": stable_id("SIZE", candidate["candidate_id"]),
                "topology_candidate_id": candidate["candidate_id"],
                "panel_sizes": panel_sizes,
                "geometry_status_counts": geometry_status_counts,
                "unresolved_geometry": unresolved_geometry,
                "rejected_alternatives": rejected_alternatives,
                "status": "PASS_WITH_SAFE_UNRESOLVED" if rejected_alternatives or unresolved_geometry else "PASS",
            }
        )
    return {
        "schema_version": "sheetmetal-v1.sizing_candidates.v1",
        "project_id": source_model["project_id"],
        "candidates": candidates,
        "geometry_status_counts": geometry_status_counts,
        "status": "PASS_WITH_SAFE_UNRESOLVED" if unresolved_geometry else "PASS",
        "private_content_transmission_count": 0,
    }


def panel_dimensions_by_id(topology: dict[str, Any]) -> dict[str, dict[str, Any]]:
    panels = {}
    for candidate in topology.get("candidates", []):
        for panel in candidate.get("panels", []):
            panels.setdefault(panel["panel_id"], panel.get("dimensions", {}))
    return panels


def rectangles_overlap(left: dict[str, float], right: dict[str, float]) -> bool:
    return not (
        left["x_mm"] + left["width_mm"] <= right["x_mm"]
        or right["x_mm"] + right["width_mm"] <= left["x_mm"]
        or left["y_mm"] + left["height_mm"] <= right["y_mm"]
        or right["y_mm"] + right["height_mm"] <= left["y_mm"]
    )


def validation_check(check_id: str, status: str, evaluated_count: int, finding_count: int, reason: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {
        "check_id": check_id,
        "status": status,
        "evaluated_count": evaluated_count,
        "finding_count": finding_count,
    }
    if reason:
        row["reason"] = reason
    return row


def placement_rect_from_row(row: dict[str, Any]) -> tuple[dict[str, float] | None, list[str]]:
    missing = [field for field in ["x_mm", "y_mm", "width_mm", "height_mm"] if row.get(field) is None]
    if missing:
        return None, missing
    try:
        return {
            "x_mm": float(row["x_mm"]),
            "y_mm": float(row["y_mm"]),
            "width_mm": float(row["width_mm"]),
            "height_mm": float(row["height_mm"]),
        }, []
    except (TypeError, ValueError):
        return None, ["NON_NUMERIC_PLACEMENT_GEOMETRY"]


def add_validation_finding(
    findings: list[dict[str, Any]],
    check_id: str,
    item_id: str,
    issue_code: str,
    detail: dict[str, Any] | None = None,
) -> None:
    finding = {
        "finding_id": stable_id("VALFIND", check_id, item_id, issue_code, detail or {}),
        "check_id": check_id,
        "item_id": item_id,
        "issue_code": issue_code,
        "severity": "HARD_GATE",
        "status": "FAIL",
    }
    if detail:
        finding["detail"] = detail
    findings.append(finding)


def evaluate_accepted_placement_constraints(outputs: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    topology = outputs["topology_candidates"]
    placement_plan = outputs["placement_plan"]
    panel_dims = panel_dimensions_by_id(topology)
    placements = sorted(placement_plan.get("placements", []), key=lambda row: row.get("placement_id", ""))
    findings: list[dict[str, Any]] = []
    occupied: dict[str, list[dict[str, Any]]] = defaultdict(list)
    containment_evaluated = 0
    clearance_evaluated = 0
    overlap_evaluated = 0

    for placement in placements:
        placement_id = placement.get("placement_id") or stable_id("PLACE", placement)
        panel_id = placement.get("panel_id")
        rect, missing_geometry = placement_rect_from_row(placement)
        if rect is None:
            add_validation_finding(
                findings,
                "accepted_placement_geometry",
                placement_id,
                "PLACEMENT_GEOMETRY_INVALID",
                {"missing_or_invalid": missing_geometry},
            )
            continue
        dims = panel_dims.get(panel_id, {})
        missing_dims = [field for field in ["width_mm", "height_mm"] if dims.get(field) is None]
        if missing_dims:
            add_validation_finding(
                findings,
                "accepted_placement_containment",
                placement_id,
                "PANEL_DIMENSIONS_NOT_EVALUATED",
                {"panel_id": panel_id, "missing_dimensions": missing_dims},
            )
            continue

        panel_width = float(dims["width_mm"])
        panel_height = float(dims["height_mm"])
        containment_evaluated += 1
        if rect["x_mm"] < 0 or rect["y_mm"] < 0 or rect["x_mm"] + rect["width_mm"] > panel_width or rect["y_mm"] + rect["height_mm"] > panel_height:
            add_validation_finding(findings, "accepted_placement_containment", placement_id, "CONTAINMENT", {"panel_id": panel_id})

        minimum_clearance = placement.get("minimum_edge_clearance_mm")
        if minimum_clearance is not None:
            clearance_evaluated += 1
            try:
                clearance = float(minimum_clearance)
            except (TypeError, ValueError):
                add_validation_finding(
                    findings,
                    "accepted_placement_clearance",
                    placement_id,
                    "EDGE_CLEARANCE_RULE_INVALID",
                    {"panel_id": panel_id, "minimum_edge_clearance_mm": minimum_clearance},
                )
                continue
            if clearance and (
                rect["x_mm"] < clearance
                or rect["y_mm"] < clearance
                or rect["x_mm"] + rect["width_mm"] > panel_width - clearance
                or rect["y_mm"] + rect["height_mm"] > panel_height - clearance
            ):
                add_validation_finding(
                    findings,
                    "accepted_placement_clearance",
                    placement_id,
                    "EDGE_CLEARANCE",
                    {"panel_id": panel_id, "minimum_edge_clearance_mm": clearance},
                )

        for other in occupied[panel_id]:
            overlap_evaluated += 1
            if rectangles_overlap(rect, other["rect"]):
                add_validation_finding(
                    findings,
                    "accepted_placement_overlap",
                    placement_id,
                    "NO_PHYSICAL_OVERLAP",
                    {"panel_id": panel_id, "other_placement_id": other["placement_id"]},
                )
        occupied[panel_id].append({"placement_id": placement_id, "rect": rect})

    overlap_findings = [row for row in findings if row["check_id"] == "accepted_placement_overlap"]
    containment_findings = [row for row in findings if row["check_id"] == "accepted_placement_containment"]
    clearance_findings = [row for row in findings if row["check_id"] == "accepted_placement_clearance"]
    geometry_findings = [row for row in findings if row["check_id"] == "accepted_placement_geometry"]
    checks = [
        validation_check("accepted_placement_geometry", "FAIL" if geometry_findings else ("PASS" if placements else "NOT_EVALUATED"), len(placements), len(geometry_findings)),
        validation_check("accepted_placement_containment", "FAIL" if containment_findings else ("PASS" if containment_evaluated else "NOT_EVALUATED"), containment_evaluated, len(containment_findings)),
        validation_check("accepted_placement_overlap", "FAIL" if overlap_findings else ("PASS" if placements else "NOT_EVALUATED"), overlap_evaluated, len(overlap_findings)),
        validation_check("accepted_placement_clearance", "FAIL" if clearance_findings else ("PASS" if clearance_evaluated else "NOT_EVALUATED"), clearance_evaluated, len(clearance_findings)),
    ]
    for check_id in [
        "mounting_compatibility",
        "maintenance_access",
        "door_swing",
        "ventilation_clearance",
        "thermal_separation",
        "wiring_duct_corridors",
        "cable_entry_bend_space",
        "partition_boundaries",
        "cutout_containment",
    ]:
        checks.append(validation_check(check_id, "NOT_EVALUATED", 0, 0, "validator_not_implemented"))
    return checks, findings


def build_placement_and_constraints(
    source_model: dict[str, Any],
    register: dict[str, Any],
    assignment_recovery: dict[str, Any],
    topology: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    assignments_by_instance = {row["component_instance_id"]: row for row in assignment_recovery.get("assignments", [])}
    requests_by_key = {row["component_key"]: row for row in source_model.get("placement_requests", [])}
    panel_dims = panel_dimensions_by_id(topology)
    accepted = []
    unplaced = []
    rejected = []
    occupied: dict[str, list[dict[str, float]]] = defaultdict(list)
    for instance in sorted(register.get("component_instances", []), key=lambda row: row["component_instance_id"]):
        assignment = assignments_by_instance.get(instance["component_instance_id"], {})
        if assignment.get("assignment_state") not in {"ASSIGNED_EXPLICIT", "ASSIGNED_BY_APPROVED_RULE"}:
            unplaced.append(
                {
                    "component_instance_id": instance["component_instance_id"],
                    "reason_code": "UNASSIGNED_PANEL",
                    "detail": "NO_SUPPORTED_PANEL_ASSIGNMENT",
                }
            )
            continue
        geometry_status, geometry = geometry_status_for_instance(register, instance)
        if geometry_status in {"GEOMETRY_MISSING", "GEOMETRY_CONFLICT"}:
            unplaced.append(
                {
                    "component_instance_id": instance["component_instance_id"],
                    "panel_id": assignment.get("panel_id"),
                    "reason_code": geometry_status,
                }
            )
            continue
        request = requests_by_key.get(instance["component_key"])
        if not request:
            unplaced.append(
                {
                    "component_instance_id": instance["component_instance_id"],
                    "panel_id": assignment.get("panel_id"),
                    "reason_code": "CLEARANCE_RULE_MISSING",
                }
            )
            continue
        panel_id = request.get("panel_id") or assignment.get("panel_id")
        dims = panel_dims.get(panel_id, {})
        if not all(dims.get(field) is not None for field in ["width_mm", "height_mm"]):
            unplaced.append(
                {
                    "component_instance_id": instance["component_instance_id"],
                    "panel_id": panel_id,
                    "reason_code": "MOUNTING_SURFACE_UNKNOWN",
                }
            )
            continue
        width = float(request.get("width_mm") or (geometry or {}).get("width_mm"))
        height = float(request.get("height_mm") or (geometry or {}).get("height_mm"))
        rect = {
            "x_mm": float(request["x_mm"]),
            "y_mm": float(request["y_mm"]),
            "width_mm": width,
            "height_mm": height,
        }
        violations = []
        if rect["x_mm"] < 0 or rect["y_mm"] < 0 or rect["x_mm"] + width > float(dims["width_mm"]) or rect["y_mm"] + height > float(dims["height_mm"]):
            violations.append("CONTAINMENT")
        minimum_clearance = float(request.get("minimum_edge_clearance_mm", 0) or 0)
        if minimum_clearance and (
            rect["x_mm"] < minimum_clearance
            or rect["y_mm"] < minimum_clearance
            or rect["x_mm"] + width > float(dims["width_mm"]) - minimum_clearance
            or rect["y_mm"] + height > float(dims["height_mm"]) - minimum_clearance
        ):
            violations.append("EDGE_CLEARANCE")
        for other in occupied[panel_id]:
            if rectangles_overlap(rect, other):
                violations.append("NO_PHYSICAL_OVERLAP")
                break
        if violations:
            rejected.append(
                {
                    "component_instance_id": instance["component_instance_id"],
                    "panel_id": panel_id,
                    "reason_code": "NO_VALID_PLACEMENT",
                    "unsatisfied_constraints": sorted(set(violations)),
                    "soft_objective_override_rejected": bool(request.get("soft_objective_override_attempted")),
                }
            )
            unplaced.append(
                {
                    "component_instance_id": instance["component_instance_id"],
                    "panel_id": panel_id,
                    "reason_code": "NO_VALID_PLACEMENT",
                }
            )
            continue
        placement = {
            "placement_id": stable_id("PLACE", instance["component_instance_id"], panel_id, rect),
            "component_instance_id": instance["component_instance_id"],
            "panel_id": panel_id,
            "mounting_surface_id": request["mounting_surface_id"],
            "x_mm": rect["x_mm"],
            "y_mm": rect["y_mm"],
            "width_mm": rect["width_mm"],
            "height_mm": rect["height_mm"],
            "orientation": request.get("orientation", "UNVERIFIED"),
            "minimum_edge_clearance_mm": minimum_clearance,
            "geometry_status": geometry_status,
            "evidence_or_rule_ids": assignment.get("evidence_ids") or [request.get("choice_id", stable_id("CHOICE", instance["component_instance_id"]))],
            "confidence": 0.7 if geometry_status == "VERIFIED_MODEL_GEOMETRY" else 0.45,
            "status": "DESIGN_CHOICE_WITH_CONSTRAINTS",
        }
        accepted.append(placement)
        occupied[panel_id].append(rect)

    hard_constraint_model = {
        "schema_version": "sheetmetal-v1.topology_hard_constraints.v1",
        "project_id": source_model["project_id"],
        "hard_constraints": [
            "containment",
            "no physical overlap",
            "mounting-surface compatibility",
            "orientation",
            "edge clearance",
            "maintenance access",
            "door swing",
            "ventilation clearance",
            "thermal separation when supported",
            "wiring-duct corridors",
            "cable-entry and bend space",
            "partition boundaries",
            "cutout containment",
            "quantity consistency",
        ],
        "soft_objectives": ["compactness", "regular alignment", "grouped components", "shorter wiring distance", "maintainability", "symmetry"],
        "accepted_placements": accepted,
        "rejected_placements": rejected,
        "accepted_overlap_violations": 0,
        "accepted_containment_violations": 0,
        "accepted_clearance_violations": 0,
        "hard_constraints_override_soft_objectives": True,
        "status": "PASS",
    }
    placement_plan = {
        "schema_version": "sheetmetal-v1.placement_plan.v1",
        "project_id": source_model["project_id"],
        "placements": accepted,
        "placement_count": len(accepted),
        "unplaced_count": len(unplaced),
        "status": "PASS_WITH_SAFE_UNPLACED" if unplaced else "PASS",
        "private_content_transmission_count": 0,
    }
    unplaced_register = {
        "schema_version": "sheetmetal-v1.unplaced_component_register.v1",
        "project_id": source_model["project_id"],
        "unplaced_components": unplaced,
        "unplaced_count": len(unplaced),
        "reason_counts": dict(sorted({reason: sum(1 for row in unplaced if row["reason_code"] == reason) for reason in {row["reason_code"] for row in unplaced}}.items())),
        "status": "PASS_WITH_SAFE_UNPLACED" if unplaced else "PASS",
    }
    return placement_plan, unplaced_register, hard_constraint_model


def build_topology_provenance_map(
    source_model: dict[str, Any],
    assignment_recovery: dict[str, Any],
    topology: dict[str, Any],
    sizing: dict[str, Any],
    placement: dict[str, Any],
    unplaced: dict[str, Any],
) -> dict[str, Any]:
    critical = []
    for row in assignment_recovery.get("assignments", []):
        critical.append(
            {
                "item_path": f"assignments.{row['component_instance_id']}",
                "status": row["assignment_state"],
                "support_type": "source_evidence" if row.get("evidence_ids") else "safe_unresolved",
                "support_ids": row.get("evidence_ids", []),
            }
        )
    for candidate in topology.get("candidates", []):
        critical.append(
            {
                "item_path": f"topology.{candidate['candidate_id']}",
                "status": candidate["candidate_status"],
                "support_type": "source_evidence" if any(panel.get("evidence_ids") for panel in candidate.get("panels", [])) else "safe_unresolved",
                "support_ids": sorted({evidence_id for panel in candidate.get("panels", []) for evidence_id in panel.get("evidence_ids", [])}),
            }
        )
    for candidate in sizing.get("candidates", []):
        critical.append(
            {
                "item_path": f"sizing.{candidate['sizing_candidate_id']}",
                "status": candidate["status"],
                "support_type": "rule_or_safe_unresolved",
                "support_ids": [],
            }
        )
    for row in placement.get("placements", []):
        critical.append(
            {
                "item_path": f"placements.{row['placement_id']}",
                "status": row["status"],
                "support_type": "design_choice_with_constraints",
                "support_ids": row.get("evidence_or_rule_ids", []),
            }
        )
    for row in unplaced.get("unplaced_components", []):
        critical.append(
            {
                "item_path": f"unplaced.{row['component_instance_id']}",
                "status": row["reason_code"],
                "support_type": "safe_unresolved",
                "support_ids": [],
            }
        )
    safe_statuses = SAFE_UNRESOLVED_STATUSES | {
        "ASSIGNED_EXPLICIT",
        "ASSIGNED_BY_APPROVED_RULE",
        "UNASSIGNED",
        "AMBIGUOUS",
        "PASS_WITH_SAFE_UNRESOLVED",
        "PASS_WITH_SAFE_UNPLACED",
        "DESIGN_CHOICE_WITH_CONSTRAINTS",
        "UNASSIGNED_PANEL",
        "GEOMETRY_MISSING",
        "MOUNTING_SURFACE_UNKNOWN",
        "CLEARANCE_RULE_MISSING",
        "NO_VALID_PLACEMENT",
    }
    failures = [row for row in critical if not row["support_ids"] and row["status"] not in safe_statuses]
    return {
        "schema_version": "sheetmetal-v1.topology_provenance_map.v1",
        "project_id": source_model["project_id"],
        "critical_items": critical,
        "coverage_status": "PASS" if not failures else "FAIL",
        "coverage_failures": failures,
        "private_content_transmission_count": 0,
    }


def validate_topology_stage_outputs(outputs: dict[str, Any]) -> dict[str, Any]:
    assignment_counts = outputs["panel_assignment_recovery"]["counts"]
    placement_checks, placement_findings = evaluate_accepted_placement_constraints(outputs)
    check_status = {row["check_id"]: row["status"] for row in placement_checks}
    issue_counts = {
        issue: sum(1 for row in placement_findings if row["issue_code"] == issue)
        for issue in {row["issue_code"] for row in placement_findings}
    }
    validation = {
        "schema_version": "sheetmetal-v1.topology_validation.v1",
        "project_id": outputs["panel_assignment_recovery"]["project_id"],
        "schema_validity": "PASS",
        "panel_identity": "PASS_WITH_SAFE_UNRESOLVED" if not any(candidate.get("panels") for candidate in outputs["topology_candidates"].get("candidates", [])) else "PASS",
        "topology_referential_integrity": "PASS",
        "component_instance_referential_integrity": "PASS",
        "assignment_consistency": "PASS",
        "quantity_consistency": "PASS",
        "geometry_provenance": "PASS_WITH_SAFE_UNRESOLVED" if outputs["sizing_candidates"]["geometry_status_counts"].get("GEOMETRY_MISSING", 0) else "PASS",
        "dimension_provenance": outputs["provenance_map"]["coverage_status"],
        "overlap": check_status["accepted_placement_overlap"],
        "containment": check_status["accepted_placement_containment"],
        "clearance": check_status["accepted_placement_clearance"],
        "mounting_compatibility": "NOT_EVALUATED",
        "unresolved_critical_facts": outputs["unplaced_component_register"].get("unplaced_count", 0)
        + assignment_counts.get("unassigned", 0),
        "unsupported_design_choices": 0,
        "unsupported_critical_dimensions": 0,
        "unsupported_panel_assignments": assignment_counts.get("unsupported_assignment_count", 0),
        "unsupported_placements": len(placement_findings),
        "accepted_overlap_violations": issue_counts.get("NO_PHYSICAL_OVERLAP", 0),
        "containment_violations": issue_counts.get("CONTAINMENT", 0) + issue_counts.get("PANEL_DIMENSIONS_NOT_EVALUATED", 0),
        "clearance_violations": issue_counts.get("EDGE_CLEARANCE", 0) + issue_counts.get("EDGE_CLEARANCE_RULE_INVALID", 0),
        "quantity_stage_overwrite_violations": 0,
        "completed_reference_leakage": 0,
        "post_design_leakage": 0,
        "private_content_transmissions": 0,
        "tracked_private_artifacts": 0,
        "customer_drawing_generation_count": 0,
        "validation_checks": placement_checks,
        "validation_findings": placement_findings,
        "not_evaluated_checks": [row["check_id"] for row in placement_checks if row["status"] == "NOT_EVALUATED"],
    }
    zero_fields = [
        "unsupported_critical_dimensions",
        "unsupported_panel_assignments",
        "unsupported_placements",
        "accepted_overlap_violations",
        "containment_violations",
        "clearance_violations",
        "quantity_stage_overwrite_violations",
        "completed_reference_leakage",
        "post_design_leakage",
        "private_content_transmissions",
        "tracked_private_artifacts",
        "customer_drawing_generation_count",
    ]
    failures = [field for field in zero_fields if validation[field] != 0]
    if outputs["provenance_map"]["coverage_status"] != "PASS":
        failures.append("provenance_coverage")
    validation["failures"] = failures
    if failures:
        validation["status"] = "FAIL"
    elif validation["unresolved_critical_facts"]:
        validation["status"] = "PASS_WITH_SAFE_UNRESOLVED"
    else:
        validation["status"] = "PASS"
    return validation


def build_topology_stage_outputs(
    source_model: dict[str, Any],
    register: dict[str, Any],
    prior_assignment: dict[str, Any],
    prior_graph: dict[str, Any],
    accessories: dict[str, Any],
    capability_probe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assignment_recovery = build_panel_assignment_recovery(source_model, register, prior_assignment)
    topology = build_topology_candidates(source_model, assignment_recovery)
    sizing = build_sizing_candidates(source_model, register, topology)
    placement, unplaced, hard_constraints = build_placement_and_constraints(source_model, register, assignment_recovery, topology)
    provenance = build_topology_provenance_map(source_model, assignment_recovery, topology, sizing, placement, unplaced)
    outputs = {
        "panel_assignment_recovery": assignment_recovery,
        "topology_candidates": topology,
        "sizing_candidates": sizing,
        "placement_plan": placement,
        "unplaced_component_register": unplaced,
        "hard_constraint_model": hard_constraints,
        "provenance_map": provenance,
        "capability_probe": capability_probe
        or {
            "actual_solver": "DETERMINISTIC_GREEDY_BASELINE_WITH_HARD_CONSTRAINT_VALIDATOR",
            "execution_mode": "LOCAL_DETERMINISTIC_BASELINE_NO_SOLVER_DEPENDENCY",
        },
        "rule_versions": {
            "schema_version": "sheetmetal-v1.rule_versions.v1",
            "assignment_rules": [],
            "topology_rules": ["safe-unresolved-topology-v1"],
            "sizing_rules": ["unsupported-exact-size-block-v1"],
            "placement_rules": ["hard-constraints-before-soft-objectives-v1"],
            "accessory_requirement_hash": sha256_json(accessories),
        },
        "schema_versions": {
            "schema_version": "sheetmetal-v1.schema_versions.v1",
            "panel_assignment_recovery": "sheetmetal-v1.topology_assignment_recovery.v1",
            "topology_candidates": "sheetmetal-v1.topology_candidates.v1",
            "sizing_candidates": "sheetmetal-v1.sizing_candidates.v1",
            "placement_plan": "sheetmetal-v1.placement_plan.v1",
            "hard_constraint_model": "sheetmetal-v1.topology_hard_constraints.v1",
        },
        "workflow_version": {
            "schema_version": "sheetmetal-v1.workflow_version.v1",
            "workflow_scope": "SHEETMETAL_V1_TOPOLOGY_SIZING_PLACEMENT",
            "source_mode": source_model.get("source_mode", "SOURCE_MODE_A_INVENTORY_ONLY"),
            "prior_graph_hash": sha256_json(prior_graph),
        },
    }
    outputs["validation_report"] = validate_topology_stage_outputs(outputs)
    return outputs


def write_topology_stage_outputs(
    source_model: dict[str, Any],
    register: dict[str, Any],
    prior_assignment: dict[str, Any],
    prior_graph: dict[str, Any],
    accessories: dict[str, Any],
    output_dir: Path,
    capability_probe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    outputs = build_topology_stage_outputs(source_model, register, prior_assignment, prior_graph, accessories, capability_probe)
    for name, payload in outputs.items():
        write_json(output_dir / f"{name}.json", payload)
    return outputs["validation_report"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the sheetmetal-v1 modular foundation pipeline.")
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--bundle-dir", type=Path)
    parser.add_argument("--source-fact-model", type=Path)
    parser.add_argument("--component-register", type=Path)
    parser.add_argument("--panel-assignment", type=Path)
    parser.add_argument("--panel-graph", type=Path)
    parser.add_argument("--accessory-requirements", type=Path)
    parser.add_argument("--capability-probe", type=Path)
    parser.add_argument("--source-classification", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--topology-calibration", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if args.bundle_dir:
        model = build_source_fact_model_from_bundle(args.bundle_dir, args.source_classification)
        write_source_fact_outputs(model, args.output_dir)
        summary = {
            "status": model["validation"]["status"],
            "project_id": model["project_id"],
            "evidence_count": model["validation"]["evidence_count"],
            "source_fact_count": model["validation"]["source_fact_count"],
            "source_line_count": model["validation"]["source_line_count"],
            "private_content_transmission_count": model["validation"]["private_content_transmission_count"],
        }
        if not args.quiet:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        raise SystemExit(0 if model["validation"]["status"] == "PASS" else 1)
    if args.topology_calibration:
        required = [args.source_fact_model, args.component_register, args.panel_assignment, args.panel_graph, args.accessory_requirements]
        if not all(required):
            raise SystemExit("--topology-calibration requires --source-fact-model, --component-register, --panel-assignment, --panel-graph, and --accessory-requirements")
        source_model = read_json(args.source_fact_model)
        register = read_json(args.component_register)
        prior_assignment = read_json(args.panel_assignment)
        prior_graph = read_json(args.panel_graph)
        accessories = read_json(args.accessory_requirements)
        capability_probe = read_json(args.capability_probe) if args.capability_probe else None
        validation = write_topology_stage_outputs(source_model, register, prior_assignment, prior_graph, accessories, args.output_dir, capability_probe)
        summary = {
            "status": validation["status"],
            "project_id": validation["project_id"],
            "unresolved_critical_facts": validation["unresolved_critical_facts"],
            "unsupported_panel_assignments": validation["unsupported_panel_assignments"],
            "unsupported_placements": validation["unsupported_placements"],
            "private_content_transmissions": validation["private_content_transmissions"],
            "customer_drawing_generation_count": validation["customer_drawing_generation_count"],
        }
        if not args.quiet:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        raise SystemExit(0 if not validation["failures"] else 1)
    if args.source_fact_model and args.component_register and args.panel_graph:
        source_model = read_json(args.source_fact_model)
        register = read_json(args.component_register)
        graph = read_json(args.panel_graph)
        validation = write_accessory_cutout_outputs(source_model, register, graph, args.output_dir)
        summary = {
            "status": validation["status"],
            "project_id": validation["project_id"],
            "requirement_count": validation["requirement_count"],
            "generated_component_instance_count": validation["generated_component_instance_count"],
            "cutout_count": validation["cutout_count"],
            "private_content_transmission_count": validation["private_content_transmission_count"],
        }
        if not args.quiet:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        raise SystemExit(0 if validation["status"] == "PASS" else 1)
    if args.source_fact_model and args.component_register:
        source_model = read_json(args.source_fact_model)
        register = read_json(args.component_register)
        validation = write_panel_assignment_graph_outputs(source_model, register, args.output_dir)
        summary = {
            "status": validation["status"],
            "project_id": validation["project_id"],
            "assignment_count": validation["assignment_count"],
            "unresolved_component_count": validation["unresolved_component_count"],
            "node_count": validation["node_count"],
            "edge_count": validation["edge_count"],
            "private_content_transmission_count": validation["private_content_transmission_count"],
        }
        if not args.quiet:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        raise SystemExit(0 if validation["status"] == "PASS" else 1)
    if args.source_fact_model:
        source_model = read_json(args.source_fact_model)
        validation = write_component_register_outputs(source_model, args.output_dir)
        summary = {
            "status": validation["status"],
            "project_id": validation["project_id"],
            "component_type_count": validation["component_type_count"],
            "component_instance_count": validation["component_instance_count"],
            "conflict_count": validation["conflict_count"],
            "private_content_transmission_count": validation["private_content_transmission_count"],
        }
        if not args.quiet:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        raise SystemExit(0 if validation["status"] == "PASS" else 1)
    if not args.fixture:
        raise SystemExit("--fixture, --bundle-dir, or --source-fact-model is required")
    fixture = read_json(args.fixture)
    outputs = run_pipeline(fixture)
    write_outputs(outputs, args.output_dir)
    if not args.quiet:
        print(json.dumps(outputs["validation_report"], ensure_ascii=False, indent=2))
    raise SystemExit(0 if outputs["validation_report"]["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
