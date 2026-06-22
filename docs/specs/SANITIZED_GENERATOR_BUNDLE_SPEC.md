# Sanitized Generator Bundle Spec

Status: PH1.5 calibration draft.

A generator bundle is built only from validated human-approved source items.
The original multi-sheet workbook is never copied into the generator workspace.

Required files:

- `bundle_manifest.json`
- `approval_manifest.json`
- `provenance_map.json`
- `visible_file_manifest.json`
- sanitized input artifacts
- readable previews
- `verification_results.json`
- `bundle_hashes.json`

The verifier fails closed unless every included artifact derives from
`HUMAN_APPROVED` items whose file hash and worksheet fingerprint still match.
Denied, hidden, stale, superseded, cross-project, parser-required, or
quarantined content cannot enter the bundle.

Bundles must not expose absolute `SRC-ALL-PROJECTS` paths, symlinks, junctions,
shortcuts, path traversal, forbidden target-output names, reference hashes,
reviewer evidence, or target-output sentinels.

All provenance uses neutral source IDs. A source mutation invalidates approval
and bundle construction.

