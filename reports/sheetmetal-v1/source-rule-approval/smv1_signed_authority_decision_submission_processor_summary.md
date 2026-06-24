# Signed Authority Decision Submission Processor

Status: `SIGNED_AUTHORITY_DECISION_SUBMISSION_PROCESSOR_READY_FAIL_CLOSED`.

The processor `scripts/process_signed_authority_decision.py` writes validation,
intake, and submission-summary artifacts from one signed source/rule authority
decision input. It does not select authority, authorize implementation,
authorize customer drawing generation, or declare production approval.

For validator-passing accepted lanes, the processor routes to
`ADD_REGRESSION_TESTS_BEFORE_ACCEPTED_AUTHORITY_LANE_FIX`. For validator-passing
reject-all decisions, it routes to `ENTER_TERMINAL_CANDIDATE_REVIEW`. Invalid
decisions fail closed and keep the next action at
`WAIT_FOR_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION`.

The current unsigned draft was processed as a fail-closed proof. The processor
returned exit code `1` and wrote
`reports/sheetmetal-v1/source-rule-approval/smv1_unsigned_authority_decision_submission/submission_summary.json`
with missing choice, signer, and date errors while packet/template hash checks
passed.

Verification:

- Python compile: `PASS`
- Targeted submission-package regression: `PASS`
- Full `scripts/run_tests.py`: `PASS`
- Legacy scoped freeze: `PASS`
- Active sheetmetal-v1 scoped freeze: `PASS`
- Topology-stage scoped freeze: `PASS`

Next action remains:
`WAIT_FOR_SIGNED_HUMAN_SOURCE_RULE_AUTHORITY_DECISION`.
