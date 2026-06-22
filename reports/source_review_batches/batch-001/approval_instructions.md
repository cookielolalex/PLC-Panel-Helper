# Approval Instructions

This review packet does not approve any item by itself.

For each row in `blank_human_decisions.csv`, fill `human_decision` with exactly
one of:

- HUMAN_APPROVED
- HUMAN_DENIED
- NEEDS_MORE_EVIDENCE

Blank cells are not approvals. Bulk approval is not accepted. Each approval
must retain the exact `decision_id`, `file_sha256`, and `worksheet_fingerprint`
shown in the packet. If a worksheet has no fingerprint, it cannot be approved
for a generator bundle in this calibration phase.
