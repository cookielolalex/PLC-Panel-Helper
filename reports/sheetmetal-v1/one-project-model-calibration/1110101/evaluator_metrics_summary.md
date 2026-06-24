# Evaluator Metrics Summary

Status: `PASS_WITH_SOURCE_LIMITED_PANEL_ASSIGNMENT_COVERAGE`.

Task: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION`.

Candidate: `1110101`.

Metric scope: neutral source coverage and hard-gate metrics.

The evaluator metrics were computed after generator freeze without modifying
generator artifacts and without opening completed-reference content for metric
values. The effective sheetmetal reference package is available for later
adjudication, but this report records only neutral counts and coverage.

Metrics:

- Source line representation: `125 / 125`, coverage `1.0`, confidence `HIGH`
- Authorized source fact retention: `87 / 87`, coverage `1.0`, confidence `HIGH`
- Component registration coverage: `53 / 53`, coverage `1.0`, confidence `HIGH`
- Conflict-free component coverage: `53 / 53`, coverage `1.0`, confidence `HIGH`
- Panel assignment resolution: `0 / 53`, coverage `0.0`, confidence `HIGH`
- Graph referential integrity: `107 / 107`, coverage `1.0`, confidence `HIGH`
- Inventory-only functional safety: `1 / 1`, coverage `1.0`, confidence `HIGH`
- Accessory rule scorability: `0 / 0`, coverage `0.0`, confidence `HIGH`
- Deterministic freeze canonical match: `9 / 9`, coverage `1.0`, confidence `HIGH`
- Evaluator reference package availability: `1 / 1`, coverage `1.0`, confidence `HIGH`
- Generator reference isolation: `2 / 2`, coverage `1.0`, confidence `HIGH`

The `0 / 53` panel-assignment metric is source-limited, not inferred. All
components remain safely unresolved for panel assignment because no approved
panel-assignment facts were present. The `0 / 0` accessory-rule metric is not
scorable because no approved accessory rules were present.

No customer drawing, PDF, DXF, DWG, drawing model, baseline generation,
generator-artifact mutation, or `SHEETMETAL_ALLOWED_EVAL` promotion occurred.
