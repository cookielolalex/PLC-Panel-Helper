# One-Project Component Register And Graph Calibration

Status: `FROZEN_PROTOCOL`.

Protocol ID: `SMV1-1110101-COMPONENT-GRAPH-CALIBRATION-V1`.

Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

Selected candidate: `1110101`.

This protocol freezes the one-project component-register and typed-graph
calibration procedure before project facts are processed. It establishes the
generator/evaluator isolation boundary, privacy boundary, source authority
rules, deterministic output contract, and hard gates for the first sheetmetal-v1
calibration case.

## Purpose

The first calibration case must determine whether the verified source-only
modular pipeline can safely produce normalized source facts, a canonical
component register, quantity reconciliation, panel assignments when supported,
a typed inventory/physical relationship graph, accessory and cutout
requirements, complete provenance, and safe unresolved statuses.

This is not a production acceptance trial. It must not generate PDF, DXF, DWG,
or other customer drawing output. It must not promote the selected project to
`SHEETMETAL_ALLOWED_EVAL` until the full calibration and independent audit
pass.

## Starting Checkpoint

The protocol is bound to repository HEAD
`5409f2998eb77e3b61762b4d2d5c2f68835cb557`, which is the expected `5409f29`
checkpoint. The tracked worktree was verified clean before protocol edits. The
only permitted untracked path was
`scripts/run_reference_detection_v4_corpus_screening.py`, which remains a
legacy file that must not be staged, modified, deleted, moved, executed, or
incorporated.

The following gates were verified before protocol freeze:

- full `scripts/run_tests.py`: `PASS`;
- legacy scoped workflow freeze: `PASS`;
- active sheetmetal-v1 scoped workflow freeze: `PASS`;
- selected `1110101` sanitized bundle verifier: `PASS`;
- bundle hash cross-check: `PASS` for 17 entries;
- approved worksheet fingerprint presence: `PASS` for 6 approved decisions;
- privacy approval: `NOT_APPROVED`;
- sheetmetal-v1 customer drawing outputs: `0`;
- sheetmetal-v1 baseline-generation directories: `0`;
- generator-bundle reference-manifest and drawing-media scan: `PASS`.

## Source Mode

This calibration runs in `SOURCE_MODE_A_INVENTORY_ONLY`.

Functional-source mode is disabled unless an accepted repository decision or
explicit current human authorization approves an applicable functional
engineering source for `1110101`. The existence of an electrical drawing or a
historical completed drawing does not authorize functional-source mode.

## Generator Lane

The generator lane may see only:

- the verified sanitized source bundle at
  `manifests/sheetmetal-v1/selected_candidate/1110101/generator_bundle/`;
- accepted source-role decisions;
- accepted chronology decisions;
- the source-fact authority matrix;
- canonical schemas;
- approved component-library entries;
- approved engineering and accessory rules;
- synthetic regression fixtures.

The generator lane must not see:

- completed customer drawings;
- production-control, sheet-metal, or punch drawing references;
- post-design allocation labels;
- evaluator labels;
- expected components, dimensions, panel assignments, layouts, or answer keys;
- completed-reference filenames, hashes, page images, OCR text, title-block
  content, crops, scores, reviewer findings, or extracted reference text.

Generator artifacts that contain project facts must be written only to an
ignored private workspace. Committed generator-side artifacts may contain only
schemas, scripts, synthetic fixtures, neutral counts, hashes, coverage metrics,
status codes, and audit summaries.

## Evaluator Lane

The evaluator lane remains closed until generator artifacts are frozen and
hashed. After freeze, it may inspect only:

- frozen generated models;
- the qualified evaluator-only sheetmetal reference package;
- accepted evaluator-only post-design labels;
- approved scoring schemas.

The evaluator lane must not modify generator artifacts or feed reference-
derived values back into generator code, rules, fixtures, or project-private
artifacts.

Evaluator committed reports may contain only:

- metrics;
- coverage;
- neutral mismatch IDs;
- generalized error classes;
- severity;
- provenance gaps;
- unsupported-inference counts.

Evaluator reports must not contain completed-reference dimensions, component
values, panel layouts, title-block text, images, crops, filenames, hashes, or
answer keys.

## Private Workspace Boundary

Project-specific component facts and graph contents are private. Before any
project-fact extraction, the coordinator must create or verify an ignored
private workspace for this calibration, such as
`.private/sheetmetal-v1/1110101/`, and must prove with `git check-ignore` that
project-specific artifacts cannot be staged.

Private runtime artifacts may include normalized source facts, component
registers, component instances, panel assignments, graph nodes and edges,
accessory reconciliation, and provenance mappings.

Private project values must not be printed to stdout, stderr, JSONL
trajectories, console transcripts, or committed reports.

## Extraction Rules

Source-fact extraction must be deterministic and local. The private sanitized
bundle must not be given to GPT-5 or another model agent.

Every extracted fact must retain internal provenance fields for neutral
evidence ID, neutral source document ID, source role, sanitized source location,
field type, normalized value, unit, authority class, confidence, chronology
status, and conflict status.

Quantities remain separated as:

- `required_qty`;
- `ordered_qty`;
- `received_qty`;
- `allocated_qty`;
- `installed_qty`.

Procurement evidence must not overwrite required quantity. Completed drawings
and post-design allocation labels must not provide generator facts.

Conflicts remain explicit `CONFLICT`. Missing or unsupported facts remain
`TBD`, `UNVERIFIED`, or `HUMAN_REVIEW_REQUIRED`. Conflicts must not be resolved
by majority vote, filenames, modified time, or completed-reference evidence.

## Component Register Rules

The canonical register separates component types from component instances.

