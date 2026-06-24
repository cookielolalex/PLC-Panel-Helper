# SMV1 Source/Rule Approval Proposal

Status: `PROPOSED_ONLY_NOT_APPLIED`

Task ID: `SMV1-SOURCE-RULE-APPROVAL-PROPOSAL`

Recommended next action: `RUN_INDEPENDENT_SOURCE_RULE_PROPOSAL_REVIEW`

## Purpose

T1 recovered no additional assignment, geometry, topology, sizing, or
placement coverage because no approved source or approved rule authority exists
for those fact families. This proposal defines reviewable authority paths. It
does not approve, implement, or apply any source, geometry, sizing, topology,
clearance, or placement rule.

No source roots, `.private` artifacts, completed references, post-design files,
customer PDFs, DXFs, DWGs, or public web sources were opened for this proposal.

## Bound Evidence

| Evidence | SHA-256 |
|---|---|
| T1 independent audit | `FA5E9697047683BDB8850A66C014F40E42C83A3D02EF9ED8728AD5ADC6AE0221` |
| T1 coordinator addendum | `DE9B58645669E6002ACCFC9DA18410B76F6FB198ED40C1B6F129B77407CBC956` |
| T1 integration summary | `9B8A9D6EB8F98F79E69B82A3F3A6F91EC20F1FF24CB3C0E4AF34821B858137EF` |
| Source fact authority matrix | `72920B19759334A49323B5BE63A2B6E59B6E073D08406D0D70B5534EF67B0FBC` |
| Source role and chronology policy | `67F25DEA549626A2ECF72DB657D66276FDDC44F6CC698ECD5728E86E25863543` |
| Sheetmetal qualification policy | `05EFAB1DE2FE03F845991E2E3010CD2856F4523DAA25AF55441B9DEE6485B622` |
| Topology/sizing/placement protocol | `9FA9E4A7E640B7D7481C34A4A5D992C822B7EE0EA46918307CB69A489D278454` |

## Proposed Authority Lanes

### Lane A: Panel Allocation Source

Propose a source-review branch to identify whether any chronologically valid,
generator-eligible `PANEL_ALLOCATION_SOURCE` exists for candidate `1110101` or
future sheetmetal-v1 cases.

Approval preconditions:

- deterministic source validation passes;
- role is `PANEL_ALLOCATION_SOURCE`;
- chronology is `PRE_DESIGN` or explicitly accepted `DURING_DESIGN`;
- file hash and worksheet fingerprint are current;
- completed-reference, derived-reference, post-design, stale, cross-project,
  hidden, macro, external-link, and forbidden dependency checks pass;
- four independent source reviewers return unanimous approval;
- separate adjudication, sanitized-bundle verification, and independent audit
  pass.

Rejected shortcut: infer assignments from historical sheet-metal drawings,
filenames, worksheet labels, component co-occurrence, procurement quantities, or
completed-reference layout.

### Lane B: Component Geometry Authority

Propose either a verified component-library approval path or a conservative
generic-envelope rule path.

Approval preconditions:

- source/library authority is explicitly approved for footprint and mounting
  geometry;
- model or family matching is deterministic and provenance-bearing;
- generic envelopes, if proposed, are explicitly conservative and domain
  approved;
- every geometry result records status as `VERIFIED_MODEL_GEOMETRY`,
  `APPROVED_GENERIC_CONSERVATIVE_ENVELOPE`, `GEOMETRY_MISSING`,
  `GEOMETRY_CONFLICT`, or `NOT_APPLICABLE`;
- no private model identifier is sent to public lookup;
- no catalog, CAD, or library candidate is used until source and leakage review
  passes.

Rejected shortcut: promote geometry from symbol names, completed drawings,
private model lookup on the public web, or synthetic fixtures alone.

### Lane C: Topology, Sizing, And Placement Rules

Propose a domain-rule approval path for reusable topology and sizing policy:
standard cabinet candidates, mounting surfaces, compartments, doors, mounting
plates, wiring allowances, cable bend allowances, access clearances,
component-class clearances, thermal/ventilation regions, spare-space policy,
and supported fill-denominator calculations.

Approval preconditions:

- each rule family has a stable rule id and version;
- each rule states its source of authority: explicit human decision, accepted
  company default, verified reusable library, or future approved source;
- rules are generic or project-parametric and not copied from completed
  references;
- every rule output carries provenance and confidence;
- unresolved facts remain `UNVERIFIED`, `TBD`, `CONFLICT`, or
  `HUMAN_REVIEW_REQUIRED` rather than guessed.

Rejected shortcut: choose exact cabinet size, surfaces, doors, compartments,
coordinates, clearances, thermal allowances, or spare-space values from
completed historical drawings or private intuition.

## Test-Before-Fix Requirements

Before any accepted proposal is implemented, add failing synthetic regression
coverage for:

- a valid `PANEL_ALLOCATION_SOURCE` assignment path;
- rejection of post-design allocation labels and completed-reference
  assignment signals;
- component geometry resolution from a verified library entry;
- conservative generic envelope behavior with provenance;
- geometry conflict and missing-geometry preservation;
- approved standard-cabinet candidate selection without exact customer-copying;
- clearance, containment, overlap, and mounting-surface validation;
- topology/sizing zero-denominator handling;
- no customer PDF/DXF/DWG generation during recovery;
- no private transmission and no tracked `.private` artifacts.

## Intended Diff Scope If Accepted

An accepted implementation may touch only the explicitly approved subset of:

- `docs/specs/` for accepted source/rule protocol amendments;
- `rules/sheetmetal-v1/` for approved versioned rule files;
- `schemas/` only if a new rule schema is required;
- `scripts/sheetmetal_v1.py`;
- `scripts/run_tests.py`;
- `evals/sheetmetal-v1/frozen_workflow_manifest.json`;
- neutral reports and manifests under `reports/sheetmetal-v1/` and
  `manifests/sheetmetal-v1/`.

It must not modify frozen releases, frozen graders, source roots, completed
references, `.private` artifacts, or legacy historical evidence.

## Rollback

Rollback is a clean revert of the accepted implementation commit(s), plus
removal of any proposal-derived neutral reports and regeneration of active
frozen-workflow manifests from the previous accepted commit. Private workspace
artifacts remain ignored and must not be staged.

## Independent Review

Before implementation, dispatch an independent proposal review to verify:

- the proposal is source/rule authority only;
- no forbidden evidence was opened;
- no implementation was smuggled in;
- each lane has a valid approval path;
- rejected shortcuts are complete enough to prevent no-invention violations;
- test-before-fix requirements are sufficient;
- rollback is exact and bounded.

If the proposal is rejected or no authority source can be approved, the next
coordinator branch is terminal-candidate review for
`STRUCTURAL_SOURCE_INSUFFICIENCY` or `FABRICATION_DOMAIN_DECISION_REQUIRED`.
