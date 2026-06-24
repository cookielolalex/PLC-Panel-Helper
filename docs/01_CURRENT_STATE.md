# Current State

Current phase: one-project topology, sizing, and placement calibration in progress.

Accepted release: none.

Current candidate: `1110101`.

Current status: `ONE_PROJECT_TOPOLOGY_SIZING_PLACEMENT_CALIBRATION_IN_PROGRESS`.

Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

Legacy workflow status: the old detector-v4.1 three-output qualification track
is preserved as historical evidence. Its last status remains
`DETECTOR_V4_1_INDEPENDENT_GATE_PASSED_SCREENING_PENDING`, but it is no longer
the active V1 objective.

Accepted amendments: `D-0017` expands baseline-024 candidate discovery beyond
the prior twenty-project metadata-only pool to the full approved development
inventory under `SRC-ALL-PROJECTS`; `D-0018` accepts
`target_output_detection_v3_page_content_isolated` as content-aware,
page-level, reference-vault-only classification; `D-0019` requires known-positive
recall calibration before reference-universe exhaustion may be declared; `D-0020`
records that GPT-5 vision children are not available for private reference-page
classification while privacy approval remains `NOT_APPROVED`; `D-0021`
authorizes constraint-preserving autonomous qualification recovery from
method-specific blockers without relaxing the `ALLOWED_EVAL` standard; `D-0024`
accepts the detector v4.1 sealed gate and authorizes minimized corpus-wide
individual screening; `D-0025` accepts
`SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1` as the active V1 goal and creates
new `sheetmetal-v1` namespaces; `D-0026` accepts frozen workflow manifests as
scope-bound and commit-anchored, separating legacy baseline-024 verification
from active sheetmetal-v1 verification; `D-0027` accepts deterministic
metadata-only selection of `1110101`, freezes its evaluator-only reference
package, source-role/chronology classification, clean sanitized input bundle,
and independent audit for one-project sheetmetal calibration; `D-0028` freezes
the one-project component graph calibration protocol; `D-0029` accepts the
ignored private workspace boundary; and `D-0030` accepts deterministic
source-fact extraction into the private workspace with neutral committed
summary evidence; `D-0031` accepts deterministic private component-register
construction from that source-fact model; `D-0032` accepts deterministic
private panel-assignment and typed graph construction; `D-0033` accepts
deterministic private accessory and cutout reconciliation; `D-0034` accepts
deterministic generator freeze evidence; `D-0035` accepts evaluator-only
component graph metrics. These amendments do not weaken
source immutability, source-root restrictions, positive source allowlisting,
evaluation-only quorum, reference isolation, cohort isolation, held-out
protection, parser requirements, sanitized-bundle verification, independent
auditing, frozen workflow requirements, grading rules, or no-invention
requirements.

Evaluator version for future cycle-000 work: `plc_layout_evaluator_v2_sensitivity` using `evals/grading_profiles/plc_layout_v2.json`.

Six-project set: 1110101, 1110104, 1110204, 1110205, 1110405, 1110410.

Baseline-024 status: six calibration anchors are retained as fresh-run anchors.
Batch-001 added `1110801` and `1120207`; batch-002 added `1110103`,
`1110203`, and `1120308`; batch-003 added `1110704` and `1120305`;
batch-004 added no projects. Current verified `ALLOWED_EVAL` count remains
`13 / 24`. No 24-project generation is authorized.

Reference detection v3 result: all 103 reference-review-required families have
at least one v3 page-level representative, plus 24 additional ranked
non-representative projects. The v3 pass processed 129 projects, 1849 PDFs, and
9031 pages. It found 0 newly verified all-three projects, 129 partial projects,
0 ambiguous projects, 0 combined packages, 0 revision supersession packages,
1644 image-only-or-no-target-text PDFs, and 205 embedded-text PDFs. All batches
returned `REFERENCE_PRESENCE_BATCH_AUDIT_PASS`.

Generator and source status: no expanded-candidate source-review quorum,
sanitized-bundle construction, final cohort freeze, baseline generation, review,
drawing-workflow optimization, or production approval occurred. Baseline
generation attempts remain `0`.

