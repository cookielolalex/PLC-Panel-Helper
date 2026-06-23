# B024-C-B003-INDEPENDENT-AUDIT

Role: `independent_auditor`

Batch: `batch-003`

Objective: independently audit the frozen batch-003 Phase C source backfill evidence using only the files listed in `orchestration\input_manifests\baseline-024\source_backfill\batch-003\B024-C-B003-INDEPENDENT-AUDIT.visible_files.json`.

Allowed files: see `orchestration\input_manifests\baseline-024\source_backfill\batch-003\B024-C-B003-INDEPENDENT-AUDIT.visible_files.json`. Do not read completed references, target drawings, target thumbnails, target hashes, expected answers, score reports, generator outputs, archived conversations, or any source-root file outside the listed manifest.

Write only:

- `reports\baseline-024\source_bundle_audit_batch_003_independent.json`
- `reports\baseline-024\source_bundle_audit_batch_003_independent.md`

Audit criteria:

1. batch-003 source selection and source approval used metadata/source-candidate evidence only, with completed-reference inspection flags false;
2. four specialist review JSONs are present, role-distinct, schema-valid, and cover the same 66 prefilter decision IDs;
3. adjudications are schema-valid and every `AGENT_QUORUM_APPROVED_EVAL` item has four `ALLOW_EVAL` votes, matching current hashes/fingerprints, and no unresolved issues;
4. accepted bundle directories are exactly `1110704` and `1120305`;
5. accepted bundles contain no original workbook files, symlinks, absolute source path leaks, forbidden sentinels, or verification/hash mismatches;
6. rejected bundle directory is exactly `1110701`, contains only `verification_results.json` and `build_status.json`, and is not counted as `ALLOWED_EVAL`;
7. `1110402`, `1110706`, and `1120102` remain no-bundle/quarantined;
8. `reports\baseline-024\source_bundle_audit_batch_003.json` reports `EVAL_SOURCE_BUNDLE_AUDIT_PASS` for the accepted bundle set;
9. no production approval was declared and no drawing generation was started.

Allowed result statuses:

- `BATCH003_SOURCE_BACKFILL_AUDIT_PASS`
- `BATCH003_SOURCE_BACKFILL_AUDIT_FAIL`
- `BATCH003_SOURCE_BACKFILL_AUDIT_INCONCLUSIVE`

Completion criteria:

- write both report files listed above;
- include file hashes for key evidence;
- explicitly state whether any forbidden material was opened;
- do not mutate any input file or bundle evidence.
