# Current State

Current phase: cycle-000 Phase A evaluator-sensitivity qualification completed.

Accepted release: none.

Current candidate: evaluation-only six-project calibration harness evidence plus evaluator-mechanics fix.

Current status: `EVALUATOR_SENSITIVITY_PASS - READY_FOR_24_PROJECT_BASELINE_PROTOCOL`.

Evaluator version for future cycle-000 work: `plc_layout_evaluator_v2_sensitivity` using `evals/grading_profiles/plc_layout_v2.json`.

Six-project set: 1110101, 1110104, 1110204, 1110205, 1110405, 1110410.

Portfolio result: mean score `42`, median `42`, minimum `42`, mean scorable coverage `38`; validity rate `100%`; critical findings `0`; high findings `36` across primary reviews.

Evaluator-sensitivity result: original calibration evaluator mechanics wrote `42/38` as constants in `scripts/compare_one_project.py`; this was fixed by `scripts/evaluator_scoring.py`. The twelve frozen calibration outputs were rescored into `reports/evaluator-sensitivity/rescored_runs/`; v2 recomputation preserves score `42` and coverage `38` from explicit scoring records, dimension arithmetic, and coverage denominators.

Independent sensitivity audit: `reports/evaluator-sensitivity/subagent_independent_audit.json` reports `EVALUATOR_SENSITIVITY_PASS`.

Recommendations remain PROPOSED. No drawing-generation behavior, accepted Instructions, production Knowledge, extraction logic, schemas, renderer behavior, validation behavior, grading weights, or tolerance profiles were optimized.

Exact next action: begin Phase B by freezing `docs/specs/24_PROJECT_BASELINE_PROTOCOL.md` and `evals/baseline-024/*` protocol manifests before any 24-project source backfill or generation.
