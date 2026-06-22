# Source Guard Spec

Status: PH1.5 calibration draft.

The source guard converts inventory rows into file-and-worksheet review
decisions. It never approves evidence by model confidence alone.

## Decision States

- `UNREVIEWED`: inventory exists but no policy decision has been applied.
- `AUTO_DENIED`: deterministic forbidden or unsafe condition.
- `CANDIDATE`: may be reviewable after all integrity checks pass.
- `NEEDS_HUMAN_REVIEW`: potentially useful, but insufficient for automation.
- `PARSER_REQUIRED`: deterministic parser support is missing or failed.
- `SUPERSEDED`: replaced by a newer approved item or revision relationship.
- `QUARANTINED`: may be useful later but is unsafe for current calibration.
- `HUMAN_APPROVED`: explicit human approval was recorded.
- `HUMAN_DENIED`: explicit human denial was recorded.
- `ALLOWED`: derived final state only after human approval, current hash,
  current worksheet fingerprint, sanitization, and bundle verification pass.

No real source item receives `ALLOWED` during PH1.5. Blank decision cells are
not approvals.

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

