# Reference Vault Boundary Spec

Status: `ACCEPTED`

Decision: `D-0018`

Version: `reference_vault_boundary_v1`

## Purpose

Reference-vault processing exists only to decide whether completed reviewer
references are available for evaluation. It does not create generator input,
source-review input, production Knowledge, drawing rules, or optimization
evidence.

## Separate Boundaries

Generator input eligibility and completed reviewer-reference eligibility are
separate decisions.

Generator inputs remain positive-allowlist only. The generator may receive
approved current-project Excel-derived sanitized artifacts, approved reusable
Knowledge, approved schemas, approved rules, and explicit current user
corrections. It must never receive completed target drawings, modified target
drawings, production-control files, electrical drawings, reviewer evidence,
reference manifests, extracted reference text, reference filenames, reference
paths, reference hashes, thumbnails, crops, score reports, or expected answers.

Reviewer-reference eligibility may inspect completed target drawing candidates
inside an isolated reference vault. A completed target PDF may qualify as
reviewer evidence even when it is stored beneath a generator-forbidden folder,
inside a revision folder, inside a nested completed-output package, or inside a
combined multipage PDF, provided that page-level classification confirms the
document itself is one of the required target outputs and confirms project
identity.

## Required Isolation

Reference-vault processes may read completed-reference PDF content only for:

- document-role classification;
- page-level target-output classification;
- project-identity confirmation;
- revision and supersession resolution;
- effective completed-reference-set construction.

Reference-vault outputs must not include:

- drawing dimensions;
- component names or equipment details;
- quantities;
- layout instructions;
- hidden expected answers;
- reference-derived design rules;
- raw extracted text;
- rendered pages, thumbnails, or title-block crops;
- absolute private paths.

## Folder Rules

Folder names may provide context but may not decide a target output by
themselves.

A target-like PDF beneath a production-control folder can be reviewer evidence
only when the PDF page content confirms target-output role and project identity.

A target-like PDF beneath an electrical folder can be reviewer evidence only
when independent page-level content confirms target-output role and project
identity. Ordinary electrical drawings, wiring diagrams, and single-line
diagrams remain non-target reviewer references even if they visually resemble a
panel drawing.

Exact duplicate files must be recorded as duplicates and must not count as
separate output types. Near duplicates must be reviewed as revision or
supersession candidates, not as automatic missing-type evidence.

## Generator-Facing Exposure

Source-review and generator systems may receive at most:

- project ID;
- eligibility boolean;
- verified all-three status;
- target output types present;
- effective revision status when needed by the evaluator gate.

Generator-facing bundles must not include neutral reference file IDs, reference
manifest hashes, reference filenames, reference paths, rendered evidence, or
reference content unless a separately accepted contamination checker requires a
minimal boolean.

## Regression Requirements

The v3 regression suite must prove that:

- a valid target PDF under a production-control folder can be used as reviewer
  evidence;
- the same PDF never enters a generator bundle;
- an ordinary electrical drawing under an electrical folder is not misclassified
  as a target output;
- an exact duplicate does not create a false three-output set;
- reference paths and filenames are not leaked to generator-facing manifests.