Reference detector calibration result after `D-0019`: a sealed known-positive
control manifest was created for the 13 verified `ALLOWED_EVAL` projects, then
detector v3 was replayed with blinded candidate manifests that omitted expected
labels, inventory roles, filenames, and relative paths. V3 detected all three
target outputs in `0 / 13` known-positive projects. Per-type recall was
`PRODUCTION_DRAWING 0/13`, `SHEETMETAL_DRAWING 8/13`, and `PUNCH_DRAWING 0/13`;
false-negative output-type count was `31`; project-identity mismatch count was
`0`. The failed gate status is `DETECTOR_V3_RECALL_FAIL`. Negative controls,
detector v4, expanded screening, and final audit were not run after the positive
recall gate failed.

Vision classifier availability result after `D-0019`: a fresh synthetic
local-image probe child correctly classified a non-private red/blue test image
and reported actual model `GPT-5`. `docs/PRIVACY_APPROVAL.md` remains
`NOT_APPROVED`, so no completed reference page, source file, generated output,
title-block crop, trajectory, or reviewer finding was sent to that vision path.
Actual private reference pages inspected by vision agents remain `0`. Detector
v4 was not created, negative controls were not run, and expanded screening did
not resume. Stop status: `VISION_CLASSIFIER_UNAVAILABLE`.

Autonomous qualification recovery result after `D-0021`: the prior
`VISION_CLASSIFIER_UNAVAILABLE` workflow stop is superseded as a terminal
condition, but the privacy restriction remains unchanged. The deterministic
controller reverified HEAD/worktree, accepted bundle hashes, frozen workflow
hashes, privacy status, and absence of baseline generation; all passed. The
controller records `13 / 24` verified `ALLOWED_EVAL` projects, a deficit of
`11`, `129` prior v3 partial projects, `262` projects not individually screened
by v3, `13` known-positive retry cases, and no accepted reserves. Phase A local
capability discovery found bundled Poppler `pdfinfo 26.05.0` and `pdftoppm
26.05.0`, Python `pypdf`, Pillow, NumPy, and Windows.Media.Ocr available
locally; no local Tesseract, OCRmyPDF, PaddleOCR, EasyOCR, ONNX Runtime,
OpenCV, PyMuPDF, ImageMagick, or `pdfimages` was available. No private project
data was opened by the probe and no network endpoint probe was performed.

Detector v4 local recovery result after `D-0021`: the v4 calibration protocol
was frozen before implementation. The split uses 8 implementation-facing
calibration IDs and 5 sealed holdout IDs, with 24 minimized real negative
controls from prior reference-vault page classifications. Windows.Media.Ocr was
bound through local `Windows.Media.Ocr.OcrEngine.RecognizeAsync` in
`powershell.exe`; installed OCR languages are `en-US` and `zh-Hant-TW`, while
Simplified Chinese was unavailable in this local probe. Synthetic OCR returned
a minimized `PUNCH_DRAWING` role signal and did not print or persist OCR text.
The private-page OCR probe was skipped because this environment did not provide
an independently enforceable per-process network-disable boundary. No private
content was transmitted outside the machine.

Detector v4 implementation status: `target_output_detection_v4_local_multisignal_recovery`
now exists with v4-specific minimized schemas and verifier. It uses pypdf
embedded text, local Poppler rendering, Pillow/NumPy layout buckets, optional
Windows.Media.Ocr role signals, Unicode normalization, weak metadata priors
that cannot independently promote target status, exact duplicate grouping,
page-level effective-set construction, and fail-closed `AMBIGUOUS` or
`UNCLASSIFIED` outcomes. Corpus-wide screening is now authorized only through
the minimized v4.1 detector-screening workflow after calibration partition,
sealed holdout, all-13 recall, negative controls, and independent audit passed.

Regression coverage after `D-0021`: `scripts/run_tests.py` includes
`test_reference_detector_v3_known_positive_recall_gate`, covering all 13 missed
known-positive projects and preventing the local deterministic v3 replay from
being treated as actual vision classification. It also includes
`test_qualification_recovery_controller_state`, which validates the recovery
state schema, privacy invariants, the `13 / 24` count, the `11` project deficit,
and separation between gate behavior and detector performance. V4 regression
coverage now includes the Windows.Media.Ocr minimized proof, combined
three-target packages, image-only OCR target pages, misleading filename/folder
hints overridden by page content, source-document target-word confusers,
missing OCR language support, OCR engine failure, fail-closed output, temporary
render deletion, raw OCR non-persistence, generator isolation, and
source-review blindness. Full test runner status: `PASS`.

Portfolio result: mean score `42`, median `42`, minimum `42`, mean scorable
coverage `38`; validity rate `100%`; critical findings `0`; high findings `36`
across primary reviews.

