# SMV1 Candidate Selection Audit Task Brief

Task ID: `SMV1-CANDIDATE-SELECTION-AUDIT`
Agent type: `independent_auditor`
Agent ID: `019ef82a-f29b-73c0-851e-120dbe9fcc93`
Project: `1110101`

Read-only audit of the sheetmetal-v1 deterministic one-project selection and bundle freeze.

Required checks:

1. exactly one candidate is selected and selection is metadata-only;
2. selection is frozen before completed-reference content is used;
3. selected project is `1110101` and ranking rationale is deterministic;
4. effective sheetmetal reference package is evaluator-only and not in the generator bundle;
5. source role/chronology classification excludes quarantined, post-design, and completed-reference material;
6. generator bundle contains only sanitized inputs, previews, source approval/provenance/visible-file/hash/verification manifests;
7. generator bundle excludes `reference_manifest.json`, original workbooks, completed drawings, path escapes, symlinks, and customer drawing outputs;
8. `verification_results.json` is `PASS` and `bundle_hashes.json` entries match actual files;
9. no customer drawing was generated in sheetmetal-v1.

The auditor must not modify files.
