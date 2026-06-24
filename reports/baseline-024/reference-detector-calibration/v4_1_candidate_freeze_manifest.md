# Detector V4.1 Candidate Freeze

- detector: `target_output_detection_v4_1_local_layout_prior_recovery`
- implementation commit: `90b0f86`
- calibration positive gate: `PASS 8/8 all-three`
- negative-control gate: `PASS 24/24 controls, 0 false targets`
- private OCR pages: `0`
- external transmission count: `0`
- sealed holdout: `NOT_RUN_AT_FREEZE_MANIFEST_CREATION`

## Hashes

- `scripts/detect_reference_presence_v4.py`: `7EBA5B8A20F6F803F4087F074F3A2DA9A5105034952911CF51B3B6CE3BFE6609`
- `scripts/verify_reference_detection_v4_output.py`: `72AFE3021A12A4D43DA8041D1C5C040B250305152CA81589D50AFE8DDE2E3B27`
- `scripts/run_reference_detection_v4_calibration_partition.py`: `73B3434A485D40A68F71139B764FE064E6649C3F02CC712995CB5BEA7BCDFF2D`
- `scripts/run_reference_detection_v4_negative_controls.py`: `F694344890D0A1AEABE68EE220777B37EA08725768CAD6A74714ABADB39ACFD5`
- `scripts/run_tests.py`: `55D30D12C243372771C44011E36C0702054B7E96E77EC0AF033CC402689A9DD3`
- `schemas/reference_page_classification_v4.schema.json`: `F1267ACE0882B0ABE50AC7B9555198AA12609D3F12E8F7B00CB383DDE34953C1`
- `schemas/reference_document_classification_v4.schema.json`: `DF7C7B8E0B1CF7FCBE3507387BDADA5BC492CDD7BB3229F3BB7BD0C785EAD032`
- `schemas/effective_reference_set_v4.schema.json`: `26C4E2FF3DF99AC36310E6F9F0AE27532D48609BD91C8499B1614867CCB6B5EF`
- `schemas/reference_detection_audit_v4.schema.json`: `D1F23538E90D964018567206D89D95DF06D238976208EE8B60CCC372525D872C`
- `manifests/reference_detection/calibration/v4_calibration_manifest.json`: `021F29FF07F99C5D9121B9591C833B3599D2C071CC448A3273E5806B0AC218AF`
- `manifests/reference_detection/calibration/v4_negative_controls.json`: `042CE2ED6C38F1B45E9E05BC32F12C54537D4E793FF0CDB938AC00E8F1409510`
- `reports/baseline-024/reference-detector-calibration/v4_1_calibration_partition/calibration_partition_summary.json`: `FF0B4C95CCF506665D8EF5CCB9EBA015D8CA746D3804B8A3F4960BA8B4AC2282`
- `reports/baseline-024/reference-detector-calibration/v4_1_negative_controls/negative_control_audit_summary.json`: `3DF9A4480722ED97944DCBDA88820704650076A8468C10AA31BF0FDD48C62338`
