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
- Ran frozen v4 on the 8-project calibration partition with private OCR
  disabled. Gate implementation passed, but detector performance failed:
  all-three recall `0 / 8`; private OCR page count `0`. Preserved failed
  evidence under `reports/baseline-024/reference-detector-calibration/v4_calibration_partition/`.
- Added v4.1 `target_output_detection_v4_1_local_layout_prior_recovery`, a
  local layout-confirmed weak-role-prior fallback that preserves explicit
  non-target override and no alias-only promotion.
- Added regression coverage for private-OCR-disabled image-only layout-prior
  recovery and weak-prior-without-layout fail-closed behavior.
- Ran v4.1 calibration positives: all-three recall `8 / 8`; each target type
  `8 / 8`; private OCR page count `0`; cleanup, minimization, generator
  isolation, and source-review blindness `PASS`.
- Ran v4.1 minimized real negative controls: `24 / 24` controls supported,
  zero false target pages, zero false all-three promotions, zero electrical or
  source-document target acceptances, private OCR page count `0`.
- Recorded v4.1 freeze manifest and independent implementation audit. Recovery
  status is `DETECTOR_V4_1_CALIBRATION_PASSED_HOLDOUT_PENDING`; next selected
  action is `RUN_DETECTOR_V4_1_SEALED_HOLDOUT_AUDIT`.
- Ran v4.1 sealed holdout with minimized aggregate output only. The gate passed
  with all-three recall `5 / 5`, each target type `5 / 5`, private OCR page
  count `0`, external transmission count `0`, no persisted holdout identities,
  and no detailed detector outputs.
- Ran v4.1 all-13 final known-positive recall with minimized aggregate output
  only. The gate passed with all-three recall `13 / 13`, each target type
  `13 / 13`, private OCR page count `0`, and no detailed detector outputs.
- Refreshed v4.1 real negative controls; they remained `PASS` with `24 / 24`
  supported controls, zero false target pages, zero false all-three promotions,
  and private OCR page count `0`.
- Recorded independent sealed-gate audit, including scoped persistence,
  temp-root absence, cleanup, aggregate-evidence, and hash checks.
- Updated the recovery controller and schema. Current status is
  `DETECTOR_V4_1_INDEPENDENT_GATE_PASSED_SCREENING_PENDING`; the next selected
  action is `RUN_DETECTOR_V4_1_CORPUS_WIDE_SCREENING`.
- Accepted decision `D-0025`, migrating the active V1 goal to
  `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1` while preserving the legacy
  three-output detector workflow as historical evidence.
- Added new `sheetmetal-v1` namespaces under `reports/`, `manifests/`,
  `evals/`, and `orchestration/` without overwriting `baseline-024`.
- Added sheetmetal-first architecture, source-role/chronology, authority
  matrix, and qualification policy specs.
- Added source evidence, source fact, component type/instance/register,
  panel definition/assignment/graph, accessory rule, component geometry,
  panel constraint, sheet-metal drawing model, and provenance schemas.
- Added `scripts/sheetmetal_v1.py`, a deterministic JSON-first modular
  foundation for synthetic source evidence, component register normalization,
  graph building, accessory/cutout reconciliation, panel assignment,
  topology/sizing, placement validation, drawing model creation, and provenance.
- Added the synthetic complete-pipeline fixture and regression coverage proving
  quantity separation, conflict preservation, post-design label rejection,
  inventory-only graph safeguards, accessory duplicate prevention,
  assignment/placement separation, named dimensions, hard placement
  constraints, provenance coverage, and reference-leakage exclusion.
- Full `scripts/run_tests.py` status remains `PASS`; no real customer drawing
  or baseline generation occurred.
- Recorded independent sheetmetal-v1 audit
  `PASS_WITH_RESIDUAL_RISKS` and coordinator addendum resolving auditor-local
  Git/Python limitations plus the migration-report status wording drift.
- Accepted decision `D-0026`, making frozen workflow manifests scope-bound and
  commit-anchored instead of global current-tree checks.
