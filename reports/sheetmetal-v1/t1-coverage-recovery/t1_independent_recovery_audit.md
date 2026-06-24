# SMV1 T1 Independent Recovery Audit

Task ID: `SMV1-T1-INDEPENDENT-RECOVERY-AUDIT`

Final status: `PASS_SAFE_UNRESOLVED_T1_NO_COMPLIANT_RECOVERY_PATHS`

Recommended next action: `RUN_PROPOSAL_FIRST_SOURCE_RULE_APPROVAL_BRANCH`

## Scope

Audited the T1 worker child results and integration summary at target
integration commit `bc02f7d` from current observed HEAD
`a6cf5d98baea9e577939bb5e529f34070c3f24fb`.

Visible-file manifest:
`orchestration/input_manifests/sheetmetal-v1/t1-coverage-recovery/SMV1-T1-INDEPENDENT-RECOVERY-AUDIT.visible_files.json`

No source roots, `.private` files, completed target drawings, post-design files,
customer PDFs/DXFs/DWGs, thumbnails, extracted target text, reviewer answers,
scores, or reference details were opened.

## Verdicts

| Criterion | Verdict | Evidence |
|---|---:|---|
| Parse all T1 worker child-result JSON and T1 integration JSON | PASS | PowerShell `ConvertFrom-Json` passed for all four child-result files and all four T1 report JSON files. |
| Worker statuses and integration conclusion internally consistent | PASS | Worker statuses are safe-unresolved/no compliant path; integration status is `SAFE_UNRESOLVED_T1_NO_COMPLIANT_CODE_OR_RULE_RECOVERY_PATHS_AUDIT_REQUIRED`. |
| No implementation/code/rule changes by T1 workers | PASS | `git diff --name-status 45ab4b4..bc02f7d` shows only 12 added recovery report and child-result files. No `scripts/`, `rules/`, `schemas/`, docs ledgers, canonical state, frozen releases, or frozen graders changed in that range. |
| Coverage remained source-limited, not capability success | PASS | Integration coverage: assignment `0/53`, geometry `0/53`, topology `0/1`, sizing `0/0`, placement `0/53`; interpretations explicitly say safe/source-limited and not capability success. |
| Hard gates remain zero/false | PASS | Integration hard gates report zero unsupported assignments, geometry promotions, critical dimensions, placements, hard-constraint violations, completed-reference leakage, post-design leakage, private transmissions, committed private values, customer drawing generation, PDF/DXF/DWG generation, and false production approval declaration. |
| Blocker taxonomy supports source/rule authority gap | PASS | Blockers are missing approved panel allocation source/rule, component geometry library/envelope rule, cabinet/surface/clearance/thermal/spare-space rules, and source-limited topology sizing coverage. Integration classifies this as `NON_TERMINAL_SOURCE_RULE_AUTHORITY_GAP_PENDING_INDEPENDENT_AUDIT`. |
| Privacy/content leakage in committed T1 reports | PASS | T1 privacy counts are zero. Sentinel scan of T1 report files found no drive paths, `.private` values, source-root paths, generated drawing claims, or production approval declaration; one generic boundary statement mentions forbidden source roots and `.private` without revealing paths or values. |
| JSON parse checks | PASS | Local PowerShell parse command passed for all visible T1 JSON inputs and reports. |
| Fresh `scripts/run_tests.py` | NOT_VERIFIED | `python --version` returns the Microsoft Store alias message; `py --version` is unavailable; no usable Python runtime was found under common local paths or `.codex`. |
| Fresh scoped frozen workflow verifier script | NOT_VERIFIED | Same Python unavailability prevents executing `scripts/verify_frozen_workflow.py`. |
| Manual active sheetmetal-v1 freeze hash check | PASS | PowerShell SHA-256 check passed for all 50 files in `evals/sheetmetal-v1/frozen_workflow_manifest.json`; active anchor `ab955b8` and integration commit `bc02f7d` are ancestors of current HEAD. |
| Legacy baseline scoped freeze in this runtime | NOT_VERIFIED | The Python verifier could not run. A naive current-worktree hash comparison finds the known `AGENTS.md` scope mismatch; `docs/04_DECISION_LEDGER.md` D-0026 says legacy and active manifests are scope-bound and current active files must not be compared to historical expected hashes. |

## Key Evidence

- Current HEAD: `a6cf5d98baea9e577939bb5e529f34070c3f24fb`
- T1 target integration commit: `bc02f7d6a2b84f06ef7d1e7d3b060ba36081a5d9`
- `git status --short`: only pre-existing untracked
  `scripts/run_reference_detection_v4_corpus_screening.py`
- T1 worker commit: `c02656f Record T1 recovery worker results`
- T1 integration commit: `bc02f7d Record T1 recovery integration summary`
- Audit-brief commit: `a6cf5d9 Add T1 recovery audit brief`
- `git diff --name-status 45ab4b4..bc02f7d`: added only the three worker
  report pairs, their three child-result JSON files, the integration summary
  pair, and the integration child-result JSON.

## Residual Risks

- Fresh Python test and scripted frozen-workflow verification were not run in
  this audit environment due missing Python runtime.
- The worker self-reports differ in local tool availability; this audit used
  direct Git, PowerShell JSON parsing, PowerShell hashing, and manifest checks
  where available.
- T1 did not recover assignment, geometry, topology, sizing, or placement
  coverage. This is acceptable only as a safe unresolved state; it must not be
  promoted to engineering capability or drawing generation readiness.

## Trajectory

1. Read task brief and visible-file manifest.
2. Read master spec, active protocol/current state, master state, queue,
   recovery ledger, thread registry, frozen workflow manifests, and relevant
   ledger/checkpoint excerpts.
3. Parsed all T1 worker child-result JSON files and the T1 integration JSON.
4. Parsed all T1 report JSON files and checked report hashes.
5. Used explicit local Git binary at `C:\Program Files\Git\cmd\git.exe` to
   inspect HEAD, status, log, ancestry, and T1 commit-range diff.
6. Checked Python availability and recorded fresh-test limitation.
7. Performed manual active sheetmetal-v1 frozen-manifest hash verification.
8. Wrote only the three allowed audit output files.
