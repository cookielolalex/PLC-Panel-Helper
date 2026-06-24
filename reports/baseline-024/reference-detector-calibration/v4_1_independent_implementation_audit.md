# Detector V4.1 Independent Implementation Audit

Auditor: `Averroes`

Status: `PASS`

## Criteria

1. `PASS` - v4 failed calibration evidence is preserved under `reports/baseline-024/reference-detector-calibration/v4_calibration_partition`; the summary reports detector performance `FAIL`, all-three recall `0/8`, and private OCR page count `0`.
2. `PASS` - `scripts/detect_reference_presence_v4.py` uses detector version `target_output_detection_v4_1_local_layout_prior_recovery`; explicit non-target content is evaluated before the weak-prior fallback, and weak role prior without layout remains unclassified.
3. `PASS` - all four v4 schemas accept both v4 and v4.1 detector version strings.
4. `PASS` - repository test result was verified from the coordinator-run final `scripts/run_tests.py` status `PASS`; the read-only auditor did not rerun tests.
5. `PASS` - v4.1 calibration summary reports implementation `PASS`, detector `PASS`, positives `8`, all-three `8/8`, each target type `8/8`, private OCR `0`, external transmission `0`, and cleanup/raw persistence/generator isolation/source-review blindness all `PASS`.
6. `PASS` - v4.1 negative-control summary reports `PASS`, supported controls `24/24`, zero false target pages, zero false all-three promotions, zero electrical/source false target pages, private OCR `0`, and cleanup/raw persistence/isolation/blindness all `PASS`.
7. `PASS` - 108 JSON/MD report files were scanned for private absolute paths, raw/OCR text keys, page/title image references, rendered-image references, or page-text-like payloads; finding count was `0`. Read-only v4 verifier passed on all 25 per-project output directories.
8. `PASS` - bundled Git verified commits `cdba0f8` and `90b0f86` are present.

## Residual Risks

- V4.1 report artifacts and freeze manifests were untracked at the time of audit.
- Canonical state files still needed updating at the time of audit.

## Command Summary

The auditor used read-only PowerShell, bundled Python, and bundled Git: `Get-Content`, `Get-FileHash`, targeted `rg`, Python JSON readers for aggregate metrics and leak scanning, `verify_reference_detection_v4_output.py` over minimized output directories, and bundled Git status/log/diff commands.

The auditor reported that no PDFs, source roots, page renders, crops, or workbook/customer content were opened.
