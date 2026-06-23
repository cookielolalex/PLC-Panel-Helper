# B024-C-B003-LEAKAGE-RED-TEAM

Role: `leakage_red_team`

Batch: `batch-003`

Objective: independently produce the schema-valid source quorum review JSON for this role using only the deterministic prefilter files listed in `orchestration\input_manifests\baseline-024\source_backfill\batch-003\B024-C-B003-LEAKAGE-RED-TEAM.visible_files.json`.

Allowed files: see `orchestration\input_manifests\baseline-024\source_backfill\batch-003\B024-C-B003-LEAKAGE-RED-TEAM.visible_files.json`. Do not read other review outputs, adjudication outputs, completed references, target drawings, thumbnails, hashes, expected answers, scores, or generator outputs.

Write only: `manifests\baseline-024\source_approvals\batch-003\reviews\leakage_red_team_review.json`.

Run this exact command from the repository root:

```powershell
& 'C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\autonomous_eval_source_approval.py review --role leakage_red_team --prefilter-root manifests\baseline-024\source_candidates\batch-003\project_manifests --output manifests\baseline-024\source_approvals\batch-003\reviews\leakage_red_team_review.json --schema schemas\source_quorum_review.schema.json
```

Completion criteria:

- output JSON validates against `schemas/source_quorum_review.schema.json`;
- `reviewer_role` equals `leakage_red_team`;
- every prefilter item has one of `ALLOW_EVAL`, `DENY`, or `QUARANTINE`;
- no completed-reference content is opened or summarized.
