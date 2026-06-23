# Backfill source review leakage_red_team

- task_id: `CAL006-B-LEAKAGE_RED_TEAM`
- calibration_id: `calibration-006`
- children may not spawn children
- completed references are reviewer-only evidence after generation freeze

## Allowed Paths
- `manifests\calibration-006\backfill\project_manifests`
- `manifests\calibration-006\backfill\source_decisions_1110101_legacy_xls.csv`

## Forbidden Paths
- `completed references`
- `reviewer results from other roles`
- `generator outputs`

## Required Output
- `C:\Users\alex1\OneDrive\Documents\PLC Panels Generation Helper\manifests\calibration-006\backfill\reviews\leakage_red_team_review.json`
