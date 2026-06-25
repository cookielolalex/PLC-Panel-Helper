# SMV1 T2 Topology/Sizing/Placement Independent Audit

Role: independent auditor.

Audit the T2 recalibration gate before any canonical model promotion, renderer work, customer drawing generation, or readiness promotion.

Inputs are limited to the visible-file manifest at `orchestration/input_manifests/sheetmetal-v1/t2-recalibration/SMV1-T2-TOPOLOGY-SIZING-PLACEMENT-INDEPENDENT-AUDIT.visible_files.json`.

Required checks:

- Verify the T2 child result and summary JSON are parseable, required-field-complete, hash-bound, and privacy-clean.
- Confirm T1A/T1B remain safe unresolved and T1C rule artifacts remain proposal-only, not promoted into the model, renderer, frozen generator, or T2 private inputs.
- Confirm no private generator rerun was performed under this heartbeat because `.private` mutation was forbidden.
- Rerun full tests and the legacy, active sheetmetal-v1, and topology/sizing/placement scoped freeze verifiers with the bundled runtime.
- Verify hard gates: source-root mutation `0`, `.private` mutation `0`, private external transmissions `0`, completed-reference leakage `0`, post-design leakage `0`, customer PDF/DXF/DWG generation `0`, and production approval `false`.

Forbidden actions:

- Do not open, copy, rename, move, overwrite, or delete source roots.
- Do not read or write `.private/**`.
- Do not generate customer drawings, PDFs, DXFs, or DWGs.
- Do not declare `PRODUCTION_APPROVED`.
- Do not use completed references or post-design labels as generator inputs.
- Do not read, stage, execute, modify, or commit `scripts/run_reference_detection_v4_corpus_screening.py`.

Expected outputs:

- `reports/sheetmetal-v1/t2-recalibration/t2_topology_sizing_placement_independent_audit.json`
- `reports/sheetmetal-v1/t2-recalibration/t2_topology_sizing_placement_independent_audit.md`
- `orchestration/master/child-results/SMV1-T2-TOPOLOGY-SIZING-PLACEMENT-INDEPENDENT-AUDIT.json`
