# Vision Classifier Availability Probe

- status: `VISION_CLASSIFIER_UNAVAILABLE`
- synthetic local-image probe: `PASS`
- actual model reported by probe child: `GPT-5`
- private project/reference images sent to vision agent: `0`
- privacy approval: `NOT_APPROVED`
- detector v4 created: `false`

The installed agent environment can inspect a synthetic local image through a
fresh GPT-5 child. That path is not usable for completed reference pages while
`docs/PRIVACY_APPROVAL.md` remains `NOT_APPROVED`, because it would transmit
private project/reference image data outside local-only execution.

Detector v3 remains failed on known positives: `0 / 13` projects detected
all-three, with per-type recall `PRODUCTION_DRAWING 0 / 13`,
`SHEETMETAL_DRAWING 8 / 13`, and `PUNCH_DRAWING 0 / 13`.

A regression gate was added in `scripts/run_tests.py` as
`test_reference_detector_v3_known_positive_recall_gate`, covering all 13 missed
known-positive projects and preventing the local deterministic v3 replay from
being treated as actual vision classification.
