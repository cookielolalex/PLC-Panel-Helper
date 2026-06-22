---
name: grading-and-reference-adjudication
description: Grade one frozen project with source-availability-aware reference adjudication.
---
# Grading And Reference Adjudication

Trigger: grade one frozen generated project with reference-availability
adjudication.

Permitted inputs: frozen generated artifacts, allowed original input evidence,
completed references in reviewer workspace, deterministic comparison evidence,
grading rubric, reference-adjudication rules, and synthetic examples.

Forbidden inputs: reference evidence in generator workspace, unfrozen generated
artifacts, optimization proposals, held-out answers outside scope, and
production approval claims.

Deterministic prerequisites: reference access occurs only after output freeze;
comparison evidence is readable; score schema is current; source availability
classes are available.

Result schema: `schemas/grading_result.schema.json` plus reviewer result
schema.

Fail-closed conditions: unsupported invented fabrication values, stale-source
use, reference leakage, missing validity fields, score-schema failure, or
critical comparison evidence missing.

Completion criteria: validity, quality score, scorable coverage, confidence,
rubric-dimension scores, output-type scores, critical/high findings, run
metadata, and comparison limitations are recorded.

Synthetic examples only: a synthetic unavailable reference value does not
penalize a safe TBD; a synthetic invented fabrication dimension is penalized.
