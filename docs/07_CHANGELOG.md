# Changelog

## 2026-06-22

- Initialized repository from the master bootstrap specification.
- Added Phase 0 scaffold, source-root records, agent definitions, schemas,
  scripts, fixtures, and orchestration task briefs.
- Ran synthetic Phase 0 harness tests and validated required child result
  schemas. Phase 0 remains blocked by missing exact declared source roots.
- Accepted the user-provided consolidated project source root and generated
  read-only file, worksheet, and project manifests without creating a generator
  bundle or starting a baseline.
- Added project-local CAD/catalog candidate indexes while keeping canonical
  reusable library roots unapproved.
- Passed `PH0-SOURCE-UPDATE-AUDIT` and `PH1-INVENTORY-AUDIT`; no generator
  bundle or real-project baseline was started.
- Added PH1.5 fail-closed source-guard schemas, policy, review-batch builder,
  approval validator, sanitized bundle builder, bundle verifier, and synthetic
  regression tests.
- Generated `reports/source_review_batches/batch-001/` for 12 historical
  reference-complete calibration projects because active year 115 has no
  all-three-completed-target projects. The packet has 56 candidate files, 69
  candidate worksheets, and 0 allowed items.
- Validated all four PH1.5 child results and reran the synthetic harness. Blank
  human decisions fail closed with `approved_count=0`.
- Ran the independent PH1.5 source-guard audit. The audit is schema-valid
  `NOT_VERIFIED` with domain status `PH1_5_SOURCE_GUARD_AUDIT_INCONCLUSIVE`:
  substantive source-guard checks passed, but the auditor could not verify the
  Git commit with its available tools. Added a coordinator Git verification
  addendum without changing the independent audit result.
- Added autonomous evaluation-only source approval policy, states, custom
  agents, Skills, and schemas while preserving the production human-approval
  requirement.
- Processed the five current-parser candidates from `batch-001`; 15 items
  reached `AGENT_QUORUM_APPROVED_EVAL`, five projects reached `ALLOWED_EVAL`,
  and the independent source-bundle audit passed.
- Activated and independently audited the codex_proxy synthetic gate with 12
  passing fixtures.
- Selected project `1110104`, ran exactly one accepted blind historical mock
  calibration after preserving one failed attempt, produced reviewer-only
  comparison evidence, and recorded a project reviewer result.
- Ran the final one-project independent audit. Result:
  `STEP_7C_AUDIT_PASS - READY_FOR_SIX_PROJECT_BASELINE`. No six-project trial
  was started.

## 2026-06-23

