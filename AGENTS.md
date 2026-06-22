# PLC Panel Drawing Workflow Agents

This repository is governed by `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`.
Use that master specification, accepted repository artifacts, approved source
manifests, and signed human decisions as authority.

## Product Boundary

The product goal is a private Custom GPT package and local evaluation harness
that generate and grade:

- `01_生管課用圖_<工程編號>.pdf`
- `02_鈑金施工圖_<工程編號>.pdf`
- `03_沖孔施工圖_<工程編號>.pdf`

All three PDFs must be rendered from one canonical `drawing_model`.

## Source Boundary

Source roots in `docs/SOURCE_ROOTS.md` are read-only. Do not rename, move,
overwrite, delete, or extract files back into those locations.

Generators may only see positive generator bundles built from approved current
project Excel files and approved worksheets, plus frozen reusable Knowledge,
approved rules, schemas, renderers, and explicit current user corrections.

Always forbidden to generators: `生管文件`, `電機施工圖`, completed target
drawings, modified target drawings, and derivatives including extracted text,
filenames, hashes, thumbnails, reviewer findings, scores, references, and
expected answers.

## Execution Rules

- The coordinator alone applies shared workflow artifacts.
- Parallel workers write only inside assigned output paths.
- Every child run needs a task brief, visible-file manifest, schema-valid
  result file, trajectory, immutable hashes, and task-registry row.
- Reject malformed, prose-only, partial, stale-hash, or unhashed results.
- Treat completed drawings as adjudicated evidence, not perfect ground truth.
- Never declare `PRODUCTION_APPROVED`; the highest automated status is
  `READY_FOR_PRIVATE_PREVIEW`.

## Change Rules

Improvements are proposal-first: add the regression test before the fix, bind
the proposal to current target hashes, provide exact diff and rollback, require
independent review, and let the coordinator apply only accepted changes.

Do not alter frozen releases, frozen graders, prior run evidence, or immutable
source roots.

