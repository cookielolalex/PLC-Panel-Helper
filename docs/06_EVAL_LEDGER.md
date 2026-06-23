# Evaluation Ledger

## RUN-1110104-AUTO-EVAL-001

Status: `FAILED`.

Purpose: preserved failed first attempt for project `1110104`.

Result: codex_proxy child metadata did not create the expected last-message
parent path before invocation. No generated artifacts were accepted.

Evidence: `evals/runs/RUN-1110104-AUTO-EVAL-001/generation_complete.json`.

## RUN-1110104-AUTO-EVAL-002

Status: `PASS`.

Project: `1110104`.

Source authority: `ALLOWED_EVAL` sanitized bundle only. Completed references
were absent from the generator workspace and introduced only in the separate
reviewer workspace after generation freeze.

Generation: three required PDF output types attempted and validated; generated
binary PDFs remain ignored local artifacts.

Review result: validity `PASS`; quality score `42`; scorable coverage `38`;
confidence `LOW`; critical findings `0`; high findings `3`.

Independent audit: `STEP_7C_AUDIT_PASS - READY_FOR_SIX_PROJECT_BASELINE`.

Evidence: `evals/runs/RUN-1110104-AUTO-EVAL-002/generation_complete.json`,
`evals/runs/RUN-1110104-AUTO-EVAL-002/review/grading_result.json`,
`evals/runs/RUN-1110104-AUTO-EVAL-002/review/project_reviewer_result.json`,
and `evals/runs/RUN-1110104-AUTO-EVAL-002/audit/one_project_audit.json`.

## calibration-006

Status: `SIX_PROJECT_CALIBRATION_PASS - READY_FOR_24_PROJECT_BASELINE`.

Projects: `1110101, 1110104, 1110204, 1110205, 1110405, 1110410`.

Generation attempts: `12`; valid generation runs: `12`; primary reviews: `12`; secondary reviews: `6`.

Portfolio mean score: `42`; mean coverage: `38`; critical findings: `0`; high findings: `36`.

Evidence: `reports/calibration-006/calibration_summary.md`, `optimization/calibration-006/machine_summary.json`, and `reports/calibration-006/independent_audit.json`.

## cycle-000 Phase A evaluator-sensitivity

Status: `EVALUATOR_SENSITIVITY_PASS - READY_FOR_24_PROJECT_BASELINE_PROTOCOL`.

Purpose: qualify evaluator sensitivity before scaling from the six-project calibration set to the 24-project baseline.

Finding: original calibration reviewer mechanics wrote score `42` and coverage `38` as constants, so original `42/38` was an evaluator-mechanics defect rather than proven independent scoring.

Fix: added `plc_layout_evaluator_v2_sensitivity` with explicit scoring records, arithmetic dimension sums, coverage denominators, hard-gate overrides, low-coverage handling, and finding deduplication. Drawing-generation behavior was not changed.

Rescore result: all 12 frozen calibration runs rescore to score `42` and scorable coverage `38` under v2; validity remains `PASS`; critical findings remain `0`; high findings remain `36`.

Evidence: `reports/evaluator-sensitivity/calibration_score_recomputation.json`, `reports/evaluator-sensitivity/project_differentiation.json`, `reports/evaluator-sensitivity/counterfactual_results.json`, `reports/evaluator-sensitivity/test_results.json`, and `reports/evaluator-sensitivity/subagent_independent_audit.json`.

## baseline-024-cycle-000 Phase B protocol freeze

Status: `BASELINE024_PROTOCOL_FROZEN - PHASE_C_SOURCE_BACKFILL_PENDING`.

Purpose: freeze the rules for the first 24-project development baseline before source backfill or generation.

Frozen seed: `BASELINE024-CYCLE000-20260623`.

Evaluator: `plc_layout_evaluator_v2_sensitivity`.

Current cohort readiness: 6 `ALLOWED_EVAL` calibration anchors retained as fresh-run anchors; 18 additional project slots remain pending Phase C source backfill; metadata-only candidate pool contains 20 reference-complete non-anchor candidates; project `1110102` remains excluded until its prior bundle-verification defect is fixed, regression-tested, and independently audited.

Generation status: not authorized. Baseline generation may begin only after exactly 24 projects have verified `ALLOWED_EVAL` bundles and a final cohort manifest is frozen.

Evidence: `docs/specs/24_PROJECT_BASELINE_PROTOCOL.md`, `evals/baseline-024/cohort_manifest.json`, `evals/baseline-024/cohort_selection_report.md`, `evals/baseline-024/frozen_workflow_manifest.json`, `evals/baseline-024/source_readiness.json`, and `evals/baseline-024/run_plan.json`.

## baseline-024-cycle-000 Phase C batch-001 source backfill

Status: `PHASE_C_BATCH_001_AUDIT_PASS_CONTINUE_BACKFILL`.

Candidate projects: `1120101, 1120204, 1120301, 1110801, 1120207, 1120201`.

