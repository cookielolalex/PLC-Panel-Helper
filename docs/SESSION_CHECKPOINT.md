# SESSION CHECKPOINT

Current phase: deterministic panel-assignment and graph construction complete
for one-project component graph calibration; accessory/cutout reconciliation
pending.

Accepted release: none.

Active production Knowledge paths: none.

Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

Current status: `ONE_PROJECT_COMPONENT_GRAPH_CALIBRATION_IN_PROGRESS`.

Current candidate: `1110101`.

Legacy workflow status: the detector-v4.1 three-output qualification track is
preserved as historical evidence. Its last legacy status remains
`DETECTOR_V4_1_INDEPENDENT_GATE_PASSED_SCREENING_PENDING`.

Privacy status: `docs/PRIVACY_APPROVAL.md` remains `NOT_APPROVED`.

Verification at migration:

- Expected starting HEAD: `a4311e7`.
- Actual verified HEAD: `a193abc3e702d1750d40585180d8839fefd920c2`.
- Worktree was not clean because `scripts/run_reference_detection_v4_corpus_screening.py`
  was already untracked; the migration leaves it untouched.
- Full test runner before migration edits: `PASS`.
- Full test runner after sheetmetal-v1 foundation: `PASS`.
- Independent audit: `PASS_WITH_RESIDUAL_RISKS`.
- Coordinator audit addendum: `PASS`; resolves auditor-local Git/Python
  limitations and the migration-report status wording drift.
- Baseline generation attempts remain `0`.
- No real customer drawing was generated.

Revised Phase-0 verification:

- Legacy scoped freeze: `LEGACY_BASELINE_024_FROZEN_WORKFLOW_PROVENANCE_PASS`.
- Legacy anchor: `fac44321491633181f1fa53a062084d072b0b582`.
- Active scoped freeze: `SHEETMETAL_V1_ACTIVE_WORKFLOW_FREEZE_PASS`.
- Active anchor: `ab955b854e31d37666445f5a62ee6556f85f1352`.
- Revised Phase-0 gate:
  `ONE_PROJECT_SHEETMETAL_REQUALIFICATION_PHASE_0_PASS`.
- Evidence:
  `reports/sheetmetal-v1/revised_phase0_verification.json`.

Implemented modules:

- source evidence role/chronology filter;
- component type and component instance register;
- separated required/ordered/received/allocated/installed quantity fields;
- panel-assignment interface;
- typed JSON graph builder and validator;
- accessory and cutout rule reconciliation;
- panel topology and dimension model;
- placement-constraint validator;
- canonical sheet-metal drawing model;
- drawing provenance map;
- synthetic fixture and regression test.

New specs:

- `docs/specs/FROZEN_WORKFLOW_SCOPE_AND_LINEAGE_POLICY.md`
- `docs/specs/SHEETMETAL_FIRST_MODULAR_ARCHITECTURE.md`
- `docs/specs/SOURCE_ROLE_AND_CHRONOLOGY_POLICY.md`
- `docs/specs/SOURCE_FACT_AUTHORITY_MATRIX.md`
- `docs/specs/SHEETMETAL_QUALIFICATION_POLICY.md`

New namespaces:

- `reports/sheetmetal-v1/`
- `manifests/sheetmetal-v1/`
- `evals/sheetmetal-v1/`
- `orchestration/sheetmetal-v1/`

Qualification state:

- `LEGACY_THREE_OUTPUT_ALLOWED_EVAL`: 13 historical projects preserved.
- `SHEETMETAL_ALLOWED_EVAL`: 0 approved projects.
- Selected one-project calibration candidate: `1110101`.
- Projects awaiting future sheetmetal requalification after this selection: 12.
- New sheetmetal baseline: not started.

Regression coverage:

