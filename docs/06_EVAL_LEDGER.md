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

## sheetmetal-v1 modular foundation

Status: `SHEETMETAL_MODULAR_FOUNDATION_READY_FOR_ONE_PROJECT_CALIBRATION`.

Decision: `D-0025`.

Purpose: migrate V1 from the historical all-three-output qualification
objective to a sheetmetal-first canonical panel-model foundation.

Implemented foundation: source evidence filtering, component register,
panel assignment, accessory and cutout rule reconciliation, panel topology,
placement-constraint validation, typed relationship graph, canonical
sheet-metal drawing model, and provenance map.

Qualification state: `SHEETMETAL_ALLOWED_EVAL` approved count is `0`; 13
legacy `ALLOWED_EVAL` projects are queued as requalification candidates and are
not grandfathered.

Synthetic regression result: full `scripts/run_tests.py` status `PASS`.
`test_sheetmetal_v1_modular_foundation` covers quantity separation, conflicts,
post-design label rejection, inventory-only graph behavior, accessory duplicate
prevention, assignment/placement separation, named dimensions, hard placement
constraints, provenance coverage, and reference-leakage exclusion.

Independent audit: `reports/sheetmetal-v1/independent_audit.md` reports
`PASS_WITH_RESIDUAL_RISKS`. The coordinator addendum resolves the auditor-local
Git/Python tool limitations and the migration-report wording drift.

Generation status: no real customer sheet-metal drawing and no new baseline
generation occurred.

Evidence: `evals/fixtures/sheetmetal-v1/complete_pipeline_fixture.json`,
`scripts/sheetmetal_v1.py`, `schemas/*sheetmetal*`,
`schemas/component_*.schema.json`, `schemas/panel_*.schema.json`,
`schemas/accessory_rule.schema.json`,
`schemas/drawing_provenance_map.schema.json`, and
`reports/sheetmetal-v1/phase0_checkpoint_verification.json`.

## sheetmetal-v1 scoped frozen workflow Phase 0

Status: `ONE_PROJECT_SHEETMETAL_REQUALIFICATION_PHASE_0_PASS`.

Decision: `D-0026`.

Purpose: replace invalid current-tree comparison against the legacy
baseline-024 manifest with two scoped freeze checks.

Legacy scope result: `LEGACY_BASELINE_024_FROZEN_WORKFLOW_PROVENANCE_PASS`.
The historical anchor is `fac44321491633181f1fa53a062084d072b0b582`; all 15
legacy frozen hashes reproduce in a detached temporary worktree, including the
legacy `AGENTS.md` hash, and cleanup passed.

Active scope result: `SHEETMETAL_V1_ACTIVE_WORKFLOW_FREEZE_PASS`. The active
manifest anchors sheetmetal-v1 workflow semantics at
`ab955b854e31d37666445f5a62ee6556f85f1352` and verifies 47 stable active
workflow files at current descendant HEAD `75e1fbb20d8ec2dc38e18ec97fffe17b41a9d21b`.

Revised Phase-0 gate: legacy scope pass, active scope pass, current HEAD as a
documented descendant of request HEAD `b55ed7625cfaad4eccffda9c4bc0d1c1cd109c4d`,
tracked worktree clean before report write, only the known untracked legacy
script present, full `scripts/run_tests.py` pass, accepted legacy bundle hashes
pass for 13 bundle hash files, privacy `NOT_APPROVED`, no real sheetmetal-v1
generation artifacts, and no generator-facing completed-reference leakage.

Evidence: `docs/specs/FROZEN_WORKFLOW_SCOPE_AND_LINEAGE_POLICY.md`,
`scripts/verify_frozen_workflow.py`,
`evals/baseline-024/frozen_workflow_attestation.json`,
`evals/sheetmetal-v1/frozen_workflow_manifest.json`, and
`reports/sheetmetal-v1/revised_phase0_verification.json`.

## sheetmetal-v1 one-project candidate selection

Status: `ONE_PROJECT_SHEETMETAL_CANDIDATE_SELECTION_FREEZE_PASS`.

Decision: `D-0027`.

Selected project: `1110101`.

Selection method: deterministic metadata-only source-bundle-readiness ranking.
The frozen score formula gives `1110101` score `1156`, the highest score among
the 13 queued legacy candidates. The selection artifact records no completed
reference files read for selection.

Ordering boundary: the candidate selection was frozen in
`manifests/sheetmetal-v1/one_project_candidate_selection.json` before
completed-reference metadata was opened. The effective sheetmetal reference
package records the matching selection hash
`5EBD8164F0B02576644EA53B61018896DEAC7BF58C017E174F5F15A0303419E5`.

Reference package: `manifests/sheetmetal-v1/selected_candidate/1110101/effective_sheetmetal_reference_package.json`
qualifies one evaluator-only completed sheetmetal reference and records that
the generator receives no reference content, paths, or hashes.

Source classification: `manifests/sheetmetal-v1/selected_candidate/1110101/source_role_chronology_classification.json`
records six `AGENT_QUORUM_APPROVED_EVAL` source-only items and keeps twelve
quarantined items out of the generator bundle.

Bundle result: `manifests/sheetmetal-v1/selected_candidate/1110101/generator_bundle/verification_results.json`
is `PASS` with zero errors and zero warnings. `bundle_hashes.json` records 17
verified files; the bundle contains six sanitized CSV inputs, six previews,
and required source approval/provenance/visible-file/hash/verification
manifests. It excludes `reference_manifest.json`, original workbooks,
completed drawings, path escapes, and symlinks.

Independent audit: `reports/sheetmetal-v1/selected_candidate_1110101_independent_audit.md`
and `orchestration/results/SMV1-CANDIDATE-SELECTION-AUDIT.json` report `PASS`.

Generation status: no customer drawing was generated. `SHEETMETAL_ALLOWED_EVAL`
approved count remains `0`.

## sheetmetal-v1 one-project component graph calibration protocol

Status: `ONE_PROJECT_COMPONENT_GRAPH_CALIBRATION_IN_PROGRESS`.

Decision: `D-0028`.

Purpose: freeze the one-project component-register and typed-graph calibration
procedure for candidate `1110101` before any project-specific fact extraction.