- Ran autonomous six-project reviewer and stability calibration as `calibration-006`.
- Backfilled project `1110101` using a local deterministic legacy `.xls` parser and evaluation-only source quorum.
- Completed 12 fresh generation runs, 12 primary reviews, 6 secondary reviews, portfolio analysis, and independent audit.
- Stopped before drawing-workflow optimization and before any 24-project baseline.
- Began cycle-000 Phase A evaluator-sensitivity qualification.
- Identified the original calibration scorer as writing `quality_score=42` and `scorable_coverage=38` directly.
- Added the failing evaluator-sensitivity regression before implementing `plc_layout_evaluator_v2_sensitivity`.
- Added `scripts/evaluator_scoring.py`, `evals/grading_profiles/plc_layout_v2.json`, counterfactual fixtures, and Phase A reports under `reports/evaluator-sensitivity/`.
- Rescored the 12 frozen calibration outputs with v2; scores remain `42/38`, now from explicit scoring records and coverage arithmetic.
- Completed fresh independent evaluator-sensitivity audit with result `EVALUATOR_SENSITIVITY_PASS`.
- Froze the cycle-000 24-project baseline protocol as `FROZEN_PROTOCOL_V1` with seed `BASELINE024-CYCLE000-20260623`.
- Added `evals/baseline-024/` protocol manifests for cohort placeholders, workflow hashes, source readiness, and the four-wave run plan.
- Stopped before Phase C source backfill and before any 24-project generation; 18 additional verified `ALLOWED_EVAL` projects are still required.
- Began Phase C source backfill with `baseline-024` batch-001.
- Ran deterministic prefiltering, four independent specialist reviews, quorum adjudication, sanitized bundle verification, and independent source-bundle audit for six candidate projects.
- Accepted `1110801` and `1120207` as evaluation-only additions; preserved verifier rejections for `1120101`, `1120204`, and `1120301`; left `1120201` quarantined/no-bundle.
- Current baseline-024 `ALLOWED_EVAL` count is `8`; generation remains blocked.
- Continued Phase C source backfill with `baseline-024` batch-002.
- Ran deterministic prefiltering, four independent specialist reviews, quorum adjudication, sanitized bundle verification, and independent source-bundle audit for six more candidate projects.
- Accepted `1110103`, `1110203`, and `1120308` as evaluation-only additions; preserved verifier rejections for `1110404` and `1120202`; left `1120309` quarantined/no-bundle.
- Current baseline-024 `ALLOWED_EVAL` count is `11`; generation remains blocked.
- Continued Phase C source backfill with `baseline-024` batch-003.
- Ran deterministic prefiltering, four independent specialist reviews, quorum adjudication, sanitized bundle verification, and independent source-bundle audit for six more candidate projects.
- Accepted `1110704` and `1120305` as evaluation-only additions; preserved verifier rejection for `1110701`; left `1110402`, `1110706`, and `1120102` no-bundle/quarantined.
- Current baseline-024 `ALLOWED_EVAL` count is `13`; generation remains blocked.
- Completed Phase C source backfill with `baseline-024` batch-004, covering the final two frozen metadata-only candidates.
- Batch-004 accepted no new evaluation-only projects; preserved verifier rejection for `1110501` and left `1110504` quarantined/no-bundle.
- Stopped baseline-024 with `INSUFFICIENT_ELIGIBLE_PROJECTS_FOR_24_BASELINE`: all 20 frozen candidates were processed, only 7 produced accepted bundles, the current verified count is `13`, and 11 additional projects are still required.
- No 24-project baseline generation, reviews, final audit, drawing-workflow optimization, or production approval occurred.
- Accepted amendment `D-0017`, expanding baseline-024 candidate discovery beyond
  the prior twenty-project metadata-only pool to the full approved development
  inventory under `SRC-ALL-PROJECTS` while preserving all source, reference,
  cohort, parser, bundle, audit, frozen workflow, grading, and no-invention
  gates.
- Reconciled the expanded project universe: 404 project IDs, 404 physical
  project folders, 13 already accepted `ALLOWED_EVAL` projects, 7 preserved
  bundle rejections, 6 preserved quarantined/no-bundle projects, and 1
  protocol-excluded project.
- Added metadata target detection v2 and expanded candidate registry v2. The
  registry found 0 immediate `READY_FOR_SOURCE_SCREENING` projects and 269
  `REFERENCE_PRESENCE_REVIEW_REQUIRED` projects.
- Ran three isolated reference-presence waves across 18 top-ranked partial
  projects. All remained sheet-metal-only `PARTIAL_REFERENCE_SET`; no project
  was promoted to all-three reference availability, and no source screening or
  generation was started.
- Accepted amendment `D-0018`, allowing completed-reference page content to be
  inspected only inside isolated reference-vault processes for v3 page-level
  presence classification, identity confirmation, revision resolution, and
  effective reference-set construction.
- Diagnosed the v2 zero-promotion result as a detector/review-contract
  limitation rather than proof that all references were genuinely missing.
- Added the reference-vault boundary spec, reference presence detector v3 spec,
  v3 schemas, renderer/evidence helper, detector, effective-set builder,
  verifier, fixtures, and regression coverage for generator isolation,
  target-under-forbidden-folder evidence, electrical false positives,
  combined packages, duplicates, near duplicates, mismatched project identity,
  missing third target type, title-block crops, and temporary render deletion.
- Tightened generator bundle exclusion redaction so completed-reference-like
  excluded IDs are not exposed to generator-facing manifests.
- Processed all 103 reference-review-required families under v3, plus 24
  additional ranked non-representative projects: 129 projects, 1849 PDFs, and
  9031 pages. No all-three reference-complete project was found.
- Refreshed v3 screening yield, alias, combined-package, revision, unresolved,
  task-registry, trajectory, and minimization-audit evidence under
  `reports/baseline-024/reference-detection-v3/`,
  `manifests/reference_detection/v3/`, and `orchestration/`.
- Stopped with `REFERENCE_REVIEW_UNIVERSE_EXHAUSTED -
  INSUFFICIENT_REFERENCE_COMPLETE_PROJECTS`; source screening and baseline
  generation remain blocked at `13 / 24` verified `ALLOWED_EVAL` projects.
- Accepted amendment `D-0019`, requiring detector recall calibration against
  known-positive controls before reference-universe exhaustion may be declared.
