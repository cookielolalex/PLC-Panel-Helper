# Source Quorum Adjudication

Trigger: adjudicate frozen deterministic prefilter and four independent source
review results.

Permitted inputs: deterministic prefilter JSON, four frozen review JSON files,
source inventory metadata, policy, schemas, and synthetic examples.

Forbidden inputs: completed target drawings, target thumbnails, expected
answers, score reports, generator outputs, non-frozen reviewer drafts, and
project-specific completed decisions.

Deterministic prerequisites: all reviewer JSON validates against
`schemas/source_quorum_review.schema.json`; all references use current file
hashes and worksheet fingerprints; prefilter passed for each approved item.

Result schema: `schemas/source_quorum_adjudication.schema.json`.

Fail-closed conditions: any DENY or QUARANTINE vote, reviewer disagreement,
hash/fingerprint/project mismatch, unresolved critical issue, forbidden signal,
stale signal, superseded required worksheet, denied dependency, external
critical source, or parser-required item.

Completion criteria: each item is `AGENT_QUORUM_APPROVED_EVAL`,
`AUTO_DENIED`, `PARSER_REQUIRED`, or `QUARANTINED`, and each project records
whether it may proceed to sanitized bundle construction.

Synthetic examples only: four matching `ALLOW_EVAL` votes can approve a clean
synthetic sheet for evaluation; any one `QUARANTINE` vote quarantines it.
