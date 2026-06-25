# SMV1 T1 Authorized Recovery Independent Audit

Role: independent auditor.

Audit the integrated T1 authorized recovery result before any T2 recalibration, model promotion, customer drawing generation, or readiness promotion.

Inputs are limited to the visible-file manifest at `orchestration/input_manifests/sheetmetal-v1/t1-authorized-recovery/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.visible_files.json`.

Required checks:

- Verify the integration child result and summary are JSON-parseable, required-field-complete, and hash-bound.
- Recompute non-self output hashes for T1A, T1B, T1C, and the integration child result.
- Confirm T1A remains safe unresolved with no approved panel allocation source promotion.
- Confirm T1B's code behavior is limited to authority-state preservation, real-project geometry coverage remains `0/53`, and synthetic fixture evidence is not treated as real-project capability success.
- Confirm T1C rule artifacts remain proposal-only and are not promoted into a model, renderer, or recalibration input unless the audit explicitly accepts that promotion under the authority decision.
- Rerun full tests and the legacy, active sheetmetal-v1, and topology/sizing/placement scoped freeze verifiers with the bundled runtime when available.
- Verify hard gates: source-root mutation count `0`, private external transmissions `0`, completed-reference leakage `0`, post-design leakage `0`, customer PDF/DXF/DWG generation `0`, and production approval `false`.

Forbidden actions:

- Do not open, copy, rename, move, overwrite, or delete source roots.
- Do not read or write `.private/**`.
- Do not generate customer drawings, PDFs, DXFs, or DWGs.
- Do not declare `PRODUCTION_APPROVED`.
- Do not use completed references or post-design labels as generator inputs.
- Do not stage, execute, or modify `scripts/run_reference_detection_v4_corpus_screening.py`.

Expected outputs:

- `reports/sheetmetal-v1/t1-authorized-recovery/independent-audit/t1_authorized_recovery_independent_audit.json`
- `reports/sheetmetal-v1/t1-authorized-recovery/independent-audit/t1_authorized_recovery_independent_audit.md`
- `orchestration/master/child-results/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.json`
