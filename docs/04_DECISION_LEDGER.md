# Decision Ledger

| decision_id | date | decision | rationale | evidence | affected_artifacts | approver | status |
|---|---|---|---|---|---|---|---|
| D-0001 | 2026-06-22 | Use `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW(4).txt` as the master source and copy it to the repo canonical name. | The user-attached file is the newest matching master spec and hashes to the copied root file. | SHA-256 `EBA9A30139A43862A7705F3123B050245DFA47FE3234D6A4E7579C6213E8FF09`. | `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt` | coordinator | ACCEPTED |
| D-0002 | 2026-06-22 | Treat exact declared source roots as missing rather than substituting nearby folders. | Positive source authorization requires exact declared roots or signed human update. | `docs/SOURCE_ROOTS.md`; Phase 0 source probe. | source manifests, Phase 1 gate | coordinator | ACCEPTED |
| D-0003 | 2026-06-22 | Accept `C:\Users\alex1\OneDrive\Desktop\All Projects` as the consolidated project source root. | The user explicitly stated all projects are now located there. This does not by itself approve CAD/catalog roots or any generator bundle. | Shallow probe found directories `111年度工作` through `115年度工作`. | `docs/SOURCE_ROOTS.md`, `manifests/source_roots_probe.json`, Phase 1 manifests | user | ACCEPTED |
