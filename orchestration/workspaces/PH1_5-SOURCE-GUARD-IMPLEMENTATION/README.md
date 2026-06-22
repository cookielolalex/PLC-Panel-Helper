# PH1_5 Source Guard Implementation Proposal

This child workspace contains patch-ready implementation artifacts only. It
does not modify canonical schemas, scripts, tests, reports, manifests, or
source roots.

Observed inputs:

- `docs/01_CURRENT_STATE.md` says no real project evidence is
  generator-approved (`ALLOWED=0`) and the next action is a source-guard review
  workflow over `reports/manual_review_queue.csv`.
- `docs/SOURCE_ROOTS.md` marks `SRC-ALL-PROJECTS` read-only and explicitly
  forbids writes/extraction into declared source locations.
- `manifests/all_projects_file_role_index.csv` has 7,400 rows:
  5,001 `FORBIDDEN`, 2,399 `HUMAN_REVIEW_REQUIRED`, 0 `ALLOWED`.
- `manifests/all_projects_workbook_sheet_index.csv` has 4,231 rows:
  2,092 `FORBIDDEN`, 2,139 `HUMAN_REVIEW_REQUIRED`, 0 `ALLOWED`.
- `manifests/115_file_role_index.csv` has 606 rows:
  328 `FORBIDDEN`, 278 `HUMAN_REVIEW_REQUIRED`, 0 `ALLOWED`.
- `manifests/115_workbook_sheet_index.csv` has 446 rows:
  194 `FORBIDDEN`, 252 `HUMAN_REVIEW_REQUIRED`, 0 `ALLOWED`.

Implementation notes:

1. Add a source review batch schema and builder that converts the manual
   review queue into a reviewer-safe JSON/CSV batch. The batch contains manifest
   metadata only, never copied source files and never generated bundle content.
2. Add a source approval schema and validator. Human approvals must be explicit,
   signed, bound to current index file hashes, and bound to per-row hashes. Any
   stale hash, forbidden role, forbidden source, unsupported workbook extension,
   hidden/stale worksheet, or missing matching workbook fails closed.
3. Add a sanitized bundle manifest schema plus builder/verifier. The builder
   consumes only a validated approval document; the verifier rejects absolute
   source paths, symlinks/junctions, forbidden roles, target-like output names,
   hash mismatches, and unapproved bundle entries.
4. Keep the existing `build_generator_bundle.py` behavior behind the new guard
   by replacing direct manifest eligibility checks with validated approval
   checks before any file copy. The proposed patch adds a new guarded builder
   instead of altering the current one in place, so the coordinator can switch
   over after review.
5. Add synthetic regression tests before wiring the guard into production
   workflow. The tests use temporary synthetic indexes only; they do not mark
   real manifest items `ALLOWED` and do not create a real generator bundle.

Patch/rollback:

- Apply candidate patch from `patches/source_guard_implementation.patch` from
  repository root after independent review.
- Rollback is removal of the added files and removal of the added source-guard
  test call from `scripts/run_tests.py`; no existing source roots, manifests, or
  run evidence are changed by this proposal.

