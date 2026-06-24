# Detector V4.1 Sealed Holdout Independent Audit

- audit status: `PASS`
- audit agent: `019ef7b2-ae20-7ae2-96f7-93fa52ea23b6`
- audited head: `7b10e79`
- audited worktree state: holdout/all-13 runner and aggregate-report changes pending commit
- audit scope: sealed holdout aggregate summary, all-13 final recall aggregate summary, refreshed negative controls, scoped persistence scan, and temporary-output cleanup

## Evidence Hashes

- `v4_1_sealed_holdout/sealed_holdout_audit_summary.json`: `6D1DCB0F3EE39AA892A9CB82A22A14099AEFBEB97FEED986B5049443FD38C4FA`
- `v4_1_all13_final_recall/all13_final_recall_summary.json`: `16A436024F7988C5E1B749D0DA81F3E66D367CA246370EA397D4AC99FA4FA625`
- `v4_1_negative_controls/negative_control_audit_summary.json`: `E8A19D7DFF6DDF04163C4AE45F69B874D8230BBE26405FD8DE4BEC2424CB0A4C`
- `scripts/run_reference_detection_v4_holdout_audit.py`: `042082B9ED997B742E5A71ECFE804102C6774BAEEA3087562A95838A06F1A2FB`
- `scripts/run_reference_detection_v4_all13_recall.py`: `D820916FA99A91A1048C917593F479F47959B777B92366D9C13F979003E4A669`

## Findings

- sealed holdout: `PASS`; holdout count `5`; all-three recall `5 / 5`; per-type recall `5 / 5`; private OCR `0`; external transmission `0`
- all-13 final recall: `PASS`; known positives `13`; all-three recall `13 / 13`; per-type recall `13 / 13`; private OCR `0`; external transmission `0`
- negative controls: `PASS`; supported controls `24 / 24`; false target pages `0`; false all-three promotions `0`; electrical/source false targets `0`; private OCR `0`
- persistence scan: `PASS`; scoped count-only scan found no private absolute paths, raw text keys, OCR text keys, page-image or title-crop references, rendered-image files, project-ID-like tokens, neutral file IDs, or long page-text-like payloads in sealed aggregate output directories
- cleanup: `PASS`; both temporary parent roots were absent after rerun, and both runners remove the timestamped detail tree plus the empty parent temp root

## Residual Risk

The audit deliberately did not open private PDFs, source roots, page renders, crops, customer workbooks, sealed identity-bearing content, or detailed detector outputs. The review was limited to aggregate summaries, script code, file hashes, Git metadata, and count-only persistence checks.
