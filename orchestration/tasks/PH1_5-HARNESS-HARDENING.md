# Task PH1_5-HARNESS-HARDENING

Agent type: implementation_worker.

Mode: bounded workspace-write only in `orchestration/workspaces/PH1_5-HARNESS-HARDENING`
and the required result file. Do not edit canonical state files. You are not
alone in the codebase; do not revert others' changes.

Exact inputs:

- `docs/specs/GENERATOR_INPUT_POLICY.md`
- `docs/specs/EVALUATION_HARNESS_SPEC.md`
- `scripts/run_tests.py`
- `scripts/harness_lib.py`
- `scripts/scan_generator_contamination.py`
- existing `evals/fixtures/`
- `schemas/child_result.schema.json`

Writable paths:

- `orchestration/workspaces/PH1_5-HARNESS-HARDENING/`
- `orchestration/results/PH1_5-HARNESS-HARDENING.json`

Forbidden paths:

- `C:\Users\alex1\OneDrive\Desktop\All Projects`
- `.git/`
- canonical docs, manifests, schemas, source-guard implementation files,
  reports
- `evals/runs/`
- `evals/references/`
- completed target PDFs or their content

Completion criteria:

- Write schema-valid JSON matching `schemas/child_result.schema.json`.
- Provide synthetic/adversarial fixture and test design or patch text covering
  hidden/veryHidden sentinels, formulas/named ranges/external links, stale
  customer/project IDs, supersession, macro-enabled workbook, parser-required
  legacy workbook, approval tampering, mutation invalidation, source-root
  path leaks, target-output name leaks, CJK names, symlink/junction when
  supported, ZIP traversal, blank decisions, and bulk approvals.

Timeout: 1800 seconds.
