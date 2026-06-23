# Current State

Current phase: cycle-000 reference detection v3 exhausted before source screening.

Accepted release: none.

Current candidate: `baseline-024-cycle-000` reference-complete project discovery.

Current status: `REFERENCE_REVIEW_UNIVERSE_EXHAUSTED - INSUFFICIENT_REFERENCE_COMPLETE_PROJECTS`.

Accepted amendments: `D-0017` expands baseline-024 candidate discovery beyond
the prior twenty-project metadata-only pool to the full approved development
inventory under `SRC-ALL-PROJECTS`; `D-0018` accepts
`target_output_detection_v3_page_content_isolated` as content-aware,
page-level, reference-vault-only classification. These amendments do not weaken
source immutability, source-root restrictions, positive source allowlisting,
evaluation-only quorum, reference isolation, cohort isolation, held-out
protection, parser requirements, sanitized-bundle verification, independent
auditing, frozen workflow requirements, grading rules, or no-invention
requirements.

Evaluator version for future cycle-000 work: `plc_layout_evaluator_v2_sensitivity` using `evals/grading_profiles/plc_layout_v2.json`.

Six-project set: 1110101, 1110104, 1110204, 1110205, 1110405, 1110410.

Baseline-024 status: six calibration anchors are retained as fresh-run anchors.
Batch-001 added `1110801` and `1120207`; batch-002 added `1110103`,
`1110203`, and `1120308`; batch-003 added `1110704` and `1120305`;
batch-004 added no projects. Current verified `ALLOWED_EVAL` count remains
`13 / 24`. No 24-project generation is authorized.

Reference detection v3 result: all 103 reference-review-required families have
at least one v3 page-level representative, plus 24 additional ranked
non-representative projects. The v3 pass processed 129 projects, 1849 PDFs, and
9031 pages. It found 0 newly verified all-three projects, 129 partial projects,
0 ambiguous projects, 0 combined packages, 0 revision supersession packages,
1644 image-only-or-no-target-text PDFs, and 205 embedded-text PDFs. All batches
returned `REFERENCE_PRESENCE_BATCH_AUDIT_PASS`.

Generator and source status: no expanded-candidate source-review quorum,
sanitized-bundle construction, final cohort freeze, baseline generation, review,
drawing-workflow optimization, or production approval occurred. Baseline
generation attempts remain `0`.

Portfolio result: mean score `42`, median `42`, minimum `42`, mean scorable
coverage `38`; validity rate `100%`; critical findings `0`; high findings `36`
across primary reviews.

Evaluator-sensitivity result: original calibration evaluator mechanics wrote
`42/38` as constants in `scripts/compare_one_project.py`; this was fixed by
`scripts/evaluator_scoring.py`. The twelve frozen calibration outputs were
rescored into `reports/evaluator-sensitivity/rescored_runs/`; v2 recomputation
preserves score `42` and coverage `38` from explicit scoring records, dimension
arithmetic, and coverage denominators.

Independent sensitivity audit: `reports/evaluator-sensitivity/subagent_independent_audit.json` reports `EVALUATOR_SENSITIVITY_PASS`.

Frozen Phase B evidence: `docs/specs/24_PROJECT_BASELINE_PROTOCOL.md`,
`evals/baseline-024/cohort_manifest.json`,
`evals/baseline-024/cohort_selection_report.md`,
`evals/baseline-024/frozen_workflow_manifest.json`,
`evals/baseline-024/source_readiness.json`, and
`evals/baseline-024/run_plan.json`.

Phase C source-backfill evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`,
`reports/baseline-024/source_backfill_summary.md`,
`reports/baseline-024/source_bundle_audit.json`,
`reports/baseline-024/insufficient_eligible_projects_for_24_baseline.json`,
and the four batch independent audits under `reports/baseline-024/`.

Reference detection v3 evidence: `docs/specs/REFERENCE_VAULT_BOUNDARY_SPEC.md`,
`docs/specs/REFERENCE_PRESENCE_DETECTION_V3.md`,
`reports/baseline-024/reference-detection-v3/v2_zero_promotion_diagnosis.json`,
`reports/baseline-024/reference-detection-v3/screening_yield.md`,
`reports/baseline-024/reference-detection-v3/batch_results/`,
`manifests/reference_detection/v3/`, and
`reports/baseline-024/reference-detection-v3/independent_audit.json`.

Recommendations remain PROPOSED. No drawing-generation behavior, accepted
Instructions, production Knowledge, extraction logic, renderer behavior,
validation behavior, grading weights, or tolerance profiles were optimized.

Exact next action: do not start source screening or baseline generation from
the v3 results. Resume only if the user authorizes a new policy amendment,
additional evidence acquisition, or a different baseline strategy; otherwise
the automated status remains `REFERENCE_REVIEW_UNIVERSE_EXHAUSTED -
INSUFFICIENT_REFERENCE_COMPLETE_PROJECTS`.
