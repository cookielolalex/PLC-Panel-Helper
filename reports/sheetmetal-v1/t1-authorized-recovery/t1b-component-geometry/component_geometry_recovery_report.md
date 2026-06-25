# T1B Component Geometry Recovery

Task: `SMV1-T1B-COMPONENT-GEOMETRY-RECOVERY`

Final status: `SAFE_UNRESOLVED_GEOMETRY_REQUIRES_MORE_AUTHORITY_OR_DATA`

Signed choice B authorizes the component-geometry lane, but it does not allow
private project context transmission, private model identifier public lookup,
completed-reference inference, customer drawing generation, or production
approval. This worker therefore recovered the tested code path and a proposed
synthetic geometry-library artifact, without promoting real-project geometry.

## What Changed

- Added synthetic fixture:
  `evals/fixtures/sheetmetal-v1/component_geometry_authority_fixture.json`
- Added regression test:
  `test_sheetmetal_v1_component_geometry_authority_states`
- Updated component-register geometry handling so structured
  `component_geometry.status` values preserve:
  `VERIFIED_MODEL_GEOMETRY`,
  `APPROVED_GENERIC_CONSERVATIVE_ENVELOPE`,
  `GEOMETRY_CONFLICT`, and `EXPLICIT_SOURCE`.
- Added proposed, test-only geometry library:
  `component_geometry_library.proposed.v1.json`

Unknown geometry statuses still fail closed to `EXPLICIT_SOURCE`. Missing
geometry remains missing and unplaced.

## Coverage

Synthetic regression coverage:

- `VERIFIED_MODEL_GEOMETRY`: `1`
- `APPROVED_GENERIC_CONSERVATIVE_ENVELOPE`: `1`
- `GEOMETRY_MISSING`: `1`

Accepted real-project T1 coverage remains unchanged:

- `VERIFIED_MODEL_GEOMETRY`: `0/53`
- `APPROVED_GENERIC_CONSERVATIVE_ENVELOPE`: `0/53`
- `GEOMETRY_MISSING`: `53/53`

The synthetic fixture is not real-project capability success.

## Verification

- Targeted geometry authority test: `PASS`
- Scoped sheetmetal tests: `PASS`
- Full `scripts/run_tests.py`: `FAIL_STALE_FROZEN_WORKFLOW_MANIFEST_HASHES`

The full runner passed through the functional sheetmetal-v1 tests, including
the new geometry authority test, then failed at frozen workflow manifest
verifiers because active and topology manifests are anchored to older hashes.
This worker did not rewrite frozen manifests.

## Hard Gates

- Public web lookup used: `0`
- Private model identifier public lookup: `0`
- Private content transmissions: `0`
- Completed-reference access: `0`
- Post-design access: `0`
- Customer PDF/DXF/DWG generation: `0`
- Production approval declaration: `0`
- Real-project geometry promotions: `0`

Recommended next action: run independent T1B authority/leakage review, then
provide approved non-private manufacturer documentation or an accepted
real-project component-geometry library before promoting any real coverage.
