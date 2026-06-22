# Batch 001 Selection Compliance Report

Status: `BATCH_001_SELECTION_CONFIRMED`

Scope: narrow metadata-only compliance review of `batch-001`. This review did
not run a generator, did not modify source roots, did not inspect completed
reference PDF contents, and did not open source workbooks. Evidence was limited
to repository manifests, source-guard scripts, batch artifacts, canonical state,
task results, and ledgers.

## Evidence Read

- `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`
- `AGENTS.md`
- `docs/01_CURRENT_STATE.md`
- `docs/04_DECISION_LEDGER.md`
- `docs/05_EVAL_SUITE.md`
- `docs/06_EVAL_LEDGER.md`
- `docs/SESSION_CHECKPOINT.md`
- `docs/SOURCE_ROOTS.md`
- `orchestration/TASK_REGISTRY.csv`
- `orchestration/results/PH1_5-SOURCE-GUARD-POLICY.json`
- `orchestration/results/PH1_5-SOURCE-GUARD-IMPLEMENTATION.json`
- `orchestration/results/PH1_5-SOURCE-GUARD-AUDIT.json`
- `reports/PH1_5_SOURCE_GUARD_AUDIT.md`
- `reports/PH1_5_COORDINATOR_AUDIT_ADDENDUM.md`
- `reports/generator_eligibility_summary.md`
- `reports/source_review_batches/batch-001/batch_manifest.json`
- `reports/source_review_batches/batch-001/source_review_batch_001.csv`
- `scripts/build_source_review_batch.py`
- `scripts/source_guard.py`
- `scripts/build_sanitized_generator_bundle.py`
- `manifests/all_projects_project_manifest.csv`
- `manifests/all_projects_file_role_index.csv`
- `manifests/all_projects_workbook_sheet_index.csv`
- `manifests/115_project_manifest.csv`
- `manifests/115_file_role_index.csv`
- `manifests/115_workbook_sheet_index.csv`

## Summary Finding

No 115-prefixed project was selected because `batch-001` was implemented as a
reference-complete calibration review batch. The selector first filtered to
projects with both workbook evidence and `has_all_three_completed_targets=true`.
The active-year 115 inventory has workbook/review candidates, but it has zero
projects with all three completed target reference classes. Therefore no
115-prefixed project survived the implemented eligibility filter.

This confirms the batch-001 active-year exclusion. No batch-002 is created.

## Verification Answers

1. Project ID prefixes reliably indicate project year.

   Verified. Across 404 real project rows in
   `manifests/all_projects_project_manifest.csv`, the first three digits of
   `project_id` match the leading year folder in `project_path` for every row.
   Prefix counts and path-year counts both are: 111=33, 112=91, 113=120,
   114=118, 115=42. Mismatch count: 0.

2. Sufficient year-115 development candidates satisfied the metadata-level
   selection requirements.

   Under the implemented reference-complete calibration requirement: no.
   There are 42 active-year 115 projects, all 42 have workbook evidence and
   `WORKSHEET_REVIEW_REQUIRED` status, but 0 have
   `has_all_three_completed_targets=true`.

   Under a broader source-review-only interpretation, 115 has many candidates:
   42 workbook-review projects, 446 worksheet rows, 266 parsed worksheet rows,
   and 23 projects with at least one parsed visible human-review worksheet row.
   Those candidates were not enough for this batch because completed-output
   reference completeness was applied first.

3. Family-level cohort protection excluded the 115 candidates.

   No. The selector builds `eligible` before family checks. Since no 115 project
   met the reference-complete eligibility filter, family protection never had a
   chance to exclude a 115 project.

4. OneDrive availability, completed-output availability, or permitted-input
   availability excluded 115 projects.

   OneDrive availability did not exclude them. `SRC-ALL-PROJECTS` exists and
   the 115 inventory is present: 42 project rows, 606 file rows, and 446
   worksheet rows.

   Completed-output availability did exclude them. In 115 projects, completed
   production target references appear in 0 projects, completed punch target
   references appear in 0 projects, completed sheetmetal target references
   appear in 29 projects, and all-three completed targets appear in 0 projects.

   Permitted-input availability did not categorically exclude them. All 42 have
   workbook evidence and worksheet-review status, but no rows are currently
   `ALLOWED`; the whole repository remains fail-closed pending human approval.

5. The selection implementation accidentally favored older IDs.

   Partially yes. After filtering to reference-complete projects, each stratum
   helper sorts candidates by `(family already used, project_id)`, and backfill
   sorts by `project_id`. This favors older eligible IDs in the historical pool.
   It did not cause the absence of 115 projects because there were no
   reference-complete 115 projects to sort or backfill.

6. Any selected project belongs to checkpoint or final held-out cohorts.

   No explicit checkpoint or final held-out cohort assignments exist in the
   canonical evaluation files. `docs/05_EVAL_SUITE.md` says real-project
   baselines remain blocked and only one eligible development project can be
   used after calibration gates. `docs/06_EVAL_LEDGER.md` records no real
   evaluation runs. Therefore none of the twelve selected projects collides
   with an assigned checkpoint or final held-out cohort.

7. The twelve projects are sufficiently family-separated.

   Sufficient for a source-guard review packet, but not maximally separated.
   The selected set has 10 unique `family_id` values across 12 projects. The
   repeated family is `國倫水電`, appearing in projects 1110103, 1110405, and
   1110410. The selector protects families until 10 projects are selected, then
   allows seeded/backfill duplicates.

   Residual caveat: the reference-complete pool has 26 eligible projects across
   21 unique families, so a strict 12-unique-family selection was possible at
   the pool level. This caveat does not affect the 115 exclusion and does not
   create held-out leakage because no held-out cohorts are assigned yet.

8. How many selected projects could possibly form a complete sanitized
   calibration bundle using currently supported parsers.

   Five selected projects have at least one visible `.xlsx` worksheet row that
   was parsed with a worksheet fingerprint and is not parser-required,
   auto-denied, or quarantined:

   - 1110104
   - 1110204
   - 1110205
   - 1110405
   - 1110410

   Current complete bundles: 0. Human approvals remain zero and
   `blank_decision_validation.json` fails closed. The count of 5 is only the
   possible path count after future human approval using the current openpyxl
   parser path.

## Conclusion

The original absence of 115-prefixed projects is justified by completed-output
availability under the implemented reference-complete calibration selection.
The implementation does favor older IDs after that filter and is only partially
family-separated, but those caveats did not displace an eligible 115 case.

`BATCH_001_SELECTION_CONFIRMED`
