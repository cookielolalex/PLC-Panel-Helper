# SMV1 Source/Rule Approval Proposal Review Task Brief

Task ID: `SMV1-SOURCE-RULE-APPROVAL-PROPOSAL-REVIEW`
Agent type: `independent_auditor`
Starting commit: `de01dd57b0c4a7db98114a5a9913b25de6069f06`
Active goal: `SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1`

Perform a read-only independent review of the proposal packet at:

- `reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_approval_proposal.json`
- `reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_approval_proposal.md`
- `orchestration/master/child-results/SMV1-SOURCE-RULE-APPROVAL-PROPOSAL.json`

Required checks:

1. Verify the proposal is proposal-only and does not implement source/rule
   behavior.
2. Verify the proposal is bound to accepted T1 evidence hashes.
3. Verify the proposal does not authorize source-root, `.private`, completed
   reference, post-design, customer PDF/DXF/DWG, public web, or production
   approval use.
4. Verify each lane has a valid authority path under accepted source-role,
   chronology, source fact authority, and qualification policies.
5. Verify rejected shortcuts are sufficient to preserve no-invention behavior.
6. Verify test-before-fix requirements cover the relevant T1 hard gates.
7. Verify intended diff scope and rollback are bounded.
8. Return PASS, FAIL, or INCONCLUSIVE, with exact blockers and recommended next
   action.

Allowed write scope:

- `reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_approval_proposal_review.json`
- `reports/sheetmetal-v1/source-rule-approval/smv1_source_rule_approval_proposal_review.md`
- `orchestration/master/child-results/SMV1-SOURCE-RULE-APPROVAL-PROPOSAL-REVIEW.json`

Forbidden actions:

- Do not edit implementation code, rules, schemas, source manifests, frozen
  releases, frozen graders, canonical ledgers, or tests.
- Do not open source roots, `.private`, completed target drawings, post-design
  files, customer PDFs, customer DXFs, customer DWGs, thumbnails, extracted
  target text, reviewer answers, scores, or reference details.
- Do not execute, stage, or modify
  `scripts/run_reference_detection_v4_corpus_screening.py`.
- Do not use public web or transmit private project context.
- Do not declare `PRODUCTION_APPROVED`.

Expected final status if evidence supports it:

`PASS_PROPOSAL_READY_FOR_HUMAN_OR_AUTHORITY_REVIEW`

Expected next action if passed:

`PREPARE_SOURCE_RULE_AUTHORITY_DECISION_PACKET`