Checkpoint verification: expected HEAD `5409f29` matched
`5409f2998eb77e3b61762b4d2d5c2f68835cb557`; the tracked worktree was clean;
the only permitted untracked file was the known legacy v4 corpus-screening
script; full `scripts/run_tests.py` returned final status `PASS`; legacy and
active scoped freeze verification returned `PASS`; the selected sanitized
bundle verifier returned `PASS`; all 17 recorded bundle hashes matched; all
six approved decisions had worksheet fingerprints; privacy remained
`NOT_APPROVED`; no sheetmetal-v1 customer drawing output or baseline-generation
directory existed.

Protocol result: the generator lane is source-only and
`SOURCE_MODE_A_INVENTORY_ONLY`; the evaluator lane remains closed until
generator artifacts are frozen and hashed; project-specific component facts and
graph contents must be written only to an ignored private workspace; committed
outputs are limited to neutral counts, hashes, coverage metrics, status codes,
schemas, scripts, synthetic fixtures, and audit summaries.

Generation status: no customer drawing was generated. `SHEETMETAL_ALLOWED_EVAL`
approved count remains `0`.

Evidence: `docs/specs/ONE_PROJECT_COMPONENT_GRAPH_CALIBRATION.md`,
`manifests/sheetmetal-v1/one-project-model-calibration/1110101/calibration_protocol.json`,
and `reports/sheetmetal-v1/one-project-model-calibration/1110101/calibration_plan.md`.

## sheetmetal-v1 one-project private workspace boundary

Status: `PASS`.

Decision: `D-0029`.

Purpose: establish the ignored private workspace before writing
project-specific source facts, component registers, graph contents, accessory
reconciliation, panel assignments, or provenance mappings.

Result: `.private/` is now ignored. The local workspace
`.private/sheetmetal-v1/1110101/` was created. `git check-ignore` passes for
`.private/sheetmetal-v1/1110101/private-output-probe.json`; `git ls-files --
.private` returns no tracked paths; and
`test_sheetmetal_v1_private_workspace_boundary` covers the boundary in the full
test suite. The active sheetmetal-v1 scoped workflow manifest was refreshed to
include `.gitignore` and the updated `scripts/run_tests.py` hash.

Generation status: no project-specific facts were written. No customer drawing
was generated. `SHEETMETAL_ALLOWED_EVAL` approved count remains `0`.

Evidence:
`evals/sheetmetal-v1/frozen_workflow_manifest.json`,
`reports/sheetmetal-v1/one-project-model-calibration/1110101/private_workspace_boundary.md`
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/private_workspace_boundary.json`.

## sheetmetal-v1 one-project source-fact extraction

Status: `PASS`.

Decision: `D-0030`.

Purpose: extract source facts from the approved sanitized `1110101` generator
bundle while keeping project-specific values in the ignored private workspace.

Implementation: `scripts/sheetmetal_v1.py` accepts `--bundle-dir`,
`--source-classification`, `--output-dir`, and `--quiet` for source-only
bundle extraction. It writes `source_fact_model.json` and
`source_fact_validation.json` only to the requested output directory.

Private run: output was written to
`.private/sheetmetal-v1/1110101/source-fact-extraction/`. Both private outputs
are ignored by Git and no `.private` path is tracked.

Validation result: schema validation `PASS`; evidence count `6`; source line
count `125`; source fact count `87`; source line accounting count `125`;
silently discarded authorized source lines `0`; quantity-stage overwrite
violations `0`; completed-reference facts `0`; private content transmission
count `0`.

Regression result: full `scripts/run_tests.py` status `PASS`.
`test_sheetmetal_v1_source_fact_extractor` covers source-value non-printing,
schema validity, row accounting, quantity-stage separation, the approved
generic current-project role token, long-form chronology normalization, and
`NO_SIGNAL_IN_APPROVED_METADATA` reference-flag parsing.

Generation status: no customer drawing, PDF, DXF, DWG, drawing model,
baseline generation, or `SHEETMETAL_ALLOWED_EVAL` promotion occurred.

Evidence:
`schemas/source_fact_model.schema.json`,
`scripts/sheetmetal_v1.py`,
`scripts/run_tests.py`,
`evals/sheetmetal-v1/frozen_workflow_manifest.json`,
`reports/sheetmetal-v1/one-project-model-calibration/1110101/source_fact_extraction_summary.md`,
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/source_fact_extraction_summary.json`.

## sheetmetal-v1 one-project component register

Status: `PASS`.

Decision: `D-0031`.

Purpose: construct the private component register from the private `1110101`
source-fact model without committing project-specific values.

Implementation: `scripts/sheetmetal_v1.py` accepts `--source-fact-model` for
register-only construction. It writes `component_register.json` and
`component_register_validation.json` only to the requested private output
directory.

Private run: input was
`.private/sheetmetal-v1/1110101/source-fact-extraction/source_fact_model.json`;
output was written to `.private/sheetmetal-v1/1110101/component-register/`.
Both private outputs are ignored by Git and no `.private` path is tracked.

Validation result: component register schema `PASS`; component type schema
`PASS`; component instance schema `PASS`; component type count `53`;
component instance count `53`; conflict count `0`; source fact count `87`;
source line count `125`; unregistered allowed component key count `0`;
completed-reference component count `0`; private content transmission count
`0`.

Regression result: full `scripts/run_tests.py` status `PASS`.
`test_sheetmetal_v1_component_register_from_source_facts` covers source-value
non-printing, formal source-fact fields, schema validity, quantity-stage
preservation, and registration coverage.

Generation status: no customer drawing, PDF, DXF, DWG, drawing model,
baseline generation, or `SHEETMETAL_ALLOWED_EVAL` promotion occurred.

