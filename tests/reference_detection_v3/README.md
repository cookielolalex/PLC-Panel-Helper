# Reference Detection V3 Tests

The executable tests live in `scripts/run_tests.py` to match the repository's
current custom runner.

The fixtures in `evals/fixtures/reference_detection_v3/fixture_manifest.json`
are synthetic definitions only. The runner creates temporary PDFs under
`tmp/reference_detection_v3_tests/`, runs detector v3, verifies schemas and data
minimization, and then relies on the detector to remove temporary rendered page
images and title-block crops.
