# One-Project Topology Sizing Placement Calibration

Status: `FROZEN_PROTOCOL`.

Protocol ID: `SMV1-1110101-TOPOLOGY-SIZING-PLACEMENT-CALIBRATION-V1`.

Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

Selected candidate: `1110101`.

This protocol freezes the topology, sizing, placement, hard-constraint, and
metric-calibration procedure for the first sheetmetal-v1 one-project case. It
extends the accepted component-register and graph calibration without
modifying any previously frozen private model artifact.

## Purpose

The topology/sizing/placement stage determines how much of a canonical panel
model can be safely produced from the already frozen source-only evidence,
component register, inventory graph, accepted source-role decisions, accepted
authority rules, approved rules, and schemas.

This task is not a drawing-generation task. It must not emit a customer PDF,
DXF, DWG, fabrication drawing, completed-reference crop, layout screenshot, or
answer key. It must not perform final independent adjudication.

## Starting Checkpoint

The protocol is bound to repository HEAD
`536c76d852f9c6c1e55017d17650b05e1915e479`, the documented descendant of
the component-register and graph audit pass.

The following checkpoint gates were verified before protocol freeze:

- full `scripts/run_tests.py`: `PASS`;
- legacy scoped workflow freeze: `PASS`;
- active sheetmetal-v1 scoped workflow freeze: `PASS`;
- selected `1110101` sanitized bundle verifier: `PASS`;
- tracked worktree clean except the permitted untracked legacy screening
  script `scripts/run_reference_detection_v4_corpus_screening.py`;
- privacy approval: `NOT_APPROVED`;
- tracked private artifacts: `0`;
- sheetmetal-v1 customer PDF/DXF/DWG outputs: `0`;
- prior component-register and graph independent audit: `PASS`;
- component-register/graph hard gates: `PASS`;
- component-register/graph determinism adjudication: `PASS`.

## Source Mode

This calibration remains in `SOURCE_MODE_A_INVENTORY_ONLY`. Functional-source
mode is disabled unless a later accepted repository decision explicitly
authorizes an applicable functional engineering source for `1110101`.

## Generator Lane

The generator lane may consume only:

- the verified sanitized source bundle;
- the previously frozen private source-fact model;
- the previously frozen private component register;
- the previously frozen private panel-assignment model and inventory graph;
- the previously frozen private accessory/cutout reconciliation;
- accepted source-role and chronology decisions;
- accepted source fact authority policy;
- approved component-library, topology, sizing, clearance, mounting,
  accessory, and validation rules;
- schemas and synthetic regression fixtures.

The generator lane must not consume:

- completed sheet-metal, production-control, or punch drawings;
- post-design allocation labels;
- electrical drawings unless explicitly authorized as functional sources;
- evaluator labels, expected panel sizes, expected assignments, expected
  surfaces, expected coordinates, reference filenames, images, OCR, title
  blocks, geometry, scores, or reviewer findings.

Project-specific topology, sizing, placement, constraint, and provenance
artifacts must be written only inside an ignored private workspace. Committed
generator evidence may contain only neutral counts, hashes, status codes,
coverage metrics, schema/rule versions, and generalized unresolved reasons.

## Evaluator Lane

The evaluator lane remains closed until all generator-side topology, sizing,
placement, validation, provenance, capability, and freeze artifacts are
written and hashed.

After generator freeze, evaluator-only comparison may access the qualified
completed-reference package only inside the evaluator lane. It may return only
neutral metrics, coverage, confidence, generalized mismatch classes, severity,
constraint findings, and provenance gaps. It must not return or persist
reference-derived dimensions, coordinates, layouts, component values,
screenshots, crops, filenames, hashes, or answer keys.

## Panel Assignment Recovery

Assignment recovery is source-only. Valid states are:

- `ASSIGNED_EXPLICIT`;
- `ASSIGNED_BY_APPROVED_RULE`;
- `UNASSIGNED`;
- `AMBIGUOUS`;
- `CONFLICT`;
- `HUMAN_REVIEW_REQUIRED`.

