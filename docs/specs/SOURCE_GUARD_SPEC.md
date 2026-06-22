# Source Guard Spec

Status: PH1.5 calibration draft plus autonomous evaluation-only amendment.

The source guard converts inventory rows into file-and-worksheet review
decisions. It never approves evidence by model confidence alone.

## Decision States

- `UNREVIEWED`: inventory exists but no policy decision has been applied.
- `AUTO_DENIED`: deterministic forbidden or unsafe condition.
- `PARSER_REQUIRED`: deterministic parser support is missing or failed.
- `QUARANTINED`: may be useful later but is unsafe for current calibration.
- `SUPERSEDED`: replaced by a newer approved item or revision relationship.
- `AGENT_QUORUM_APPROVED_EVAL`: deterministic source validation passed and all
  four independent source-review agents returned `ALLOW_EVAL` for the same
  current file hash, worksheet fingerprint, and project identity.
- `ALLOWED_EVAL`: evaluation-only sanitized bundle passed verification and
  independent audit. Only sanitized artifacts in that bundle may enter a
  historical mock generator workspace.
- `ALLOWED_PRODUCTION`: explicit human approval remains required.
- `CANDIDATE`: legacy/intermediate state; may be reviewable after all integrity
  checks pass.
- `NEEDS_HUMAN_REVIEW`: legacy manual-review state. It remains fail-closed for
  production, but may enter the autonomous evaluation-only quorum path when no
  deterministic denial or quarantine condition exists.
- `HUMAN_APPROVED`: explicit human approval was recorded.
- `HUMAN_DENIED`: explicit human denial was recorded.
- `ALLOWED`: legacy alias for the human-production path. New artifacts must use
  `ALLOWED_EVAL` or `ALLOWED_PRODUCTION`.

No real source item receives production approval during PH1.5. Blank decision
cells are not approvals. The blank human decision CSV is preserved as
historical evidence, but the manual-edit gate is superseded for evaluation-only
trials by `docs/specs/AUTONOMOUS_EVAL_SOURCE_APPROVAL.md`.

## Automatic Denial

The guard denies generator access to items beneath `生管文件`, beneath
`電機施工圖`, completed target drawings, target modifications/revisions,
review/evaluation artifacts, known completed-reference sentinels, other-project
worksheets, mutated files, items outside `SRC-ALL-PROJECTS`, unsupported
objects masquerading as inputs, or anything that cannot be safely sanitized.

## Worksheet Fingerprint

For supported `.xlsx`/`.xlsm` files, the fingerprint payload contains:

- sheet name and visibility;
- workbook sheet count;
- used-range dimensions;
- normalized visible-cell content as `(coordinate, type, normalized value)`;
- merged ranges;
- formula locations and normalized formula text;
- workbook defined-name references touching the sheet;
- identity-like cells containing project IDs, dates, or known document labels.

The payload is serialized as UTF-8 JSON with sorted keys and hashed with
SHA-256. Legacy `.xls` receives `PARSER_REQUIRED` and no approving fingerprint.

## Human Review

Review packets expose only candidate input evidence: project identity, file
hashes, worksheet metadata, role, parser status, warnings, reason codes,
limited inventory-derived previews, and explicit approval instructions. They do
not include completed-reference images, completed dimensions, reviewer findings,
scores, or comparison evidence.
