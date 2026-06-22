# Decision Ledger

| decision_id | date | decision | rationale | evidence | affected_artifacts | approver | status |
|---|---|---|---|---|---|---|---|
| D-0001 | 2026-06-22 | Use `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW(4).txt` as the master source and copy it to the repo canonical name. | The user-attached file is the newest matching master spec and hashes to the copied root file. | SHA-256 `EBA9A30139A43862A7705F3123B050245DFA47FE3234D6A4E7579C6213E8FF09`. | `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt` | coordinator | ACCEPTED |
| D-0002 | 2026-06-22 | Treat exact declared source roots as missing rather than substituting nearby folders. | Positive source authorization requires exact declared roots or signed human update. | `docs/SOURCE_ROOTS.md`; Phase 0 source probe. | source manifests, Phase 1 gate | coordinator | ACCEPTED |

