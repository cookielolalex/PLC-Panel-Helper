# Architecture

The workflow is a guarded pipeline:

1. Read-only source inventory and worksheet adjudication.
2. Positive generator bundle construction.
3. Leakage and contamination scan.
4. `job_spec_<工程編號>.json` with cell-level provenance.
5. One canonical `drawing_model_<工程編號>.json`.
6. Three deterministic PDF renderers.
7. Cross-PDF validation and freeze/hash.
8. Reference sheet manifest and adjudication after output freeze.
9. Deterministic grading, independent review, portfolio aggregation.
10. Proposal-first optimization with regression tests and rollback.

No backward edge may expose references, target hashes, scores, reviewer
findings, or expected answers to a generator run being graded.

