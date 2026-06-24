# Private Workspace Boundary

Status: `PASS`.

Task: `ONE_PROJECT_COMPONENT_REGISTER_AND_GRAPH_CALIBRATION`.

Candidate: `1110101`.

The private project workspace for component facts and graph contents is:

`.private/sheetmetal-v1/1110101/`

The repository now ignores `.private/` before any project-specific component
facts are written there. This boundary is covered by
`test_sheetmetal_v1_private_workspace_boundary`, which verifies that Git
ignores `.private/sheetmetal-v1/1110101/private-output-probe.json` and that no
`.private` path is tracked.

Private workspace contents remain non-committable and must not be printed to
stdout, stderr, trajectories, or committed reports.