Evidence:
`scripts/sheetmetal_v1.py`,
`scripts/run_tests.py`,
`evals/sheetmetal-v1/frozen_workflow_manifest.json`,
`reports/sheetmetal-v1/one-project-model-calibration/1110101/component_register_summary.md`,
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/component_register_summary.json`.

## sheetmetal-v1 one-project panel graph

Status: `PASS`.

Decision: `D-0032`.

Purpose: construct private panel-assignment and typed graph artifacts from the
private `1110101` source-fact model and component register without committing
project-specific values.

Implementation: `scripts/sheetmetal_v1.py` accepts `--source-fact-model` plus
`--component-register` for panel-assignment and inventory-only graph
construction. It writes `panel_assignment.json`, `panel_graph.json`, and
`panel_graph_validation.json` only to the requested private output directory.

Private run: inputs were the private source-fact model and private component
register; output was written to `.private/sheetmetal-v1/1110101/panel-graph/`.
All private outputs are ignored by Git and no `.private` path is tracked.

Validation result: panel assignment schema `PASS`; panel graph schema `PASS`;
assignment count `0`; unresolved component count `53`; rejected assignment
count `0`; graph node count `56`; graph edge count `107`; dangling edge count
`0`; edge counts `CONNECTS_TO=1`, `INSTANCE_OF=53`, `REQUIRED_BY=53`;
private content transmission count `0`.

Regression result: full `scripts/run_tests.py` status `PASS`.
`test_sheetmetal_v1_panel_assignment_graph_from_private_models` covers explicit
panel assignment acceptance, unresolved component preservation, graph
referential integrity, inventory-only unverified functional edges, and
source-value non-printing.

Generation status: no customer drawing, PDF, DXF, DWG, drawing model,
baseline generation, or `SHEETMETAL_ALLOWED_EVAL` promotion occurred.

Evidence:
`scripts/sheetmetal_v1.py`,
`scripts/run_tests.py`,
`evals/sheetmetal-v1/frozen_workflow_manifest.json`,
`reports/sheetmetal-v1/one-project-model-calibration/1110101/panel_graph_summary.md`,
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/panel_graph_summary.json`.

## sheetmetal-v1 one-project accessory and cutout reconciliation

Status: `PASS`.

Decision: `D-0033`.

Purpose: reconcile private accessory requirements and generated cutouts against
the private `1110101` source-fact model, component register, and typed graph
without committing project-specific values.

Implementation: `scripts/sheetmetal_v1.py` accepts `--source-fact-model` plus
`--component-register` plus `--panel-graph` for accessory/cutout
reconciliation. It writes `accessory_requirements.json` and
`accessory_cutout_validation.json` only to the requested private output
directory.

Private run: inputs were the private source-fact model, private component
register, and private panel graph; output was written to
`.private/sheetmetal-v1/1110101/accessory-cutout/`. All private outputs are
ignored by Git and no `.private` path is tracked.

Validation result: requirement count `0`; generated component instance count
`0`; cutout count `0`; duplicate accessory count `0`; graph node count `56`;
graph edge count `107`; missing requirement source count `0`; missing cutout
source count `0`; private content transmission count `0`.

Regression result: full `scripts/run_tests.py` status `PASS`.
`test_sheetmetal_v1_accessory_cutout_reconciliation_from_private_models`
covers source-value non-printing, generated accessory and cutout behavior from
an approved synthetic rule, graph-source referential integrity, and privacy
counter preservation.

Generation status: no customer drawing, PDF, DXF, DWG, drawing model,
baseline generation, or `SHEETMETAL_ALLOWED_EVAL` promotion occurred.

Evidence:
`scripts/sheetmetal_v1.py`,
`scripts/run_tests.py`,
`evals/sheetmetal-v1/frozen_workflow_manifest.json`,
`reports/sheetmetal-v1/one-project-model-calibration/1110101/accessory_cutout_summary.md`,
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/accessory_cutout_summary.json`.

## sheetmetal-v1 one-project generator freeze

Status: `PASS`.

Decision: `D-0034`.

Purpose: freeze generator-side private artifacts and prove deterministic rerun
behavior before opening evaluator-only calibration.

Implementation: the source-fact extraction, component-register, panel-graph,
and accessory/cutout stages were rerun from the frozen sanitized source bundle
and source-role/chronology classification into
`.private/sheetmetal-v1/1110101/freeze-rerun/`.

Deterministic result: 9 private artifacts were compared. Seven were
byte-identical. All 9 matched under canonical JSON hashing with sorted keys
and compact separators. No fields were excluded.

Hard gates: full tests `PASS`; legacy scoped freeze `PASS`; active scoped
freeze `PASS`; bundle hashes and worksheet fingerprints `PASS`; private
content transmission count `0`; reference leakage `0`; post-design leakage
`0`; unsupported critical generated facts `0`; silently discarded authorized
source lines `0`; quantity-stage overwrite violations `0`; graph
referential-integrity failures `0`; forbidden functional edges in
inventory-only mode `0`; unsupported panel assignments `0`; duplicate inferred
accessories `0`; temporary private-artifact leakage into Git `0`; customer
drawing outputs `0`.

Generation status: no customer drawing, PDF, DXF, DWG, drawing model,
baseline generation, or `SHEETMETAL_ALLOWED_EVAL` promotion occurred.

Evidence:
`reports/sheetmetal-v1/one-project-model-calibration/1110101/generator_freeze_summary.md`
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/generator_freeze_summary.json`.

## sheetmetal-v1 one-project evaluator metrics

Status: `PASS_WITH_SOURCE_LIMITED_PANEL_ASSIGNMENT_COVERAGE`.

Decision: `D-0035`.

Purpose: record evaluator-only component graph metrics with explicit
numerators, denominators, scorable coverage, and confidence after generator
freeze.

Method: metrics were computed from frozen generator summaries and the
qualified effective sheetmetal reference package metadata. Completed-reference
content was not opened for metric values, generator artifacts were not
modified, and only neutral counts were committed.

Result: source line representation `125 / 125`; authorized source fact
retention `87 / 87`; component registration coverage `53 / 53`; conflict-free
component coverage `53 / 53`; panel assignment resolution `0 / 53`; graph
referential integrity `107 / 107`; inventory-only functional safety `1 / 1`;
accessory rule scorability `0 / 0`; deterministic freeze canonical match
`9 / 9`; evaluator reference package availability `1 / 1`; generator
reference isolation `2 / 2`.

Interpretation: panel assignment remains source-limited and safely unresolved
for all 53 components. Accessory-rule scoring is denominator-zero because no
approved accessory rules were present.