Evaluator-sensitivity result: original calibration evaluator mechanics wrote
`42/38` as constants in `scripts/compare_one_project.py`; this was fixed by
`scripts/evaluator_scoring.py`. The twelve frozen calibration outputs were
rescored into `reports/evaluator-sensitivity/rescored_runs/`; v2 recomputation
preserves score `42` and coverage `38` from explicit scoring records, dimension
arithmetic, and coverage denominators.

Independent sensitivity audit: `reports/evaluator-sensitivity/subagent_independent_audit.json` reports `EVALUATOR_SENSITIVITY_PASS`.

Frozen Phase B evidence: `docs/specs/24_PROJECT_BASELINE_PROTOCOL.md`,
`evals/baseline-024/cohort_manifest.json`,
`evals/baseline-024/cohort_selection_report.md`,
`evals/baseline-024/frozen_workflow_manifest.json`,
`evals/baseline-024/source_readiness.json`, and
`evals/baseline-024/run_plan.json`.

Phase C source-backfill evidence: `manifests/baseline-024/source_approvals/phase_c_status.json`,
`reports/baseline-024/source_backfill_summary.md`,
`reports/baseline-024/source_bundle_audit.json`,
`reports/baseline-024/insufficient_eligible_projects_for_24_baseline.json`,
and the four batch independent audits under `reports/baseline-024/`.

Reference detection v3 evidence: `docs/specs/REFERENCE_VAULT_BOUNDARY_SPEC.md`,
`docs/specs/REFERENCE_PRESENCE_DETECTION_V3.md`,
`reports/baseline-024/reference-detection-v3/v2_zero_promotion_diagnosis.json`,
`reports/baseline-024/reference-detection-v3/screening_yield.md`,
`reports/baseline-024/reference-detection-v3/batch_results/`,
`manifests/reference_detection/v3/`, and
`reports/baseline-024/reference-detection-v3/independent_audit.json`.

Recommendations remain PROPOSED. No drawing-generation behavior, accepted
Instructions, production Knowledge, extraction logic, renderer behavior,
validation behavior, grading weights, or tolerance profiles were optimized.

Detector v4/v4.1 calibration update: frozen v4 was run on the 8-project
calibration partition with private OCR disabled and failed detector performance
with all-three recall `0 / 8`; private OCR page count remained `0`, cleanup and
minimization passed, and the failed evidence is preserved. Version v4.1
(`target_output_detection_v4_1_local_layout_prior_recovery`) added a
layout-confirmed weak-role-prior fallback that still lets explicit page content
override hints and keeps weak priors without layout unclassified. Full tests
passed. V4.1 calibration-positive recall is `8 / 8`; per-type recall is
`PRODUCTION_DRAWING 8 / 8`, `SHEETMETAL_DRAWING 8 / 8`, and
`PUNCH_DRAWING 8 / 8`. The 24 minimized real negative controls passed with
zero false target pages, zero false all-three promotions, zero electrical or
source-document target acceptances, private OCR page count `0`, external
transmission count `0`, cleanup `PASS`, raw-content persistence `PASS`,
generator isolation `PASS`, and source-review blindness `PASS`. Independent
implementation audit passed.

Detector v4.1 sealed-gate update: sealed holdout passed with all-three recall
`5 / 5`, per-type recall `5 / 5`, private OCR page count `0`, external
transmission count `0`, no persisted holdout identities, and no detailed
detector outputs. The final all-13 known-positive recall passed `13 / 13` with
private OCR page count `0`. Refreshed real negative controls remained `PASS`.
Independent sealed-gate audit passed scoped persistence, cleanup, aggregate
evidence, and temp-root absence checks.

Sheetmetal-first migration result after `D-0025`: the root coordinator accepted
`SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1` as the active V1 goal. The migration
creates new `sheetmetal-v1` namespaces without overwriting `baseline-024`,
classifies the prior 13 accepted projects as
`LEGACY_THREE_OUTPUT_ALLOWED_EVAL`, creates a new empty
`SHEETMETAL_ALLOWED_EVAL` queue with 13 pending requalification candidates,
adds source-role, chronology, authority, architecture, and qualification specs,
adds schemas for source evidence, facts, components, panel assignment, graph,
accessory rules, constraints, the sheet-metal drawing model, and provenance,
and implements the deterministic synthetic modular framework in
`scripts/sheetmetal_v1.py`.

