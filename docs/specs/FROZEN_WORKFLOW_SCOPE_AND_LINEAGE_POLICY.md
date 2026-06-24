# Frozen Workflow Scope And Lineage Policy

Status: ACCEPTED.

Decision: `D-0026`.

## Purpose

Frozen-workflow manifests are not global repository snapshots. They are
scope-bound evidence artifacts that prove a named workflow was reproducible at
an explicit commit with an explicit file list and hash algorithm.

## Policy

1. A frozen-workflow manifest is bound to:
   - workflow scope;
   - project goal;
   - anchor commit;
   - explicit file list;
   - verification algorithm.

2. A later accepted goal migration may legitimately change a workflow file.

3. Such a change does not invalidate historical evidence when:
   - the old manifest still reproduces at its historical anchor;
   - the new workflow has its own manifest;
   - the migration is recorded in the decision ledger.

4. Current-file verification may be used only for the active workflow scope.

5. Historical verification must be performed against the historical anchor.

6. No manifest may silently inherit files from another scope.

7. A mismatch must never be waived merely because a change was intentional; it
   must be represented by a new scoped manifest.

## Active Scopes

`LEGACY_BASELINE_024` reproduces and verifies the historical three-output
baseline-024 workflow. Its manifest is
`evals/baseline-024/frozen_workflow_manifest.json`. Its historical anchor is
resolved by provenance attestation, not by comparing the current working tree.

`SHEETMETAL_V1_ACTIVE` freezes the active modular sheet-metal workflow for
one-project calibration. Its manifest is
`evals/sheetmetal-v1/frozen_workflow_manifest.json`. Its verification target is
the accepted sheetmetal-v1 workflow anchor and current tracked files descended
from that anchor.

## Boundaries

The legacy baseline-024 manifest remains byte-for-byte preserved as historical
evidence. Its expected `AGENTS.md` hash is the legacy three-output workflow
hash and must not be compared to the current sheetmetal-v1 `AGENTS.md`.

The sheetmetal-v1 manifest supersedes no historical manifest. It represents a
new active workflow scope created after decision `D-0025`.

Dynamic state and evidence files are excluded from workflow freezes. They may
change as phases progress and must be verified by phase-specific evidence, not
by stable workflow semantics manifests.
