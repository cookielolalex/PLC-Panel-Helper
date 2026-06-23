# Evaluator Sensitivity Audit

Task: `CYCLE000-A4-EVALUATOR-SENSITIVITY-AUDIT`

Final status: `EVALUATOR_SENSITIVITY_PASS`

Scope was constrained to the task brief's allowed read paths. I did not inspect raw source roots, archived conversations, raw portfolio PDFs, checkpoint-validation packs, or final-held-out references. Trajectory paths were read from `orchestration/TASK_REGISTRY.csv`, but trajectory file contents were outside the allowed read set.

## Evidence Base

- Master spec hash: `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt` sha256 `eba9a30139a43862a7705f3123b050245dfa47fe3234d6a4e7579c6213e8ff09`
- Current state hash: `docs/01_CURRENT_STATE.md` sha256 `34d18598a665eb1625b72ed5b7240f283177354a1dff6aa5e6c927d25ad99e38`
- v2 evaluator hash: `scripts/evaluator_scoring.py` sha256 `83c8fb6f0198129cc6b0a6e8f18cc15dae692db9b2080f56d6e4fa7a7baa436b`
- v2 grading profile hash: `evals/grading_profiles/plc_layout_v2.json` sha256 `efbf014e0c6e98e09af9d4309aac96519a3c114c4975ef4a243914412dbfac52`
- Recompute report hash: `reports/evaluator-sensitivity/calibration_score_recomputation.json` sha256 `c155bce68e1e11c5222de6a0a2d51a38636f175663eaf2f8909972b43ecb9f2d`
- Counterfactual report hash: `reports/evaluator-sensitivity/counterfactual_results.json` sha256 `f5353a73af8699396c7a4dd74c03362992eb71590cf3d5492b89215a3c9e539f`
- Project differentiation report hash: `reports/evaluator-sensitivity/project_differentiation.json` sha256 `90675d75b7fefad8b66fdf8ae3209cc8351a9ea7b6f5bbc9f6a9dd130d5f194b`
- Test output hash: `reports/evaluator-sensitivity/test_results.json` sha256 `4db893b7877799705cc2d1f653e7ff304063c5d64b0efb9e5a6b5602da54a5f5`
- Prior frozen audit hash: `reports/calibration-006/independent_audit.json` sha256 `f57a428653a355befcefc7f0b54881e2031b1926bbf0ac990d6e5ecce2a43412`

Scoped Git evidence used bundled Git at `C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe`.

- `git rev-parse HEAD`: `b8c26b5e92608ae3c2c045ca18d08e320ae78747`
- `git status --short -- <allowed paths>`: modified `scripts/compare_one_project.py`, modified `scripts/run_tests.py`, plus new evaluator sensitivity files/directories.
- `git diff --name-status -- <allowed paths>`: only `M scripts/compare_one_project.py` and `M scripts/run_tests.py`.
- `git diff -- scripts/compare_one_project.py scripts/run_tests.py`: removed the hardcoded `quality_score: 42` and `scorable_coverage: 38` grading object from `compare_one_project.py`; added `compute_score(...)` and the evaluator sensitivity test.
- `git log -n 12 --oneline --decorate -- <allowed paths>` begins at `b8c26b5 Record six-project calibration audit`.

## Criteria

| Criterion | Status | Evidence |
|---|---|---|
| Score arithmetic | PASS | PowerShell recomputed 12 rescored records; every record dimension sum and result dimension sum matched `quality_score=42`. |
| Coverage arithmetic | PASS | PowerShell recomputed `scorable_elements/total_elements*100`; every run matched `38/100*100 = 38`. |
| Original hardcoded `42/38` defect identification | PASS | Git diff shows removal of literal `quality_score: 42` and `scorable_coverage: 38`; recomputation report records `FAIL_HARDCODED_SCORE_AND_COVERAGE`. |
| v2 absence of magic total/coverage constants in `compute_score` | PASS | Extracted `compute_score` contains no word-boundary `42` or `38`; score is summed from dimensions and coverage comes from `_coverage(record)`. |
| Hard-gate behavior | PASS | Code sets validity `FAIL` and score `0`; counterfactuals `missing_required_output` and `unsupported_critical_value` both pass with score `0`. |
| Monotonicity/counterfactual results | PASS | Counterfactual report status `PASS`, 10/10 cases passed; corrections increase score, added defect decreases score, same-total vector remains distinguishable. |
| Finding deduplication | PASS | Deduplication uses `dedupe_key`; all 12 v2 results have deduped count `3`, and duplicate-finding counterfactual keeps high findings at `3`. |
| Project differentiation | PASS | Project differentiation report status `PASS`; six project IDs, distinct source/reference evidence, no identical generated PDF hash pairs. Scores remain numerically identical, but project artifacts are not collapsed. |
| Low-coverage handling | PASS | `_coverage` returns `INSUFFICIENT_COVERAGE` for zero scorable/total elements; counterfactual `remove_all_scorable` has coverage `0` and evidence strength `INSUFFICIENT_COVERAGE`. |
| Registration handling | PASS | Recompute checks mark `registration_failure_not_undocumented_fixed_total=True`; `registration_unsuitable` counterfactual preserves explicit cross-PDF dimension behavior without a hidden total override. |
| Unchanged drawing-generation workflow | PASS | Scoped Git status/diff shows only evaluator/reviewer/test changes and new evaluator sensitivity artifacts; no generator, renderer, instruction, Knowledge, schema, source-bundle, `job_spec`, or `drawing_model` workflow files are modified in the allowed evidence. |
| Test results | PASS | Existing `test_results.json` records `scripts/run_tests.py` returncode `0`, empty stderr, and includes `test_evaluator_sensitivity_monotonicity`. I did not rerun tests because the suite writes tmp artifacts and this audit may write only the two audit files. |
| Preservation of prior frozen evidence | PASS | Scoped Git status/diff shows no modifications to `reports/calibration-006/independent_audit.json`, `optimization/calibration-006/machine_summary.json`, or calibration manifests; prior audit still reports `SIX_PROJECT_CALIBRATION_AUDIT_PASS`. |

## Result

All requested criteria are `PASS`.

Result token: `EVALUATOR_SENSITIVITY_PASS`
