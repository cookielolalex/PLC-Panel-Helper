# Independent Audit - Sheetmetal V1 Migration

Audit time: 2026-06-24T12:58:06.4599371+08:00

Overall status: PASS_WITH_RESIDUAL_RISKS.

Scope: read the requested governance docs, current state, decision/eval ledgers,
session checkpoint, sheetmetal-v1 specs, migration reports, manifests, fixture,
scripts, schemas, existing synthetic test output, `.git/HEAD`, and `.git/logs/HEAD`.
I did not inspect private source roots or completed drawings. I did not modify
legacy baseline evidence.

## Criteria

| Criterion | Status | Evidence |
|---|---|---|
| Legacy evidence preserved | PASS | `manifests/sheetmetal-v1/namespace_manifest.json` says `overwrite_legacy_evidence=false`; `reports/sheetmetal-v1/phase0_checkpoint_verification.json` says `old_evidence_rewritten=false` and records legacy hashes; legacy namespace directories still exist. |
| Privacy remains NOT_APPROVED | PASS | `docs/PRIVACY_APPROVAL.md` status is `NOT_APPROVED`; phase0 verification records `approval_status=NOT_APPROVED` and privacy file SHA-256 `EC70B7AB47DDBB23EC029E7E5BF0F744C96DAB641DA2056FB4CD4B1619F3489E`. |
| Baseline generation remains zero | PASS | `reports/sheetmetal-v1/phase0_checkpoint_verification.json` has `baseline_generation_attempts=0` and `baseline_generation_started=false`; current state and checkpoint repeat that baseline generation remains `0`. |
| No real customer drawing generated | PASS | Phase0 verification has `real_customer_drawing_generated=false`; restricted search under `reports/sheetmetal-v1`, `manifests/sheetmetal-v1`, `evals/sheetmetal-v1`, and `orchestration/sheetmetal-v1` found no `.pdf`, `.dwg`, `.dxf`, `.xlsx`, `.xlsm`, or `.xls` files. |
| New sheetmetal-v1 namespaces exist | PASS | `reports/sheetmetal-v1`, `manifests/sheetmetal-v1`, `evals/sheetmetal-v1`, and `orchestration/sheetmetal-v1` all exist as directories. |
| Legacy 13 are not grandfathered | PASS | `legacy_three_output_allowed_eval.json` records 13 historical projects as `LEGACY_THREE_OUTPUT_ALLOWED_EVAL` and `not_counted_as=SHEETMETAL_ALLOWED_EVAL`; `requalification_queue.json` has `approved_count=0` and 13 `PENDING_REQUALIFICATION` candidates. |
| Schemas parse and validate relevant artifacts | PASS | Node read-only schema parse covered 13 new schema files; fixture validation covered 21 `source_facts` against `schemas/source_fact.schema.json` and 1 `panel_definition` against `schemas/panel_definition.schema.json`; existing synthetic outputs validated against source evidence, component register/type/instance/geometry, panel assignment/graph/constraint, sheetmetal drawing model, and provenance schemas. |
| Synthetic pipeline proves listed invariants | PASS | Existing `tmp/sheetmetal_v1_pipeline_test/validation_report.json` is `PASS`; extracted values show `required_qty=1`, `ordered_qty=2`, breaker `CONFLICT`, duplicate accessory count `0`, post-design/reference assignments rejected, placement unresolved in assignments, functional edge `UNVERIFIED`, named dimensions `800/2300/800`, hard `CONTAINMENT` failure with soft override rejected, and provenance coverage `PASS`. |
| Generator artifacts exclude completed-reference/post-design tokens | PASS | Existing synthetic `validation_report.json` leakage scan is `PASS` with `forbidden_hits=[]`; `rg` found `REF-COMPLETE-001`, `completed-reference-secret`, and `post-design-secret` only in the fixture and test assertion, not in generated synthetic artifacts. `scripts/sheetmetal_v1.py` filters facts through generator-allowed evidence and scans serialized generator artifacts. |

## Hash Evidence

- `AGENTS.md`: `4CA078C3F02217CED8491C53A11641152B38A364F157E36523408016074EB227`
- `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`: `EBA9A30139A43862A7705F3123B050245DFA47FE3234D6A4E7579C6213E8FF09`
- `docs/01_CURRENT_STATE.md`: `61893133619A321CB0D1E08D729951931D5C7F47ED59C1A9A4A74C6E4FC7AA81`
- `docs/04_DECISION_LEDGER.md`: `FCE0BBA05DBF8896105EB457BADF6F7DEFB31875FBA7E1936414B141A9349764`
- `docs/06_EVAL_LEDGER.md`: `28039C0AC05EC1D0D50DDECA5AD25318019708E5AED35AA24BAB50238A029126`
- `docs/SESSION_CHECKPOINT.md`: `D107DDA9F4358E3A6FB2E87DE2CB98734ED4BDFC6FEB553F6334F7EB83F50D28`
- `reports/sheetmetal-v1/phase0_checkpoint_verification.json`: `3CD97117DFA343E93B7B4777563BA33F987A3EA8AE2EC33BAF0225467F7A115D`
- `evals/fixtures/sheetmetal-v1/complete_pipeline_fixture.json`: `96F50B3279EA537B2E183E1EF9065DEEB4DEBBCC3C74AFC1C21FACD521020017`
- `scripts/sheetmetal_v1.py`: `28BEBE451D9CEA356C46C51E17E4E334AF54185C909DCBCE098DABA23800E94C`
- `scripts/run_tests.py`: `0067F90069F5539BB127225E030CFCAF6F5E9F180650B88A8F82BAA335A2A420`

## Residual Risks

- Git executable was unavailable (`where.exe git` failed), so `git diff` and
  worktree cleanliness were NOT_VERIFIED. `.git/HEAD` points to `refs/heads/main`
  at `a193abc3e702d1750d40585180d8839fefd920c2`; `.git/logs/HEAD` was readable.
- Fresh `python scripts/run_tests.py` was NOT_VERIFIED in this shell because the
  only `python.exe` was the Windows Store alias. I did not run the full test
  runner because it writes `tmp/` outputs and the audit was constrained to only
  two report files. Existing recorded test evidence and read-only validation were used.
- Status wording is inconsistent: `reports/sheetmetal-v1/migration_report.md`
  still says `SHEETMETAL_FIRST_GOAL_MIGRATION_IN_PROGRESS`, while current state,
  session checkpoint, eval ledger, and decision `D-0025` say
  `SHEETMETAL_MODULAR_FOUNDATION_READY_FOR_ONE_PROJECT_CALIBRATION`.
