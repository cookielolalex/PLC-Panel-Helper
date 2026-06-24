# Sheetmetal-First Modular Architecture

Status: ACCEPTED FOUNDATION V1.

Decision: V1 is sheetmetal-first. The historical three-output workflow remains
frozen evidence, but it is no longer the controlling qualification objective
for the first trial. Production-control and punch renderers may be added later
only as downstream projections of the same frozen canonical panel model.

## Active Goal

The canonical panel model is the central product. The first runnable foundation
builds and validates:

1. source-role and chronology classification;
2. normalized evidence facts;
3. canonical component register;
4. panel assignment;
5. typed relationship graph;
6. accessory and cutout rule outputs;
7. panel topology and dimension model;
8. constraint-based placement validation;
9. canonical sheet-metal drawing model;
10. drawing provenance map.

The sheet-metal PDF renderer is intentionally not productionized in this
migration task. No real customer sheet-metal drawing is generated.

## Required Pipeline

Approved project sources feed normalized facts. Normalized facts feed the
component register. Panel assignment consumes component instances but does not
place them. Placement consumes panel-specific component sets and panel topology.
The drawing model consumes topology, assignment, placement, cutouts, dimensions,
unresolved facts, and provenance.

Future downstream renderers must consume the same canonical model:

- production-control renderer: assembly, arrangement, and production-control
  views;
- punch renderer: hole and cutout projections.

They must not independently re-extract components, assign panels, infer
dimensions, or recalculate geometry.

## Operating Modes

`SOURCE_MODE_A_INVENTORY_ONLY` uses contract, material, procurement,
customer-supplied, and approved panel-allocation sources. It may build
inventory, quantity reconciliation, panel candidates, and physical accessory
requirements supported by rules. Unsupported functional relationships remain
`UNVERIFIED`.

`SOURCE_MODE_B_FUNCTIONAL_SOURCE_ENABLED` may add circuits, protection,
control, PLC I/O groups, loops, and interlocks only after an accepted
repository decision or explicit current authorization approves a functional
engineering source.

## Legacy Relationship

The old detector-v4.1 track and the 13 legacy `ALLOWED_EVAL` projects remain
historical evidence under `LEGACY_THREE_OUTPUT_ALLOWED_EVAL`. They are not
grandfathered into `SHEETMETAL_ALLOWED_EVAL`.

New artifacts use separate namespaces:

- `reports/sheetmetal-v1/`
- `manifests/sheetmetal-v1/`
- `evals/sheetmetal-v1/`
- `orchestration/sheetmetal-v1/`

