# T1C Topology Sizing Rule Recovery

Task: `SMV1-T1C-TOPOLOGY-SIZING-RULE-RECOVERY`

Status: `RECOVERABLE_BLOCKER`

Signed choice C authorizes a versioned topology, sizing, clearance, and
placement rule authority lane, but this worker did not activate rules in the
frozen generator or update canonical master state. It produced an audit-ready
rule artifact and synthetic regression fixture coverage under the assigned
output path.

## Artifacts

- `rule_artifacts/smv1_choice_c_topology_sizing_placement_rules.v1.json`
- `synthetic_regression/synthetic_rule_fixture_manifest.json`
- `synthetic_regression/artifact_gate_validation.json`
- `topology_sizing_rule_recovery_report.json`
- `topology_sizing_rule_recovery_report.md`

## Rule Coverage

The rule package contains 8 rules:

- `SMV1-C-TOPOLOGY-001@1.0.0`
- `SMV1-C-TOPOLOGY-002@1.0.0`
- `SMV1-C-SIZING-001@1.0.0`
- `SMV1-C-SIZING-002@1.0.0`
- `SMV1-C-CLEARANCE-001@1.0.0`
- `SMV1-C-PLACEMENT-001@1.0.0`
- `SMV1-C-PLACEMENT-002@1.0.0`
- `SMV1-C-PROVENANCE-001@1.0.0`

Hard constraints are separated from soft objectives. Every rule has
applicability, exclusions, evidence or engineering basis, fail-closed behavior,
synthetic fixture coverage, and independent-audit requirements.

## Verification

Artifact gate validation passed with 8 rules and 5 synthetic fixtures. The
fixtures contain zero private source values and zero completed-reference values.

Broader full-test and scoped-freeze verification is blocked by stale hash gates
already present in the current tree:

- `scripts/run_tests.py` failed only at active/topology frozen-manifest checks.
- `verify_frozen_workflow.py --scope sheetmetal-v1-active` reported hash
  mismatches across existing frozen entries.
- `verify_frozen_workflow.py --scope sheetmetal-v1-topology-sizing-placement`
  reported hash mismatches across existing frozen entries.
- A rerun of the signed-authority validator reported bound packet/template
  hash mismatches, although the committed intake summary records PASS.

This worker did not modify frozen manifests, source roots, customer artifacts,
private artifacts, completed references, post-design labels, generator code,
or customer drawing outputs.

## Next Action

`COORDINATOR_REFRESH_OR_ADJUDICATE_STALE_HASH_GATES_THEN_RUN_INDEPENDENT_CHOICE_C_RULE_AUDIT`