Every resolved assignment requires an evidence ID or approved rule ID, rule
version, confidence, and source class. Unsupported assignment count must remain
zero. Safe `UNASSIGNED` is preferred over unsupported inference.

## Topology Model

Topology candidates may include panels, cabinet count, cabinet type,
environment class, doors, mounting plates, compartments, partitions, roof,
base, side/rear surfaces, cable-entry regions, ventilation regions, and
mounting surfaces.

Every topology fact must be classified as:

- `EXPLICIT_SOURCE`;
- `DERIVED_BY_APPROVED_RULE`;
- `DESIGN_CHOICE_WITH_CONSTRAINTS`;
- `UNVERIFIED`;
- `CONFLICT`;
- `HUMAN_REVIEW_REQUIRED`.

If several valid candidates remain, the generator must preserve multiple
neutral candidate IDs rather than silently selecting one. Reference drawings
must not be used to infer topology.

## Sizing Model

Sizing is separate from placement. It may use explicit allowed dimensions,
verified component envelopes, approved generic conservative envelopes,
approved standard-cabinet library entries, wiring-duct allowances, cable-bend
allowances, access/maintenance clearances, thermal/ventilation rules, spare
space policy, structural rules, and mounting rules.

Geometry states are:

- `VERIFIED_MODEL_GEOMETRY`;
- `APPROVED_GENERIC_CONSERVATIVE_ENVELOPE`;
- `GEOMETRY_MISSING`;
- `GEOMETRY_CONFLICT`;
- `NOT_APPLICABLE`.

Dimensions must be named as `width_mm`, `height_mm`, and `depth_mm`. Ambiguous
dimension strings must be rejected. Unsupported exact cabinet sizes must remain
range/TBD rather than guessed.

## Placement Model

Placement may operate only on component instances with supported panel
assignment, allowed mounting surface, verified or approved conservative
geometry, and applicable clearance rules.

Each accepted placement must include neutral instance ID, panel ID, mounting
surface ID, `x_mm`, `y_mm`, `width_mm`, `height_mm`, orientation, geometry
status, evidence/rule IDs, and confidence.

Unplaceable components must stay explicit with reason codes such as:

- `UNASSIGNED_PANEL`;
- `GEOMETRY_MISSING`;
- `MOUNTING_SURFACE_UNKNOWN`;
- `CLEARANCE_RULE_MISSING`;
- `CONFLICTING_SOURCE`;
- `NO_VALID_PLACEMENT`;
- `HUMAN_REVIEW_REQUIRED`.

Hard constraints include containment, no physical overlap, mounting-surface
compatibility, orientation, edge clearance, maintenance access, door swing,
ventilation clearance, thermal separation when supported, wiring-duct
corridors, cable-entry and bend space, partition boundaries, cutout
containment, and quantity consistency. Soft objectives never override hard
constraints.

## Validation And Freeze

The validator must cover schema validity, panel identity, topology referential
integrity, component-instance referential integrity, assignment consistency,
quantity consistency, geometry provenance, dimension provenance, overlap,
containment, clearance, mounting compatibility, unresolved critical facts,
unsupported design choices, completed-reference leakage, and post-design
leakage.

Required zero counts:

- unsupported critical dimensions;
- unsupported panel assignments;
- unsupported placements;
- overlap violations among accepted placements;
- containment violations;
- quantity-stage overwrite violations;
- completed-reference leakage;
- post-design leakage;
- private-content transmissions;
- tracked private artifacts.

The generator-side run must execute twice from identical frozen inputs.
Canonical JSON hashes must match for every output. Byte differences are
allowed only when structurally identical JSON is proven and no fields are
excluded.

## Completion State

If implementation, tests, generator freeze, and evaluator-metric generation
complete, the status becomes
`ONE_PROJECT_TOPOLOGY_SIZING_PLACEMENT_FROZEN_AUDIT_PENDING` and the next
action becomes
`RUN_INDEPENDENT_ONE_PROJECT_TOPOLOGY_SIZING_PLACEMENT_AUDIT`.

The implementation thread must not issue the final PASS/FAIL adjudication.
