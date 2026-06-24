# Source Fact Extraction Summary

Status: `PASS`.

Task: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION`.

Candidate: `1110101`.

Mode: `SOURCE_MODE_A_INVENTORY_ONLY`.

Private output directory:

`.private/sheetmetal-v1/1110101/source-fact-extraction/`

The deterministic extractor wrote the project-specific source fact model only
inside the ignored private workspace. The extractor ran with `--quiet`; the
committed record contains only neutral validation counts and hashes.

Neutral validation:

- Schema validation: `PASS`
- Evidence count: `6`
- Source line count: `125`
- Source fact count: `87`
- Source line accounting count: `125`
- Silently discarded authorized source lines: `0`
- Quantity-stage overwrite violations: `0`
- Completed-reference facts: `0`
- Private content transmission count: `0`

Quantity stage counts:

- `required_qty`: `0`
- `ordered_qty`: `0`
- `received_qty`: `0`
- `allocated_qty`: `0`
- `installed_qty`: `0`

Private output hashes:

- `source_fact_model.json`: `23A1F4731794A3F6574B709567859351323AFB53F6F77849937F1E77809E5738`
- `source_fact_validation.json`: `8B9DD11E67CCBFD8E9DED710D917A9D736B963FCC331FBC51382AF2AB0849B16`

Git ignore verification passed for both private output files, and no `.private`
path is tracked. No customer drawing, PDF, DXF, DWG, or drawing model was
generated.
