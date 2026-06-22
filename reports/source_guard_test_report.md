# Source Guard Test Report

Status: PASS for synthetic harness only. Real generation remains blocked.

Command:

`C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/run_tests.py`

Result:

- 10 repository tests passed.
- 3 expected negative subprocess fixtures printed `FAIL` while validating fail-closed behavior.
- 0 real project generator runs were started.
- 0 real source items were marked `ALLOWED`.
- Blank human decisions failed validation as expected, with `approved_count=0`.

PH1.5 source-guard coverage added:

- hidden and very-hidden worksheet quarantine;
- formula dependency quarantine;
- external-link and named-range quarantine;
- macro-enabled workbook quarantine;
- legacy `.xls` parser-required blocking;
- source hash mutation denial;
- blank human decision denial;
- worksheet fingerprint tamper denial;
- sanitized bundle verification failure on source-path and target-output leaks.

Evidence files:

- `reports/harness/phase1_5_test_output.txt`
- `reports/source_review_batches/batch-001/blank_decision_validation.json`
- `reports/harness/phase1_5_child_result_validation.json`
