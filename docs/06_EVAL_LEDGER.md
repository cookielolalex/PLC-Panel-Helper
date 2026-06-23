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
