# Source Role And Chronology Policy

Status: ACCEPTED FOUNDATION V1.

No source document receives global precedence. Authority is assigned by fact
type and chronology. Source documents are never modified; normalized facts are
written into new canonical artifacts.

## Source Roles

- `CONTRACT_REQUIREMENT`
- `MATERIAL_REQUIREMENT`
- `PROCUREMENT_EVIDENCE`
- `CUSTOMER_SUPPLIED_LIST`
- `APPROVED_FUNCTIONAL_ENGINEERING_SOURCE`
- `PANEL_ALLOCATION_SOURCE`
- `POST_DESIGN_ALLOCATION_LABEL`
- `COMPLETED_SHEETMETAL_REFERENCE`
- `DERIVED_PRODUCTION_REFERENCE`
- `DERIVED_PUNCH_REFERENCE`
- `UNKNOWN_OR_QUARANTINED`

## Chronology Classes

- `PRE_DESIGN`: prepared before panel assignment, sizing, placement, or
  completed drawings.
- `DURING_DESIGN`: prepared during active design and accepted as an input by
  explicit policy.
- `POST_DESIGN`: prepared from completed drawings or after design decisions.
- `AFTER_COMPLETION`: completed references or derivatives.
- `UNKNOWN`: insufficient evidence; cannot provide critical generator facts.

## Generator Eligibility

Generator-eligible roles are:

- `CONTRACT_REQUIREMENT`
- `MATERIAL_REQUIREMENT`
- `PROCUREMENT_EVIDENCE`
- `CUSTOMER_SUPPLIED_LIST`
- `APPROVED_FUNCTIONAL_ENGINEERING_SOURCE`
- `PANEL_ALLOCATION_SOURCE`

`POST_DESIGN_ALLOCATION_LABEL`, completed references, derived references, and
unknown/quarantined sources are forbidden to generator input. They may be kept
as evaluation labels or adjudicated reference evidence after output freeze.

## Mandatory Separations

Quantities are stored separately:

- `required_qty`
- `ordered_qty`
- `received_qty`
- `allocated_qty`
- `installed_qty`

Procurement quantity must never silently replace required quantity.

Panel assignment is separate from placement. A source may support assignment
without supporting coordinates, dimensions, or cutouts.

## Conflict Handling

When critical sources conflict, preserve all competing facts and mark the field
`CONFLICT`. Do not produce a resolved value from completed references, filename
intuition, modified time, or procurement evidence unless that fact type gives
the source authority.

