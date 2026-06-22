# Sanitized Generator Bundle

Trigger: build or verify an evaluation-only sanitized generator bundle from
quorum-approved source items.

Permitted inputs: `AGENT_QUORUM_APPROVED_EVAL` adjudication, current source
inventory metadata, approved visible worksheet parser output, source-guard
policy, schemas, and synthetic examples.

Forbidden inputs: original workbook copies in generator workspace, unapproved
sheets, hidden sheets, veryHidden sheets, stale sheets, cross-project sheets,
macros, external links, denied named ranges, private absolute paths, completed
target drawings, reviewer evidence, and expected answers.

Deterministic prerequisites: file hash matches inventory; worksheet fingerprint
matches inventory; only visible approved worksheets are included; formulas with
unapproved dependencies are not recalculated.

Result schema: `schemas/sanitized_source_manifest.schema.json`.

Fail-closed conditions: source mutation, missing approval, hidden/denied
content, original workbook copied, absolute path leak, symlink, shortcut,
junction, path traversal, forbidden sentinel, or verification hash mismatch.

Completion criteria: bundle contains manifest, approval manifest, provenance
map, visible-file manifest, sanitized artifacts, readable previews,
verification results, and bundle hashes; verification status is `PASS`.

Synthetic examples only: a clean synthetic sheet becomes CSV plus preview; a
synthetic hidden sheet never enters the bundle.
