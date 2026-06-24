# One-Project Topology Sizing Placement Calibration Plan

Status: `FROZEN_PROTOCOL`.

Candidate: `1110101`.

Starting checkpoint: `536c76d`, with component-register and graph calibration
accepted as `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION_PASS`.

## Phase Order

1. Verify checkpoint gates and set
   `ONE_PROJECT_TOPOLOGY_SIZING_PLACEMENT_CALIBRATION_IN_PROGRESS`.
2. Probe installed local solver capabilities without downloading packages.
3. Recover source-only panel assignments from frozen private generator inputs.
4. Build topology candidates, preserving unresolved and ambiguous facts.
5. Build sizing candidates separately from placement.
6. Build placement and unplaced-component registers under hard constraints.
7. Validate schema, provenance, dimensions, geometry, containment, overlap,
   clearance, assignment, leakage, privacy, and no-drawing gates.
8. Rerun generator-side artifacts twice and freeze canonical hashes.
9. Run evaluator-only metric generation after generator freeze.
10. Set
    `ONE_PROJECT_TOPOLOGY_SIZING_PLACEMENT_FROZEN_AUDIT_PENDING` and next
    action `RUN_INDEPENDENT_ONE_PROJECT_TOPOLOGY_SIZING_PLACEMENT_AUDIT`.

## Expected Safe Coverage

The previous accepted audit records panel-assignment resolution at `0/53`.
Unless source-only recovery finds approved explicit panel allocation evidence,
placement coverage is expected to remain low. Low coverage is acceptable only
when each omission is explicit, safe, and supported by reason codes. It must
not be called a pass or failure in this implementation thread.

## Hard Prohibitions

This plan does not authorize customer PDF, DXF, DWG, fabrication drawing,
completed-reference inspection in the generator lane, final independent
adjudication, `SHEETMETAL_ALLOWED_EVAL` count increases, or legacy three-output
detector work.
