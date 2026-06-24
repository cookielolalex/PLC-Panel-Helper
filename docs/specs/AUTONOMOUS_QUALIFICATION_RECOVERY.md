# Autonomous Qualification Recovery

Status: `ACCEPTED`

Decision: `D-0021`

Date: 2026-06-24

Baseline: `baseline-024-cycle-000`

## Purpose

This specification governs constraint-preserving autonomous recovery from
qualification blockers while the baseline-024 cohort remains short of twenty
four verified `ALLOWED_EVAL` projects.

The objective is to continue autonomously until at least twenty four unique
projects satisfy the existing `ALLOWED_EVAL` standard, with up to three fully
qualified reserve projects when available. Baseline generation remains blocked
until the final twenty four project cohort is frozen and audited.

## Unchanged Qualification Standard

This recovery workflow does not relax the substantive definition of a qualified
project. A project may count toward the baseline only when all existing gates
pass:

1. all three target reference types are confirmed:
   `PRODUCTION_DRAWING`, `SHEETMETAL_DRAWING`, and `PUNCH_DRAWING`;
2. project identity is confirmed;
3. combined packages, revisions, supersession, and duplicates are resolved;
4. ordinary electrical drawings and source documents are excluded;
5. reference evidence remains private and isolated from source reviewers and
   generators;
6. deterministic source prefilter passes;
7. the independent source-review quorum unanimously returns `ALLOW_EVAL`;
8. a sanitized generator bundle is constructed;
9. bundle schema, hashes, worksheet fingerprints, leakage checks, and
   independent audit pass;
10. approval is bound to current hashes and fingerprints.

The workflow must not count synthetic projects, duplicate project IDs, probable
or ambiguous reference sets, filename-only or folder-alias-only approvals,
projects requiring forbidden reference-derived source facts, source-quorum
failures, or bundle-verification failures.

## Privacy Boundary

`docs/PRIVACY_APPROVAL.md` remains `NOT_APPROVED`.

Therefore recovery work must not transmit private PDFs, workbook content,
reference pages, page renders, crops, thumbnails, OCR text, title-block content,
visual signatures, trajectories, reviewer findings, scores, or expected answers
to GPT-5, inherited child agents, external APIs, connectors, cloud OCR, or
network endpoints.

Private reference inspection may occur only in verified local processes. A child
agent reporting actual model `GPT-5` is not a local private-reference
classifier. Public dependency downloads are not authorized by this decision.

Reference-vault outputs remain minimized and may not persist raw OCR text,
rendered pages, crops, detailed title-block text, dimensions, components,
quantities, layouts, private absolute paths, or reference-derived engineering
data.

## Recoverable Blockers

Method-specific failures are branch blockers, not terminal project statuses,
unless all compliant recovery branches have been exhausted and an independent
auditor proves structural corpus insufficiency.

Allowed blocker classes:

- `RECOVERABLE_DETECTOR_LIMITATION`
- `RECOVERABLE_OCR_LIMITATION`
- `RECOVERABLE_PARSER_LIMITATION`
- `RECOVERABLE_SANITIZATION_LIMITATION`
- `RECOVERABLE_PROCEDURE_AMBIGUITY`
- `SUBSTANTIVE_REFERENCE_INCOMPLETE`
- `SUBSTANTIVE_SOURCE_DISQUALIFICATION`
- `PRIVACY_PERMISSION_REQUIRED`
- `UNKNOWN_REQUIRES_NEW_TEST`

Do not permanently reject a project for a recoverable blocker. Repair the
responsible procedure, add regression coverage, and retry the affected project
from the appropriate gate.

Do not repeat an identical failed strategy unless its code, configuration,
inputs, or evidence have changed. Every attempt must have a deterministic
signature.

## Recovery Controller

The deterministic controller records:

- current verified `ALLOWED_EVAL` count;
- deficit to twenty four and reserve target;
- minimized candidate queues;
- blocker taxonomy and counts;
- attempted strategies and their signatures;
- requested classifier and actual classifier separately;
- detector version and calibration status;
- local capability discovery results;
- source-review status;
- bundle-verification status;
- next selected action;
- progress since the previous iteration.

The controller may select only compliant next actions:

- local capability discovery;
- detector/OCR improvement;
- CJK normalization improvement;
- combined-package resolver improvement;
- revision/supersession resolver improvement;
- duplicate resolver improvement;
- project-identity improvement;
- workbook parser improvement;
- worksheet-role classifier improvement;
- sanitized-bundle builder improvement;
- retrying projects affected by a repaired procedure;
- screening the next unscreened individual projects after detector calibration.

## Detector Calibration Rule

Detector v3 performance status and regression-gate behavior must be reported
separately. A test such as
`test_reference_detector_v3_known_positive_recall_gate` passes when it correctly
preserves and blocks a failing detector result. That does not mean detector v3
performance passed.

Detector v4 and later versions may deploy corpus-wide only after independent
audit confirms:

- known-positive all-three recall is `13 / 13`;
- per-type recall is `13 / 13` for all three target types;
- supported real negative controls have zero false all-three promotions;
- electrical-negative pages have zero target acceptances;
- privacy, minimization, render cleanup, and generator isolation checks pass;
- sealed identities or results were not used for direct tuning.

## Completion and Stop Rules

The only successful stop for this recovery track is:

`TWENTY_FOUR_ALLOWED_EVAL_PROJECTS - BASELINE_GENERATION_PENDING`

The following are not terminal reasons by themselves:

- `VISION_CLASSIFIER_UNAVAILABLE`
- one detector version failing calibration
- no GPT-5 private-reference access
- no promotions in one batch
- no promotions among family representatives
- one OCR engine missing
- parser failure
- source-review disagreement caused by tooling defect
- recoverable sanitized-bundle failure

A non-success terminal status requires an independent auditor to prove
`STRUCTURAL_CORPUS_INSUFFICIENCY` after every unique relevant project receives
an individual decision from a calibrated detector, all recoverable branches and
retryable quarantines are exhausted, every unqualified project has a
project-specific substantive reason, and the arithmetic proves fewer than
twenty four projects can satisfy the unchanged standard.
