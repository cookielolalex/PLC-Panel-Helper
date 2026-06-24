# One-Project Component Graph Calibration Plan

Status: `PROTOCOL_FROZEN`.

Task: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION`.

Candidate: `1110101`.

## Checkpoint Verification

- HEAD: `5409f2998eb77e3b61762b4d2d5c2f68835cb557`.
- Expected short HEAD: `5409f29`.
- Tracked worktree before protocol edits: clean.
- Only permitted untracked file: `scripts/run_reference_detection_v4_corpus_screening.py`.
- Full test runner: `PASS`.
- Legacy scoped freeze: `PASS`.
- Active sheetmetal-v1 scoped freeze: `PASS`.
- Selected sanitized bundle verifier: `PASS`.
- Bundle hash cross-check: `PASS`, 17 entries.
- Approved worksheet fingerprint presence: `PASS`, 6 decisions.
- Privacy: `NOT_APPROVED`.
- Customer drawing outputs under sheetmetal-v1: `0`.
- Baseline-generation directories under sheetmetal-v1: `0`.

## Frozen Lane Boundary

The generator lane remains source-only and inventory-only. It may read the
verified sanitized bundle, accepted source-role/chronology decisions, authority
policy, schemas, approved rules, approved library entries, and synthetic
fixtures. It may not read completed references, post-design labels, evaluator
labels, expected answers, reference hashes, title-block data, images, crops,
or reviewer findings.

The evaluator lane remains closed until generator artifacts are frozen and
hashed. After freeze it may inspect the evaluator-only reference package and
accepted evaluator labels, but committed reports may contain only neutral
metrics, coverage, mismatch IDs, generalized error classes, severity,
provenance gaps, and unsupported-inference counts.

## Execution Plan

1. Create and verify the ignored private workspace before writing project
   facts.
2. Add synthetic regression coverage for source-fact extraction, component
   normalization, quantity reconciliation, panel assignment, graph validation,
   accessory reconciliation, deterministic rerun, and privacy leakage.
3. Implement deterministic local project-data processing for the verified
   sanitized bundle without exposing project values to model agents.
4. Write project-specific models only inside the ignored private workspace.
5. Run the generator pipeline twice from the same frozen inputs and compare
   canonical outputs.
6. Freeze private outputs and commit only neutral hashes, counts, status codes,
   validation summaries, and audit summaries.
7. Open the evaluator lane only after generator freeze, then persist only
   neutral metrics and coverage.
8. Run the independent audit against the hard gates.

## Non-Goals

- Do not generate PDF, DXF, DWG, or customer drawing output.
- Do not run corpus-wide requalification.
- Do not select another candidate.
- Do not resume the legacy three-output detector workflow.
- Do not promote `SHEETMETAL_ALLOWED_EVAL` before a passing independent audit.

## Current Status

The calibration is ready for the private-workspace boundary phase.
