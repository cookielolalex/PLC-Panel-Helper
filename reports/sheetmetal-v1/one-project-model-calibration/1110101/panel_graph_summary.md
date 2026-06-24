# Panel Assignment And Graph Summary

Status: `PASS`.

Task: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION`.

Candidate: `1110101`.

Mode: `SOURCE_MODE_A_INVENTORY_ONLY`.

Private inputs:

- `.private/sheetmetal-v1/1110101/source-fact-extraction/source_fact_model.json`
- `.private/sheetmetal-v1/1110101/component-register/component_register.json`

Private output directory:

`.private/sheetmetal-v1/1110101/panel-graph/`

The deterministic builder consumed the private source-fact model and private
component register, then wrote panel-assignment and typed graph artifacts only
inside the ignored private workspace. The committed record contains only
neutral validation counts and hashes.

Neutral validation:

- Panel assignment schema validation: `PASS`
- Panel graph schema validation: `PASS`
- Assignment count: `0`
- Unresolved component count: `53`
- Rejected assignment count: `0`
- Graph node count: `56`
- Graph edge count: `107`
- Dangling edge count: `0`
- Inventory-only unverified function edges: `1`
- Private content transmission count: `0`

Edge type counts:

- `CONNECTS_TO`: `1`
- `INSTANCE_OF`: `53`
- `REQUIRED_BY`: `53`

Private output hashes:

- `panel_assignment.json`: `1531D1DFA7BD6AB329AD6964C38367C9C0094AD8B32AE2802176712F3D957FD8`
- `panel_graph.json`: `B3A68E597703AA8C8B6C29998F8D28A811912A071BCA34C7018F4BDB38479CB1`
- `panel_graph_validation.json`: `02209B427FFDD9C1947F7A22CD77D43E714C9930A72177DF68A9C289F1C1D9E8`

No approved source panel-assignment fields were present in the private source
facts, so all 53 components remain unresolved for panel assignment. This is a
fail-closed inventory-only result, not an inferred placement.

Git ignore verification passed for all private output files, and no `.private`
path is tracked. No customer drawing, PDF, DXF, DWG, or drawing model was
generated.
