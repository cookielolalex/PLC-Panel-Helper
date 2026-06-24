# SESSION CHECKPOINT

Current phase: cycle-000 autonomous qualification recovery, Phase A local
capability discovery complete.

Accepted release: none.

Active production Knowledge paths: none.

Six-project set: 1110101, 1110104, 1110204, 1110205, 1110405, 1110410.

Evaluator version for future cycle-000 work: `plc_layout_evaluator_v2_sensitivity`.

Baseline-024 seed: `BASELINE024-CYCLE000-20260623`.

Current status: `RECOVERY_PHASE_A_LOCAL_CAPABILITY_DISCOVERY_COMPLETE`.

Latest evidence: `reports/baseline-024/reference-detection-v3/screening_yield.md`,
`reports/baseline-024/reference-detection-v3/independent_audit.json`,
`reports/baseline-024/reference-detection-v3/batch_results/`,
`manifests/reference_detection/v3/`,
`reports/baseline-024/reference-detector-calibration/known_positive_replay_summary.json`,
`manifests/reference_detection/calibration/known_positive_controls.sealed.json`,
`manifests/reference_detection/calibration/v3_known_positive_replay/`,
`reports/baseline-024/reference-detector-calibration/vision_classifier_availability_probe.json`,
`docs/specs/AUTONOMOUS_QUALIFICATION_RECOVERY.md`,
`reports/baseline-024/qualification-recovery/recovery_state.json`,
`reports/baseline-024/qualification-recovery/recovery_state.md`,
`reports/baseline-024/qualification-recovery/checkpoint_verification.json`,
`reports/baseline-024/qualification-recovery/local_capability_probe.json`,
`orchestration/QUALIFICATION_RECOVERY_QUEUE.json`,
`docs/specs/REFERENCE_VAULT_BOUNDARY_SPEC.md`,
`docs/specs/REFERENCE_PRESENCE_DETECTION_V3.md`,
`reports/baseline-024/reference-detection-v3/v2_zero_promotion_diagnosis.json`,
`reports/baseline-024/expanded-screening/inventory_reconciliation_report.md`,
`reports/baseline-024/expanded-screening/target_detection_v2_report.md`,
`evals/baseline-024/expanded_candidate_selection_report.md`,
`manifests/baseline-024/source_approvals/phase_c_status.json`,
`reports/baseline-024/insufficient_eligible_projects_for_24_baseline.json`,
and the prior source-bundle independent audits under `reports/baseline-024/`.

Phase A result: original `42/38` was identified as an evaluator-mechanics
defect in the v1 comparison scorer. The v2 evaluator keeps the twelve-run
calibration scores at `42/38` through explicit scoring records, not constants.

Phase B result: the 24-project protocol is frozen, the six calibration projects
are retained as fresh-run anchors, and generation is not authorized until a
final 24-project `ALLOWED_EVAL` cohort is verified and frozen.

Phase C source-backfill result before expanded discovery: the frozen
metadata-only candidate pool was exhausted. Only seven projects were added to
the six anchors, leaving `13 / 24` verified `ALLOWED_EVAL` projects.

Amendment `D-0017` on 2026-06-23: the user accepted expanding baseline-024
candidate discovery to the full approved development inventory under
`SRC-ALL-PROJECTS`. This supersedes only the twenty-project discovery cap and
does not weaken source immutability, source-root restrictions, positive source
allowlisting, evaluation-only approval quorum, reference isolation, cohort
isolation, held-out protection, parser requirements, sanitized-bundle
verification, independent auditing, frozen workflow requirements, grading
rules, or no-invention requirements.

Expanded screening after `D-0017`: 404 project IDs and 404 physical project
folders were reconciled. Metadata target detection v2 found 0 immediate
`READY_FOR_SOURCE_SCREENING` projects and 269
`REFERENCE_PRESENCE_REVIEW_REQUIRED` projects. Three isolated v2
reference-presence waves reviewed 18 top-ranked partial projects; all remained
partial.

Amendment `D-0018` on 2026-06-23: the user accepted Reference Presence
Detection V3 as content-aware, page-level, reference-vault-only
classification. Completed-reference content may be inspected only inside
isolated reference-vault processes and remains forbidden to source reviewers,
generator agents, production Knowledge, portfolio optimizers, and
drawing-workflow implementation agents.

V2 diagnosis: zero promotions were caused by metadata-only and restricted
document-level review mechanics, lack of page rendering/visual evidence,
one-file-one-type assumptions, incomplete combined/revision handling, and
policy confusion between generator-forbidden location and reviewer-reference
eligibility. The diagnosis did not prove the references were genuinely missing.

