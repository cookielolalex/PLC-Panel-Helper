# Phase 0 Execution Plan

Status: ACTIVE.

1. Verify workspace root, master specification hash, Codex CLI features/config,
   bundled Git, and declared source roots.
2. Initialize Git and create canonical repository structure.
3. Create routing docs, source-root records, schemas, agent definitions, skills,
   synthetic fixtures, scripts, and task registry.
4. Run initial local tests using bundled Python.
5. Spawn bounded read-only `repo_explorer` and `independent_auditor` children.
6. Validate child result files against `schemas/child_result.schema.json`.
7. Update checkpoint/current state and commit if Git succeeds.

Do not run a real-project baseline. Do not substitute undeclared source roots.