`test_sheetmetal_v1_modular_foundation` proves procurement quantity does not
overwrite required quantity, explicit accessories prevent duplicate inferred
accessories, conflicting models remain `CONFLICT`, post-design allocation
labels are rejected, functional edges are not invented in inventory-only mode,
missing electrical relationships remain `UNVERIFIED`, a component can have
several graph relationships, panel assignment is separate from placement,
width/height/depth cannot be silently reordered, hard placement constraints
cannot be overridden, every critical drawing-model fact has evidence or a safe
unresolved status, and completed-reference IDs/content do not enter generator
artifacts.

One-project candidate freeze:

- Decision: `D-0027`.
- Selected project: `1110101`.
- Selection artifact:
  `manifests/sheetmetal-v1/one_project_candidate_selection.json`.
- Effective reference package:
  `manifests/sheetmetal-v1/selected_candidate/1110101/effective_sheetmetal_reference_package.json`.
- Source-role/chronology classification:
  `manifests/sheetmetal-v1/selected_candidate/1110101/source_role_chronology_classification.json`.
- Verified source bundle:
  `manifests/sheetmetal-v1/selected_candidate/1110101/generator_bundle/`.
- Independent audit:
  `reports/sheetmetal-v1/selected_candidate_1110101_independent_audit.md`.
- Audit result: `PASS`.
- Bundle verification: `PASS`.
- Customer drawing generated: no.
- `SHEETMETAL_ALLOWED_EVAL` promotion: not yet; still requires model
  calibration and adjudication.

One-project component graph calibration protocol:

- Decision: `D-0028`.
- Protocol:
  `docs/specs/ONE_PROJECT_COMPONENT_GRAPH_CALIBRATION.md`.
- Machine protocol:
  `manifests/sheetmetal-v1/one-project-model-calibration/1110101/calibration_protocol.json`.
- Plan:
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/calibration_plan.md`.
- Status: `ONE_PROJECT_COMPONENT_GRAPH_CALIBRATION_IN_PROGRESS`.
- Source mode: `SOURCE_MODE_A_INVENTORY_ONLY`.
- Generator lane: source-only; no completed references, post-design labels,
  evaluator labels, expected answers, reference hashes, images, OCR, title-block
  text, or reviewer findings.
- Evaluator lane: closed until generator artifacts are frozen and hashed.
- Privacy: project-specific facts and graph contents must be written only to an
  ignored private workspace and must not be printed or committed.
- Checkpoint gates before protocol freeze: full tests `PASS`, legacy scoped
  freeze `PASS`, active sheetmetal-v1 freeze `PASS`, selected bundle verifier
  `PASS`, bundle hash cross-check `PASS`, worksheet fingerprint presence
  `PASS`, privacy `NOT_APPROVED`, real customer drawing count `0`, baseline
  generation attempts `0`.

Private workspace boundary:

- Decision: `D-0029`.
- Private workspace: `.private/sheetmetal-v1/1110101/`.
- Git ignore pattern: `.private/`.
- Direct check: `git check-ignore` passes for the project-private probe path.
- Tracked private paths: `0`.
- Regression test: `test_sheetmetal_v1_private_workspace_boundary`.
- Active scoped manifest refreshed for `.gitignore` and `scripts/run_tests.py`.
- Evidence:
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/private_workspace_boundary.json`.
- Project-specific facts written: yes, but only inside the ignored private
  source-fact extraction directory after `D-0030`.

Source-fact extraction:

- Decision: `D-0030`.
- Extractor: `scripts/sheetmetal_v1.py --bundle-dir ... --source-classification ... --output-dir ... --quiet`.
- Private output directory:
  `.private/sheetmetal-v1/1110101/source-fact-extraction/`.
- Private outputs: `source_fact_model.json` and
  `source_fact_validation.json`.
- Private output hashes:
  `source_fact_model.json`
  `23A1F4731794A3F6574B709567859351323AFB53F6F77849937F1E77809E5738`;
  `source_fact_validation.json`
  `8B9DD11E67CCBFD8E9DED710D917A9D736B963FCC331FBC51382AF2AB0849B16`.
