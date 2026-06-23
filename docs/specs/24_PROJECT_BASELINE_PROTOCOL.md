# 24-Project Baseline Protocol

Status: `FROZEN_PROTOCOL_V1`

Cycle: `cycle-000`

Frozen on: 2026-06-23

Random seed: `BASELINE024-CYCLE000-20260623`

Evaluator: `plc_layout_evaluator_v2_sensitivity`

## Boundary

This protocol freezes the rules for the first 24-project development baseline.
It does not authorize drawing workflow optimization and does not change the
accepted Instructions, production Knowledge, extraction logic, job_spec schema,
renderer behavior, source-classification behavior, validation behavior, grading
weights, or tolerance profile.

The six calibration anchors remain:

- `1110101`
- `1110104`
- `1110204`
- `1110205`
- `1110405`
- `1110410`

The remaining eighteen projects must be approved through autonomous
evaluation-only source approval in Phase C. Do not use `1110102` unless its
original bundle-verification defect is corrected, regression tested, and
independently audited.

## Cohort Target

The final cohort must contain exactly 24 project IDs:

- 6 existing calibrated anchor projects;
- 18 additional independently approved development projects;
- approximately 12 representative ordinary projects;
- approximately 6 high-conflict or high-uncertainty projects;
- approximately 3 uncommon panel/template families;
- approximately 3 randomly selected eligible projects.

The existing six anchors count toward these totals.

Related project families, copied jobs, customer templates, revisions, and near
duplicates must stay in one cohort. Near duplicates may be replaced only when a
safe eligible alternative exists under the same frozen selection rules.

## Exclusions

Exclude:

- checkpoint-validation projects;
- final-held-out projects;
- projects used as completed examples in production Knowledge;
- inaccessible OneDrive cases;
- projects without all three completed target outputs;
- projects whose permitted sources cannot be isolated safely;
- projects with completed target output, modified target output, reviewer
  evidence, score reports, expected answers, thumbnails, or target hashes in a
  generator-facing workspace.

Selection must occur without inspecting completed-reference contents.

## Source Approval

Additional projects must pass:

1. deterministic prefiltering;
2. four independent specialist reviews;
3. unanimous source quorum;
4. source adjudication;
5. sanitized bundle construction;
6. bundle isolation and hash verification;
7. independent source-bundle audit.

Any disagreement becomes `QUARANTINED`. Unsupported parser formats become
`PARSER_REQUIRED` until deterministic parser support is added, tested, and
audited.

## Frozen Runtime Policy

Use the same:

- private evaluation-only Custom GPT package state;
- `gpt-config/INSTRUCTIONS.md`;
- production Knowledge manifest;
- schemas;
- deterministic renderer;
- validators;
- source guard policy;
- evaluator `plc_layout_evaluator_v2_sensitivity`;
- tolerance profile `plc_layout_tolerances_v1`;
- generator task wording;
- reviewer task wording;
- requested model policy inherited through `codex_proxy`;
- local no-external-transmission policy.

## Generation And Review Plan

Run one fresh standardized generation for every project. The six calibration
runs remain calibration evidence and do not replace fresh cycle-000 baseline
runs.

Process four waves of six. For each wave, freeze generated outputs before any
completed references are opened in reviewer workspaces. Never allow reference
paths, hashes, reviewer findings, or scores back into generator workspaces.

After all 24 primary reviews, select six blind secondary reviews using the
frozen random seed:

- one from each generation wave;
- one low-coverage case;
- one relatively high-coverage case;
- one complex or revision-sensitive case;
- fill overlaps with another distinct family.

Continue only if reviewer agreement meets the frozen rubric-calibration gates.

## Baseline Stop Condition

After portfolio aggregation and independent audit, stop with either:

- `FIRST_24_PROJECT_BASELINE_COMPLETE - OPTIMIZATION_READY`
- the precise failed gate.

Do not implement cycle-001 or any optimization in this protocol.
