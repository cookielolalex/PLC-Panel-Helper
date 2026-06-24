# SESSION CHECKPOINT

Current phase: sheetmetal-first modular foundation migration.

Accepted release: none.

Active production Knowledge paths: none.

Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

Current status: `SHEETMETAL_MODULAR_FOUNDATION_READY_FOR_ONE_PROJECT_CALIBRATION`.

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
- Projects awaiting sheetmetal requalification: 13.
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

Exact next action:

Run one-project sheetmetal calibration setup. Select or requalify exactly one
candidate as `SHEETMETAL_ALLOWED_EVAL` using the new qualification policy,
source-role chronology review, source guard, source-review quorum, sanitized
bundle verification, and reference isolation. Do not begin the new baseline.
Do not generate a real customer sheet-metal drawing until the one-project
calibration gate explicitly authorizes it. Do not expose completed references,
post-design labels, private filenames, raw workbook contents, OCR text, or
customer drawing content to generator-facing artifacts.
