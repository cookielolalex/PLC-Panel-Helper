# Generator Input Policy

Generator workspaces are built from a positive manifest. The generator must
fail closed if the manifest is missing, invalid, stale, contaminated, or does
not match the visible files.

Allowed project-specific evidence:

- approved current-project Excel workbooks;
- approved worksheets within those workbooks;
- explicit current user corrections recorded in a signed decision artifact;
- approved deterministic rule outputs with rule IDs.

Always forbidden:

- `生管文件`;
- `電機施工圖`;
- completed or modified target drawings;
- derivatives of forbidden references including extracted text, filenames,
  target hashes, page counts, thumbnails, reviewer findings, scores, and
  expected answers.

