# SMV1 Signed Source/Rule Authority Decision Template

Status: `TEMPLATE_ONLY_NO_AUTHORITY_SELECTED`

This template is a decision aid for the pending
`REQUEST_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION` gate. It is not a
decision, approval, implementation plan, or waiver.

Bound decision packet:

- JSON:
  `reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_authority_decision_packet.json`
- SHA-256:
  `A22FC1CA7C6D299E21EFCFBE495F1BFAA6F14D74049085133CB02C00ED152AA1`

## Instructions

To continue, provide a signed decision selecting one or more choices below, or
reject all lanes. A valid decision must name the selected choice IDs and state
that all non-negotiable constraints remain in force.

## Choices

| Choice | Select? | Meaning |
|---|---|---|
| `A` | `[ ]` | `AUTHORIZE_PANEL_ALLOCATION_SOURCE_REVIEW` |
| `B` | `[ ]` | `AUTHORIZE_COMPONENT_GEOMETRY_AUTHORITY` |
| `C` | `[ ]` | `AUTHORIZE_TOPOLOGY_SIZING_PLACEMENT_RULE_AUTHORITY` |
| `D` | `[ ]` | `REJECT_ALL_AUTHORITY_LANES` |

Choice `D` is mutually exclusive with choices `A`, `B`, and `C`.

## Required Signed Statement

```text
I authorize the following SMV1 source/rule authority choice(s): <A/B/C or D>.

I understand this does not authorize production approval, customer drawing
generation, source-root mutation, completed-reference inference, post-design
label authority, public lookup of private model identifiers, or staging private
artifacts.

Signed: <name or authority>
Date: <YYYY-MM-DD>
```

## After A Valid Decision

- Accepted lane(s) still require regression tests before behavior changes.
- Any implementation must be bounded to the accepted lane(s).
- Full tests and relevant scoped frozen workflow verification must pass.
- Independent audit is required before recalibration or model promotion.