Component types must preserve family, manufacturer, model, specification,
geometry-library status, mounting-method status, accessory-rule applicability,
source evidence, confidence, and conflict state.

Component instances must preserve deterministic neutral instance ID, component
type ID, separated quantity records, panel-assignment status,
mounting-surface status, function status, evidence IDs, unresolved fields, and
conflict records.

The pipeline must not infer absent manufacturer or model, collapse similar
models without evidence, silently merge duplicate-looking source rows, or
invent missing physical geometry. Generic family footprints may not be marked
as verified model-specific footprints.

Every authorized source line must be accounted for as represented, merged with
justification, conflicting, excluded by accepted source policy, or unresolved.
No authorized source line may silently disappear.

## Panel Assignment Rules

Panel assignment is separate from extraction and placement. It may use only
explicit pre-design panel tags, approved pre-design allocation sources,
authorized source annotations, and approved deterministic assignment rules.

Valid assignment states are:

- `ASSIGNED_EXPLICIT`;
- `ASSIGNED_BY_APPROVED_RULE`;
- `UNASSIGNED`;
- `AMBIGUOUS`;
- `CONFLICT`;
- `HUMAN_REVIEW_REQUIRED`.

A safe `UNASSIGNED` result is preferable to an unsupported assignment. This
task must not perform geometric component placement.

## Graph Rules

The typed graph runs in inventory-only mode. Required node classes may include
`PROJECT`, `PANEL`, `COMPONENT_TYPE`, `COMPONENT_INSTANCE`,
`REQUIREMENT_LINE`, `PROCUREMENT_LINE`, `CUSTOMER_SUPPLIED_ITEM`, `ACCESSORY`,
`SOURCE_EVIDENCE`, `ENGINEERING_RULE`, `MOUNTING_SURFACE`, and `CONSTRAINT`.

Allowed inventory/physical edge types are `REQUIRED_BY`, `SATISFIES`,
`ORDERED_AS`, `CUSTOMER_SUPPLIED_AS`, `ASSIGNED_TO_PANEL`,
`REQUIRES_ACCESSORY`, `REQUIRES_CUTOUT`, `MOUNTED_ON`, `DERIVED_FROM`, and
`CONFLICTS_WITH`.

The graph must not create functional edges such as `SUPPLIES`, `PROTECTS`,
`CONTROLS`, `MEASURES`, `REPORTS_TO`, or `INTERLOCKS_WITH` without an
authorized functional source.

Every edge must include evidence ID or approved rule ID, confidence, source
class, status, and graph version. Unsupported relationships remain absent or
explicitly `UNVERIFIED`.

Graph validation must check node-ID uniqueness, edge referential integrity,
duplicate edges, orphan nodes, applicable cycles, and forbidden functional
edges in inventory-only mode.

## Accessory And Cutout Rules

Accessory and cutout reconciliation may use only versioned approved rules, with
this precedence:

1. explicit source accessory;
2. verified model-specific library rule;
3. approved family-level rule;
4. otherwise `UNVERIFIED`.

The pipeline must not create duplicate inferred accessories when explicit
source items already satisfy the requirement. Inferred requirements must record
rule ID, rule version, triggering component instance ID, reconciliation status,
evidence class, and confidence.

Final cutout geometry may be emitted only from a verified model-specific
library entry or explicit allowed source. Generic family knowledge may emit
`CUTOUT_GEOMETRY_REQUIRED_BUT_UNVERIFIED`, but it must not emit unsupported
dimensions.

## Determinism And Freeze

The generator-side pipeline must run twice from the same frozen source bundle
and configuration. Outputs must be byte-identical or canonicalized
semantically identical with excluded timestamp fields explicitly declared.

The coordinator must freeze and hash the source-fact model, component
register, panel-assignment model, graph, accessory reconciliation, provenance
map, and validation report. The freeze must record input bundle hash,
worksheet fingerprints, schema versions, rule-library versions, workflow hash,
output hashes, runtime version, and actual execution mode.

After generator freeze, generator artifacts may not be modified based on
completed-reference values during this task.

## Evaluation And Gates

Evaluator-only calibration runs after generator freeze. Every metric must
include numerator, denominator, scorable coverage, and confidence. Percentages
without denominators are prohibited.

Hard gates include:

- schema validation: `PASS`;
- full `scripts/run_tests.py`: `PASS`;
- scoped workflow freezes: `PASS`;
- sanitized bundle hashes and fingerprints: `PASS`;
- private-content transmission count: `0`;
- reference leakage into generator artifacts: `0`;
- post-design leakage into generator artifacts: `0`;
- unsupported critical generated facts: `0`;
- silently discarded authorized source lines: `0`;
- quantity-stage overwrite violations: `0`;
- graph referential-integrity failures: `0`;
- forbidden functional edges in inventory-only mode: `0`;
- unsupported panel assignments: `0`;
- duplicate inferred accessories: `0`;
- temporary private-artifact leakage into Git: `0`;
- deterministic rerun: `PASS`;
- real customer drawings generated: `0`.

Precision is more important than recall. The calibration may pass with safe
unresolved facts only when omissions are explicitly recorded, no unsafe
substitution occurred, coverage and confidence are reported, and remaining
gaps are assigned to a specific later module or library deficit.

## Completion States

If every hard gate passes and the independent audit passes, the status becomes
`ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION_PASS`, and the next
action becomes `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION`.

If safety gates pass but scorable coverage is insufficient, the status becomes
`ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION_INCONCLUSIVE_LOW_COVERAGE`.

If a hard gate fails, the coordinator must use the most precise failure status
from the approved calibration failure set and keep `SHEETMETAL_ALLOWED_EVAL`
at `0`.