Evidence:
`reports/sheetmetal-v1/one-project-model-calibration/1110101/evaluator_metrics_summary.md`
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/evaluator_metrics_summary.json`.

## sheetmetal-v1 one-project topology sizing placement implementation freeze

Status: `FROZEN_AUDIT_PENDING`.

Decision: `D-0038`.

Purpose: execute `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION`
for candidate `1110101` without generating customer drawings or performing
final independent adjudication in the implementation thread.

Protocol: `D-0037` freezes the generator/evaluator lane split, private
workspace, source-only panel-assignment recovery, topology/sizing separation,
placement hard constraints, deterministic rerun, and minimized evaluator
metrics.

Capability result: no approved installed OR-Tools, SciPy optimize, PuLP, or
Z3 solver was available. The selected execution is a deterministic greedy
baseline plus complete hard-constraint validator. No dependency download
occurred.

Private generator result: 53 component instances were processed. Source-only
assignment recovery produced 0 explicit assignments, 0 rule assignments, 53
safe unassigned components, and 0 unsupported assignments. Topology remained
safe unresolved with 1 neutral candidate. Geometry coverage was source-limited
at 0 verified/generic envelopes out of 53 component instances. Placement
produced 0 accepted placements and 53 explicit unplaced components.

Determinism result: 12 topology-stage private artifacts were rerun from
identical frozen inputs. All 12 were byte-identical and canonical-JSON
identical. No fields were excluded.

Validation result: unsupported critical dimensions `0`, unsupported panel
assignments `0`, unsupported placements `0`, accepted overlap violations `0`,
containment violations `0`, clearance violations `0`, quantity-stage
overwrite violations `0`, completed-reference leakage `0`, post-design leakage
`0`, private transmissions `0`, tracked private artifacts `0`, and customer
PDF/DXF/DWG generation `0`.

Evaluator metrics: assignment coverage `0/53`, placement coverage `0/53`, and
deterministic rerun `12/12`. Topology and sizing recall are not reported for
zero source-supported denominators. Safe unresolved values are not scored as
wrong merely because completed historical drawings may contain unavailable
design choices.

Verification result: full `scripts/run_tests.py` status `PASS`; legacy scoped
freeze `PASS`; active sheetmetal-v1 scoped freeze `PASS`; topology-stage
scoped freeze `PASS`.

Evidence:
`reports/sheetmetal-v1/one-project-topology-calibration/1110101/implementation_checkpoint.json`,
`reports/sheetmetal-v1/one-project-topology-calibration/1110101/generator_freeze_summary.json`,
`reports/sheetmetal-v1/one-project-topology-calibration/1110101/evaluator_metrics_summary.json`,
and
`evals/sheetmetal-v1/topology-sizing-placement/frozen_workflow_manifest.json`.


## sheetmetal-v1 one-project independent component graph audit

Status: `PASS`.

Decision: `D-0036`.

Purpose: independently adjudicate candidate `1110101` after source-fact extraction, component-register construction, panel-assignment/graph construction, accessory/cutout reconciliation, deterministic generator freeze, and evaluator-only metrics.

Checkpoint result: HEAD `abc5a86`; tracked worktree clean except for the permitted legacy untracked screening script; full tests `PASS`; active sheetmetal-v1 scoped freeze `PASS`; legacy baseline-024 scoped freeze `PASS`; selected sanitized bundle verification `PASS`; privacy `NOT_APPROVED`; no tracked private artifacts; no generated customer drawings.

Determinism result: canonical matches `9 / 9`; byte-identical matches `7 / 9`. The byte-only mismatches were `source_fact_model.json` and `component_register_validation.json`; both had structural diff count `0`, matching canonical hashes, and no excluded fields.

Hard-gate result: all qualification-critical gates passed, including generator/reference separation, post-design-label separation, private transmission count `0`, unsupported critical facts `0`, silently discarded source lines `0`, quantity overwrite violations `0`, graph referential failures `0`, forbidden functional edges `0`, unsupported panel assignments `0`, duplicate inferred accessories `0`, unsupported cutout geometry `0`, private Git leakage `0`, temporary cleanup `PASS`, and customer drawing generation count `0`.

Metric interpretation: panel assignment remains safely unresolved at `0 / 53` and is assigned to `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION`. Accessory-rule scorability remains `0 / 0`; no recall is reported for a zero denominator.

Result: `1110101` is accepted as the first `SHEETMETAL_ALLOWED_EVAL` calibration project for the modular component-register and graph stage. Approved count is now `1`. This is not production approval and does not authorize drawing generation.

Evidence:
`manifests/sheetmetal-v1/one-project-model-calibration/1110101/audit_input_manifest.json`,
`reports/sheetmetal-v1/one-project-model-calibration/1110101/independent_audit.json`,
`reports/sheetmetal-v1/one-project-model-calibration/1110101/hard_gate_adjudication.json`,
and
`reports/sheetmetal-v1/one-project-model-calibration/1110101/determinism_adjudication.json`.

## sheetmetal-v1 one-project topology sizing placement independent audit

Status: `INCONCLUSIVE_LOW_COVERAGE`.

Decision: `D-0039`.

Purpose: independently adjudicate the frozen topology/sizing/placement
implementation for candidate `1110101` before any model or renderer promotion.

Safety and implementation integrity: `PASS`. The coordinator addendum reran
fresh full tests and the legacy, active sheetmetal-v1, and topology-stage
scoped freezes with the bundled runtime; all passed. Deterministic rerun
remains `12 / 12`, completed-reference leakage remains `0`, post-design
leakage remains `0`, private transmissions remain `0`, tracked private
artifacts remain `0`, and customer PDF/DXF/DWG generation remains `0`.

Engineering capability: `INCONCLUSIVE_LOW_COVERAGE`. Assignment coverage is
`0 / 53`, geometry coverage is `0 / 53`, and placement coverage is `0 / 53`.
These safe unresolved states are not capability success.

Result: branch to `RUN_TARGETED_COVERAGE_RECOVERY_T1`. No customer drawing was
generated, no production approval was declared, and
`SHEETMETAL_ALLOWED_EVAL` remains `1`.

Evidence:
`manifests/sheetmetal-v1/one-project-topology-calibration/1110101/audit_input_manifest.json`,
`reports/sheetmetal-v1/one-project-topology-calibration/1110101/independent_audit.json`,
`reports/sheetmetal-v1/one-project-topology-calibration/1110101/hard_gate_adjudication.json`,
`reports/sheetmetal-v1/one-project-topology-calibration/1110101/determinism_adjudication.json`,
`reports/sheetmetal-v1/one-project-topology-calibration/1110101/coordinator_audit_addendum.json`,
and
`orchestration/master/child-results/SMV1-T0-INDEPENDENT-TOPOLOGY-AUDIT.json`.

## sheetmetal-v1 T1 targeted coverage recovery

Status: `T1_SAFE_UNRESOLVED_AUDIT_ACCEPTED_SOURCE_RULE_PROPOSAL_PENDING`.

Decision: `D-0040`.

Purpose: attempt bounded recovery for the T0 low-coverage result without
inventing unsupported panel assignments, component geometry, topology, sizing,
or placements.

Worker result: the panel-assignment, component-geometry, and
topology/sizing-rule recovery workers all returned safe-unresolved outcomes.
They found no compliant approved-source or approved-rule path and made no
implementation, rule, schema, frozen-release, or frozen-grader changes.

Integration result: `SAFE_UNRESOLVED_T1_NO_COMPLIANT_CODE_OR_RULE_RECOVERY_PATHS_AUDIT_REQUIRED`.

Independent audit result:
`PASS_SAFE_UNRESOLVED_T1_NO_COMPLIANT_RECOVERY_PATHS`.

Coordinator addendum: full `scripts/run_tests.py` passed with the bundled
runtime, and the legacy baseline-024, active sheetmetal-v1, and
topology-stage scoped frozen workflow verifiers all passed.

Coverage remains source-limited: assignment `0/53`, component geometry `0/53`,
topology `0/1`, sizing `0/0`, and placement `0/53`. This is safe unresolved
evidence only, not engineering capability success and not drawing readiness.

Generation status: no customer drawing, PDF, DXF, or DWG was generated; no
production approval was declared; `SHEETMETAL_ALLOWED_EVAL` remains `1`.

Evidence:
`reports/sheetmetal-v1/t1-coverage-recovery/panel_assignment_recovery_report.json`,
`reports/sheetmetal-v1/t1-coverage-recovery/component_geometry_recovery_report.json`,
`reports/sheetmetal-v1/t1-coverage-recovery/topology_sizing_rule_recovery_report.json`,
`reports/sheetmetal-v1/t1-coverage-recovery/t1_integration_summary.json`,
`reports/sheetmetal-v1/t1-coverage-recovery/t1_independent_recovery_audit.json`,
`reports/sheetmetal-v1/t1-coverage-recovery/t1_coordinator_audit_addendum.json`,
and `orchestration/master/child-results/SMV1-T1-INDEPENDENT-RECOVERY-AUDIT.json`.

## sheetmetal-v1 source/rule approval proposal review

Status: `SOURCE_RULE_PROPOSAL_REVIEW_PASS_AUTHORITY_DECISION_PENDING`.

Decision: `D-0041`.

Purpose: review a proposal-first authority branch for T1 blockers before any
implementation or rule/source approval can occur.

Proposal lanes:

- `LANE_A_PANEL_ALLOCATION_SOURCE`;
- `LANE_B_COMPONENT_GEOMETRY_AUTHORITY`;
- `LANE_C_TOPOLOGY_SIZING_PLACEMENT_RULES`.

Independent review result:
`PASS_PROPOSAL_READY_FOR_HUMAN_OR_AUTHORITY_REVIEW`.

The review verified the proposal was proposal-only, bound to T1 evidence
hashes, preserved forbidden-use boundaries, defined valid authority paths,
rejected no-invention shortcuts, required regression tests before fixes, and
bounded diff scope and rollback.

Generation status: no implementation was applied, no customer drawing, PDF,
DXF, or DWG was generated, and no production approval was declared.

Evidence:
`reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_approval_proposal.json`,
`reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_approval_proposal_review.json`,
and
`orchestration/master/child-results/SMV1-SOURCE-RULE-APPROVAL-PROPOSAL-REVIEW.json`.

## sheetmetal-v1 source/rule authority decision packet

Status: `SOURCE_RULE_AUTHORITY_DECISION_PACKET_PREPARED_HUMAN_DECISION_REQUIRED`.

Decision: `D-0042`.

Purpose: create the explicit source/rule authority decision surface after the
proposal review passed.

Packet result:

- `LANE_A_PANEL_ALLOCATION_SOURCE`:
  `AUTHORITY_REQUIRED_NOT_ACCEPTED_AUTONOMOUSLY`.
- `LANE_B_COMPONENT_GEOMETRY_AUTHORITY`:
  `AUTHORITY_REQUIRED_NOT_ACCEPTED_AUTONOMOUSLY`.
- `LANE_C_TOPOLOGY_SIZING_PLACEMENT_RULES`:
  `FABRICATION_DOMAIN_DECISION_REQUIRED_NOT_ACCEPTED_AUTONOMOUSLY`.

Human authority choices are to authorize panel allocation source review,
authorize component geometry authority, authorize topology/sizing/placement
rule authority, or reject all lanes. Rejecting all lanes moves to
terminal-candidate review.

Generation status: no implementation was applied, no customer drawing, PDF,
DXF, or DWG was generated, and no production approval was declared.

Evidence:
`reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_authority_decision_packet.json`
and
`orchestration/master/child-results/SMV1-SOURCE-RULE-AUTHORITY-DECISION-PACKET.json`.

## sheetmetal-v1 signed authority decision template

Status: `SIGNED_AUTHORITY_DECISION_TEMPLATE_PREPARED_NO_AUTHORITY_SELECTED`.

Purpose: provide a signed-decision form for the pending source/rule authority
gate without selecting any lane or authorizing implementation.

Template choices remain panel allocation source review, component geometry
authority, topology/sizing/placement rule authority, or reject all lanes.

Generation status: no implementation was applied, no customer drawing, PDF,
DXF, or DWG was generated, and no production approval was declared.

Evidence:
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_template.json`,
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_template.md`,
and
`orchestration/master/child-results/SMV1-SIGNED-HUMAN-SOURCE-RULE-AUTHORITY-DECISION-TEMPLATE.json`.

## sheetmetal-v1 signed authority decision validator

Status: `SIGNED_AUTHORITY_DECISION_VALIDATOR_READY_NO_AUTHORITY_SELECTED`.

Decision: `D-0043`.

Purpose: make the pending signed human/source-rule authority decision
machine-checkable before any accepted-lane implementation work can start.

Validator result:

- Validates choices `A`, `B`, `C`, or mutually exclusive `D`.
- Verifies the decision is bound to the authority packet and signed-decision
  template by SHA-256.
- Requires signer, date, signed statement, and all non-negotiable constraint
  acknowledgements.
- Rejects customer PDF/DXF/DWG generation and production approval flags.
- Reports `implementation_can_start` as false; accepted lanes still require
  regression tests before fixes.

Verification: full `scripts/run_tests.py` passed, including legacy, active
sheetmetal-v1, and topology-stage scoped frozen workflow checks.

Generation status: no implementation lane was selected, no customer drawing,
PDF, DXF, or DWG was generated, and no production approval was declared.

Evidence:
`schemas/signed_authority_decision.schema.json`,
`scripts/validate_signed_authority_decision.py`,
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_validator_summary.json`,
and
`orchestration/master/child-results/SMV1-SIGNED-AUTHORITY-DECISION-VALIDATOR.json`.