- Added `docs/specs/FROZEN_WORKFLOW_SCOPE_AND_LINEAGE_POLICY.md` and
  `scripts/verify_frozen_workflow.py` with regression coverage for legacy and
  active scoped freeze verification.
- Resolved legacy baseline-024 historical anchor
  `fac44321491633181f1fa53a062084d072b0b582` and recorded
  `evals/baseline-024/frozen_workflow_attestation.json` without rewriting the
  old manifest.
- Created `evals/sheetmetal-v1/frozen_workflow_manifest.json`, anchored at
  `ab955b854e31d37666445f5a62ee6556f85f1352`, covering 47 stable active
  workflow files and superseding no historical manifest.
- Recorded revised Phase-0 evidence:
  `ONE_PROJECT_SHEETMETAL_REQUALIFICATION_PHASE_0_PASS`. The next action is
  `DETERMINISTIC_ONE_PROJECT_CANDIDATE_SELECTION`.
- Accepted decision `D-0027`, selecting project `1110101` for one-project
  sheetmetal calibration by deterministic metadata-only source-bundle
  readiness ranking.
- Froze `manifests/sheetmetal-v1/one_project_candidate_selection.json` before
  opening completed-reference metadata, with `1110101` score `1156` and rank
  `1` among 13 candidates.
- Qualified the evaluator-only effective sheetmetal reference package for
  `1110101`; completed references remain reviewer-only and are excluded from
  generator inputs.
- Recorded source-role/chronology classification for `1110101`: six
  `AGENT_QUORUM_APPROVED_EVAL` source-only items and twelve quarantined items
  excluded from the generator bundle.
- Built and verified a clean sheetmetal-v1 sanitized bundle under
  `manifests/sheetmetal-v1/selected_candidate/1110101/generator_bundle/`.
  Bundle verification is `PASS`; it excludes `reference_manifest.json`,
  original workbooks, completed drawings, path escapes, and symlinks.
- Recorded independent candidate-selection audit `PASS` in
  `reports/sheetmetal-v1/selected_candidate_1110101_independent_audit.md` and
  `orchestration/results/SMV1-CANDIDATE-SELECTION-AUDIT.json`.
- Updated `manifests/sheetmetal-v1/requalification_queue.json`: `1110101` is
  selected and bundle-verified; `SHEETMETAL_ALLOWED_EVAL` approved count
  remains `0`. No customer drawing was generated.
- Began `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION` for candidate
  `1110101`.
- Verified checkpoint gates at HEAD `5409f29`: full tests passed, legacy and
  active scoped workflow freezes passed, the selected sanitized bundle
  verifier passed, bundle hashes and worksheet fingerprints checked out,
  privacy remained `NOT_APPROVED`, no sheetmetal-v1 drawing output was present,
  and no sheetmetal-v1 baseline-generation directory existed.
- Froze `docs/specs/ONE_PROJECT_COMPONENT_GRAPH_CALIBRATION.md`,
  `manifests/sheetmetal-v1/one-project-model-calibration/1110101/calibration_protocol.json`,
  and
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/calibration_plan.md`.
  The protocol fixes generator/evaluator lane isolation, inventory-only mode,
  private-workspace requirements, deterministic freeze requirements, evaluator
  metric minimization, and hard gates before project-specific fact extraction.
- Added the `.private/` ignore boundary and created local workspace
  `.private/sheetmetal-v1/1110101/` before writing project-specific facts.
- Added `test_sheetmetal_v1_private_workspace_boundary`, covering
  `git check-ignore` for the project-private path and proving no `.private`
  path is tracked.
- Refreshed `evals/sheetmetal-v1/frozen_workflow_manifest.json` for the
  `.gitignore` boundary and updated test-runner hash, preserving scoped active
  workflow verification.
- Recorded private-boundary evidence under
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/`.
- Added deterministic source-fact extraction to `scripts/sheetmetal_v1.py` for
  approved sanitized generator bundles, with quiet private-output mode and
  neutral committed summaries only.
