# PH1.5 Source Guard Independent Audit

Task ID: `PH1_5-SOURCE-GUARD-AUDIT`

Role: independent auditor.

Timebox: 20 minutes.

Repository commit to audit: `0a944ec` (`Implement PH1.5 source guard review workflow`).

Allowed read paths:

- `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`
- `AGENTS.md`
- `docs/01_CURRENT_STATE.md`
- `docs/04_DECISION_LEDGER.md`
- `docs/07_CHANGELOG.md`
- `docs/SESSION_CHECKPOINT.md`
- `docs/specs/GENERATOR_INPUT_POLICY.md`
- `docs/specs/EVALUATION_HARNESS_SPEC.md`
- `docs/specs/SOURCE_GUARD_SPEC.md`
- `docs/specs/SANITIZED_GENERATOR_BUNDLE_SPEC.md`
- `docs/SOURCE_ROOTS.md`
- `manifests/source_guard/`
- `reports/source_review_batches/batch-001/`
- `reports/source_guard_coverage_summary.json`
- `reports/source_guard_coverage_summary.md`
- `reports/source_guard_test_report.md`
- `reports/harness/phase1_5_child_result_validation.json`
- `reports/harness/phase1_5_test_output.txt`
- `reports/source_hash_reverification.json`
- `schemas/`
- `scripts/source_guard.py`
- `scripts/build_source_review_batch.py`
- `scripts/validate_source_approval.py`
- `scripts/build_sanitized_generator_bundle.py`
- `scripts/verify_generator_bundle.py`
- `scripts/run_tests.py`
- `tests/source_guard/`
- `evals/fixtures/source_guard/`
- `orchestration/results/PH1_5-*.json`
- `orchestration/TASK_REGISTRY.csv`

Allowed write paths:

- `orchestration/results/PH1_5-SOURCE-GUARD-AUDIT.json`
- `reports/PH1_5_SOURCE_GUARD_AUDIT.md`

Forbidden paths and actions:

- Do not read, list, or hash `C:\Users\alex1\OneDrive\Desktop\All Projects`.
- Do not inspect completed or modified target drawings.
- Do not read `生管文件`, `電機施工圖`, completed target drawings, modified target drawings, `evals/references/`, or `evals/runs/`.
- Do not run a real generator, build a real generator bundle, mark any source row `ALLOWED`, modify repository code, use web/network APIs, or create a top-level Codex thread.

Audit checklist:

1. Verify the master spec hash is recorded as `EBA9A30139A43862A7705F3123B050245DFA47FE3234D6A4E7579C6213E8FF09`.
2. Verify the PH1.5 child result validation report is PASS and all four child results are schema-valid.
3. Verify source-hash reverification passed before review packet construction.
4. Verify `batch-001` has exactly the 12 selected project IDs and the reported counts.
5. Verify real source approvals remain zero: no `ALLOWED` rows and `blank_decision_validation.json` has `status=FAIL` and `approved_count=0`.
6. Verify source-guard scripts fail closed for hidden sheets, stale/mutated hashes, parser-required `.xls`, macro `.xlsm`, formula/named-range/external-link risks, approval tampering, and bundle leakage.
7. Verify no generator output, real baseline, or real sanitized bundle was produced.
8. Identify any blocking defect or residual risk.

Required result JSON schema shape:

```json
{
  "task_id": "PH1_5-SOURCE-GUARD-AUDIT",
  "agent_type": "independent_auditor",
  "status": "PH1_5_SOURCE_GUARD_AUDIT_PASS | PH1_5_SOURCE_GUARD_AUDIT_FAIL | PH1_5_SOURCE_GUARD_AUDIT_INCONCLUSIVE",
  "checks": [
    {"criterion": "string", "status": "PASS | FAIL | NOT_VERIFIED", "evidence": "string"}
  ],
  "artifacts": ["orchestration/results/PH1_5-SOURCE-GUARD-AUDIT.json", "reports/PH1_5_SOURCE_GUARD_AUDIT.md"],
  "hashes": {"path": "SHA256"},
  "summary": "string",
  "blockers": ["string"]
}
```

Completion criteria:

- Write the JSON result and Markdown report.
- Cite file paths and hashes for evidence.
- Use PASS only if all blocking checklist items pass.
