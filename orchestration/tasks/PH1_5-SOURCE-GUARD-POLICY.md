# Task PH1_5-SOURCE-GUARD-POLICY

Agent type: repo_explorer.

Mode: read-only. Do not edit shared files.

Exact inputs:

- `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`
- `AGENTS.md`
- `docs/01_CURRENT_STATE.md`
- `docs/SOURCE_ROOTS.md`
- `manifests/all_projects_file_role_index.csv`
- `manifests/all_projects_workbook_sheet_index.csv`
- `manifests/all_projects_project_manifest.csv`
- `manifests/115_file_role_index.csv`
- `manifests/115_workbook_sheet_index.csv`
- `reports/manual_review_queue.csv`
- `reports/stale_sheet_review_queue.csv`
- `reports/generator_eligibility_summary.md`
- `schemas/child_result.schema.json`

Writable path:

- `orchestration/results/PH1_5-SOURCE-GUARD-POLICY.json`

Forbidden paths:

- `C:\Users\alex1\OneDrive\Desktop\All Projects`
- `.git/`
- `evals/runs/`
- `evals/references/`
- completed target PDFs or their content
- any file outside this workspace

Completion criteria:

- Write schema-valid JSON matching `schemas/child_result.schema.json`.
- Analyze role taxonomy, review queues, stale/hidden/cross-project risks,
  parser gaps, family selection, and proposed deterministic source-guard
  decision rules/evidence fields.
- Include PASS/FAIL/NOT_VERIFIED checks and cite manifest/report evidence.

Timeout: 1800 seconds.

