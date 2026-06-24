# Generator Freeze Summary

Status: `PASS`.

Task: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION`.

Candidate: `1110101`.

Mode: `SOURCE_MODE_A_INVENTORY_ONLY`.

The generator-side private artifacts were rerun from the frozen sanitized
bundle and classification inputs under a separate ignored private directory.
No private values were printed or committed.

Deterministic rerun:

- Status: `PASS_CANONICAL_JSON_SEMANTIC`
- Artifact count: `9`
- Byte-identical artifacts: `7`
- Canonical JSON matches: `9`
- Canonicalization: `json-sort-keys-compact-separators`
- Excluded fields: none
- Byte-only mismatches: `source_fact_model.json`,
  `component_register_validation.json`

Hard gates:

- Full `scripts/run_tests.py`: `PASS`
- Legacy scoped workflow freeze: `PASS`
- Active scoped workflow freeze: `PASS`
- Bundle hashes and worksheet fingerprints: `PASS`
- Private content transmission count: `0`
- Completed-reference leakage into generator artifacts: `0`
- Post-design leakage into generator artifacts: `0`
- Unsupported critical generated facts: `0`
- Silently discarded authorized source lines: `0`
- Quantity-stage overwrite violations: `0`
- Graph referential-integrity failures: `0`
- Forbidden functional edges in inventory-only mode: `0`
- Unsupported panel assignments: `0`
- Duplicate inferred accessories: `0`
- Temporary private-artifact leakage into Git: `0`
- Real customer drawings generated: `0`
- Sheetmetal-v1 PDF/DXF/DWG files generated: `0`
- Sheetmetal-v1 baseline-generation directory exists: `false`

Frozen private artifact hashes are recorded in
`generator_freeze_summary.json`. The two byte-only mismatches have zero JSON
structural differences and match under canonical JSON hashing with no excluded
timestamp or volatile fields.

No customer drawing, PDF, DXF, DWG, drawing model, baseline generation, or
`SHEETMETAL_ALLOWED_EVAL` promotion occurred.
