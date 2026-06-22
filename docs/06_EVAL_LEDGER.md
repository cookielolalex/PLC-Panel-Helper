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