- Added sealed known-positive controls and blinded v3 replay evidence for the
  13 accepted `ALLOWED_EVAL` projects. V3 detected all three target outputs in
  `0 / 13` controls; per-type recall was `PRODUCTION_DRAWING 0/13`,
  `SHEETMETAL_DRAWING 8/13`, and `PUNCH_DRAWING 0/13`.
- Stopped with `DETECTOR_V3_RECALL_FAIL`. The previous v3 exhaustion result is
  preserved but provisional; no negative controls, detector v4, source
  screening, cohort freeze, or baseline generation was started.
- Added regression coverage for the v3 known-positive miss set:
  `test_reference_detector_v3_known_positive_recall_gate` covers all 13 missed
  controls and prevents local deterministic v3 output from being treated as
  actual vision classification.
- Probed fresh child-agent vision on a non-private synthetic image; the child
  reported actual model `GPT-5` and passed the red/blue image check.
- Stopped with `VISION_CLASSIFIER_UNAVAILABLE` because
  `docs/PRIVACY_APPROVAL.md` remains `NOT_APPROVED`; no private completed
  reference page, title-block crop, source file, generated output, trajectory,
  or reviewer finding was sent to the GPT-5 vision path. Detector v4, negative
  controls, expanded screening, cohort freeze, and baseline generation remain
  blocked.

## 2026-06-24

- Accepted decision `D-0021`, constraint-preserving autonomous qualification
  recovery, superseding `VISION_CLASSIFIER_UNAVAILABLE` as a workflow stop while
  preserving privacy `NOT_APPROVED`, reference isolation, source quorum,
  sanitized-bundle verification, grading, and no-generation gates.
- Added `docs/specs/AUTONOMOUS_QUALIFICATION_RECOVERY.md`.
- Added `schemas/qualification_recovery_state.schema.json` and
  `scripts/run_qualification_recovery.py`.
- Added `test_qualification_recovery_controller_state` to validate recovery
  state schema, privacy invariants, `13 / 24` count, `11` project deficit, and
  separation between detector gate behavior and detector performance.
- Ran the recovery controller. Checkpoint verification passed: accepted bundle
  hashes `PASS`, frozen workflow hashes `PASS`, privacy `NOT_APPROVED`, and
  baseline generation attempts `0`.
- Completed local capability discovery without opening private project data or
  probing network endpoints. Available local capabilities: Poppler `pdfinfo
  26.05.0`, Poppler `pdftoppm 26.05.0`, `pypdf 6.10.0`, Pillow `12.2.0`, NumPy
  `2.3.5`, and Windows.Media.Ocr. Tesseract, OCRmyPDF, PaddleOCR, EasyOCR,
  ONNX Runtime, OpenCV, PyMuPDF, ImageMagick, and `pdfimages` were unavailable
  in the local probe.
- Wrote minimized recovery state and queue under
  `reports/baseline-024/qualification-recovery/` and
  `orchestration/QUALIFICATION_RECOVERY_QUEUE.json`. The next selected action is
  `CREATE_DETECTOR_V4_LOCAL_MULTISIGNAL_RECOVERY_PROTOTYPE`.
- Froze `docs/specs/REFERENCE_DETECTION_V4_CALIBRATION_PROTOCOL.md` with an
  8-project calibration partition, a 5-project sealed holdout partition, and 24
  minimized real negative controls.
- Added a local Windows.Media.Ocr signal bridge and synthetic OCR proof. The
  probe found `en-US` and `zh-Hant-TW`; Simplified Chinese was unavailable.
  OCR text was not persisted or printed, and the private-page probe was skipped
  because an enforceable per-process network-disable boundary was unavailable.
- Added `target_output_detection_v4_local_multisignal_recovery` with minimized
  v4 schemas, Poppler rendering, pypdf text extraction, Pillow/NumPy layout
  buckets, optional Windows OCR role signals, weak-prior handling, duplicate
  grouping, combined-package segmentation, and fail-closed ambiguity.
- Added v4 regression coverage for combined target packages, image-only OCR
  pages, misleading target hints, electrical and source-document negatives,
  missing OCR language support, OCR failure, temporary cleanup, raw OCR
  non-persistence, generator isolation, and source-review blindness.
- Updated the recovery controller. Current status is
  `DETECTOR_V4_LOCAL_CALIBRATION_IN_PROGRESS`; the next selected action is
  `RUN_DETECTOR_V4_CALIBRATION_PARTITION`.
