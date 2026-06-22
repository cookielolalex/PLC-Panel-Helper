# PH1_5-HARNESS-HARDENING Task Brief

Agent: `PH1_5-HARNESS-HARDENING`

Mode: bounded workspace-write only.

Writable paths used:

- `orchestration/workspaces/PH1_5-HARNESS-HARDENING/`
- `orchestration/results/PH1_5-HARNESS-HARDENING.json`

Read inputs:

- `docs/specs/GENERATOR_INPUT_POLICY.md`
- `docs/specs/EVALUATION_HARNESS_SPEC.md`
- `scripts/run_tests.py`
- `scripts/harness_lib.py`
- `scripts/scan_generator_contamination.py`
- `evals/fixtures/synthetic_cases_manifest.json`
- `evals/fixtures/utf8_labels.txt`
- `schemas/child_result.schema.json`

Forbidden actions observed:

- Did not inspect `C:\Users\alex1\OneDrive\Desktop\All Projects`.
- Did not inspect completed PDFs or reference PDF content.
- Did not edit canonical docs, manifests, schemas, scripts, tests, reports, source roots, `evals/runs/`, or `evals/references/`.
- Did not run a real project generator.

Deliverable intent:

- Provide a concrete synthetic fixture and test plan for adversarial source-guard hardening.
- Provide patch-ready unified diff content for scanner and harness test hardening.
- Provide schema-valid child result JSON.
