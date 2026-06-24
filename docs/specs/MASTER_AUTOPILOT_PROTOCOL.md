# Master Autopilot Protocol

Status: ACTIVE COORDINATOR PROTOCOL.

Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`.

This protocol defines the durable root-coordinator operating model for
advancing the sheetmetal-first modular panel model through
`READY_FOR_PRIVATE_PREVIEW`. It does not authorize fabrication, production
approval, customer drawing generation, or external transmission of private
project data.

## Authority

The coordinator must follow, in order:

1. `CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt`;
2. `AGENTS.md`;
3. accepted repository specs, manifests, ledgers, and checkpoint files;
4. signed human decisions recorded in the repository or current thread.

Historical three-output workflow evidence remains immutable legacy evidence.
The active V1 objective is the canonical sheetmetal-first panel model. Future
production-control and punch outputs must consume the same frozen canonical
model and must not independently re-extract, assign, size, or place components.

## Coordinator Scope

Only the root coordinator may update shared canonical state:

- `docs/01_CURRENT_STATE.md`;
- `docs/04_DECISION_LEDGER.md`;
- `docs/06_EVAL_LEDGER.md`;
- `docs/07_CHANGELOG.md`;
- `docs/SESSION_CHECKPOINT.md`;
- `orchestration/TASK_REGISTRY.csv`;
- `orchestration/NEXT_THREAD_PROMPT.txt`;
- `orchestration/master/*`;
- global qualification counts;
- active status and readiness status.

Workers and auditors may write only inside their assigned output paths or
worktrees. Implementation workers may not audit their own accepted work.

## Privacy And Source Boundaries

Default execution is local-only while `docs/PRIVACY_APPROVAL.md` is
`NOT_APPROVED`. The coordinator and child tasks must not transmit source files,
completed references, generated outputs, trajectories, title blocks, private
paths, quantities, component inventories, model identifiers, coordinates,
dimensions, reviewer findings, scores, or project-specific context to any
external API, website, connector, or public location.

Source roots listed in `docs/SOURCE_ROOTS.md` are read-only. Generators may see
only approved generator bundles, approved worksheets, frozen reusable
Knowledge, accepted rules, schemas, renderers, and explicit current
corrections. Completed drawings, modified drawings, post-design labels, and
their derivatives remain forbidden to generators.

## Durable Master Files

The coordinator maintains these local master artifacts:

- `orchestration/master/MASTER_STATE.json`;
- `orchestration/master/THREAD_REGISTRY.csv`;
- `orchestration/master/NEXT_ACTION_QUEUE.json`;
- `orchestration/master/CHECKPOINT_GRAPH.json`;
- `orchestration/master/HEARTBEAT.jsonl`;
- `orchestration/master/RECOVERY_LEDGER.json`;
- `orchestration/master/MASTER_AUTOPILOT_SUMMARY.md`;
- `docs/specs/MASTER_AUTOPILOT_PROTOCOL.md`.

Master orchestration files must contain only minimized operational state,
neutral counts, statuses, hashes, task IDs, thread IDs, worktree paths, commit
IDs, and blocker classes. They must not contain project-specific private
engineering facts, component values, dimensions, coordinates, customer text, or
completed-reference details.

## Child Task Contract

Each child task must have a bounded brief, a visible-file manifest or allowed
file list, forbidden file list, expected artifacts, status vocabulary, runtime
budget, sandbox/network policy, starting commit, and result path.

Each child emits a minimized JSON result at:

`orchestration/master/child-results/<TASK_ID>.json`

Required fields:

- `task_id`;
- `starting_commit`;
- `ending_commit`;
- `tracked_worktree_status`;
- `test_result`;
- `workflow_freeze_results`;
- `artifacts_created`;
- `schemas_validated`;
- `hard_gates`;
- `coverage`;
- `privacy_leakage_counts`;
- `exact_final_status`;
- `exact_recommended_next_action`;
- `blocker_taxonomy`;
- `requested_model`;
- `actual_model`;
- `runtime`;
- `output_hashes`.

Malformed, prose-only, stale-hash, partial, private-content-bearing, or
unhashed child results are rejected.

## Heartbeat And Stall Policy

The coordinator appends neutral events to `HEARTBEAT.jsonl` and refreshes
state from the master files, `docs/SESSION_CHECKPOINT.md`, and
`orchestration/NEXT_THREAD_PROMPT.txt`.

A child is stale when it shows no observable progress for 15 minutes, repeats
the same action without evidence, exits without a child result, or leaves its
worktree unchanged across two heartbeat checks.

On the first stale heartbeat, the coordinator sends one concise reprompt with
the current task, last verified progress, missing artifact, next executable
action, and remaining time budget. On the second consecutive stale heartbeat,
the coordinator marks the child `STALLED`, preserves evidence, and starts a
narrower replacement from the last accepted commit when recovery remains safe.

## Stage Graph

The active autonomous stage graph is:

| stage | purpose | completion signal |
|---|---|---|
| T0 | Independent topology/sizing/placement audit | PASS, FAIL, or INCONCLUSIVE with separated safety and coverage conclusions |
| T1 | Targeted assignment, geometry, and topology rule coverage recovery | accepted recovery artifacts, tests, and independent recovery audit |
| T2 | One-project topology/sizing/placement recalibration | deterministic source-only rerun with hard gates and independent audit |
| T3 | Canonical sheetmetal drawing model | frozen deterministic model with complete provenance or safe unresolved states |
| T4 | Renderer foundation | synthetic previews, PDFs, optional DXF, traceability, and private-preview watermark gates |
| T5 | One-project blind private preview | frozen generator lane, separate evaluator lane, neutral quality metrics |
| T6 | Multi-project expansion | independently qualified cohort stability evidence |
| T7 | Private preview readiness audit | `READY_FOR_PRIVATE_PREVIEW` or a permitted irreducible terminal state |

The coordinator must not skip an independent audit where the stage requires
one. Low coverage is not capability success; unsupported private inference is a
hard failure.

## Permitted Terminal States

Successful terminal state:

- `READY_FOR_PRIVATE_PREVIEW`

Non-success terminal states are allowed only when no compliant recovery branch
remains:

- `PRIVACY_PERMISSION_REQUIRED`;
- `FABRICATION_DOMAIN_DECISION_REQUIRED`;
- `STRUCTURAL_SOURCE_INSUFFICIENCY`;
- `ENVIRONMENT_CAPABILITY_UNAVAILABLE_AFTER_EXHAUSTIVE_LOCAL_RECOVERY`.

The coordinator must never declare `PRODUCTION_APPROVED`.
