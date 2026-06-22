---
name: completed-work-comparison
description: Compare frozen generated artifacts to completed references after freeze.
---
# Completed Work Comparison

Trigger: compare frozen generated artifacts to completed references after
generation freeze.

Permitted inputs: frozen generated artifacts, completed references in a separate
reviewer workspace, deterministic render/registration evidence, effective
sheet/revision manifest, grading rubric, and synthetic examples.

Forbidden inputs: completed references before generated artifact freeze,
reference evidence inside generator workspace, generator prompts, unfrozen
outputs, and held-out answers outside the selected case.

Deterministic prerequisites: generated artifacts are validated, frozen, hashed,
and leakage-scanned; reviewer workspace is separate; reference manifest is
constructed conservatively.

Result schema: `schemas/comparison_metrics.schema.json` and reviewer result
schema.

Fail-closed conditions: unreadable PDF, unreliable registration treated as
exact, missing reference provenance, reference access before freeze, or
contamination between generator and reviewer workspaces.

Completion criteria: pairings, registration confidence, metrics, overlays when
safe, limitations, and uncertain pairings are recorded.

Synthetic examples only: a synthetic generated PDF and reference PDF can be
paired; an unregistered synthetic overlay is marked uncertain.
