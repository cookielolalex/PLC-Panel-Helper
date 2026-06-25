# SMV1 T1 Authorized Recovery Independent Audit

Role: independent auditor.

Audit the integrated T1 authorized recovery result before any T2 recalibration, model promotion, customer drawing generation, or readiness promotion.

Inputs are limited to the visible-file manifest at `orchestration/input_manifests/sheetmetal-v1/t1-authorized-recovery/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.visible_files.json`.

Use the bundled Python runtime recorded in the visible-file manifest for test commands. Do not rely on a bare `python` command.

Required checks:

- Verify the manifest's `current_integration_head` is the committed integration baseline `55d151f578a2dd5189ed9d1124279746ea0f5199` and is an ancestor of current `HEAD`. It does not need to equal current `HEAD` if an audit-setup commit exists on top.
- Verify the integration child result, integration summary, and T1A/T1B/T1C child/report JSON files are JSON-parseable, required-field-complete, and hash-bound.
- Recompute every non-self output hash declared by T1A, T1B, T1C, and the integration child result.
- Confirm T1A remains safe unresolved with no approved panel allocation source promotion.
- Confirm T1B's code behavior is limited to authority-state preservation, real-project geometry coverage remains `0/53`, and synthetic fixture evidence is not treated as real-project capability success.
- Confirm T1C rule artifacts remain proposal-only and are not promoted into a model, renderer, or recalibration input unless the audit explicitly accepts that promotion under the authority decision.
- Rerun full tests and the legacy, active sheetmetal-v1, and topology/sizing/placement scoped freeze verifiers with the bundled runtime recorded in the manifest.
- Verify hard gates: source-root mutation count `0`, private external transmissions `0`, completed-reference leakage `0`, post-design leakage `0`, customer PDF/DXF/DWG generation `0`, and production approval `false`.
- Treat the pre-existing untracked `scripts/run_reference_detection_v4_corpus_screening.py` according to `MASTER_STATE.json`: its presence alone is not a failure, but reading, staging, executing, modifying, or committing it is forbidden.
- Review the preserved attempt-001-not-accepted audit artifacts as failed setup evidence, not as the final audit result.

Forbidden actions:

- Do not open, copy, rename, move, overwrite, or delete source roots.
- Do not read or write `.private/**`.
- Do not generate customer drawings, PDFs, DXFs, or DWGs.
- Do not declare `PRODUCTION_APPROVED`.
- Do not use completed references or post-design labels as generator inputs.
- Do not read, stage, execute, modify, or commit `scripts/run_reference_detection_v4_corpus_screening.py`.

Expected outputs:

- `reports/sheetmetal-v1/t1-authorized-recovery/independent-audit/t1_authorized_recovery_independent_audit.json`
- `reports/sheetmetal-v1/t1-authorized-recovery/independent-audit/t1_authorized_recovery_independent_audit.md`
- `orchestration/master/child-results/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.json`
