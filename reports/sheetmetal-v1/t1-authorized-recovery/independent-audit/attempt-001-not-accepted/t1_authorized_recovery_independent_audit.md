# SMV1 T1 Authorized Recovery Independent Audit

Exact status: `INDEPENDENT_AUDIT_NOT_ACCEPTED`

Overall result: `FAIL`

## Scope

Audit read boundary was limited to:

- `orchestration/tasks/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.md`
- `orchestration/input_manifests/sheetmetal-v1/t1-authorized-recovery/SMV1-T1-AUTHORIZED-RECOVERY-INDEPENDENT-AUDIT.visible_files.json`
- files listed visible in that manifest

Manifest SHA-256: `09D8ED948FB7D493AEDC6F8F7177C73FCACB6E9580623D1CDB7751FBB0E29419`

All visible-file hashes matched the manifest.

## Findings

1. `FAIL`: current HEAD is not the manifest head.
   - Manifest `current_integration_head`: `980529e32c6014be23c9e3c7e53046ea62b718d4`
   - `git rev-parse HEAD`: `55d151f578a2dd5189ed9d1124279746ea0f5199`

2. `PASS`: integration, T1A, T1B, and T1C JSON artifacts are parseable and required-field-complete.
   - Checked child results, integration summary, recovery reports, and T1C rule artifact with `ConvertFrom-Json` and required-field checks.

3. `NOT_VERIFIED`: non-self output hashes are only partially verified.
   - Visible declared outputs matched their hashes.
   - Seven declared output paths were outside the visible manifest and were not read.

4. `PASS`: T1A remains safe unresolved with no panel allocation promotion.
   - T1A report keeps `explicitly_assigned: 0`, `rule_assigned: 0`, `unassigned: 53`, `unsupported_assignment_count: 0`, and `capability_success_claimed: false`.

5. `PASS` / `NOT_VERIFIED`: T1B real-project geometry remains `0/53`, but synthetic execution was not rerun.
   - T1B report keeps real-project `verified_model_geometry: 0`, `approved_generic_conservative_envelope: 0`, `geometry_missing: 53`, denominator `53`, and promotion counts `0`.
   - The synthetic fixture/proposed library were not visible, and Python was unavailable.

6. `PASS`: T1C remains proposal-only in visible evidence.
   - T1C report says rule artifacts were built but not activated in the frozen generator.
   - Integration summary says `model_promotion_performed: false`, `t2_recalibration_started: false`, `customer_drawing_generated: false`, and `t1c_rule_artifacts_promoted: false`.
   - Visible scripts and frozen manifests contain no reference to the proposed T1C rule artifact.

7. `NOT_VERIFIED`: required test reruns and scoped freeze reruns could not execute.
   - `python scripts/run_tests.py`: exit `1`, Python not found.
   - `python scripts/verify_frozen_workflow.py --scope legacy-baseline-024`: exit `1`, Python not found.
   - `python scripts/verify_frozen_workflow.py --scope sheetmetal-v1-active`: exit `1`, Python not found.
   - `python scripts/verify_frozen_workflow.py --scope sheetmetal-v1-topology-sizing-placement`: exit `1`, Python not found.

8. `PASS`: hard gates are zero/false in visible integration evidence.
   - Source-root mutation count `0`
   - Private external transmissions `0`
   - Completed-reference leakage `0`
   - Post-design leakage `0`
   - Customer PDF/DXF/DWG generation `0`
   - Production approval declared `false`

9. `FAIL`: current worktree contains an untracked forbidden script path.
   - `git status --porcelain=v1`: `?? scripts/run_reference_detection_v4_corpus_screening.py`
   - This audit did not read, stage, execute, or modify that path.

10. `NOT_VERIFIED`: master spec, current phase plan, canonical state content, and trajectories were not read because they were not visible in the manifest.

## Command Results

- `git rev-parse HEAD`: `55d151f578a2dd5189ed9d1124279746ea0f5199`
- `git log -1 --format='%H%n%an%n%ae%n%aI%n%s'`: latest commit `55d151f578a2dd5189ed9d1124279746ea0f5199`, `Integrate T1 authorized recovery artifacts`
- `git diff --name-status HEAD`: no tracked diff output
- `git status --porcelain=v1`: `?? scripts/run_reference_detection_v4_corpus_screening.py`

## Blockers

- Visible manifest is one commit behind current `HEAD`.
- Python runtime is unavailable for required validation reruns.
- Visible manifest omits seven declared non-self child output paths.
- Untracked forbidden screening script path is present.
- Non-visible master/canonical/trajectory files were not opened under the audit read boundary.

## Recommended Next Action

Regenerate a visible-file manifest bound to current `HEAD`, include every declared child output hash path or explicitly relax that verification requirement, provide an executable Python runtime, and adjudicate or remove the untracked forbidden screening script before rerunning the independent audit.
