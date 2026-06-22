# Task PH0-REPO-EXPLORER

Agent type: repo_explorer.

Mode: bounded read-only.

Exact inputs:

- `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`
- `AGENTS.md`
- `docs/01_CURRENT_STATE.md`
- `docs/SOURCE_ROOTS.md`
- `orchestration/TASK_REGISTRY.csv`
- `schemas/child_result.schema.json`
- shallow repository file list

Writable path:

- `orchestration/results/PH0-REPO-EXPLORER.json`

Forbidden paths:

- declared source roots in `docs/SOURCE_ROOTS.md`
- `.git/`
- `releases/`
- `evals/runs/`
- `evals/references/`
- any file outside this workspace

Completion criteria:

- write schema-valid JSON matching `schemas/child_result.schema.json`;
- include observed workspace root, master hash if computed, source-root probe
  status, repository structure gaps, and no edits except the result file;
- report `PASS`, `FAIL`, or `NOT_VERIFIED` per check.

Timeout: 1800 seconds.

