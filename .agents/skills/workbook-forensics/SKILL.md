# Workbook Forensics

Trigger: inspect workbook parser/package risks before evaluation-only approval.

Permitted inputs: candidate permitted-input workbooks, parser output,
inventory metadata, source-guard policy, task brief, and synthetic examples.

Forbidden inputs: completed target drawings, target thumbnails, target hashes,
expected answers, reviewer findings, comparison evidence, other reviewer
results, and adjudicator recommendations.

Deterministic prerequisites: macros are never executed; workbook parser has a
known deterministic result; file hash matches inventory.

Result schema: `schemas/source_quorum_review.schema.json`.

Fail-closed conditions: hidden or veryHidden required sheet, macro-required
content, unsupported objects required for critical values, external critical
dependency, denied named range, formula dependency on denied content, malformed
file, source mutation, or parser-required format.

Completion criteria: every item records visibility, formula, cached-value,
merged-cell, external-link, named-range, macro, and object risks with a final
decision.

Synthetic examples only: a visible no-link synthetic sheet may be `ALLOW_EVAL`;
a synthetic formula depending on a denied sheet is `QUARANTINE`; a legacy
synthetic `.xls` is `DENY` with `PARSER_REQUIRED`.