Accepted evaluation-only additions: `1110801, 1120207`.

Rejected or quarantined: `1120101, 1120204, 1120301` failed sanitized bundle verification on forbidden modification-content sentinel; `1120201` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 2 new Phase C additions, for 8 verified `ALLOWED_EVAL` projects. Sixteen additional verified projects are still required before generation.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_001.json`, and `reports/baseline-024/source_bundle_audit_batch_001_independent.json`.

## baseline-024-cycle-000 Phase C batch-002 source backfill

Status: `PHASE_C_BATCH_002_AUDIT_PASS_CONTINUE_BACKFILL`.

Candidate projects: `1120309, 1120202, 1120308, 1110103, 1110203, 1110404`.

Accepted evaluation-only additions: `1110103, 1110203, 1120308`.

Rejected or quarantined: `1110404` and `1120202` failed sanitized bundle verification on forbidden modification-content sentinel; `1120309` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 5 new Phase C additions, for 11 verified `ALLOWED_EVAL` projects. Thirteen additional verified projects are still required before generation.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_002.json`, and `reports/baseline-024/source_bundle_audit_batch_002_independent.json`.

## baseline-024-cycle-000 Phase C batch-003 source backfill

Status: `PHASE_C_BATCH_003_AUDIT_PASS_CONTINUE_BACKFILL`.

Candidate projects: `1110701, 1110704, 1110706, 1120305, 1110402, 1120102`.

Accepted evaluation-only additions: `1110704, 1120305`.

Rejected or quarantined: `1110701` failed sanitized bundle verification on forbidden modification-content sentinel; `1110402` had no reviewable items; `1110706` and `1120102` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 7 new Phase C additions, for 13 verified `ALLOWED_EVAL` projects. Eleven additional verified projects are still required before generation.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_003.json`, and `reports/baseline-024/source_bundle_audit_batch_003_independent.json`.

## baseline-024-cycle-000 Phase C batch-004 source backfill

Status: `BATCH004_SOURCE_BACKFILL_AUDIT_PASS_NO_ACCEPTED_BUNDLES`.

Candidate projects: `1110501, 1110504`.

Accepted evaluation-only additions: none.

Rejected or quarantined: `1110501` failed sanitized bundle verification on forbidden modification-content sentinel; `1110504` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 7 new Phase C additions, for 13 verified `ALLOWED_EVAL` projects. Eleven additional verified projects are still required, but the frozen metadata-only candidate pool is exhausted.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_004.json`, and `reports/baseline-024/source_bundle_audit_batch_004_independent.json`.

## baseline-024-cycle-000 Phase C shortfall

Status: `INSUFFICIENT_ELIGIBLE_PROJECTS_FOR_24_BASELINE`.

Processed frozen metadata-only candidates: `20 / 20`.

Accepted Phase C additions: `1110801, 1120207, 1110103, 1110203, 1120308, 1110704, 1120305`.

Bundle-verification rejected projects: `1120101, 1120204, 1120301, 1110404, 1120202, 1110701, 1110501`.

Quarantined/no-bundle projects: `1120201, 1120309, 1110402, 1110706, 1120102, 1110504`.

Generation attempts: `0`; valid baseline runs: `0`; primary reviews: `0`; secondary reviews: `0`.

Evidence: `reports/baseline-024/insufficient_eligible_projects_for_24_baseline.json` and `reports/baseline-024/insufficient_eligible_projects_for_24_baseline.md`.

## baseline-024-cycle-000 expanded discovery after D-0017

Status: `PRE_SOURCE_SCREENING_BLOCKED_BY_REFERENCE_PRESENCE`.

Purpose: supersede only the twenty-project metadata-only discovery cap and
reconcile the full approved development inventory under `SRC-ALL-PROJECTS`.

Inventory reconciliation: 404 project IDs and 404 physical project folders.

Target detection v2: 27 `VERIFIED_ALL_THREE` projects, all already accepted,
previously rejected, quarantined/no-bundle, or protocol-excluded. No completed
reference content was inspected during metadata target detection.

Expanded candidate registry: 0 `READY_FOR_SOURCE_SCREENING`; 269
`REFERENCE_PRESENCE_REVIEW_REQUIRED`.

Reference-presence waves: 18 top-ranked partial-reference projects reviewed in
three isolated waves. All remained `PARTIAL_REFERENCE_SET` with only sheet-metal
target evidence; 0 projects were promoted to all-three reference availability.

Generation status: not authorized. Source-review quorum and sanitized bundle
construction have not started for expanded candidates.

Evidence: `reports/baseline-024/expanded-screening/inventory_reconciliation_report.md`,
`reports/baseline-024/expanded-screening/target_detection_v2_report.md`,
`evals/baseline-024/expanded_candidate_selection_report.md`,
`reports/baseline-024/expanded-screening/screening_yield_summary.md`, and
`reports/baseline-024/expanded-screening/dominant_blockers.json`.
