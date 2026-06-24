# Evaluation Ledger

## RUN-1110104-AUTO-EVAL-001

Status: `FAILED`.

Purpose: preserved failed first attempt for project `1110104`.

Result: codex_proxy child metadata did not create the expected last-message
parent path before invocation. No generated artifacts were accepted.

Evidence: `evals/runs/RUN-1110104-AUTO-EVAL-001/generation_complete.json`.

## RUN-1110104-AUTO-EVAL-002

Status: `PASS`.

Project: `1110104`.

Source authority: `ALLOWED_EVAL` sanitized bundle only. Completed references
were absent from the generator workspace and introduced only in the separate
reviewer workspace after generation freeze.

Generation: three required PDF output types attempted and validated; generated
binary PDFs remain ignored local artifacts.

Review result: validity `PASS`; quality score `42`; scorable coverage `38`;
confidence `LOW`; critical findings `0`; high findings `3`.

Independent audit: `STEP_7C_AUDIT_PASS - READY_FOR_SIX_PROJECT_BASELINE`.

Evidence: `evals/runs/RUN-1110104-AUTO-EVAL-002/generation_complete.json`,
`evals/runs/RUN-1110104-AUTO-EVAL-002/review/grading_result.json`,
`evals/runs/RUN-1110104-AUTO-EVAL-002/review/project_reviewer_result.json`,
and `evals/runs/RUN-1110104-AUTO-EVAL-002/audit/one_project_audit.json`.

## calibration-006

Status: `SIX_PROJECT_CALIBRATION_PASS - READY_FOR_24_PROJECT_BASELINE`.

Projects: `1110101, 1110104, 1110204, 1110205, 1110405, 1110410`.

Generation attempts: `12`; valid generation runs: `12`; primary reviews: `12`; secondary reviews: `6`.

Portfolio mean score: `42`; mean coverage: `38`; critical findings: `0`; high findings: `36`.

Evidence: `reports/calibration-006/calibration_summary.md`, `optimization/calibration-006/machine_summary.json`, and `reports/calibration-006/independent_audit.json`.

## cycle-000 Phase A evaluator-sensitivity

Status: `EVALUATOR_SENSITIVITY_PASS - READY_FOR_24_PROJECT_BASELINE_PROTOCOL`.

Purpose: qualify evaluator sensitivity before scaling from the six-project calibration set to the 24-project baseline.

Finding: original calibration reviewer mechanics wrote score `42` and coverage `38` as constants, so original `42/38` was an evaluator-mechanics defect rather than proven independent scoring.

Fix: added `plc_layout_evaluator_v2_sensitivity` with explicit scoring records, arithmetic dimension sums, coverage denominators, hard-gate overrides, low-coverage handling, and finding deduplication. Drawing-generation behavior was not changed.

Rescore result: all 12 frozen calibration runs rescore to score `42` and scorable coverage `38` under v2; validity remains `PASS`; critical findings remain `0`; high findings remain `36`.

Evidence: `reports/evaluator-sensitivity/calibration_score_recomputation.json`, `reports/evaluator-sensitivity/project_differentiation.json`, `reports/evaluator-sensitivity/counterfactual_results.json`, `reports/evaluator-sensitivity/test_results.json`, and `reports/evaluator-sensitivity/subagent_independent_audit.json`.

## baseline-024-cycle-000 Phase B protocol freeze

Status: `BASELINE024_PROTOCOL_FROZEN - PHASE_C_SOURCE_BACKFILL_PENDING`.

Purpose: freeze the rules for the first 24-project development baseline before source backfill or generation.

Frozen seed: `BASELINE024-CYCLE000-20260623`.

Evaluator: `plc_layout_evaluator_v2_sensitivity`.

Current cohort readiness: 6 `ALLOWED_EVAL` calibration anchors retained as fresh-run anchors; 18 additional project slots remain pending Phase C source backfill; metadata-only candidate pool contains 20 reference-complete non-anchor candidates; project `1110102` remains excluded until its prior bundle-verification defect is fixed, regression-tested, and independently audited.

Generation status: not authorized. Baseline generation may begin only after exactly 24 projects have verified `ALLOWED_EVAL` bundles and a final cohort manifest is frozen.

Evidence: `docs/specs/24_PROJECT_BASELINE_PROTOCOL.md`, `evals/baseline-024/cohort_manifest.json`, `evals/baseline-024/cohort_selection_report.md`, `evals/baseline-024/frozen_workflow_manifest.json`, `evals/baseline-024/source_readiness.json`, and `evals/baseline-024/run_plan.json`.

