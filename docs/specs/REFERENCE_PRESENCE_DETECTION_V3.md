# Reference Presence Detection V3

Status: `ACCEPTED`

Decision: `D-0018`

Detector version: `target_output_detection_v3_page_content_isolated`

## Objective

Version 3 determines whether a project has an effective completed reference set
containing all three target outputs:

- `PRODUCTION_DRAWING`;
- `SHEETMETAL_DRAWING`;
- `PUNCH_DRAWING`.

The detector operates at page level inside an isolated reference vault. It
separates reviewer-reference eligibility from generator input eligibility and
does not weaken generator isolation.

## Required Pipeline

For each candidate PDF, v3 must:

1. verify the source hash and project association;
2. read PDF metadata;
3. extract embedded text from every page when available;
4. record page dimensions and orientation;
5. render every page locally;
6. create temporary full-page images;
7. create temporary title-block-region crops;
8. calculate neutral visual signatures;
9. classify each page separately;
10. group pages into effective target-output sets;
11. resolve duplicates, revisions, and supersession;
12. delete temporary renders and crops after classification and audit.

The preferred renderer is PyMuPDF when available. In the current bundled
runtime PyMuPDF is absent, so the accepted local renderer is Poppler
`pdftoppm`, discovered from the bundled Codex runtime. The detector records the
renderer used in every audit.

Temporary renders must live only beneath:

`tmp/reference_detection_v3/<task_id>/`

No temporary render, thumbnail, crop, OCR output, raw drawing text, completed
drawing content, or private path may be committed.

## Page Classifications

Allowed page classifications:

- `PRODUCTION_DRAWING`
- `SHEETMETAL_DRAWING`
- `PUNCH_DRAWING`
- `ELECTRICAL_DRAWING`
- `SOURCE_DOCUMENT`
- `COVER_OR_INDEX`
- `REVISION_NOTICE`
- `OTHER_DRAWING`
- `UNCLASSIFIED`

Folder names and filename aliases are supporting signals only. No project may
become verified all-three from folder names alone or from filename aliases alone
when project identity or revision is ambiguous.

## Effective Reference Set

An effective reference set records only minimized presence data:

- neutral file ID;
- file SHA-256;
- page number or page range;
- detected target type;
- project identity status;
- panel or sheet identity when safely determinable without storing drawing
  details;
- revision identity;
- supersedes relationship;
- current/effective status;
- classification method;
- confidence;
- evidence IDs.

It must not store extracted dimensions, equipment information, quantities,
layout descriptions, or drawing-specific expected values.

## Verification Statuses

Allowed project statuses:

- `VERIFIED_ALL_THREE_BY_CONTENT`
- `VERIFIED_ALL_THREE_COMBINED_PACKAGE`
- `VERIFIED_ALL_THREE_WITH_PAGE_SUPERSESSION`
- `PARTIAL_REFERENCE_SET`
- `AMBIGUOUS_REFERENCE_SET`
- `NO_REFERENCE_SET`
- `INACCESSIBLE_REFERENCE_SET`

Promotion requires all three target types, confirmed project identity, effective
pages identified, revision conflicts resolved, no target output inferred only
from folder name, no electrical drawing misused as target evidence, no duplicate
counted as a separate output type, independent classifiers agree when required,
and schema-valid minimized records.

## Data Minimization

Reference-vault outputs may be used by source screening only as eligibility
evidence. Source-review agents and generators remain reference-blind. Generator
bundles must not receive reference file IDs, reference filenames, reference
paths, reference hashes, page renders, crops, extracted text, reviewer findings,
scores, or expected answers.
