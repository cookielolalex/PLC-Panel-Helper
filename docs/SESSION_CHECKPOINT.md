# SESSION CHECKPOINT

Current phase: cycle-000 reference detector v3 known-positive calibration failed before source screening.

Accepted release: none.

Active production Knowledge paths: none.

Six-project set: 1110101, 1110104, 1110204, 1110205, 1110405, 1110410.

Evaluator version for future cycle-000 work: `plc_layout_evaluator_v2_sensitivity`.

Baseline-024 seed: `BASELINE024-CYCLE000-20260623`.

Current status: `DETECTOR_V3_RECALL_FAIL`.

Latest evidence: `reports/baseline-024/reference-detection-v3/screening_yield.md`,
`reports/baseline-024/reference-detection-v3/independent_audit.json`,
`reports/baseline-024/reference-detection-v3/batch_results/`,
`manifests/reference_detection/v3/`,
`reports/baseline-024/reference-detector-calibration/known_positive_replay_summary.json`,
`manifests/reference_detection/calibration/known_positive_controls.sealed.json`,
`manifests/reference_detection/calibration/v3_known_positive_replay/`,
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

No drawing workflow optimization occurred. No expanded-candidate source
screening, sanitized bundle construction, final cohort freeze, baseline
generation, review, or production approval occurred. Baseline generation
attempts remain `0`.

Exact next action: do not start source-review quorum, sanitized-bundle
construction, cohort freeze, baseline generation, review, or optimization from
the v3 exhaustion result. Treat v3 exhaustion as provisional after the failed
known-positive recall gate. If work resumes, add regression coverage from the
missed known-positive controls and determine whether actual vision-capable
classification is available before creating detector v4. Preserve v3 and
calibration evidence separately.