## baseline-024-cycle-000 Phase C batch-001 source backfill

Status: `PHASE_C_BATCH_001_AUDIT_PASS_CONTINUE_BACKFILL`.

Candidate projects: `1120101, 1120204, 1120301, 1110801, 1120207, 1120201`.

Accepted evaluation-only additions: `1110801, 1120207`.

Rejected or quarantined: `1120101, 1120204, 1120301` failed sanitized bundle verification on forbidden modification-content sentinel; `1120201` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 2 new Phase C additions, for 8 verified `ALLOWED_EVAL` projects. Sixteen additional verified projects are still required before generation.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_001.json`, and `reports/baseline-024/source_bundle_audit_batch_001_independent.json`.

## baseline-024-cycle-000 Phase C batch-002 source backfill

Status: `PHASE_C_BATCH_002_AUDIT_PASS_CONTINUE_BACKFILL`.

Candidate projects: `1120309, 1120202, 1120308, 1110103, 1110203, 1110404`.

Accepted evaluation-only additions: `1110103, 1110203, 1120308`.

Rejected or quarantined: `1110404` and `1120202` failed sanitized bundle verification on forbidden modification-content sentinel; `1120309` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 5 new Phase C additions, for 11 verified `ALLOWED_EVAL` projects. Thirteen additional verified projects are still required before generation.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_002.json`, and `reports/baseline-024/source_bundle_audit_batch_002_independent.json`.

## baseline-024-cycle-000 Phase C batch-003 source backfill

Status: `PHASE_C_BATCH_003_AUDIT_PASS_CONTINUE_BACKFILL`.

Candidate projects: `1110701, 1110704, 1110706, 1120305, 1110402, 1120102`.

Accepted evaluation-only additions: `1110704, 1120305`.

Rejected or quarantined: `1110701` failed sanitized bundle verification on forbidden modification-content sentinel; `1110402` had no reviewable items; `1110706` and `1120102` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 7 new Phase C additions, for 13 verified `ALLOWED_EVAL` projects. Eleven additional verified projects are still required before generation.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_003.json`, and `reports/baseline-024/source_bundle_audit_batch_003_independent.json`.

## baseline-024-cycle-000 Phase C batch-004 source backfill

Status: `BATCH004_SOURCE_BACKFILL_AUDIT_PASS_NO_ACCEPTED_BUNDLES`.

Candidate projects: `1110501, 1110504`.

Accepted evaluation-only additions: none.

Rejected or quarantined: `1110501` failed sanitized bundle verification on forbidden modification-content sentinel; `1110504` remained `QUARANTINED` with no approved bundle.

Current baseline-024 readiness: 6 anchor projects plus 7 new Phase C additions, for 13 verified `ALLOWED_EVAL` projects. Eleven additional verified projects are still required, but the frozen metadata-only candidate pool is exhausted.

Generation status: not authorized.

Evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`, `reports/baseline-024/source_backfill_summary.md`, `reports/baseline-024/source_bundle_audit.json`, `reports/baseline-024/source_bundle_audit_batch_004.json`, and `reports/baseline-024/source_bundle_audit_batch_004_independent.json`.

## baseline-024-cycle-000 Phase C shortfall

Status: `INSUFFICIENT_ELIGIBLE_PROJECTS_FOR_24_BASELINE`.

Processed frozen metadata-only candidates: `20 / 20`.

Accepted Phase C additions: `1110801, 1120207, 1110103, 1110203, 1120308, 1110704, 1120305`.

Bundle-verification rejected projects: `1120101, 1120204, 1120301, 1110404, 1120202, 1110701, 1110501`.

Quarantined/no-bundle projects: `1120201, 1120309, 1110402, 1110706, 1120102, 1110504`.

Generation attempts: `0`; valid baseline runs: `0`; primary reviews: `0`; secondary reviews: `0`.

Evidence: `reports/baseline-024/insufficient_eligible_projects_for_24_baseline.json` and `reports/baseline-024/insufficient_eligible_projects_for_24_baseline.md`.

## baseline-024-cycle-000 expanded discovery after D-0017

Status: `PRE_SOURCE_SCREENING_BLOCKED_BY_REFERENCE_PRESENCE`.

Purpose: supersede only the twenty-project metadata-only discovery cap and
reconcile the full approved development inventory under `SRC-ALL-PROJECTS`.

Inventory reconciliation: 404 project IDs and 404 physical project folders.

Target detection v2: 27 `VERIFIED_ALL_THREE` projects, all already accepted,
previously rejected, quarantined/no-bundle, or protocol-excluded. No completed
reference content was inspected during metadata target detection.

