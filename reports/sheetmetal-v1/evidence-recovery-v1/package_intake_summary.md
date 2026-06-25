# SMV1 Evidence Recovery Package Intake

Status: `ADDITIONAL_EVIDENCE_PACKAGE_INTAKE_IN_PROGRESS`.

Decision: `D-0054`.

Package `SMV1-EVIDENCE-RECOVERY-PACKAGE-V1-2026-06-25` was received, hash-validated, JSON-parse checked, and copied into an ignored local intake workspace. The committed evidence records only neutral hashes, counts, parse status, and gate status.

Neutral validation:

- Zip SHA-256: `9C875A2D829781D958075A9FF09A7B00378730B2F63C56660F4FEBE7BEBAB62F`.
- Package file count: `7`.
- Manifest-declared file checks: `PASS` (6 of 6).
- JSON parse checks: `PASS` (4 of 4).
- Private intake copy: `PASS`; committed private paths: `0`.
- Full tests: `PASS`.
- Legacy, active sheetmetal-v1, and topology scoped freezes: `PASS`.

Decision boundary:

- Preserve `1110101` as the accepted component-register and graph calibration case.
- Open a parallel source-rich requalification path with preferred candidate `1140304`.
- Do not transfer source-rich assignments, dimensions, or source facts into `1110101`.
- Proposed source, geometry, and rule artifacts are not automatically promoted.
- `PRODUCTION_APPROVED`, fabrication release, customer PDF/DXF/DWG generation, private external transmission, completed-reference leakage, and post-design leakage remain forbidden.

Next action: `RUN_PHASE1_PANEL_ALLOCATION_SOURCE_QUALIFICATION_1140304`.