- Added `schemas/source_fact_model.schema.json` and
  `test_sheetmetal_v1_source_fact_extractor`, covering source-value
  non-printing, row accounting, approved generic current-project role tokens,
  long-form chronology normalization, and string reference-flag parsing.
- Ran the private `1110101` source-fact extraction under
  `.private/sheetmetal-v1/1110101/source-fact-extraction/`; schema validation
  passed with 6 evidence records, 125 represented source lines, 87 source facts,
  0 completed-reference facts, and 0 private content transmissions.
- Refreshed the active sheetmetal-v1 frozen workflow manifest for the
  source-fact schema, extractor, and regression test hashes.
- Recorded neutral source-fact extraction evidence under
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/`.
- Added `--source-fact-model` register-only mode to `scripts/sheetmetal_v1.py`
  so private source facts can produce a private component register without
  running panel assignment, graph construction, or drawing-model generation.
- Updated component fact helpers to accept formal source-fact fields
  `field_type` and `normalized_value`, while preserving legacy synthetic
  aliases.
- Added `test_sheetmetal_v1_component_register_from_source_facts`, covering
  source-value non-printing, schema validity, complete registration of allowed
  source-fact component keys, and quantity-stage preservation.
- Ran the private `1110101` component-register build under
  `.private/sheetmetal-v1/1110101/component-register/`; schema validation
  passed with 53 component types, 53 component instances, 0 conflicts, 0
  unregistered allowed component keys, and 0 private content transmissions.
- Recorded neutral component-register evidence under
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/`.
- Added private panel-assignment and inventory-only graph construction to
  `scripts/sheetmetal_v1.py` using `--source-fact-model` plus
  `--component-register`.
- Added `test_sheetmetal_v1_panel_assignment_graph_from_private_models`,
  covering explicit panel assignment acceptance, unresolved component handling,
  graph referential integrity, inventory-only unverified functional edges, and
  source-value non-printing.
- Ran the private `1110101` panel graph build under
  `.private/sheetmetal-v1/1110101/panel-graph/`; schema validation passed with
  0 explicit panel assignments, 53 unresolved components, 56 graph nodes, 107
  graph edges, 0 dangling edges, and 0 private content transmissions.
