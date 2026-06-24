# SESSION CHECKPOINT

Current phase: one-project component register and graph calibration private
workspace boundary complete; deterministic source-fact extraction pending.

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
- Project-specific facts written: no.

Exact next action:

Add deterministic source-fact extraction and synthetic regression coverage
before processing the private `1110101` sanitized source bundle. Do not
generate a customer drawing and do not promote `1110101` to
`SHEETMETAL_ALLOWED_EVAL` until calibration and adjudication pass.
