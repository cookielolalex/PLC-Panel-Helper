# Current State

Current phase: cycle-000 Phase B 24-project baseline protocol frozen.

Accepted release: none.

Current candidate: `baseline-024-cycle-000` protocol manifests.

Current status: `BASELINE024_PROTOCOL_FROZEN - PHASE_C_SOURCE_BACKFILL_PENDING`.

Evaluator version for future cycle-000 work: `plc_layout_evaluator_v2_sensitivity` using `evals/grading_profiles/plc_layout_v2.json`.

Six-project set: 1110101, 1110104, 1110204, 1110205, 1110405, 1110410.

Baseline-024 status: six calibration anchors are retained as fresh-run anchors, eighteen additional project slots remain `PENDING_PHASE_C_SOURCE_BACKFILL`, and no 24-project generation is authorized until exactly 24 projects reach verified `ALLOWED_EVAL`.

Portfolio result: mean score `42`, median `42`, minimum `42`, mean scorable coverage `38`; validity rate `100%`; critical findings `0`; high findings `36` across primary reviews.

Evaluator-sensitivity result: original calibration evaluator mechanics wrote `42/38` as constants in `scripts/compare_one_project.py`; this was fixed by `scripts/evaluator_scoring.py`. The twelve frozen calibration outputs were rescored into `reports/evaluator-sensitivity/rescored_runs/`; v2 recomputation preserves score `42` and coverage `38` from explicit scoring records, dimension arithmetic, and coverage denominators.

Independent sensitivity audit: `reports/evaluator-sensitivity/subagent_independent_audit.json` reports `EVALUATOR_SENSITIVITY_PASS`.

Frozen Phase B evidence: `docs/specs/24_PROJECT_BASELINE_PROTOCOL.md`, `evals/baseline-024/cohort_manifest.json`, `evals/baseline-024/cohort_selection_report.md`, `evals/baseline-024/frozen_workflow_manifest.json`, `evals/baseline-024/source_readiness.json`, and `evals/baseline-024/run_plan.json`.

Recommendations remain PROPOSED. No drawing-generation behavior, accepted Instructions, production Knowledge, extraction logic, schemas, renderer behavior, validation behavior, grading weights, or tolerance profiles were optimized.

Exact next action: begin Phase C source backfill in batches, using deterministic prefiltering, four independent specialist reviews, source adjudication, sanitized bundle construction, bundle verification, and independent audit before any generation.