Expanded candidate registry: 0 `READY_FOR_SOURCE_SCREENING`; 269
`REFERENCE_PRESENCE_REVIEW_REQUIRED`.

Reference-presence waves: 18 top-ranked partial-reference projects reviewed in
three isolated waves. All remained `PARTIAL_REFERENCE_SET` with only sheet-metal
target evidence; 0 projects were promoted to all-three reference availability.

Generation status: not authorized. Source-review quorum and sanitized bundle
construction have not started for expanded candidates.

Evidence: `reports/baseline-024/expanded-screening/inventory_reconciliation_report.md`,
`reports/baseline-024/expanded-screening/target_detection_v2_report.md`,
`evals/baseline-024/expanded_candidate_selection_report.md`,
`reports/baseline-024/expanded-screening/screening_yield_summary.md`, and
`reports/baseline-024/expanded-screening/dominant_blockers.json`.

## baseline-024-cycle-000 reference detection v3

Status: `REFERENCE_REVIEW_UNIVERSE_EXHAUSTED - INSUFFICIENT_REFERENCE_COMPLETE_PROJECTS`.

Purpose: replace the metadata/transient-text-only reference-presence review
with content-aware, page-level, reference-vault-only completed-target
classification while preserving generator and source-review isolation.

Detector: `target_output_detection_v3_page_content_isolated`.

V2 diagnosis: zero promotions were caused by metadata-only and restricted
document-level review mechanics, lack of page rendering/visual evidence,
one-file-one-type assumptions, incomplete combined/revision handling, and
policy confusion between generator-forbidden location and reviewer-reference
eligibility. The diagnosis did not prove references were genuinely missing.

V3 screening: 129 projects processed across all 103 reference-review-required
families plus an additional ranked non-representative pass; 1849 PDFs and 9031
pages classified; 1644 image-only-or-no-target-text PDFs and 205 embedded-text
PDFs handled; 3252 electrical/false-positive alias pages rejected; 0 combined
packages and 0 revision supersession packages resolved.

Result: 0 newly verified all-three projects, 129 partial projects, 0 ambiguous
projects. Source screening, sanitized-bundle construction, final cohort freeze,
and baseline generation did not start. Current baseline-024 `ALLOWED_EVAL`
count remains `13 / 24`.

Audit: all 129 project outputs validate against the v3 schemas and
minimization verifier; all 22 batch summaries report
`REFERENCE_PRESENCE_BATCH_AUDIT_PASS`. Because no new reference-complete
projects reached source screening, the source-pool portion of the independent
audit is not applicable and no cohort freeze is permitted.

Evidence: `docs/specs/REFERENCE_VAULT_BOUNDARY_SPEC.md`,
`docs/specs/REFERENCE_PRESENCE_DETECTION_V3.md`,
`reports/baseline-024/reference-detection-v3/v2_zero_promotion_diagnosis.json`,
`reports/baseline-024/reference-detection-v3/screening_yield.md`,
`reports/baseline-024/reference-detection-v3/batch_results/`,
`reports/baseline-024/reference-detection-v3/combined_package_registry.json`,
`reports/baseline-024/reference-detection-v3/revision_resolution_registry.json`,
`reports/baseline-024/reference-detection-v3/unresolved_reference_sets.json`,
`manifests/reference_detection/v3/`, and
`reports/baseline-024/reference-detection-v3/independent_audit.json`.

## baseline-024-cycle-000 reference detector calibration

Status: `DETECTOR_V3_RECALL_FAIL`.

Purpose: calibrate the frozen detector v3 recall against the 13 accepted
known-positive `ALLOWED_EVAL` projects before accepting any reference-universe
exhaustion conclusion.

Known-positive controls: `1110101, 1110103, 1110104, 1110203, 1110204,
1110205, 1110405, 1110410, 1110704, 1110801, 1120207, 1120305, 1120308`.

Blinding: classifier runtime manifests omitted expected labels, inventory
roles, filenames, and relative paths. The sealed control manifest was used by
the coordinator only after all replay outputs were frozen.

Detector: `target_output_detection_v3_page_content_isolated`.

Result: `0 / 13` known-positive projects detected all-three. Per-type recall:
`PRODUCTION_DRAWING 0 / 13`, `SHEETMETAL_DRAWING 8 / 13`, `PUNCH_DRAWING 0 /
13`. False-negative output-type count: `31`. Project-identity mismatch count:
`0`.

