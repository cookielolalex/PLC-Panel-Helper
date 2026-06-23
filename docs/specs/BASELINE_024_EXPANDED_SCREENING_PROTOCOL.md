# Baseline-024 Expanded Screening Protocol

Status: `EXPANDED_DISCOVERY_AUTHORIZED`

Decision: `D-0017`

Date: 2026-06-23

Baseline: `baseline-024-cycle-000`

## Amendment Scope

The prior twenty-project metadata-only discovery pool is no longer a hard
candidate-discovery limit for baseline-024 source backfill.

Candidate discovery may inspect the full approved development inventory under
`SRC-ALL-PROJECTS`, subject to existing source-root, cohort, family, reference
isolation, source-quorum, and bundle-verification rules.

This amendment exists only to find eleven additional verified `ALLOWED_EVAL`
projects, plus up to three reserve projects when available.

## Unchanged Gates

This protocol does not supersede or weaken:

- source immutability;
- source-root restrictions;
- positive source allowlisting;
- evaluation-only approval quorum;
- reference isolation;
- cohort isolation;
- checkpoint-validation and final-held-out protection;
- parser requirements;
- sanitized-bundle verification;
- independent auditing;
- frozen workflow requirements;
- grading rules;
- no-invention requirements.

## Required Expanded Screening

Expanded screening must:

1. reconcile the full project universe beneath `SRC-ALL-PROJECTS`;
2. improve completed-target presence detection without exposing reference
   contents to source-review agents or generators;
3. create a new ranked expanded candidate registry without overwriting prior
   candidate evidence;
4. preserve all previous accepted, rejected, quarantined, and no-bundle results;
5. process source-screening candidates in six-project waves;
6. produce sanitized bundles only after unanimous quorum, source adjudication,
   deterministic bundle verification, and independent audit;
7. stop before generation unless exactly twenty-four verified `ALLOWED_EVAL`
   projects are frozen and the expanded source-screening audit passes.

## Generation Boundary

No cycle-000 baseline generation is authorized by this amendment alone.

Generation may begin only after:

- the original thirteen verified projects remain valid;
- at least eleven additional projects reach `ALLOWED_EVAL`;
- exactly twenty-four projects are selected and frozen;
- source-bundle and cohort audits pass;
- no completed reference material has entered a generator workspace.
