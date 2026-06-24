# SMV1 T1 Independent Recovery Audit Task Brief

Task ID: `SMV1-T1-INDEPENDENT-RECOVERY-AUDIT`
Agent type: `independent_auditor`
Starting commit: `bc02f7d`
Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`

Perform a read-only independent audit of the T1 targeted coverage recovery
results and integration conclusion. The audit must decide whether the T1 stage
is a safe unresolved source/rule authority gap, whether any worker introduced
privacy leakage or unsupported fabrication assertions, and whether the
coordinator may proceed to a proposal-first source/rule approval branch.

Required checks:

1. Parse all T1 worker child-result JSON files and the T1 integration JSON.
2. Verify the three T1 workers made no implementation changes and did not
   generate customer PDF, DXF, DWG, or completed-reference derivatives.
3. Verify panel assignment, component geometry, topology, sizing, and placement
   coverage remained source-limited and were not reported as capability success.
4. Verify the blocker taxonomy is consistent with approved-source-only rules.
5. Verify no private values, source-root paths, completed-reference details, or
   post-design evidence were committed in the T1 reports.
6. Run available JSON parse checks and, if the local runtime allows, run
   `scripts/run_tests.py` and scoped frozen workflow verification.
7. Emit an explicit PASS, FAIL, or INCONCLUSIVE outcome with exact blockers.

Allowed write scope:

- `reports/sheetmetal-v1/t1-coverage-recovery/t1_independent_recovery_audit.json`
- `reports/sheetmetal-v1/t1-coverage-recovery/t1_independent_recovery_audit.md`
- `orchestration/master/child-results/SMV1-T1-INDEPENDENT-RECOVERY-AUDIT.json`

Forbidden actions:

- Do not edit implementation code, docs ledgers, canonical state, tests,
  schemas, frozen releases, frozen graders, or source manifests.
- Do not open or copy source roots, `.private`, completed target drawings,
  post-design files, customer PDFs, customer DXFs, customer DWGs, thumbnails,
  extracted target text, reviewer answers, scores, or reference details.
- Do not execute, stage, or modify
  `scripts/run_reference_detection_v4_corpus_screening.py`.
- Do not use public web or transmit private project context.
- Do not declare `PRODUCTION_APPROVED`.

Required result structure:

- Include task id, starting commit, ending commit or observed HEAD, visible file
  manifest path, parsed inputs, hard gate verdicts, coverage verdicts, privacy
  leakage counts, tests run or not run with reasons, hashes for each output,
  final status, recommended next action, trajectory, and any residual risks.
