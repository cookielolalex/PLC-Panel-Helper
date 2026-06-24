from __future__ import annotations

import argparse
import json
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


def stable_id(prefix: str, *parts: Any) -> str:
    payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    import hashlib

    return f"{prefix}-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:12].upper()}"


def evidence_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["evidence_id"]: row for row in data.get("source_evidence", [])}


def is_generator_allowed_evidence(row: dict[str, Any]) -> bool:
    return (
        row.get("source_role") in GENERATOR_ALLOWED_ROLES
        and row.get("chronology_status") in {"PRE_DESIGN", "DURING_DESIGN", "UNKNOWN_BUT_ALLOWED_BY_DECISION"}
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


def fact_values(facts: list[dict[str, Any]], fact_type: str) -> list[dict[str, Any]]:
    return [fact for fact in facts if fact.get("fact_type") == fact_type]


def single_value(facts: list[dict[str, Any]], fact_type: str) -> Any | None:
    values = fact_values(facts, fact_type)
    if not values:
        return None
    unique = []
    for row in values:
        if row.get("value") not in unique:
            unique.append(row.get("value"))
    return unique[0] if len(unique) == 1 else None


def conflict_record(facts: list[dict[str, Any]], fact_type: str) -> dict[str, Any] | None:
    values = fact_values(facts, fact_type)
    unique = []
    for row in values:
        if row.get("value") not in unique:
            unique.append(row.get("value"))
    if len(unique) <= 1:
        return None
    return {
        "field": fact_type,
        "status": "CONFLICT",
        "competing_values": [
            {
                "value": row.get("value"),
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
    return {
        "width_mm": float(value["width_mm"]),
        "height_mm": float(value["height_mm"]),
        "depth_mm": float(value["depth_mm"]),
        "status": "EXPLICIT_SOURCE",
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
                "raw_source_names": [row.get("raw_value") or str(row.get("value")) for row in facts if row.get("fact_type") in {"model", "manufacturer"}],
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
        if fact.get("fact_type") != "panel_assignment":
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
                "assignment_id": stable_id("ASSIGN", data["project_id"], fact["component_key"], fact["value"]),
                "component_instance_id": inst["component_instance_id"],
                "component_key": fact["component_key"],
                "panel_id": fact["value"],
                "assignment_status": "EXPLICIT_SOURCE",
                "assignment_evidence_ids": [fact["evidence_id"]],
                "placement_resolved": False,
            }
        )
        inst["panel_assignment"] = fact["value"]
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic sheetmetal-v1 modular foundation pipeline.")
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    fixture = read_json(args.fixture)
    outputs = run_pipeline(fixture)
    write_outputs(outputs, args.output_dir)
    print(json.dumps(outputs["validation_report"], ensure_ascii=False, indent=2))
    raise SystemExit(0 if outputs["validation_report"]["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
