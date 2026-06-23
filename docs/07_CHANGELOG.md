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
- Ran the independent PH1.5 source-guard audit. The audit is schema-valid
  `NOT_VERIFIED` with domain status `PH1_5_SOURCE_GUARD_AUDIT_INCONCLUSIVE`:
  substantive source-guard checks passed, but the auditor could not verify the
  Git commit with its available tools. Added a coordinator Git verification
  addendum without changing the independent audit result.
- Added autonomous evaluation-only source approval policy, states, custom
  agents, Skills, and schemas while preserving the production human-approval
  requirement.
- Processed the five current-parser candidates from `batch-001`; 15 items
  reached `AGENT_QUORUM_APPROVED_EVAL`, five projects reached `ALLOWED_EVAL`,
  and the independent source-bundle audit passed.
- Activated and independently audited the codex_proxy synthetic gate with 12
  passing fixtures.
- Selected project `1110104`, ran exactly one accepted blind historical mock
  calibration after preserving one failed attempt, produced reviewer-only
  comparison evidence, and recorded a project reviewer result.
- Ran the final one-project independent audit. Result:
  `STEP_7C_AUDIT_PASS - READY_FOR_SIX_PROJECT_BASELINE`. No six-project trial
  was started.

## 2026-06-23

- Ran autonomous six-project reviewer and stability calibration as `calibration-006`.
- Backfilled project `1110101` using a local deterministic legacy `.xls` parser and evaluation-only source quorum.
- Completed 12 fresh generation runs, 12 primary reviews, 6 secondary reviews, portfolio analysis, and independent audit.
- Stopped before drawing-workflow optimization and before any 24-project baseline.
- Began cycle-000 Phase A evaluator-sensitivity qualification.
- Identified the original calibration scorer as writing `quality_score=42` and `scorable_coverage=38` directly.
- Added the failing evaluator-sensitivity regression before implementing `plc_layout_evaluator_v2_sensitivity`.
- Added `scripts/evaluator_scoring.py`, `evals/grading_profiles/plc_layout_v2.json`, counterfactual fixtures, and Phase A reports under `reports/evaluator-sensitivity/`.
- Rescored the 12 frozen calibration outputs with v2; scores remain `42/38`, now from explicit scoring records and coverage arithmetic.
- Completed fresh independent evaluator-sensitivity audit with result `EVALUATOR_SENSITIVITY_PASS`.
- Froze the cycle-000 24-project baseline protocol as `FROZEN_PROTOCOL_V1` with seed `BASELINE024-CYCLE000-20260623`.
- Added `evals/baseline-024/` protocol manifests for cohort placeholders, workflow hashes, source readiness, and the four-wave run plan.
- Stopped before Phase C source backfill and before any 24-project generation; 18 additional verified `ALLOWED_EVAL` projects are still required.
- Began Phase C source backfill with `baseline-024` batch-001.
- Ran deterministic prefiltering, four independent specialist reviews, quorum adjudication, sanitized bundle verification, and independent source-bundle audit for six candidate projects.
- Accepted `1110801` and `1120207` as evaluation-only additions; preserved verifier rejections for `1120101`, `1120204`, and `1120301`; left `1120201` quarantined/no-bundle.
- Current baseline-024 `ALLOWED_EVAL` count is `8`; generation remains blocked.
- Continued Phase C source backfill with `baseline-024` batch-002.
- Ran deterministic prefiltering, four independent specialist reviews, quorum adjudication, sanitized bundle verification, and independent source-bundle audit for six more candidate projects.
- Accepted `1110103`, `1110203`, and `1120308` as evaluation-only additions; preserved verifier rejections for `1110404` and `1120202`; left `1120309` quarantined/no-bundle.
- Current baseline-024 `ALLOWED_EVAL` count is `11`; generation remains blocked.
- Continued Phase C source backfill with `baseline-024` batch-003.
- Ran deterministic prefiltering, four independent specialist reviews, quorum adjudication, sanitized bundle verification, and independent source-bundle audit for six more candidate projects.
- Accepted `1110704` and `1120305` as evaluation-only additions; preserved verifier rejection for `1110701`; left `1110402`, `1110706`, and `1120102` no-bundle/quarantined.
- Current baseline-024 `ALLOWED_EVAL` count is `13`; generation remains blocked.