Sheetmetal-v1 synthetic coverage: `test_sheetmetal_v1_modular_foundation`
proves procurement quantity does not overwrite required quantity, explicit
accessories prevent duplicate inferred accessories, conflicting models remain
`CONFLICT`, post-design allocation labels are rejected, inventory-only mode does
not invent supported functional edges, missing electrical relationships remain
`UNVERIFIED`, one component may hold several graph relationships, panel
assignment remains separate from placement, width/height/depth are individually
named, hard placement constraints reject soft-objective overrides, critical
drawing-model facts have provenance or safe unresolved status, and completed
reference IDs/content do not enter generator artifacts.

New qualification status: `SHEETMETAL_ALLOWED_EVAL` approved count is `1`; `1110101` is the first accepted sheetmetal-v1 calibration project for the component-register and graph stage.
Project `1110101` is selected for one-project calibration; the other 12 legacy
projects remain pending future sheetmetal requalification.

Audit result: independent audit reports `PASS_WITH_RESIDUAL_RISKS`; coordinator
addendum resolves the auditor-local Git/Python tool limitations and the
migration-report status wording drift. No private source root or completed
drawing was inspected by the audit.

Scoped freeze result after `D-0026`: legacy baseline-024 verification passes
against historical anchor commit `fac44321491633181f1fa53a062084d072b0b582`
through `evals/baseline-024/frozen_workflow_attestation.json`; the active
sheetmetal-v1 workflow freeze passes through
`evals/sheetmetal-v1/frozen_workflow_manifest.json`; and
`reports/sheetmetal-v1/revised_phase0_verification.json` records
`ONE_PROJECT_SHEETMETAL_REQUALIFICATION_PHASE_0_PASS`. Current `AGENTS.md` is
not compared to the legacy baseline-024 expected hash.

One-project selection result after `D-0027`: project `1110101` is selected by
metadata-only source-bundle readiness ranking and frozen in
`manifests/sheetmetal-v1/one_project_candidate_selection.json` before any
completed-reference metadata is opened. The evaluator-only effective
sheetmetal reference package is qualified, source-role/chronology
classification approves six source-only items and excludes twelve quarantined
items, and the clean sheetmetal-v1 generator bundle verifies `PASS` under
`manifests/sheetmetal-v1/selected_candidate/1110101/generator_bundle/`.
Independent audit passes in
`reports/sheetmetal-v1/selected_candidate_1110101_independent_audit.md`.
`SHEETMETAL_ALLOWED_EVAL` approved count remains `0`; no customer drawing was
generated.

One-project component graph calibration after `D-0028`: the protocol for
`ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION` is frozen for candidate
`1110101`. It fixes `SOURCE_MODE_A_INVENTORY_ONLY`, isolates generator and
evaluator lanes, binds the starting checkpoint hashes, requires an ignored
private workspace before project fact extraction, and keeps committed outputs
limited to neutral counts, hashes, status codes, coverage metrics, and audit
summaries. The full test suite, legacy scoped freeze, active sheetmetal-v1
scoped freeze, selected bundle verifier, bundle hash cross-check, worksheet
fingerprint presence check, privacy status, no drawing-output scan, and no
baseline-generation scan passed before protocol freeze.

Private workspace boundary after `D-0029`: `.private/` is ignored before any
project-specific facts are written. The private workspace
`.private/sheetmetal-v1/1110101/` exists locally, `git check-ignore` passes for
the project-private probe path, no `.private` path is tracked, and
`test_sheetmetal_v1_private_workspace_boundary` covers this boundary.

Source-fact extraction after `D-0030`: `scripts/sheetmetal_v1.py` now supports
source-only sanitized bundle extraction into an ignored output directory and
writes `source_fact_model.json` plus `source_fact_validation.json`. The
extractor normalizes the approved generic current-project role and chronology
tokens, treats `NO_SIGNAL_IN_APPROVED_METADATA` as non-reference content, and
keeps completed-reference-marked evidence out of source facts. Synthetic
coverage is in `test_sheetmetal_v1_source_fact_extractor`; the active
sheetmetal-v1 scoped manifest includes `schemas/source_fact_model.schema.json`.
The private `1110101` run produced 6 evidence records, 125 represented source
lines, 87 source facts, 0 silently discarded authorized source lines, 0
completed-reference facts, 0 quantity-stage overwrite violations, and 0
private content transmissions. Private model files remain ignored and are
recorded only by neutral hashes in
`reports/sheetmetal-v1/one-project-model-calibration/1110101/source_fact_extraction_summary.json`.

