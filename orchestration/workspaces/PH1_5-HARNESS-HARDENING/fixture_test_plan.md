# Adversarial Source-Guard Fixture and Test Plan

## Scope

The hardening should make `scripts/scan_generator_contamination.py` fail closed for generator bundle inputs that expose forbidden reference evidence, unverifiable workbook surfaces, stale identity data, approval abuse, filesystem escapes, or target-output leakage. Tests are synthetic only and create small local fixtures under `tmp/phase1_5_source_guard/`.

## Proposed Test Cases

| Case | Synthetic fixture | Expected scan status | Guard exercised |
| --- | --- | --- | --- |
| `hidden_worksheet_sentinel` | `.xlsx` ZIP with workbook sheet state `hidden` and hidden sheet XML containing `reference_only_sentinel` | `FAIL` | hidden sheet and sentinel extraction |
| `very_hidden_worksheet_sentinel` | `.xlsx` ZIP with sheet state `veryHidden` | `FAIL` | veryHidden sheet detection |
| `formula_named_range_external_link` | `.xlsx` ZIP with `<f>`, `<definedName>`, and `xl/externalLinks/` | `FAIL` | formulas, named ranges, external links |
| `stale_customer_project_ids` | workbook XML/shared text with `project_id=9999999` and `customer_id=OLD_CUSTOMER` while CLI current IDs are `1150101` and `CUSTOMER-OK` | `FAIL` | stale current-project/customer rejection |
| `superseded_manifest_entry` | manifest record with `superseded_by` or `supersession_status=SUPERSEDED` | `FAIL` | supersession fail-closed |
| `macro_enabled_workbook` | `.xlsm` ZIP and/or `xl/vbaProject.bin` | `FAIL` | macro-enabled workbook rejection |
| `legacy_xls_parser_required` | `.xls` file in bundle | `FAIL` | parser-required legacy workbook rejection |
| `approval_tampering` | decision artifact with `approved=true`, no signature, or `tampered=true` | `FAIL` | approval integrity guard |
| `mutation_invalidation` | manifest claims a SHA-256 that does not match the visible bundle file | `FAIL` | stale/mutated manifest invalidation |
| `source_root_path_leak` | text file containing a synthetic `All Projects`/`SOURCE_ROOT` path canary | `FAIL` | source-root path leak rejection |
| `target_output_name_leak` | bundle path containing `01_生管課用圖_1150101.pdf` | `FAIL` | target-output filename leakage |
| `clean_cjk_path` | clean CJK-named workbook `箱體資料_1150101.xlsx` with no hidden sheets or sentinels | `PASS` | UTF-8 path safety without overblocking |
| `symlink_or_junction_escape` | symlink or reparse-point file inside bundle pointing outside bundle, skipped when unsupported by OS | `FAIL` if created | symlink/junction escape rejection |
| `zip_traversal_entry` | workbook ZIP entry `../escape.txt` | `FAIL` | archive traversal rejection |
| `blank_decisions` | decision artifact with blank `decision_id`, `approver`, or `signature` | `FAIL` | blank decision rejection |
| `bulk_approvals` | decision artifact with `bulk_approval=true` or `approval_scope=bulk` | `FAIL` | bulk approval rejection |

## Patch Strategy

- Keep the existing contamination scan command working with `--bundle-dir`, `--manifest`, and `--output`.
- Add optional `--project-id`, `--customer-id`, `--decision-artifact`, and repeatable `--source-root-canary` arguments.
- Recursively inspect manifest JSON for approval, supersession, path, and hash evidence.
- Resolve every visible bundle path before reading it; reject symlinks, junctions/reparse points, and paths resolving outside the bundle root.
- Inspect `.xlsx` and `.xlsm` as ZIP packages; reject hidden/veryHidden sheets, formulas, named ranges, external links, macros, path traversal, and forbidden terms in XML/text members.
- Reject `.xls` legacy workbooks because the current scanner cannot inspect binary workbook internals.
- Emit structured hit records with `path`, `term`, `location`, and `category` so reviewer findings are deterministic.

## Verification Plan

1. Apply `proposed_patch.diff` to a clean branch.
2. Run `python -B scripts/run_tests.py`.
3. Confirm the new `test_adversarial_source_guard_hardening` passes without invoking a real project generator.
4. Inspect generated contamination JSON for each case under `tmp/phase1_5_source_guard/`.
5. Review any platform skip note for symlink/junction if the OS denies symlink creation.
