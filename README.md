# PLC Panels Generation Helper

Repository for the PLC panel drawing-helper workflow governed by
`CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`.

Active V1 goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

Current gate: source-rich `1140304` Phase 1 qualification failed closed because
approved, independently verifiable source-document bytes or an approved
source-rich candidate index are still required. The accepted calibration case
remains `1110101`, and baseline-024 currently has `13 / 24` verified
`ALLOWED_EVAL` projects. No 24-project generation trial, customer drawing
generation, production approval, or private external transmission is authorized.
Privacy remains `NOT_APPROVED` unless `docs/PRIVACY_APPROVAL.md` records a
later accepted change.

Key paths:

- `docs/01_CURRENT_STATE.md` - compact current state and next action.
- `docs/PRIVACY_APPROVAL.md` - private-data transmission approval status.
- `docs/SOURCE_ROOTS.md` - declared read-only source roots and probe status.
- `evals/baseline-024/` - frozen baseline-024 protocol and cohort state.
- `evals/sheetmetal-v1/` - active sheetmetal-v1 scoped freeze manifests.
- `orchestration/TASK_REGISTRY.csv` - child/run registry.
- `schemas/` - artifact schemas.
- `scripts/` - deterministic local harness utilities.
- `evals/fixtures/` - sanitized synthetic fixtures only.