Component-register construction after `D-0031`: `scripts/sheetmetal_v1.py` now
supports `--source-fact-model` register-only mode and writes
`component_register.json` plus `component_register_validation.json` to an
ignored output directory. The private `1110101` run consumed the private
source-fact model and produced 53 component types, 53 component instances, 0
conflicts, 0 unregistered allowed component keys, 0 completed-reference
components, and 0 private content transmissions. Private register files remain
ignored and are recorded only by neutral hashes in
`reports/sheetmetal-v1/one-project-model-calibration/1110101/component_register_summary.json`.

Panel-assignment and graph construction after `D-0032`: `scripts/sheetmetal_v1.py`
now supports private panel-assignment and inventory-only typed graph output
from a private source-fact model plus private component register. The private
`1110101` run produced 0 explicit panel assignments, 53 unresolved components,
0 rejected assignments, 56 graph nodes, 107 graph edges, 0 dangling edges, 1
inventory-only unverified function edge, and 0 private content transmissions.
No panel assignment was inferred from unavailable facts. Private panel graph
files remain ignored and are recorded only by neutral hashes in
`reports/sheetmetal-v1/one-project-model-calibration/1110101/panel_graph_summary.json`.

Accessory and cutout reconciliation after `D-0033`: `scripts/sheetmetal_v1.py`
now supports private accessory/cutout reconciliation from a private source-fact
model, private component register, and private typed graph. The private
`1110101` run produced 0 accessory requirements, 0 generated accessory
component instances, 0 cutouts, 0 duplicate accessories, 0 missing requirement
sources, 0 missing cutout sources, and 0 private content transmissions. No
accessory or cutout was inferred from unavailable facts. Private
accessory/cutout files remain ignored and are recorded only by neutral hashes
in
`reports/sheetmetal-v1/one-project-model-calibration/1110101/accessory_cutout_summary.json`.

Generator freeze after `D-0034`: the private source-fact extraction,
component-register, panel-graph, and accessory/cutout stages were rerun from
the frozen sanitized bundle and source-role/chronology classification into
`.private/sheetmetal-v1/1110101/freeze-rerun/`. Seven of nine private artifacts
were byte-identical and all nine matched under canonical JSON hashing with no
excluded fields. Full tests, legacy scoped freeze, active scoped freeze, bundle
hash/fingerprint checks, privacy, reference/post-design leakage, graph,
accessory, and no-drawing gates passed. Evidence is recorded in
`reports/sheetmetal-v1/one-project-model-calibration/1110101/generator_freeze_summary.json`.

Evaluator metrics after `D-0035`: neutral post-freeze metrics record
numerators, denominators, scorable coverage, and confidence without modifying
generator artifacts or opening completed-reference content for metric values.
Component registration coverage is `53/53`, graph referential integrity is
`107/107`, deterministic freeze canonical match is `9/9`, panel-assignment
resolution is source-limited at `0/53`, and accessory-rule scorability is
`0/0`. Evidence is recorded in
`reports/sheetmetal-v1/one-project-model-calibration/1110101/evaluator_metrics_summary.json`.

Exact next action: run
`RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION`. Do not generate a
customer drawing during that calibration step unless a later approved protocol
explicitly authorizes it.


Independent component graph audit after `D-0036`: the independent audit/adjudication for candidate `1110101` passes. Checkpoint verification confirmed HEAD `abc5a86`, clean tracked worktree with only the permitted legacy untracked script, full tests `PASS`, active and legacy scoped freezes `PASS`, selected bundle verification `PASS`, privacy `NOT_APPROVED`, no tracked private artifacts, no temporary render leftovers, and no generated customer drawing/PDF/DXF/DWG. Determinism adjudication identified the two byte-only mismatches as `source_fact_model.json` and `component_register_validation.json`; both were parsed-JSON equal and canonically hash-identical with no excluded fields. All hard gates passed. `SHEETMETAL_ALLOWED_EVAL` increments from `0` to `1`, preserving `1110101` as the first accepted sheetmetal-v1 calibration project for this stage. Current next action: `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION`. Evidence is recorded in `reports/sheetmetal-v1/one-project-model-calibration/1110101/independent_audit.json`, `hard_gate_adjudication.json`, `determinism_adjudication.json`, and `manifests/sheetmetal-v1/one-project-model-calibration/1110101/audit_input_manifest.json`.
