# Classification Validation

Phase 0 validation scope is synthetic only.

The classifier must treat any path, file, archive member, or worksheet matching
`生管文件`, `電機施工圖`, completed target drawing aliases, modified target
drawings, or target derivatives as generator-forbidden.

Read-only inventory validation after D-0003:

- Target-like PDFs under `電機施工圖` paths were classified as forbidden
  electrical drawings.
- `生管文件` paths were classified as forbidden production-control files.
- Completed target drawing labels were classified as completed reference roles,
  not generator evidence.
- Legacy `.xls` workbooks were not parsed as if safe; they were marked
  `HUMAN_REVIEW_REQUIRED` with parser-required status.
- Hidden or insufficient-identity sheets were queued for review.

Known limitation: the bootstrap classifier is path/label and workbook
metadata/sample based. It does not OCR or parse completed PDF content, and it
does not yet classify CAD/vendor catalog roots beyond files found under the
approved project root.