## sheetmetal-v1 signed authority decision intake

Status: `SIGNED_AUTHORITY_DECISION_INTAKE_READY_NO_AUTHORITY_SELECTED`.

Decision: `D-0044`.

Purpose: route future signed source/rule authority decisions after validator
success without selecting any authority lane or authorizing implementation.

Intake result:

- Accepted valid lanes route to
  `ADD_REGRESSION_TESTS_BEFORE_ACCEPTED_AUTHORITY_LANE_FIX`.
- Valid reject-all decisions route to `ENTER_TERMINAL_CANDIDATE_REVIEW`.
- Invalid signed decisions fail closed and remain at
  `WAIT_FOR_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION`.

Verification: full `scripts/run_tests.py` passed, including the new
`test_signed_authority_decision_intake_routing` regression and the legacy,
active sheetmetal-v1, and topology-stage scoped frozen workflow checks.

Generation status: no implementation lane was selected, no customer drawing,
PDF, DXF, or DWG was generated, and no production approval was declared.

Evidence:
`scripts/prepare_signed_authority_intake.py`,
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_intake_summary.json`,
and
`orchestration/master/child-results/SMV1-SIGNED-AUTHORITY-DECISION-INTAKE.json`.

## sheetmetal-v1 unsigned signed authority decision draft

Status: `UNSIGNED_AUTHORITY_DECISION_DRAFT_READY_FAIL_CLOSED`.

Decision: `D-0045`.

Purpose: provide a fillable JSON draft for the pending signed source/rule
authority decision while preserving fail-closed behavior until a valid signed
decision exists.

Draft result:

- `selected_choice_ids` is empty.
- `signed_by` is empty.
- `signed_at` is the literal placeholder `YYYY-MM-DD`.
- The draft is bound to the current source/rule authority decision packet and
  signed-decision template hashes.
- The validator intentionally returns `FAIL` with missing choice, signer, and
  date errors while hash checks pass.

Verification: full `scripts/run_tests.py` passed, including
`test_signed_authority_decision_draft_scaffold_fail_closed` and the legacy,
active sheetmetal-v1, and topology-stage scoped frozen workflow checks.

Generation status: no authority lane was selected, no implementation was
applied, no customer drawing, PDF, DXF, or DWG was generated, and no
production approval was declared.

Evidence:
`scripts/prepare_signed_authority_decision_draft.py`,
`reports/sheetmetal-v1/source-rule-approval/smv1_unsigned_authority_decision_draft.json`,
`reports/sheetmetal-v1/source-rule-approval/smv1_unsigned_authority_decision_draft_validation.json`,
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_draft_summary.json`,
and
`orchestration/master/child-results/SMV1-SIGNED-AUTHORITY-DECISION-DRAFT.json`.

