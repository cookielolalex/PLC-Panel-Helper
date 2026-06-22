# Skill Governance

Active skills live under `.agents/skills/` and are frozen into release
manifests by hash.

Candidate changes live under `optimization/skill_proposals/` as proposal
metadata and exact diffs. A proposal must include trigger and non-trigger
examples, current target hash, scanner/test state, risks, rollback, and review
decision.

Only the coordinator may apply accepted proposals to active skills.