Evidence: `manifests/reference_detection/calibration/known_positive_controls.sealed.json`,
`manifests/reference_detection/calibration/v3_known_positive_replay/`,
`reports/baseline-024/reference-detector-calibration/known_positive_replay_summary.json`,
`reports/baseline-024/reference-detector-calibration/known_positive_replay_summary.md`,
and `orchestration/trajectories/reference_detection/calibration/`.

Generation status: not authorized. Negative controls, detector v4, expanded
screening, and final independent calibration audit were not run because the
positive recall gate failed.

## baseline-024-cycle-000 vision classifier availability gate

Status: `VISION_CLASSIFIER_UNAVAILABLE`.

Purpose: determine whether actual vision-capable classifiers may be used for
private completed-reference page and title-block classification before detector
v4.

Result: a fresh child inspected a non-private synthetic image and reported
actual model `GPT-5`, proving the installed child-agent path can inspect images.
However, `docs/PRIVACY_APPROVAL.md` remains `NOT_APPROVED`, so that path is not
available for private reference pages or title-block crops. No private project
image was transmitted. Actual private reference pages inspected by vision
agents: `0`.

Regression coverage: `scripts/run_tests.py` now includes
`test_reference_detector_v3_known_positive_recall_gate`, covering all 13 missed
known-positive replay projects and preventing deterministic local v3 output from
being accepted as actual vision classification. Full test runner status:
`PASS`.

Generation status: not authorized. Detector v4, negative controls, expanded
screening, final cohort freeze, and baseline generation did not run.

Evidence: `reports/baseline-024/reference-detector-calibration/vision_classifier_availability_probe.json`,
`reports/baseline-024/reference-detector-calibration/vision_classifier_availability_probe.md`,
and `scripts/run_tests.py`.

## baseline-024-cycle-000 autonomous qualification recovery

Status: `RECOVERY_PHASE_A_LOCAL_CAPABILITY_DISCOVERY_COMPLETE`.

Decision: `D-0021`.

Purpose: continue from method-specific blockers without weakening the
substantive `ALLOWED_EVAL` qualification gates, privacy boundary, reference
isolation, source-review quorum, sanitized-bundle verification, or no-generation
rule.

Checkpoint verification: HEAD `6d43a24f8c1d4150c2f81e0f3791ffd9df6b3983` was
clean at controller start; accepted bundle hash verification `PASS` for 13
bundle hash files; frozen workflow hash verification `PASS`; privacy remains
`NOT_APPROVED`; baseline generation attempts observed `0`.

Controller state: current verified `ALLOWED_EVAL` count remains `13 / 24`,
deficit `11`, reserve target `3`, prior v3 partial projects `129`,
not-individually-screened-by-v3 projects `262`, known-positive detector retry
cases `13`, previous bundle rejections `7`, and previous quarantined/no-bundle
projects `6`.

Detector reporting: regression gate behavior is
`PASS_BLOCKS_KNOWN_FAILING_DETECTOR`; detector performance remains `FAIL` with
known-positive all-three recall `0 / 13` and negative controls executed `0`.

Local capability discovery: Poppler `pdfinfo 26.05.0` and `pdftoppm 26.05.0`
are available from the bundled native runtime. Python modules `pypdf 6.10.0`,
Pillow `12.2.0`, and NumPy `2.3.5` are available. Windows.Media.Ocr is
available through a local Windows runtime probe. `pdfimages`, Tesseract,
OCRmyPDF, PaddleOCR, EasyOCR, ONNX Runtime, OpenCV, PyMuPDF, and ImageMagick
were unavailable in the local probe. No private project data was opened and no
network endpoint probe was performed.

Generation status: not authorized. Source-review quorum, sanitized-bundle
construction, final cohort freeze, baseline generation, review, and production
approval remain blocked until detector recovery, positive and negative
calibration, source qualification, bundle verification, and cohort audit pass.

Evidence: `docs/specs/AUTONOMOUS_QUALIFICATION_RECOVERY.md`,
`schemas/qualification_recovery_state.schema.json`,
`scripts/run_qualification_recovery.py`,
`orchestration/QUALIFICATION_RECOVERY_QUEUE.json`,
`reports/baseline-024/qualification-recovery/recovery_state.json`,
`reports/baseline-024/qualification-recovery/recovery_state.md`,
`reports/baseline-024/qualification-recovery/checkpoint_verification.json`,
and `reports/baseline-024/qualification-recovery/local_capability_probe.json`.

## baseline-024-cycle-000 detector v4 local recovery prototype

Status: `DETECTOR_V4_LOCAL_CALIBRATION_IN_PROGRESS`.

Purpose: create the next local-only detector candidate after v3 known-positive
recall failed and GPT-5/private-reference vision remained prohibited.

