# Project Identity And Revision

Trigger: verify project ID, customer, revision, supersession, and stale-template
risk for autonomous evaluation-only source quorum.

Permitted inputs: candidate source metadata, parser output, neutral project
identity evidence, task brief, source-guard policy, and synthetic examples.

Forbidden inputs: completed target drawings, completed-output filenames or
hashes, expected answers, reviewer findings, comparison overlays, other
reviewer results, and adjudicator recommendations.

Deterministic prerequisites: source hash and worksheet fingerprint are current;
candidate project ID is supported by inventory/path evidence; no deterministic
cross-project denial is present.

Result schema: `schemas/source_quorum_review.schema.json`.

Fail-closed conditions: conflicting project ID, conflicting customer identity,
stale template signal, superseded required worksheet, ambiguous required
revision, copied-project signal, or unresolved critical identity issue.

Completion criteria: every item records identity support, revision status,
risks, unresolved issues, and one of `ALLOW_EVAL`, `DENY`, or `QUARANTINE`.

Synthetic examples only: a workbook path and sheet both saying project
`1999001` may be `ALLOW_EVAL`; a sheet saying `1998001` is `DENY`; a silent
sheet with no conflicting ID is `QUARANTINE` unless other deterministic project
evidence is sufficient for evaluation-only review.
