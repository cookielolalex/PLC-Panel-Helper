# Autonomous Evaluation-Only Source Approval

Status: accepted workflow amendment for historical mock evaluation only.

This policy supersedes the manual CSV edit gate for evaluation-only trials. It
does not authorize production use and does not weaken any existing fail-closed
source-guard rule.

## Boundary

`ALLOWED_PRODUCTION` continues to require explicit human approval. Automated
review can only produce `AGENT_QUORUM_APPROVED_EVAL` and then `ALLOWED_EVAL`
after sanitized-bundle verification and independent audit. Only `ALLOWED_EVAL`
sanitized artifacts may enter historical mock generator workspaces.

Completed target drawings remain reference evidence. They may never enter a
generator workspace, source-approval reviewer input, source-adjudication input,
or sanitized bundle.

The historical `reports/source_review_batches/batch-001/blank_human_decisions.csv`
is preserved as evidence. Blank rows still fail the human-production validator.
For evaluation-only trials, row-level manual approval is replaced by the quorum
process below.

## States

- `UNREVIEWED`: inventory exists but no current policy decision is final.
- `AUTO_DENIED`: deterministic forbidden or unsafe condition.
- `PARSER_REQUIRED`: deterministic parser support is missing or failed.
- `QUARANTINED`: unsafe, ambiguous, conflicted, or disagreed item.
- `SUPERSEDED`: replaced by a newer approved item or revision relationship.
- `AGENT_QUORUM_APPROVED_EVAL`: deterministic prefilter passed and all four
  independent reviewers voted `ALLOW_EVAL` on the same current hash,
  worksheet fingerprint, and project identity.
- `ALLOWED_EVAL`: a quorum-approved item is present only through a verified
  sanitized bundle that passed independent audit for evaluation-only use.
- `ALLOWED_PRODUCTION`: explicit human approval plus production release gates.

Legacy states such as `NEEDS_HUMAN_REVIEW`, `HUMAN_APPROVED`,
`HUMAN_DENIED`, and `ALLOWED` remain historical/production-path vocabulary.
They do not grant evaluation approval by themselves under this policy.

## Required Sequence

1. Deterministic source validation.
2. Four independent specialist reviews:
   `source_role_classifier`, `project_identity_reviewer`,
   `workbook_forensics_reviewer`, and `leakage_red_team`.
3. Unanimous agent quorum.
4. Separate adjudication.
5. Sanitized-bundle verification.
6. Independent audit.

No LLM reviewer can override a deterministic denial, parser-required condition,
source mutation, forbidden-source signal, hidden required sheet, stale or
cross-project signal, denied formula dependency, denied named range, or external
critical dependency.

## Reviewer Inputs

Reviewers may receive candidate permitted-input workbooks, source inventory
metadata, parser output, neutral project identity evidence, source-guard policy,
and synthetic examples.

Reviewers may not receive completed target PDF content, completed drawing
thumbnails, extracted completed drawing dimensions, expected answers, another
reviewer's result, adjudicator recommendations, proposed final approval status,
score reports, or optimization evidence.

## Quorum Rule

An item can become `AGENT_QUORUM_APPROVED_EVAL` only when:

- deterministic prefilter passed;
- all four reviewers returned `ALLOW_EVAL`;
- every result references the same current SHA-256;
- every result references the same worksheet fingerprint;
- every result references the same project identity;
- no critical issue is unresolved;
- no forbidden-source signal was detected;
- no stale or cross-project signal was detected;
- no superseded worksheet is required;
- no formula depends on denied content;
- no named range reaches denied content;
- no external source supplies a critical value;
- parser result is deterministic and supported.

Any disagreement becomes `QUARANTINED`. The user is not asked to resolve
evaluation-only disagreements.

## Bundle Rule

The original workbook is never copied into a generator workspace. A sanitized
bundle may contain only approved visible worksheet displayed values, approved
merged-cell structure, locally valid approved formulas, approved permitted
objects, neutral provenance IDs, readable previews, and machine-readable
normalized content.

The bundle must remove unapproved, hidden, veryHidden, stale, cross-project, and
superseded sheets; macros; external links; denied named ranges; denied embedded
objects; private absolute paths; review/reference evidence; and completed target
derivatives.

When a formula depends on unapproved content, the workflow must not recalculate
it. It may retain only a safely extracted cached value marked `UNVERIFIED` when
policy permits; otherwise the value is `HUMAN_REVIEW_REQUIRED`.
