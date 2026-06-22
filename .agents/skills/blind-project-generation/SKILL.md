---
name: blind-project-generation
description: Run blind historical mock generation from a verified ALLOWED_EVAL bundle.
---
# Blind Project Generation

Trigger: run one blind historical mock generation from a verified
`ALLOWED_EVAL` bundle.

Permitted inputs: verified sanitized bundle, frozen Instructions, frozen
production Knowledge, approved schemas, approved renderer/validator tools,
task contract, and synthetic examples.

Forbidden inputs: original project trees, completed target PDFs, target
filenames, target hashes, thumbnails, reviewer findings, comparison evidence,
expected dimensions, scores, and project-specific completed decisions.

Deterministic prerequisites: codex_proxy synthetic gate passed; generator
allowlist and visible-file manifest are frozen; contamination scan passed;
release/workflow hashes are recorded.

Result schema: current generation complete, job spec, drawing model, and
validation schemas.

Fail-closed conditions: contaminated input, missing manifest, schema failure,
unsupported critical value invented as fact, reference exposure, path escape,
non-fresh session, missing model recording, or artifact mutation after freeze.

Completion criteria: generator attempts three PDFs, writes job spec,
provenance, validation and completion records, closes process, and preserves
failed runs under immutable run IDs.

Synthetic examples only: a synthetic one-panel bundle may produce TBD-marked
draft PDFs; a synthetic forbidden sentinel aborts before generation.
