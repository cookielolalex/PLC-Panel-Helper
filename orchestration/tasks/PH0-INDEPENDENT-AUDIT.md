# Task PH0-INDEPENDENT-AUDIT

Agent type: independent_auditor.

Mode: bounded read-only.

Exact inputs:

- `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`
- `docs/exec-plans/active/phase0_bootstrap.md`
- `docs/01_CURRENT_STATE.md`
- `docs/04_DECISION_LEDGER.md`
- `docs/SOURCE_ROOTS.md`
- `orchestration/TASK_REGISTRY.csv`
- `reports/harness/phase0_test_output.txt` when present
- `schemas/child_result.schema.json`

Writable path:

- `orchestration/results/PH0-INDEPENDENT-AUDIT.json`

Forbidden paths:

- declared source roots in `docs/SOURCE_ROOTS.md`
- `.git/`
- `releases/`
- `evals/runs/`
- `evals/references/`
- any file outside this workspace

Completion criteria:

- write schema-valid JSON matching `schemas/child_result.schema.json`;
- audit each Phase 0 done criterion with PASS, FAIL, or NOT_VERIFIED;
- cite file/hash/command evidence where available;
- do not implement fixes or mutate shared artifacts.

Timeout: 1800 seconds.