- Recorded neutral panel graph evidence under
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/`.
- Added private accessory and cutout reconciliation to `scripts/sheetmetal_v1.py`
  using `--source-fact-model`, `--component-register`, and `--panel-graph`.
- Added `test_sheetmetal_v1_accessory_cutout_reconciliation_from_private_models`,
  covering source-value non-printing, synthetic approved-rule accessory/cutout
  derivation, graph-source referential integrity, and privacy counter
  preservation.
- Ran the private `1110101` accessory/cutout reconciliation under
  `.private/sheetmetal-v1/1110101/accessory-cutout/`; validation passed with 0
  accessory requirements, 0 generated accessory component instances, 0 cutouts,
  0 duplicate accessories, 0 missing graph sources, and 0 private content
  transmissions.
- Recorded neutral accessory/cutout evidence under
  `reports/sheetmetal-v1/one-project-model-calibration/1110101/`.
- Reran the generator-side private stages under
  `.private/sheetmetal-v1/1110101/freeze-rerun/` from the frozen sanitized
  bundle and source-role classification.
- Recorded deterministic generator freeze evidence: 7 of 9 private artifacts
  were byte-identical and all 9 matched under canonical JSON hashing with no
  excluded fields.
- Reverified hard gates: full tests `PASS`, legacy and active scoped freezes
  `PASS`, private content transmission `0`, private Git leakage `0`, and no
  customer drawing/PDF/DXF/DWG/baseline-generation output.
- Added evaluator-only component graph metrics with numerator, denominator,
  scorable coverage, and confidence for each metric.
- Recorded source-limited coverage explicitly: component registration `53/53`,
  graph referential integrity `107/107`, deterministic freeze `9/9`, panel
  assignment `0/53`, and accessory-rule scorability `0/0`.

- Added independent component-register and graph calibration audit artifacts for `1110101`, including the audit-input manifest, hard-gate adjudication table, determinism adjudication, and minimized Markdown summary.
- Adjudicated the generator freeze byte-only mismatches: `source_fact_model.json` and `component_register_validation.json` are structurally identical parsed JSON with matching canonical hashes and no excluded fields.
- Accepted `1110101` as the first sheetmetal-v1 calibration project for the modular component-register and graph stage; `SHEETMETAL_ALLOWED_EVAL` approved count is now `1`.
- Set next action to `RUN_ONE_PROJECT_TOPOLOGY_SIZING_AND_PLACEMENT_CALIBRATION` while preserving privacy `NOT_APPROVED` and customer drawing generation count `0`.
- Froze the topology/sizing/placement calibration protocol for `1110101`.
- Added deterministic topology calibration mode to `scripts/sheetmetal_v1.py`,
  keeping private project topology, sizing, placement, constraint, provenance,
  rule-version, schema-version, and workflow-version artifacts under ignored
  `.private/` paths.
- Added regression coverage for missing geometry, unassigned components,
  post-design allocation rejection, completed-reference geometry exclusion,
  multiple topology candidates, unsupported exact cabinet-size blocking,
  generic geometry separation, overlap detection, containment detection,
  clearance detection, hard constraints overriding soft objectives,
  deterministic IDs/order, provenance coverage, and no drawing generation.
- Recorded local capability evidence: no approved installed OR-Tools, SciPy
  optimize, PuLP, or Z3 solver was available, so the deterministic greedy
  baseline plus hard-constraint validator was selected without downloading
  dependencies.
- Ran the private `1110101` topology/sizing/placement generator twice. All 12
  private artifacts were byte-identical and canonical-JSON identical.
- Recorded neutral summaries: assignment coverage `0/53`, geometry coverage
  `0/53`, placement coverage `0/53`, unsupported assignments `0`,
  unsupported placements `0`, accepted overlap/containment/clearance
  violations `0`, reference leakage `0`, post-design leakage `0`, private
  transmissions `0`, tracked private artifacts `0`, and customer drawing
  generation `0`.
- Added `SHEETMETAL_V1_TOPOLOGY_SIZING_PLACEMENT` scoped workflow manifest and
  verifier support. Legacy, active sheetmetal-v1, and topology-stage freezes
  all pass.
- Set next action to
  `RUN_INDEPENDENT_ONE_PROJECT_TOPOLOGY_SIZING_PLACEMENT_AUDIT` while keeping
  `SHEETMETAL_ALLOWED_EVAL` at `1`, privacy `NOT_APPROVED`, and customer
  drawing generation count `0`.
- Created the master autopilot protocol and durable master orchestration state
  under `orchestration/master/`.
- Dispatched the T0 independent topology/sizing/placement audit. The Codex App
  worktree request remained pending without a concrete thread id, so a bounded
  independent-auditor subagent performed the fallback audit.
- Recorded the T0 audit result `INCONCLUSIVE_LOW_COVERAGE`: safety and
  implementation integrity pass, but assignment, geometry, and placement
  coverage remain `0/53` and are not capability success.
- Resolved the auditor's fresh-command caveat by rerunning full tests and the
  legacy, active sheetmetal-v1, and topology-stage scoped freezes with the
  bundled runtime; all passed.
- Set next action to `RUN_TARGETED_COVERAGE_RECOVERY_T1` while keeping
  `SHEETMETAL_ALLOWED_EVAL` at `1`, privacy `NOT_APPROVED`, and customer
  drawing generation count `0`.
- Recorded T1 targeted recovery results for panel assignment, component
  geometry, and topology/sizing rules. All three branches returned safe
  unresolved because no compliant approved-source or approved-rule recovery
  path exists at the current authority level.
- Integrated T1 worker outputs and accepted the independent T1 recovery audit
  as `PASS_SAFE_UNRESOLVED_T1_NO_COMPLIANT_RECOVERY_PATHS`.
- Resolved the auditor's Python-runtime limitation with coordinator-side full
  tests and legacy, active sheetmetal-v1, and topology-stage scoped freeze
  verification; all passed.
- Preserved hard gates: no implementation code/rule/schema/frozen artifacts
  changed during T1, no customer drawing/PDF/DXF/DWG was generated, no
  production approval was declared, and coverage remains assignment `0/53`,
  component geometry `0/53`, topology `0/1`, sizing `0/0`, and placement
  `0/53`.
- Set next action to `RUN_PROPOSAL_FIRST_SOURCE_RULE_APPROVAL_BRANCH`.
- Added the source/rule approval proposal packet with three reviewable lanes:
  panel allocation source, component geometry authority, and
  topology/sizing/placement rules.
- Independently reviewed the proposal packet. The review passed all readiness
  criteria and confirmed it is proposal-only, hash-bound to accepted T1
  evidence, preserves no-invention and forbidden-use boundaries, requires
  tests before fixes, and has bounded diff scope and rollback.
- Set next action to `PREPARE_SOURCE_RULE_AUTHORITY_DECISION_PACKET`.
- Prepared the source/rule authority decision packet. No lane was accepted
  autonomously; panel allocation source review, component geometry authority,
  and topology/sizing/placement rule authority all require signed human/source
  or fabrication-domain approval before implementation.
- Set next action to `REQUEST_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION`.
- Added a template-only signed authority decision form bound to the decision
  packet hashes. No authority lane was selected, no implementation was applied,
  and the next action is still to obtain a signed human/source-rule authority
  decision.
- Added fail-closed validation for future signed authority decisions, including
  schema, validator, regression coverage, refreshed active/topology scoped
  freeze manifests, neutral summary evidence, and child-result evidence.
- Added neutral intake routing for future validator-passing signed authority
  decisions. Accepted lanes route to the required regression-test-before-fix
  gate, reject-all routes to terminal-candidate review, invalid decisions fail
  closed, and no authority lane or implementation is authorized.
- Added an unsigned signed-authority decision JSON draft scaffold bound to the
  current packet/template hashes, plus fail-closed regression coverage and
  neutral draft evidence. The draft intentionally remains invalid until a
  signed human/source-rule authority decision is filled, validated, and routed.
- Added an atomic signed-authority decision submission processor that writes
  validation, intake, and summary artifacts together. The current unsigned
  draft was processed as expected-fail evidence, preserving the signed-human
  authority wait state and all no-implementation/no-drawing gates.
- Recorded a strict blocked audit for the signed human/source-rule authority
  decision gate. All safe autonomous gate-preparation work is complete; the
  remaining queued task requires an external signed decision selecting `A`,
  `B`, `C`, or `D`.
- Recorded the signed `D-0047` source/rule authority decision from
  `PROJECT_OWNER_USER`, selecting `A`, `B`, and `C`, and explicitly not
  selecting `D`.
- Validated and processed the signed decision with
  `scripts/validate_signed_authority_decision.py` and
  `scripts/process_signed_authority_decision.py`; the accepted decision routes
  to `ADD_REGRESSION_TESTS_BEFORE_ACCEPTED_AUTHORITY_LANE_FIX`.
- Preserved the decision boundary: implementation authorization remains
  false until tests-before-fix are added, customer PDF/DXF/DWG generation is
  still unauthorized, production approval remains forbidden, and privacy
  remains `NOT_APPROVED`.
- Re-created the master heartbeat automation as
  `plc-panels-master-autopilot-heartbeat` on the 15-minute cadence.
- Queued three bounded authorized recovery worktrees:
  `SMV1-T1A-PANEL-ALLOCATION-RECOVERY`,
  `SMV1-T1B-COMPONENT-GEOMETRY-RECOVERY`, and
  `SMV1-T1C-TOPOLOGY-SIZING-RULE-RECOVERY`.