## sheetmetal-v1 signed authority decision submission processor

Status: `SIGNED_AUTHORITY_DECISION_SUBMISSION_PROCESSOR_READY_FAIL_CLOSED`.

Decision: `D-0046`.

Purpose: process a future signed source/rule authority decision into a complete
validation, intake, and submission-summary package with one command.

Processor result:

- Validator-passing accepted lanes route to
  `ADD_REGRESSION_TESTS_BEFORE_ACCEPTED_AUTHORITY_LANE_FIX`.
- Validator-passing reject-all decisions route to
  `ENTER_TERMINAL_CANDIDATE_REVIEW`.
- Invalid decisions fail closed and remain at
  `WAIT_FOR_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION`.
- Implementation authorization, customer PDF/DXF/DWG generation, and
  production approval remain false.

Unsigned draft proof: the current unsigned draft was processed into
`reports/sheetmetal-v1/source-rule-approval/smv1_unsigned_authority_decision_submission/`.
The processor returned expected exit code `1`, reported missing choice, signer,
and date errors, preserved passing packet/template hash checks, and kept the
next action at `WAIT_FOR_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION`.

Verification: full `scripts/run_tests.py` passed, including
`test_signed_authority_decision_submission_package` and the legacy, active
sheetmetal-v1, and topology-stage scoped frozen workflow checks.

Generation status: no authority lane was selected, no implementation was
applied, no customer drawing, PDF, DXF, or DWG was generated, and no
production approval was declared.