- Git ignore verification: `PASS`; no `.private` path is tracked.
- Schema validation: `PASS`.
- Neutral counts: 6 evidence records, 125 represented source lines, 87 source
  facts, 0 silently discarded authorized source lines, 0 quantity-stage
  overwrite violations, 0 completed-reference facts, and 0 private content
  transmissions.
- Regression test: `test_sheetmetal_v1_source_fact_extractor`.
- Active scoped manifest refreshed for `schemas/source_fact_model.schema.json`,
  `scripts/sheetmetal_v1.py`, and `scripts/run_tests.py`.
- Evidence:
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/source_fact_extraction_summary.json`.

Component-register construction:

- Decision: `D-0031`.
- Builder: `scripts/sheetmetal_v1.py --source-fact-model ... --output-dir ... --quiet`.
- Private input:
  `.private/sheetmetal-v1/1110101/source-fact-extraction/source_fact_model.json`.
- Private output directory:
  `.private/sheetmetal-v1/1110101/component-register/`.
- Private outputs: `component_register.json` and
  `component_register_validation.json`.
- Private output hashes:
  `component_register.json`
  `D0C354C964D3D9D614E5BCE300F877DE3E43F6E7C770CA9461C7A5DF9481E247`;
  `component_register_validation.json`
  `AD1917C52019D2BDE516B414333D2761CA9C0E31DEAC537940486EE39C0D6B69`.
- Git ignore verification: `PASS`; no `.private` path is tracked.
- Schema validation: `PASS` for component register, component types, and
  component instances.
- Neutral counts: 53 component types, 53 component instances, 0 conflicts, 87
  source facts, 125 source lines, 0 unregistered allowed component keys, 0
  completed-reference components, and 0 private content transmissions.
- Regression test: `test_sheetmetal_v1_component_register_from_source_facts`.
- Active scoped manifest refreshed for `scripts/sheetmetal_v1.py` and
  `scripts/run_tests.py`.
- Evidence:
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/component_register_summary.json`.

Panel-assignment and graph construction:

- Decision: `D-0032`.
- Builder: `scripts/sheetmetal_v1.py --source-fact-model ... --component-register ... --output-dir ... --quiet`.
- Private inputs:
  `.private/sheetmetal-v1/1110101/source-fact-extraction/source_fact_model.json`
  and `.private/sheetmetal-v1/1110101/component-register/component_register.json`.
- Private output directory:
  `.private/sheetmetal-v1/1110101/panel-graph/`.
- Private outputs: `panel_assignment.json`, `panel_graph.json`, and
  `panel_graph_validation.json`.
- Private output hashes:
  `panel_assignment.json`
  `1531D1DFA7BD6AB329AD6964C38367C9C0094AD8B32AE2802176712F3D957FD8`;
  `panel_graph.json`
  `B3A68E597703AA8C8B6C29998F8D28A811912A071BCA34C7018F4BDB38479CB1`;
  `panel_graph_validation.json`
  `02209B427FFDD9C1947F7A22CD77D43E714C9930A72177DF68A9C289F1C1D9E8`.
- Git ignore verification: `PASS`; no `.private` path is tracked.
- Schema validation: `PASS` for panel assignment and panel graph.
- Neutral counts: 0 explicit panel assignments, 53 unresolved components, 0
  rejected assignments, 56 graph nodes, 107 graph edges, 0 dangling edges, 1
  inventory-only unverified function edge, and 0 private content transmissions.
- Regression test: `test_sheetmetal_v1_panel_assignment_graph_from_private_models`.
- Active scoped manifest refreshed for `scripts/sheetmetal_v1.py` and
  `scripts/run_tests.py`.
- Evidence:
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/panel_graph_summary.json`.

Exact next action:

Implement deterministic accessory and cutout reconciliation against the private
`1110101` component register and panel graph with synthetic regression
coverage. Do not generate a customer drawing and do not promote `1110101` to
`SHEETMETAL_ALLOWED_EVAL` until calibration and adjudication pass.
