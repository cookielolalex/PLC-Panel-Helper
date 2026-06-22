# Source Role Classification

Trigger: classify source-file or worksheet role for autonomous evaluation-only
source quorum.

Permitted inputs: source inventory metadata, deterministic parser output,
candidate permitted-input workbook paths, source-guard policy, task brief,
visible-file manifest, and synthetic examples.

Forbidden inputs: completed target drawings, target thumbnails, target hashes,
extracted reference text, reviewer findings, scores, expected answers, other
reviewer results, adjudicator recommendations, and unapproved source roots.

Deterministic prerequisites: source root is approved; file hash matches
inventory; worksheet fingerprint matches inventory when present; parser status
is known; worksheet visibility is known; source role is not deterministically
forbidden.

Result schema: `schemas/source_quorum_review.schema.json`.

Fail-closed conditions: forbidden role, target-output role, production-control
role, electrical drawing role, unclear role required for critical values,
misleading filename, source mutation, unsupported parser, or outside-root path.

Completion criteria: every item has `ALLOW_EVAL`, `DENY`, or `QUARANTINE` with
reason codes, evidence IDs, risk list, unresolved issues, policy version, and
run metadata.

Synthetic examples only: a visible synthetic contract workbook may be
`ALLOW_EVAL`; a synthetic completed-output PDF is `DENY`; a synthetic workbook
with unclear role is `QUARANTINE`.
