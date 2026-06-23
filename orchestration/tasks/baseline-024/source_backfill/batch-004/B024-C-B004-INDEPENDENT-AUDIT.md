# B024-C-B004-INDEPENDENT-AUDIT

Role: `independent_auditor`

Batch: `batch-004`

Objective: independently audit the frozen batch-004 Phase C source backfill evidence and verify the final safe-candidate shortfall using only the files listed in `orchestration\input_manifests\baseline-024\source_backfill\batch-004\B024-C-B004-INDEPENDENT-AUDIT.visible_files.json`.

Allowed files: see `orchestration\input_manifests\baseline-024\source_backfill\batch-004\B024-C-B004-INDEPENDENT-AUDIT.visible_files.json`. Do not read completed references, target drawings, target thumbnails, target hashes, expected answers, score reports, generator outputs, archived conversations, or any source-root file outside the listed manifest.

Write only:

- `reports\baseline-024\source_bundle_audit_batch_004_independent.json`
- `reports\baseline-024\source_bundle_audit_batch_004_independent.md`

Audit criteria:

1. batch-004 source selection and source approval used metadata/source-candidate evidence only, with completed-reference inspection flags false;
2. four specialist review JSONs are present, role-distinct, schema-valid, and cover the same 9 prefilter decision IDs;
3. adjudications are schema-valid and the single `AGENT_QUORUM_APPROVED_EVAL` item has four `ALLOW_EVAL` votes, matching current hashes/fingerprints, and no unresolved issues;
4. no accepted bundle directory exists for batch-004;
5. rejected bundle directory is exactly `1110501`, contains only `verification_results.json` and `build_status.json`, and is not counted as `ALLOWED_EVAL`;
6. `1110504` remains quarantined/no-bundle;
7. `reports\baseline-024\source_bundle_audit_batch_004.json` reports `EVAL_SOURCE_BUNDLE_AUDIT_NO_ACCEPTED_BUNDLES`;
8. the frozen backfill plan processed all 20 metadata-only candidates and none remain unprocessed;
9. no production approval was declared and no drawing generation was started.

Allowed result statuses:

- `BATCH004_SOURCE_BACKFILL_AUDIT_PASS`
- `BATCH004_SOURCE_BACKFILL_AUDIT_FAIL`
- `BATCH004_SOURCE_BACKFILL_AUDIT_INCONCLUSIVE`

Completion criteria:

- write both report files listed above;
- include file hashes for key evidence;
- explicitly state whether any forbidden material was opened;
- do not mutate any input file or bundle evidence.
