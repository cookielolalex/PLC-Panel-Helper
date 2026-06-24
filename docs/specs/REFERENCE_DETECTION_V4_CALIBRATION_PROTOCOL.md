# Reference Detection V4 Calibration Protocol

Status: `FROZEN_PROTOCOL`

Decision: `D-0021`

Detector under test: `target_output_detection_v4_local_multisignal_recovery`

## Purpose

This protocol freezes the calibration procedure for the local-only detector v4
recovery branch before detector implementation. It preserves the existing
privacy, reference-vault, generator-isolation, source-review blindness, and
baseline no-generation boundaries.

## Split Rule

Known-positive controls are the 13 already accepted `ALLOWED_EVAL` projects.
Each is independently established to contain all three completed target output
types. The split is produced by sorting:

`SHA256("reference-detector-v4-local-multisignal-recovery-20260624:" + project_id)`

The first 8 projects are calibration controls. The remaining 5 projects are a
sealed holdout. The implementation-facing manifest may expose calibration
project IDs only. The sealed holdout manifest is auditor-only and must not be
used to tune detector code, aliases, thresholds, or failure handling.

After sealed holdout audit, the frozen detector must be run once against all 13
known positives to compute final recall. Any code or configuration change after
that result requires a new detector version and newly sealed evaluation
procedure.

## Positive Gates

The detector may proceed beyond calibration only if all of these hold:

- known-positive all-three recall: `13 / 13`;
- `PRODUCTION_DRAWING` recall: `13 / 13`;
- `SHEETMETAL_DRAWING` recall: `13 / 13`;
- `PUNCH_DRAWING` recall: `13 / 13`;
- project identity conflicts: `0`;
- privacy failures: `0`;
- raw OCR persistence failures: `0`;
- temporary-render cleanup failures: `0`;
- generator or source-review leakage failures: `0`.

## Negative Controls

The negative-control manifest is built from minimized, prior reference-vault
page classifications, not from completed-reference content. It includes real
non-target page controls for electrical drawings, source documents, and
cover/index material where available.

The frozen detector must report:

- zero false all-three promotions among supported real negative controls;
- zero electrical-negative pages classified as target pages.

The current real negative-control count is 24. This count supports a recovery
gate, but it is not a statistically conclusive false-positive assessment of the
entire corpus.

## Privacy And Minimization

Private completed-reference pages may be processed only by verified local
binaries or local operating-system APIs. No private page image, crop, raw OCR
text, embedded text, filename, source-root path, target hash, drawing detail,
component, quantity, or layout description may be persisted in v4 outputs or
printed to stdout/stderr.

The OCR bridge, when used, may return only minimized role signals, identity
status, language tag, engine identifier, elapsed time, page count, and evidence
codes. It must not return recognized text to the Python parent process.

Generator-facing and source-review-facing systems may receive at most project
ID plus reference-complete eligibility status after detector calibration and
audit. They must not receive reference file IDs, reference paths, hashes,
OCR text, title-block details, reviewer findings, scores, or expected answers.

## Required Reports

Calibration reports must be written separately:

- local OCR execution proof and privacy audit;
- calibration partition run;
- sealed holdout independent audit;
- all-13 final recall;
- negative-control audit;
- minimization and cleanup audit.

Corpus-wide screening remains unauthorized until the calibration and holdout
gates pass and the independent audit confirms holdout isolation.
