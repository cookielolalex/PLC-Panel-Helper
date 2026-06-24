# Topology Sizing Rule Recovery

Task: `SMV1-T1-TOPOLOGY-SIZING-RULE-RECOVERY`

Status: `SAFE_UNRESOLVED_NO_CODE_CHANGE`

No code, rule, or synthetic fixture was added. The repository has authority to
use approved topology, sizing, clearance, mounting, thermal, ventilation, and
spare-space rules, but the committed rule namespace does not contain approved
rule values or standard libraries for those families. Adding deterministic
defaults here would invent fabrication facts.

## Evidence Reviewed

- Governing workflow files, sheetmetal-v1 architecture, authority matrix,
  topology/sizing/placement protocol, schemas, `scripts/sheetmetal_v1.py`, and
  `scripts/run_tests.py`.
- Committed neutral topology audit summaries: implementation checkpoint,
  topology sizing summary, placement validation summary, generator freeze,
  evaluator metrics, independent audit, hard gates, determinism, coordinator
  addendum, audit manifest, and T0 child result.
- Local rule/fixture namespace: source authority profile, bootstrap no
  dimension-invention rule, synthetic accessory rule, panel definition schema,
  and component type schema.

Forbidden source roots, `.private`, completed drawings, modified drawings,
post-design files, reference crops/images/OCR/title blocks, customer drawing
files, public web, and the forbidden screening script were not opened.

## Coverage Decision

The existing implementation safely supports explicit panel definitions and
passes through explicit mounting surfaces, compartments, doors, mounting
plates, and dimensions when source-backed. It also blocks unsupported exact
cabinet sizes and preserves safe unresolved statuses.

Requested recovery families remain unresolved:

- `enclosure_candidates`: no approved standard cabinet library or candidate
  selection rule.
- `mounting_surfaces`: no approved inference rule or verified mounting surface
  library.
- `compartments`: no approved compartment rule.
- `doors`: no approved door topology rule.
- `plates`: no approved mounting plate rule.
- `wiring_allowance`: no approved wiring or cable-bend allowance policy.
- `access_clearance`: no approved global clearance rule or component-class
  clearance library.
- `thermal_ventilation_requirements`: no approved thermal or ventilation
  region rule.
- `spare_space_policy`: no approved spare-space policy or supported panel-fill
  calculation denominator.

## Verification

- Full tests: `PASS` via bundled Python and `scripts/run_tests.py`.
- Legacy baseline-024 scoped freeze: `PASS`.
- Active sheetmetal-v1 scoped freeze: `PASS`.
- Topology/sizing/placement scoped freeze: `PASS`.
- JSON parse validation: `PASS`.

The test suite uses existing synthetic harness outputs under `tmp`; this
recovery did not generate a customer drawing, PDF, DXF, or DWG.

## Next Action

`COORDINATOR_REVIEW_BLOCKER_TAXONOMY_AND_AUTHORIZE_SOURCE_BACKED_RULE_LIBRARY_OR_KEEP_T1_UNRESOLVED`
