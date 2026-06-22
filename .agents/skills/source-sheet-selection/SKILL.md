---
name: source-sheet-selection
description: Classify candidate Excel files and worksheets for generator eligibility.
---
# Source Sheet Selection

Use when classifying candidate Excel files or worksheets for generator
eligibility.

Do not use for rendering, grading, or reference review.

Rules:

- Prefer positive allowlists over path-name exclusions.
- Inventory visible, hidden, and very-hidden sheets.
- Record project identity, customer, revision/date markers, formulas, named
  ranges, print areas, cached values, and external links.
- Mark conflicting or insufficient identity as `HUMAN_REVIEW_REQUIRED`.
- Mark stale current-project conflicts as `STALE_TEMPLATE_SHEET`.
- Any `生管文件`, `電機施工圖`, target drawing, modified target drawing, or
  derivative is generator-forbidden.