Evidence:
`scripts/process_signed_authority_decision.py`,
`reports/sheetmetal-v1/source-rule-approval/smv1_unsigned_authority_decision_submission/submission_summary.json`,
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_submission_processor_summary.json`,
and
`orchestration/master/child-results/SMV1-SIGNED-AUTHORITY-DECISION-SUBMISSION-PROCESSOR.json`.

## sheetmetal-v1 signed authority decision accepted

Status: `SIGNED_AUTHORITY_DECISION_VALIDATED_INTAKE_READY`.

Decision: `D-0047`.

Result:

- Selected choices: `A`, `B`, and `C`.
- Rejected choice: `D`.
- Validator status: `PASS`.
- Processor next action:
  `ADD_REGRESSION_TESTS_BEFORE_ACCEPTED_AUTHORITY_LANE_FIX`.
- Implementation authorization: `false`.
- Customer PDF/DXF/DWG generation authorization: `false`.
- Production approval declared: `false`.
- Privacy approval remains `NOT_APPROVED`.

Verification:

- Full `scripts/run_tests.py`: `PASS`.
- Legacy baseline-024 scoped freeze: `PASS`.
- Active sheetmetal-v1 scoped freeze: `PASS`.
- Topology/sizing/placement scoped freeze: `PASS`.

T1 authorized recovery queue:

- `SMV1-T1A-PANEL-ALLOCATION-RECOVERY` pending worktree
  `local:4d54348d-e6ef-46c5-b8a7-f1daf3df1732`.
- `SMV1-T1B-COMPONENT-GEOMETRY-RECOVERY` pending worktree
  `local:05e9923c-fa55-4899-a85a-9a21cfe9d508`.
- `SMV1-T1C-TOPOLOGY-SIZING-RULE-RECOVERY` pending worktree
  `local:15401954-4eed-43da-9544-e517d1ddecc5`.

Evidence:
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision.json`,
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_validation.json`,
`reports/sheetmetal-v1/source-rule-approval/smv1_signed_authority_decision_submission/submission_summary.json`,
and
`orchestration/master/child-results/SMV1-SIGNED-HUMAN-SOURCE-RULE-AUTHORITY-DECISION.json`.

## sheetmetal-v1 T1 authorized recovery integration

Status: `T1_AUTHORIZED_RECOVERY_INTEGRATED_AUDIT_REQUIRED`.

Decision: `D-0049`.

Purpose: integrate the adjudicated authorized recovery worker outputs for T1A,
T1B, and T1C after the signed A+B+C authority decision, while preserving the
independent audit gate before T2, model promotion, or drawing generation.

Integration result:

- T1A remains `SAFE_UNRESOLVED_NO_APPROVED_PANEL_ALLOCATION_SOURCE`.
- T1B remains `SAFE_UNRESOLVED_GEOMETRY_REQUIRES_MORE_AUTHORITY_OR_DATA`; real-project geometry coverage remains `0/53`, and the new authority-state coverage is synthetic only.
- T1C worker status was `RECOVERABLE_BLOCKER`; the coordinator did not reproduce stale hash gates on `main`, and the rule artifacts remain proposal-only pending independent audit.

Verification:

- Full `scripts/run_tests.py`: `PASS`.
- Legacy baseline-024 scoped freeze: `PASS`.
- Active sheetmetal-v1 scoped freeze: `PASS`.
- Topology/sizing/placement scoped freeze: `PASS`.

Hard gates: source-root mutation `0`, private external transmission `0`,
completed-reference leakage `0`, post-design leakage `0`, customer
PDF/DXF/DWG generation `0`, and production approval `false`.

Evidence:
`reports/sheetmetal-v1/t1-authorized-recovery/integration/t1_authorized_recovery_integration_summary.json`,
`orchestration/master/child-results/SMV1-T1-AUTHORIZED-RECOVERY-INTEGRATION.json`,
`orchestration/tasks/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.md`, and
`orchestration/input_manifests/sheetmetal-v1/t1-authorized-recovery/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.visible_files.json`.

## sheetmetal-v1 T1 authorized recovery independent audit

Status: `T1_AUTHORIZED_RECOVERY_INDEPENDENT_AUDIT_PASS_T2_READY`.

Decision: `D-0050`.

Purpose: independently audit the integrated authorized T1A/T1B/T1C recovery
result before T2 recalibration, model promotion, renderer work, customer
drawing generation, or readiness promotion.

Result:

- Independent audit status:
  `PASS_T1_AUTHORIZED_RECOVERY_INDEPENDENT_AUDIT_SAFE_UNRESOLVED_PROPOSAL_ONLY`.
- T1A remains `SAFE_UNRESOLVED_NO_APPROVED_PANEL_ALLOCATION_SOURCE`.
- T1B remains safe unresolved with real-project geometry coverage `0/53`;
  synthetic authority-state fixture coverage is not counted as real-project
  capability success.
- T1C remains proposal-only and was not promoted into the canonical model,
  renderer, frozen generator, or T2 recalibration input.

Verification:

- Full `scripts/run_tests.py`: `PASS`.
- Legacy baseline-024 scoped freeze: `PASS`.
- Active sheetmetal-v1 scoped freeze: `PASS`.
- Topology/sizing/placement scoped freeze: `PASS`.
- Declared non-self output hashes: `PASS`.

Hard gates: source-root mutation `0`, private external transmission `0`,
completed-reference leakage `0`, post-design leakage `0`, customer
PDF/DXF/DWG generation `0`, and production approval `false`.

Evidence:
`reports/sheetmetal-v1/t1-authorized-recovery/independent-audit/t1_authorized_recovery_independent_audit.json`,
`reports/sheetmetal-v1/t1-authorized-recovery/independent-audit/t1_authorized_recovery_independent_audit.md`,
and
`orchestration/master/child-results/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.json`.

## sheetmetal-v1 T2 topology/sizing/placement recalibration gate

Status: `T2_TOPOLOGY_SIZING_PLACEMENT_RECALIBRATION_SAFE_UNRESOLVED_AUDIT_REQUIRED`.

Decision: `D-0051`.

The accepted T1 audit produced no promotable T2 input. T1A and T1B remain safe unresolved, T1C rule artifacts remain proposal-only, and coverage remains assignment `0/53`, real-project geometry `0/53`, sizing with zero source-supported denominator, and placement `0/53`. No private generator rerun was performed because this heartbeat forbids `.private` mutation. Full tests and legacy, active sheetmetal-v1, and topology-stage scoped freezes pass. Evidence: `reports/sheetmetal-v1/t2-recalibration/t2_topology_sizing_placement_recalibration_summary.json`, `reports/sheetmetal-v1/t2-recalibration/t2_topology_sizing_placement_recalibration_summary.md`, and `orchestration/master/child-results/SMV1-T2-TOPOLOGY-SIZING-PLACEMENT-RECALIBRATION.json`.

## sheetmetal-v1 T2 topology/sizing/placement independent audit

Status: `T2_RECALIBRATION_AUDIT_PASS_SAFE_UNRESOLVED_MODEL_RENDERER_PROMOTION_BLOCKED`.

Decision: `D-0052`.

The independent auditor accepted the T2 recalibration gate only as safe
unresolved. JSON parseability, required fields, declared hashes, visible-file
manifest hashes, full tests, and legacy, active sheetmetal-v1, and
topology-stage scoped freezes all pass. T1A and T1B remain safe unresolved,
T1C rule artifacts remain proposal-only and not promoted, and promotable T2
inputs remain `0`. Coverage remains assignment `0/53`, real-project geometry
`0/53`, sizing with zero source-supported denominator, and placement `0/53`.

Hard gates remain closed: source-root mutation `0`, `.private` mutation `0`,
private external transmissions `0`, completed-reference leakage `0`,
post-design leakage `0`, customer PDF/DXF/DWG generation `0`, and production
approval `false`.

Evidence:
`reports/sheetmetal-v1/t2-recalibration/independent-audit/t2_topology_sizing_placement_independent_audit.json`,
`reports/sheetmetal-v1/t2-recalibration/independent-audit/t2_topology_sizing_placement_independent_audit.md`,
and
`orchestration/master/child-results/SMV1-T2-TOPOLOGY-SIZING-PLACEMENT-INDEPENDENT-AUDIT.json`.


## sheetmetal-v1 T2 safe-unresolved terminal-candidate review

Status: `T2_SAFE_UNRESOLVED_TERMINAL_CANDIDATE_REVIEW_RECORDED`.

Decision: `D-0053`.

The coordinator reviewed the accepted T2 independent audit as a terminal-candidate gate. JSON parseability, required fields, declared non-self hashes, and privacy cleanliness passed. The result is a terminal candidate for `STRUCTURAL_SOURCE_INSUFFICIENCY`, with additional approved evidence required before any model, renderer, private preview, or customer drawing promotion can resume.

Boundaries remain unchanged: T1A and T1B are safe unresolved, T1C rule artifacts are proposal-only, source roots and `.private` were not mutated, customer PDF/DXF/DWG generation remains `0`, and production approval remains `false`.

Evidence:
`orchestration/master/blocked-audits/SMV1-T2-SAFE-UNRESOLVED-TERMINAL-CANDIDATE-REVIEW.json`,
`reports/sheetmetal-v1/t2-recalibration/terminal-candidate-review/t2_safe_unresolved_terminal_candidate_review.json`,
and
`reports/sheetmetal-v1/t2-recalibration/terminal-candidate-review/t2_safe_unresolved_terminal_candidate_review.md`.


## sheetmetal-v1 additional evidence recovery package intake

Status: `ADDITIONAL_EVIDENCE_PACKAGE_INTAKE_IN_PROGRESS`.

Decision: `D-0054`.

Package `SMV1-EVIDENCE-RECOVERY-PACKAGE-V1-2026-06-25` was accepted for local development/evaluation/private-preview calibration intake only. The zip integrity check, package manifest hash checks, JSON parse checks, git-ignore boundary, full tests, and legacy/active/topology scoped freezes passed. The package contents remain outside committed evidence; committed artifacts record only hashes, counts, and gate status.

The source-rich branch preserves `1110101` and opens preferred candidate `1140304` for Phase 1 panel-allocation source qualification. `SHEETMETAL_ALLOWED_EVAL` remains `1`; no source-rich candidate is promoted yet.

Hard gates remain closed: privacy is `NOT_APPROVED`, private external transmissions `0`, completed-reference leakage `0`, post-design leakage `0`, customer PDF/DXF/DWG generation `0`, and production approval `false`.

Evidence:
`reports/sheetmetal-v1/evidence-recovery-v1/package_intake_summary.json`,
`reports/sheetmetal-v1/evidence-recovery-v1/package_intake_summary.md`,
and
`orchestration/master/child-results/SMV1-EVIDENCE-RECOVERY-PACKAGE-INTAKE.json`.


## sheetmetal-v1 Phase 1 1140304 panel-allocation source qualification

Status: `PHASE1_PANEL_ALLOCATION_SOURCE_QUALIFICATION_1140304_FAIL_CLOSED_SOURCE_DOCUMENTS_REQUIRED`.

Decision: `D-0055`.

The coordinator reconciled the accepted package intake summary and child result, verified the proposed panel-allocation evidence hash from ignored local intake storage, and recorded only neutral counts. Candidate `1140304` is not approved for generator use because source-document identity, revision, chronology, leakage, and reconciliation gates cannot be independently verified from a package index alone.

Generation status: no customer drawing, PDF, DXF, or DWG was generated; no production approval was declared; accepted panel-allocation facts remain `0`; `SHEETMETAL_ALLOWED_EVAL` remains `1`.

Evidence: `reports/sheetmetal-v1/evidence-recovery-v1/phase1_panel_allocation_source_qualification_1140304.json`, `reports/sheetmetal-v1/evidence-recovery-v1/phase1_panel_allocation_source_qualification_1140304.md`, and `orchestration/master/child-results/SMV1-PHASE1-PANEL-ALLOCATION-SOURCE-QUALIFICATION-1140304.json`.


## sheetmetal-v1 source fact metadata fail-closed hardening

Status: `SOURCE_FACT_MISSING_METADATA_FAIL_CLOSED`.

Decision: `D-0056`.

The source-fact extractor now rejects generator eligibility before row parsing
when source role classification, chronology classification, or completed-
reference/derivative metadata is missing. Synthetic regression coverage proves
all three missing-metadata cases produce no source facts, while explicit
approved metadata still extracts facts.

Verification: targeted source-fact extraction regression checks passed; full
test runner and scoped freeze results are recorded in the heartbeat report for
this checkpoint.

Hard gates remain closed: private external transmissions `0`, source-root
mutation `0`, `.private` mutation `0`, completed-reference inference `0`,
customer PDF/DXF/DWG generation `0`, and production approval `false`.

## sheetmetal-v1 topology validation evidence-derived hardening

Status: `TOPOLOGY_VALIDATION_EVIDENCE_DERIVED_MUTATION_TESTED`.

Decision: `D-0057`.

Accepted-placement topology validation now recomputes placement geometry,
containment, overlap, and edge-clearance checks from emitted topology artifacts.
Violation counters derive from structured validation findings, and listed hard
constraints without implemented validators are reported as `NOT_EVALUATED`
instead of optimistic `PASS`.

Synthetic mutation coverage proves accepted placements fail validation when
they are intentionally moved outside panel containment, inside edge clearance,
or duplicated into a physical overlap.

Hard gates remain closed: private external transmissions `0`, source-root
mutation `0`, `.private` mutation `0`, completed-reference inference `0`,
customer PDF/DXF/DWG generation `0`, and production approval `false`.

## sheetmetal-v1 topology reference and assignment validation hardening

Status: `TOPOLOGY_REFERENTIAL_ASSIGNMENT_VALIDATION_MUTATION_TESTED`.

Decision: `D-0058`.

Topology validation now checks emitted placement and unplaced artifacts against
topology panel IDs and recovered component assignments. Topology-reference,
component-reference, and assignment-consistency counters derive from structured
validation findings instead of static `PASS` fields.

Synthetic mutation coverage proves validation fails when accepted placements
reference an unknown panel, reference an unknown component instance, or use a
panel that conflicts with the approved assignment.

Hard gates remain closed: private external transmissions `0`, source-root
mutation `0`, `.private` mutation `0`, completed-reference inference `0`,
customer PDF/DXF/DWG generation `0`, and production approval `false`.
