# Task PH1-INVENTORY-AUDIT

Agent type: independent_auditor.

Mode: bounded read-only.

Exact inputs:

- `docs/01_CURRENT_STATE.md`
- `docs/03_KNOWLEDGE_MANIFEST.md`
- `docs/04_DECISION_LEDGER.md`
- `docs/SOURCE_ROOTS.md`
- `manifests/all_projects_inventory_summary.json`
- `manifests/all_projects_file_role_index.csv`
- `manifests/115_file_role_index.csv`
- `manifests/all_projects_workbook_sheet_index.csv`
- `manifests/115_workbook_sheet_index.csv`
- `manifests/all_projects_project_manifest.csv`
- `manifests/115_project_manifest.csv`
- `manifests/st_block_library_index.csv`
- `manifests/vendor_catalog_index.csv`
- `reports/source_inventory_summary.md`
- `reports/generator_eligibility_summary.md`
- `reports/classification_validation.md`
- `reports/knowledge_pack_validation.md`
- `reports/harness/phase0_test_output.txt`
- `reports/harness/phase0_child_result_validation.json`
- `orchestration/TASK_REGISTRY.csv`
- `schemas/child_result.schema.json`

Writable path:

- `orchestration/results/PH1-INVENTORY-AUDIT.json`

Forbidden paths:

- `C:\Users\alex1\OneDrive\Desktop\All Projects` except shallow existence
  verification if needed; do not hash, parse, copy, move, delete, or modify
  source files.
- `.git/`
- `releases/`
- `evals/runs/`
- `evals/references/`
- any file outside this workspace other than shallow source-root existence
  verification.

Completion criteria:

- write schema-valid JSON matching `schemas/child_result.schema.json`;
- verify inventory row counts, hash presence, fail-closed generator eligibility,
  stale/hidden sheet queueing, CAD/catalog candidate status, tests, and no
  baseline boundary;
- report PASS, FAIL, or NOT_VERIFIED for each criterion;
- do not implement fixes or mutate shared artifacts.

Timeout: 1800 seconds.
