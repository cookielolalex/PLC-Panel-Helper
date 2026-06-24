# SMV1 Source/Rule Authority Decision Packet

Status: `DECISION_PACKET_PREPARED_HUMAN_AUTHORITY_REQUIRED`

Task ID: `SMV1-SOURCE-RULE-AUTHORITY-DECISION-PACKET`

Recommended next action: `REQUEST_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION`

## Purpose

This packet converts the independently reviewed proposal into an explicit
decision surface. It does not approve, implement, or apply any source,
geometry, topology, sizing, clearance, placement, or fabrication rule.

No source roots, `.private` artifacts, completed references, post-design files,
customer PDFs, DXFs, DWGs, or public web sources were opened for this packet.

## Bound Evidence

| Evidence | SHA-256 |
|---|---|
| Source/rule proposal | `959D5DC73938B056D43600BD5EF73DEE5CC36D045D73B0EAA563D8E1702BE740` |
| Source/rule proposal review | `D729355456551101A5DC1CC7E8EC86A3D3ED06A0B78FA494B6963F391BD6AB70` |
| Proposal review child result | `136951D0CEB1B70AF8AA20ADCC2A2B601ED0D994EC5DE918C86D90AF8DE8585A` |
| T1 independent recovery audit | `FA5E9697047683BDB8850A66C014F40E42C83A3D02EF9ED8728AD5ADC6AE0221` |

## Decision Summary

| Lane | Coordinator decision | Why |
|---|---|---|
| `LANE_A_PANEL_ALLOCATION_SOURCE` | `AUTHORITY_REQUIRED_NOT_ACCEPTED_AUTONOMOUSLY` | No approved pre-design `PANEL_ALLOCATION_SOURCE` has been identified in the accepted generator bundle. |
| `LANE_B_COMPONENT_GEOMETRY_AUTHORITY` | `AUTHORITY_REQUIRED_NOT_ACCEPTED_AUTONOMOUSLY` | No verified component geometry library or approved generic conservative envelope rule exists for the active evidence set. |
| `LANE_C_TOPOLOGY_SIZING_PLACEMENT_RULES` | `FABRICATION_DOMAIN_DECISION_REQUIRED_NOT_ACCEPTED_AUTONOMOUSLY` | Cabinet, surface, clearance, thermal, ventilation, spare-space, and fill-denominator policy choices are fabrication/domain rules requiring explicit authority. |

No lane is accepted for implementation by this packet.

## Human Authority Choices

### Choice A: Authorize Panel Allocation Source Review

Authorize a bounded source-review branch to search for and adjudicate a
chronologically valid `PANEL_ALLOCATION_SOURCE`.

If accepted, the next branch must use deterministic source validation, four
independent specialist reviews, unanimous quorum, separate adjudication,
sanitized-bundle verification, and independent audit before any generator input
changes.

### Choice B: Authorize Component Geometry Authority

Provide or approve a verified component geometry library, or explicitly approve
a conservative generic-envelope rule family.

If accepted, implementation still requires failing synthetic regressions first,
versioned rule/library provenance, leakage review, and independent audit.

### Choice C: Authorize Topology/Sizing/Placement Rule Authority

Approve reusable domain rules for standard cabinet candidates, mounting
surfaces, compartments, doors, mounting plates, wiring/cable allowances,
clearance, thermal/ventilation, spare-space, and fill-denominator policy.

If accepted, each rule family must have a stable id, version, authority source,
synthetic regression coverage, and independent audit before application.

### Choice D: Reject All Authority Lanes

If all lanes are rejected or no authority can be granted, the compliant next
branch is terminal-candidate review for `STRUCTURAL_SOURCE_INSUFFICIENCY` and
`FABRICATION_DOMAIN_DECISION_REQUIRED`.

## Non-Negotiable Constraints

- Do not infer assignments, geometry, topology, cabinet sizes, surfaces,
  clearances, thermal allowances, spare-space, or coordinates from completed
  drawings.
- Do not use post-design labels as generator authority.
- Do not send private model identifiers to public lookup.
- Do not mutate source roots or `.private` artifacts.
- Do not generate customer PDF, DXF, DWG, or fabrication drawings during this
  authority step.
- Do not declare production approval.

## Implementation Gate If Any Lane Is Accepted

Any accepted lane must go through:

1. a new accepted decision bound to this packet;
2. failing synthetic regression tests before behavior changes;
3. bounded implementation with exact diff scope and rollback;
4. full test runner pass;
5. relevant scoped frozen workflow verification;
6. independent audit before recalibration or model promotion.

## Current Stop Point

The coordinator has prepared the decision packet. Further progress requires a
signed human/source/rule authority decision selecting one or more choices above
or rejecting all lanes.
