# Source Guard Tests

The PH1.5 source-guard tests live in `scripts/run_tests.py` so they run with the repository bootstrap harness.

Current cases cover fail-closed source decisions, approval validation, and sanitized bundle verification. All fixtures are synthetic and generated under `tmp/`; no real project workbook, completed target drawing, reference PDF, or source-root file is copied into this test directory.

Run:

`C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/run_tests.py`

Expected status is repository-level `PASS`. Some subprocesses intentionally print `FAIL` while exercising negative fixtures.
