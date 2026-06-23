# Current State

Current phase: cycle-000 Phase C expanded source discovery blocked before source screening.

Accepted release: none.

Current candidate: `baseline-024-cycle-000` Phase C source approvals.

Current status: `PRE_SOURCE_SCREENING_BLOCKED_BY_REFERENCE_PRESENCE`.

Accepted amendment: `D-0017` expands baseline-024 candidate discovery beyond
the prior twenty-project metadata-only pool to the full approved development
inventory under `SRC-ALL-PROJECTS`. This supersedes only the discovery cap; all
source immutability, source-root restrictions, positive allowlisting, reference
isolation, cohort isolation, parser, bundle-verification, independent-audit,
frozen workflow, and grading gates remain in force.

Evaluator version for future cycle-000 work: `plc_layout_evaluator_v2_sensitivity` using `evals/grading_profiles/plc_layout_v2.json`.

Six-project set: 1110101, 1110104, 1110204, 1110205, 1110405, 1110410.

Baseline-024 status: six calibration anchors are retained as fresh-run anchors. Batch-001 added `1110801` and `1120207`; batch-002 added `1110103`, `1110203`, and `1120308`; batch-003 added `1110704` and `1120305`; batch-004 added no projects. The frozen metadata-only candidate pool is exhausted at `13` verified `ALLOWED_EVAL` projects, with `11` still required. No 24-project generation is authorized.

Portfolio result: mean score `42`, median `42`, minimum `42`, mean scorable coverage `38`; validity rate `100%`; critical findings `0`; high findings `36` across primary reviews.

Evaluator-sensitivity result: original calibration evaluator mechanics wrote `42/38` as constants in `scripts/compare_one_project.py`; this was fixed by `scripts/evaluator_scoring.py`. The twelve frozen calibration outputs were rescored into `reports/evaluator-sensitivity/rescored_runs/`; v2 recomputation preserves score `42` and coverage `38` from explicit scoring records, dimension arithmetic, and coverage denominators.

Independent sensitivity audit: `reports/evaluator-sensitivity/subagent_independent_audit.json` reports `EVALUATOR_SENSITIVITY_PASS`.

Frozen Phase B evidence: `docs/specs/24_PROJECT_BASELINE_PROTOCOL.md`, `evals/baseline-024/cohort_manifest.json`, `evals/baseline-024/cohort_selection_report.md`, `evals/baseline-024/frozen_workflow_manifest.json`, `evals/baseline-024/source_readiness.json`, and `evals/baseline-024/run_plan.json`.

Phase C batch evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/insufficient_eligible_projects_for_24_baseline.json`, `reports/baseline-024/source_bundle_audit_batch_001_independent.json`, `reports/baseline-024/source_bundle_audit_batch_002_independent.json`, `reports/baseline-024/source_bundle_audit_batch_003_independent.json`, and `reports/baseline-024/source_bundle_audit_batch_004_independent.json`. Batch-001 verifier rejected `1120101`, `1120204`, and `1120301`; `1120201` remained quarantined/no-bundle. Batch-002 verifier rejected `1110404` and `1120202`; `1120309` remained quarantined/no-bundle. Batch-003 verifier rejected `1110701`; `1110402`, `1110706`, and `1120102` remained no-bundle/quarantined. Batch-004 verifier rejected `1110501`; `1110504` remained quarantined/no-bundle.

Recommendations remain PROPOSED. No drawing-generation behavior, accepted Instructions, production Knowledge, extraction logic, schemas, renderer behavior, validation behavior, grading weights, or tolerance profiles were optimized.

Expanded screening result: full inventory reconciliation found 404 project IDs
and 404 physical project folders. Metadata target detection v2 produced 27
`VERIFIED_ALL_THREE` projects, all already accepted, rejected, quarantined, or
protocol-excluded. The expanded candidate registry therefore has 0
`READY_FOR_SOURCE_SCREENING` projects and 269 projects requiring reference
presence review. Three isolated reference-presence waves reviewed the top 18
partial-reference projects; all remained `PARTIAL_REFERENCE_SET` with only
sheet-metal target evidence.

Exact next action: do not start source screening or baseline generation. Resume
only at the reference-presence layer: either continue isolated reference review
with improved, auditable target classification, or make a proposal-first detector
improvement with regression coverage and independent review. Do not weaken the
all-three completed-target requirement.
