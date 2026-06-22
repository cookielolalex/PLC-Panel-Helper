# Generator Eligibility Summary

No real project is generator-eligible yet.

After D-0003, the approved project root was inventoried read-only. File-level
classification found:

- `FORBIDDEN`: 5,001 files
- `HUMAN_REVIEW_REQUIRED`: 2,399 files
- `ALLOWED`: 0 files

Worksheet-level classification found:

- `FORBIDDEN`: 2,092 worksheet/index rows
- `HUMAN_REVIEW_REQUIRED`: 2,139 worksheet/index rows
- `ALLOWED`: 0 worksheet/index rows

Stale/hidden/review signals:

- `FORBIDDEN_SOURCE`: 2,067
- `HUMAN_REVIEW_REQUIRED` for legacy `.xls` parser or equivalent review: 1,466
- `INSUFFICIENT_IDENTITY`: 617
- `HIDDEN_SHEET_REVIEW_REQUIRED`: 29
- `CURRENT_PROJECT_ID_MATCH`: 27
- `STALE_TEMPLATE_SHEET`: 25

The generator bundle builder must continue to fail closed until a project has
explicitly approved files and worksheets in a positive manifest.