Protocol: v4 calibration was frozen before implementation. The deterministic
salted split creates 8 calibration controls and 5 sealed holdout controls from
the 13 known-positive `ALLOWED_EVAL` projects. The negative-control manifest
contains 24 minimized real non-target page controls from prior reference-vault
outputs. Holdout identities and results remain unavailable for tuning.

OCR proof: Windows.Media.Ocr synthetic execution passed through local
`Windows.Media.Ocr.OcrEngine.RecognizeAsync` hosted by `powershell.exe`.
Installed languages were `en-US` and `zh-Hant-TW`; Simplified Chinese was not
available. OCR text was not persisted, printed, logged, or returned. The
private-page OCR probe was skipped because an enforceable per-process
network-disable boundary was not available.

Implementation: `target_output_detection_v4_local_multisignal_recovery` adds
minimized v4 schemas, local Poppler rendering, pypdf embedded text, optional
Windows OCR role signals, Pillow/NumPy layout buckets, weak metadata priors,
duplicate grouping, combined-package page segmentation, and fail-closed
`AMBIGUOUS`/`UNCLASSIFIED` behavior.

Regression coverage: full repository test runner `PASS`. New coverage includes
Windows.Media.Ocr minimization, combined three-target packages, image-only OCR
target PDFs, CJK language availability recording, misleading target hints,
electrical/source-document negatives, OCR failure, missing OCR language support,
temporary-render deletion, raw OCR non-persistence, generator isolation, and
source-review blindness.

V4 calibration execution: frozen v4 ran on the 8-project calibration partition
with private OCR disabled. Gate implementation passed, but detector performance
failed with all-three recall `0 / 8` and private OCR page count `0`; cleanup,
minimization, generator isolation, and source-review blindness passed. The
failed evidence is preserved.

V4.1 calibration execution: `target_output_detection_v4_1_local_layout_prior_recovery`
passed the calibration partition with all-three recall `8 / 8` and per-type
recall `8 / 8` for `PRODUCTION_DRAWING`, `SHEETMETAL_DRAWING`, and
`PUNCH_DRAWING`. V4.1 passed all 24 minimized real negative controls with zero
false target pages, zero false all-three promotions, zero electrical/source
false target pages, private OCR page count `0`, external transmission count
`0`, cleanup `PASS`, raw-content persistence `PASS`, generator isolation
`PASS`, and source-review blindness `PASS`. Independent implementation audit
passed.

Generation status at this checkpoint: not authorized. This section is
superseded by the sealed-gate entry below; source qualification, cohort freeze,
baseline generation, review, optimization, and production approval remain
blocked.

## baseline-024-cycle-000 detector v4.1 sealed gate

Status: `DETECTOR_V4_1_INDEPENDENT_GATE_PASSED_SCREENING_PENDING`.

Purpose: complete the frozen v4.1 detector gate without exposing sealed
holdout identities, private page content, OCR text, rendered pages, crops, or
detailed detector outputs to implementation or generator-facing workspaces.

Sealed holdout result: `PASS`. All-three recall was `5 / 5`; per-type recall
was `5 / 5` for `PRODUCTION_DRAWING`, `SHEETMETAL_DRAWING`, and
`PUNCH_DRAWING`; private OCR page count was `0`; external transmission count
was `0`; holdout identities and detailed detector outputs were not persisted.

All-13 final recall result: `PASS`. Known-positive all-three recall was
`13 / 13`; per-type recall was `13 / 13`; private OCR page count was `0`;
detailed detector outputs were not persisted.

Negative controls: refreshed v4.1 real negative controls remained `PASS` with
`24 / 24` supported controls, zero false target pages, zero false all-three
promotions, zero electrical/source false target pages, and private OCR page
count `0`.

Independent audit: sealed-gate audit passed scoped persistence, temp-root
absence, cleanup, aggregate-evidence, and hash checks.

Evidence: `reports/baseline-024/reference-detector-calibration/v4_1_sealed_holdout/`,
`reports/baseline-024/reference-detector-calibration/v4_1_all13_final_recall/`,
`reports/baseline-024/reference-detector-calibration/v4_1_sealed_holdout_independent_audit.md`,
`reports/baseline-024/qualification-recovery/recovery_state.json`, and
`orchestration/QUALIFICATION_RECOVERY_QUEUE.json`.

Generation status: not authorized. The next action is
`RUN_DETECTOR_V4_1_CORPUS_WIDE_SCREENING` with minimized detector output only.
Source-review quorum, sanitized-bundle construction, cohort freeze, baseline
generation, review, optimization, and production approval remain blocked.
