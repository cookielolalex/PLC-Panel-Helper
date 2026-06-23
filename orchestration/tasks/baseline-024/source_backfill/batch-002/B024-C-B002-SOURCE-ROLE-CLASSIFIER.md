# B024-C-B002-SOURCE-ROLE-CLASSIFIER

Role: `source_role_classifier`

Batch: `batch-002`

Objective: independently produce the schema-valid source quorum review JSON for this role using only the deterministic prefilter files listed in `orchestration\input_manifests\baseline-024\source_backfill\batch-002\B024-C-B002-SOURCE-ROLE-CLASSIFIER.visible_files.json`.

Allowed files: see `orchestration\input_manifests\baseline-024\source_backfill\batch-002\B024-C-B002-SOURCE-ROLE-CLASSIFIER.visible_files.json`. Do not read other review outputs, adjudication outputs, completed references, target drawings, thumbnails, hashes, expected answers, scores, or generator outputs.

Write only: `manifests\baseline-024\source_approvals\batch-002\reviews\source_role_classifier_review.json`.

Run this exact command from the repository root:

```powershell
& 'C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\autonomous_eval_source_approval.py review --role source_role_classifier --prefilter-root manifests\baseline-024\source_candidates\batch-002\project_manifests --output manifests\baseline-024\source_approvals\batch-002\reviews\source_role_classifier_review.json --schema schemas\source_quorum_review.schema.json
```

Completion criteria:

- output JSON validates against `schemas/source_quorum_review.schema.json`;
- `reviewer_role` equals `source_role_classifier`;
- every prefilter item has one of `ALLOW_EVAL`, `DENY`, or `QUARANTINE`;
- no completed-reference content is opened or summarized.
