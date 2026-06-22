# Phase 0 Preflight Evidence

Workspace root:

`C:\Users\alex1\OneDrive\Documents\PLC Panels Generation Helper`

Master specification:

- canonical repo path: `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`
- selected source copy: `C:\Users\alex1\Downloads\CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW(4).txt`
- SHA-256: `EBA9A30139A43862A7705F3123B050245DFA47FE3234D6A4E7579C6213E8FF09`

Local Codex probe:

- WindowsApps `codex.exe`: present but direct execution returned `Access is denied`.
- configured CLI: `C:\Users\alex1\AppData\Local\OpenAI\Codex\bin\8e55c2dd143b6354\codex.exe`
- version: `codex-cli 0.142.0-alpha.6`
- `codex exec --help`: supports `--config`, `--enable`, `--disable`,
  `--strict-config`, `--model`, `--sandbox read-only|workspace-write|danger-full-access`,
  `--cd`, `--add-dir`, `--skip-git-repo-check`, `--ephemeral`,
  `--ignore-user-config`, `--ignore-rules`, `--output-schema`, `--json`, and
  `--output-last-message`.
- `codex features list`: `multi_agent` stable true; `apps`, `browser_use`,
  `goals`, `image_generation`, `plugins`, `shell_tool`, `workspace_dependencies`
  stable true; `enable_fanout` under development false.

Git:

- PATH `git`: missing.
- bundled Git used:
  `C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe`
- repository initialized on branch `main`.

Bundled Python:

`C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

Declared source roots:

All four exact paths from the master specification were missing during Phase 0.
No source extraction or full source scan was performed.

