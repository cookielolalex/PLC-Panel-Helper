# Task PH1_5-SOURCE-GUARD-IMPLEMENTATION

Agent type: implementation_worker.

Mode: bounded workspace-write only in `orchestration/workspaces/PH1_5-SOURCE-GUARD-IMPLEMENTATION`
and the required result file. Do not edit canonical state files. You are not
alone in the codebase; do not revert others' changes.

Exact inputs:

- `docs/01_CURRENT_STATE.md`
- `docs/SOURCE_ROOTS.md`
- `manifests/all_projects_file_role_index.csv`
- `manifests/all_projects_workbook_sheet_index.csv`
- `manifests/all_projects_project_manifest.csv`
- `manifests/115_file_role_index.csv`
- `manifests/115_workbook_sheet_index.csv`
- existing `schemas/*.json`
- existing `scripts/*.py`
- `schemas/child_result.schema.json`

Writable paths:

- `orchestration/workspaces/PH1_5-SOURCE-GUARD-IMPLEMENTATION/`
- `orchestration/results/PH1_5-SOURCE-GUARD-IMPLEMENTATION.json`

Forbidden paths:

- `C:\Users\alex1\OneDrive\Desktop\All Projects`
- `.git/`
- canonical docs, manifests, schemas, scripts, tests, reports
- `evals/runs/`
- `evals/references/`
- completed target PDFs or their content

Completion criteria:

- Write schema-valid JSON matching `schemas/child_result.schema.json`.
- Provide implementation notes and/or patch text for source-guard schemas,
  `source_guard.py`, review-batch builder, source approval validator,
  sanitized bundle builder, bundle verifier, reports, and tests.
- Do not mark any real item ALLOWED and do not build a real generator bundle.

Timeout: 1800 seconds.

