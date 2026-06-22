# Knowledge Manifest

Production Knowledge status: not built.

Bootstrap reusable rules:

- `rules/source_authority_profile.json`
- `rules/derivation_rules/bootstrap_dimension_rule.json`
- `rules/constraint_rules/bootstrap_cross_pdf_rule.json`

Reusable metadata inventory:

- `manifests/st_block_library_index.csv` exists, but contains project-local CAD
  candidates only; no canonical `ST-Block1` production library is approved.
- `manifests/vendor_catalog_index.csv` exists, but contains project-local
  catalog candidates only; no canonical vendor catalog production Knowledge is
  approved.

Forbidden in production Knowledge:

- project-specific completed layouts;
- held-out expected outputs;
- reviewer findings;
- failed generated outputs;
- reference manifests/adjudication;
- sample-project hidden decisions;
- stale workbook content.
