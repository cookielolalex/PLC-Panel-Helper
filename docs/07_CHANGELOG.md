# Changelog

## 2026-06-22

- Initialized repository from the master bootstrap specification.
- Added Phase 0 scaffold, source-root records, agent definitions, schemas,
  scripts, fixtures, and orchestration task briefs.
- Ran synthetic Phase 0 harness tests and validated required child result
  schemas. Phase 0 remains blocked by missing exact declared source roots.
- Accepted the user-provided consolidated project source root and generated
  read-only file, worksheet, and project manifests without creating a generator
  bundle or starting a baseline.
- Added project-local CAD/catalog candidate indexes while keeping canonical
  reusable library roots unapproved.
- Passed `PH0-SOURCE-UPDATE-AUDIT` and `PH1-INVENTORY-AUDIT`; no generator
  bundle or real-project baseline was started.
- Added PH1.5 fail-closed source-guard schemas, policy, review-batch builder,
  approval validator, sanitized bundle builder, bundle verifier, and synthetic
  regression tests.
- Generated `reports/source_review_batches/batch-001/` for 12 historical
  reference-complete calibration projects because active year 115 has no
  all-three-completed-target projects. The packet has 56 candidate files, 69
  candidate worksheets, and 0 allowed items.
- Validated all four PH1.5 child results and reran the synthetic harness. Blank
  human decisions fail closed with `approved_count=0`.
