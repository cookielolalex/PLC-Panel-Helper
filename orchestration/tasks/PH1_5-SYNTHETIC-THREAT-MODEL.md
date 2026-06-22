# Task PH1_5-SYNTHETIC-THREAT-MODEL

Agent type: repo_explorer.

Mode: read-only. Do not edit shared files.

Exact inputs:

- `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`
- `docs/specs/GENERATOR_INPUT_POLICY.md`
- `docs/specs/EVALUATION_HARNESS_SPEC.md`
- `scripts/build_generator_bundle.py`
- `scripts/scan_generator_contamination.py`
- `scripts/run_tests.py`
- `manifests/all_projects_workbook_sheet_index.csv`
- `reports/classification_validation.md`
- `schemas/child_result.schema.json`

Writable path:

- `orchestration/results/PH1_5-SYNTHETIC-THREAT-MODEL.json`

Forbidden paths:

- `C:\Users\alex1\OneDrive\Desktop\All Projects`
- `.git/`
- `evals/runs/`
- `evals/references/`
- completed target PDFs or their content
- any file outside this workspace

Completion criteria:

- Write schema-valid JSON matching `schemas/child_result.schema.json`.
- Identify leakage/contamination paths involving workbook sheets, formulas,
  named ranges, external links, hidden content, revisions, duplicates, source
  mutations, symlinks/junctions, path traversal, and approval tampering.
- Propose deterministic fail-closed fixture/test expectations.

Timeout: 1800 seconds.

