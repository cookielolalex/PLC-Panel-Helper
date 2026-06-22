# Source Guard Review Workflow

Status: proposed only. No real item is approved by this report.

Purpose:

- Convert `reports/manual_review_queue.csv` into a metadata-only review batch.
- Require a signed source approval file before any item can enter a generator
  bundle.
- Bind every approval to the current source index hashes and the exact current
  row hash for each approved item.
- Build a sanitized generator bundle manifest that contains approved workbook
  and worksheet identifiers only, plus copied workbook files after verification.

Fail-closed rules:

- `FORBIDDEN` rows are never eligible for approval.
- Completed target drawing roles, production-control roles, electrical drawing
  roles, target-like PDF names, and rows with forbidden signature matches are
  rejected even if a human approval document names them.
- `.xls` workbooks remain unsupported until a parser/conversion path is
  separately approved and tested.
- Hidden, stale, insufficient-identity, or non-current worksheets are rejected.
- Missing source hashes, stale approval row hashes, mismatched index hashes, and
  missing signature fields reject the approval.
- Bundle manifests must not expose absolute source paths.
- Bundle files must not be symlinks, junctions, reparse points, or hash
  mismatches.

Review sequence:

1. Coordinator builds a review batch:

   ```powershell
   python scripts/build_source_review_batch.py `
     --manual-review-queue reports/manual_review_queue.csv `
     --file-role-index manifests/all_projects_file_role_index.csv `
     --workbook-sheet-index manifests/all_projects_workbook_sheet_index.csv `
     --output-json reports/source_review_batch.json `
     --output-csv reports/source_review_batch.csv
   ```

2. Human reviewer creates a separate source approval JSON matching
   `schemas/source_approval.schema.json`.
3. Coordinator validates the approval:

   ```powershell
   python scripts/validate_source_approval.py `
     --approval reports/source_approval.json `
     --file-role-index manifests/all_projects_file_role_index.csv `
     --workbook-sheet-index manifests/all_projects_workbook_sheet_index.csv `
     --output reports/source_approval_validation.json
   ```

4. Only after validation passes, coordinator builds a sanitized bundle:

   ```powershell
   python scripts/build_sanitized_generator_bundle.py `
     --approval reports/source_approval.json `
     --file-role-index manifests/all_projects_file_role_index.csv `
     --workbook-sheet-index manifests/all_projects_workbook_sheet_index.csv `
     --bundle-dir tmp/sanitized_generator_bundle `
     --output-manifest tmp/sanitized_generator_bundle/manifest.json `
     --project-id 1150001 `
     --run-id REVIEWED-1150001 `
     --copy-files
   ```

5. Coordinator verifies the bundle before any generator invocation:

   ```powershell
   python scripts/verify_sanitized_bundle.py `
     --bundle-dir tmp/sanitized_generator_bundle `
     --manifest tmp/sanitized_generator_bundle/manifest.json `
     --output tmp/sanitized_generator_bundle/verification.json
   ```

