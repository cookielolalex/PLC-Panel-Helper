# Component Register Summary

Status: `PASS`.

Task: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION`.

Candidate: `1110101`.

Mode: `SOURCE_MODE_A_INVENTORY_ONLY`.

Private input:

`.private/sheetmetal-v1/1110101/source-fact-extraction/source_fact_model.json`

Private output directory:

`.private/sheetmetal-v1/1110101/component-register/`

The deterministic register builder consumed the private source-fact model and
wrote the project-specific component register only inside the ignored private
workspace. The committed record contains only neutral validation counts and
hashes.

Neutral validation:

- Schema validation: `PASS`
- Component type count: `53`
- Component instance count: `53`
- Conflict count: `0`
- Source fact count: `87`
- Source line count: `125`
- Unregistered allowed component keys: `0`
- Completed-reference component count: `0`
- Private content transmission count: `0`

Quantity stage instance counts:

- `required_qty`: `0`
- `ordered_qty`: `0`
- `received_qty`: `0`
- `allocated_qty`: `0`
- `installed_qty`: `0`

Private output hashes:

- `component_register.json`: `D0C354C964D3D9D614E5BCE300F877DE3E43F6E7C770CA9461C7A5DF9481E247`
- `component_register_validation.json`: `AD1917C52019D2BDE516B414333D2761CA9C0E31DEAC537940486EE39C0D6B69`

Git ignore verification passed for both private output files, and no `.private`
path is tracked. No customer drawing, PDF, DXF, DWG, or drawing model was
generated.