V3 result: all 103 reference-review-required families have a v3 page-level
representative, plus 24 additional ranked non-representative projects. The pass
processed 129 projects, 1849 PDFs, and 9031 pages; classified 1644
image-only-or-no-target-text PDFs and 205 embedded-text PDFs; rejected 3252
electrical/false-positive alias pages; identified 0 combined packages, 0
revision supersession packages, 0 newly verified all-three projects, 129
partial projects, and 0 ambiguous projects.

Audit state: all 129 v3 project outputs validate against schemas and
minimization checks; all 22 batch summaries report
`REFERENCE_PRESENCE_BATCH_AUDIT_PASS`. Temporary render directories were
removed. No page renders, title-block crops, raw extracted text, private source
paths, or completed drawing content are committed in v3 outputs.

Amendment `D-0019` on 2026-06-23: the user accepted that reference detector
recall must be calibrated against known positives before reference-universe
exhaustion may be declared.

Known-positive calibration result: the 13 accepted `ALLOWED_EVAL` projects were
sealed as controls and detector v3 was replayed with blinded candidate
manifests that omitted expected labels, inventory roles, filenames, and
relative paths. V3 detected all three target outputs in `0 / 13` projects.
Per-type recall was `PRODUCTION_DRAWING 0/13`, `SHEETMETAL_DRAWING 8/13`, and
`PUNCH_DRAWING 0/13`; false-negative output-type count was `31`;
project-identity mismatch count was `0`. The stop status is
`DETECTOR_V3_RECALL_FAIL`.

Calibration verification: accepted bundle hash verification `PASS`; frozen
workflow hash verification `PASS`; source-root immutability verification
`PASS`; baseline generation attempts observed `0`. The classifier requested
model was `local`; actual model was
`local_poppler_pypdf_deterministic_reference_detector_v3`.

Vision availability result: a fresh child was launched on a non-private
synthetic red/blue image and correctly inspected the pixels, reporting actual
model `GPT-5`. `docs/PRIVACY_APPROVAL.md` remains `NOT_APPROVED`, so no private
completed reference page, title-block crop, source file, generated output,
trajectory, or reviewer finding was sent to that vision path. Actual private
reference pages inspected by vision agents remain `0`. Detector v4 was not
created. Stop status: `VISION_CLASSIFIER_UNAVAILABLE`.

Amendment `D-0021` on 2026-06-24: the user accepted constraint-preserving
autonomous qualification recovery. Method-specific failures such as
`VISION_CLASSIFIER_UNAVAILABLE`, OCR absence, parser limits, and avoidable
quarantines are branch blockers rather than terminal workflow stops, but the
substantive `ALLOWED_EVAL` gates and privacy boundary remain unchanged.

Recovery controller result: `scripts/run_qualification_recovery.py` produced a
schema-valid recovery state and minimized queue. It reverified accepted bundle
hashes `PASS`, frozen workflow hashes `PASS`, privacy `NOT_APPROVED`, and
baseline generation attempts `0`. It records current verified `ALLOWED_EVAL`
projects as `13 / 24`, deficit `11`, reserve target `3`, prior v3 partial
projects `129`, projects not individually screened by v3 `262`, known-positive
detector retry cases `13`, previous bundle rejections `7`, and previous
quarantined/no-bundle projects `6`.

Local capability discovery result: bundled Poppler `pdfinfo 26.05.0` and
`pdftoppm 26.05.0` are available; Python `pypdf 6.10.0`, Pillow `12.2.0`,
NumPy `2.3.5`, and Windows.Media.Ocr are available locally. `pdfimages`,
Tesseract, OCRmyPDF, PaddleOCR, EasyOCR, ONNX Runtime, OpenCV, PyMuPDF, and
ImageMagick were not available in the local probe. No private project data was
opened and no network endpoint probe was performed.

Regression coverage result: `scripts/run_tests.py` now includes
`test_reference_detector_v3_known_positive_recall_gate`, covering all 13 missed
known-positive projects from the v3 replay, and
`test_qualification_recovery_controller_state`, covering the recovery state
schema and privacy/count invariants. Full repository test runner status: `PASS`.

No drawing workflow optimization occurred. No expanded-candidate source
screening, sanitized bundle construction, final cohort freeze, baseline
generation, review, or production approval occurred. Baseline generation
attempts remain `0`.

Exact next action: do not start source-review quorum, sanitized-bundle
construction, cohort freeze, baseline generation, review, optimization, or
expanded screening from the v3 exhaustion result. Build
`target_output_detection_v4_local_multisignal_recovery` as a local-only
prototype using the capability report, add regression coverage for the current
known-positive false negatives and real negative controls, then rerun positive
and negative calibration before any corpus-wide screening.
