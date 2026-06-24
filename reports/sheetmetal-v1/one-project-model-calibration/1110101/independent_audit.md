# Independent Component Graph Audit - 1110101

Status: `PASS`.

Audit task: `INDEPENDENT_ONE_PROJECT_COMPONENT_GRAPH_AUDIT_AND_ADJUDICATION`.

Audited commit: `abc5a86306aa3a68d54d0e516e849c2e95e6a1f5`.

Candidate: `1110101`.

Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

Final calibration status: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION_PASS`.

Next action: `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION`.

## Checkpoint

- HEAD matched expected short commit `abc5a86`.
- Tracked worktree was clean before audit outputs; the only untracked path was the permitted legacy screening script.
- Full `scripts/run_tests.py`: `PASS`.
- Active sheetmetal-v1 scoped freeze: `PASS`.
- Legacy baseline-024 scoped freeze: `PASS`.
- Selected sanitized generator bundle verifier: `PASS`.
- Privacy approval remained `NOT_APPROVED`.
- Generated customer drawing/PDF/DXF/DWG count remained `0`.
- Tracked private artifact count remained `0`.

## Determinism

Recorded generator freeze result: canonical matches `9 / 9`; byte-identical outputs `7 / 9`.

The two byte-only mismatches were:

| Artifact | Structural diff | Canonical hash match | Adjudication |
| --- | ---: | --- | --- |
| `source_fact_model.json` | `0` | `PASS` | JSON serialization only; no excluded fields |
| `component_register_validation.json` | `0` | `PASS` | JSON serialization only; no excluded fields |

Canonicalization used sorted JSON keys and compact separators with no excluded fields. The policy and deterministic implementation predated this adjudication and are included in the active sheetmetal-v1 workflow freeze.

## Hard Gates

All qualification-critical hard gates passed. The hard-gate table is recorded in `hard_gate_adjudication.json`.

Key zero counts: private external transmissions `0`, completed-reference leakage `0`, post-design leakage `0`, unsupported critical facts `0`, silently discarded authorized source lines `0`, quantity overwrite violations `0`, graph referential failures `0`, forbidden functional edges `0`, unsupported panel assignments `0`, duplicate inferred accessories `0`, unsupported cutout geometry `0`, tracked private artifacts `0`, temporary render leftovers `0`, and generated customer drawings `0`.

## Metric Adjudication

Every evaluator metric recorded numerator, denominator, scorable coverage, and confidence. Component registration was `53 / 53`; graph referential integrity was `107 / 107`; deterministic canonical match was `9 / 9`.

Panel assignment resolution is source-limited at `0 / 53`, but the frozen protocol permits safe unresolved facts when they are recorded and assigned to a later module. The gap is assigned to `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION` and is not converted into a favorable accuracy claim. Accessory-rule scorability is `0 / 0`; no recall is reported for that denominator-zero metric.

## Final Adjudication

Result: `PASS`.

This does not mean production readiness. It accepts `1110101` as the first sheetmetal-v1 one-project calibration case for the modular component-register and graph stage. `SHEETMETAL_ALLOWED_EVAL` may move from `0` to `1`; the next authorized work is `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION`. No drawing generation is authorized by this audit.
