# Reference Leakage Detection

Trigger: red-team candidate source or sanitized bundle for forbidden completed
reference exposure.

Permitted inputs: candidate permitted-input workbooks, source inventory
metadata, parser output, sanitized bundle files, source-guard policy, task
brief, and synthetic examples.

Forbidden inputs: completed target drawings, target thumbnails, target hashes,
expected answers, score reports, reviewer findings, comparison overlays, other
reviewer results, and adjudicator recommendations.

Deterministic prerequisites: approved source root is known; file hashes match;
bundle file list is explicit; symlink and path traversal checks are possible.

Result schema: `schemas/source_quorum_review.schema.json`.

Fail-closed conditions: completed-output name/content sentinel, reviewer
evidence, target hash, target thumbnail, embedded reference material, absolute
source path leak, symlink, junction, shortcut, path escape, or outside-root path.

Completion criteria: every item records leakage probes, detected risks,
unresolved issues, evidence IDs, and one of `ALLOW_EVAL`, `DENY`, or
`QUARANTINE`.

Synthetic examples only: a clean synthetic visible workbook may be
`ALLOW_EVAL`; a synthetic file containing `reference_only_sentinel` is `DENY`;
a synthetic bundle with `../escape.csv` is `DENY`.
