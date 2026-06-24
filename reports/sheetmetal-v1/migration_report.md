# Sheetmetal V1 Goal Migration Report

Status: `SHEETMETAL_MODULAR_FOUNDATION_READY_FOR_ONE_PROJECT_CALIBRATION`.

## Verification

- Expected starting HEAD: `a4311e7`.
- Actual HEAD at migration verification: `a193abc3e702d1750d40585180d8839fefd920c2`, a documented descendant in the existing ledger history.
- Worktree at migration start: not clean because `scripts/run_reference_detection_v4_corpus_screening.py` was already untracked. It is left untouched.
- Full test runner before migration edits: `PASS`.
- Full test runner after adding sheetmetal-v1 foundation: `PASS`.
- Privacy approval: `docs/PRIVACY_APPROVAL.md` remains `NOT_APPROVED`.
- Baseline generation attempts: `0`.
- No real customer drawing or baseline generation occurred in this migration.

## Rationale

The former three-output requirement is retired for V1 because the controlling
product risk has moved from detecting all historical outputs to building a
source-grounded, auditable canonical panel model. The sheet-metal drawing is
the first useful downstream projection, but the model, not the PDF, is the
central product.

Production-control and punch outputs are treated as downstream projections
because they should consume panel topology, placement, cutouts, dimensions, and
provenance from the same canonical model. Letting them independently extract
components, assign panels, or infer geometry would reintroduce inconsistency
and reference-leakage risk.

The old `13 / 24` `ALLOWED_EVAL` count is not directly comparable with the new
cohort because it qualified projects for the historical all-three-output
objective. Sheetmetal-v1 requires independent source-role, chronology,
reference isolation, source coverage, component-register, and panel-assignment
qualification.

Detector-v3 all-three recall is no longer the controlling gate for V1. It
remains historical evidence for the legacy detector workflow, while the new
sheetmetal-first foundation starts from source facts and model validation.

## Frozen Legacy Artifacts

Legacy artifacts remain preserved under their existing paths, including:

- `evals/baseline-024/`
- `manifests/baseline-024/`
- `manifests/reference_detection/`
- `reports/baseline-024/`
- `reports/calibration-006/`
- `optimization/calibration-006/`

They are not deleted, rewritten, or counted as sheetmetal-v1 qualification.

## New Namespaces

- `reports/sheetmetal-v1/`
- `manifests/sheetmetal-v1/`
- `evals/sheetmetal-v1/`
- `orchestration/sheetmetal-v1/`
