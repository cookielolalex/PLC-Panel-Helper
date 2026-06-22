# Source Inventory Summary

Phase 0 did not perform a full source scan.

Initial declared roots were missing at the exact paths from the master
specification. On 2026-06-22 the user approved
`C:\Users\alex1\OneDrive\Desktop\All Projects` as the consolidated project root.

Shallow probe found five yearly directories: `111年度工作`, `112年度工作`,
`113年度工作`, `114年度工作`, and `115年度工作`. Full read-only manifest generation
has now run.

Generated manifests:

- `manifests/all_projects_file_role_index.csv`
- `manifests/115_file_role_index.csv`
- `manifests/all_projects_workbook_sheet_index.csv`
- `manifests/115_workbook_sheet_index.csv`
- `manifests/all_projects_project_manifest.csv`
- `manifests/115_project_manifest.csv`
- `manifests/all_projects_inventory_summary.json`
- `manifests/st_block_library_index.csv`
- `manifests/vendor_catalog_index.csv`

Inventory summary:

- Files hashed: 7,400
- Total approved-root active-year 115 files: 606
- Workbook records inspected or marked parser-required: 2,847
- Worksheet/index rows: 4,231
- Active-year 115 worksheet/index rows: 446
- Projects detected: 404
- Runtime: 493.74 seconds

Top file roles:

- `forbidden_production_control_file`: 2,006
- `completed_sheetmetal_drawing_reference`: 1,860
- `spreadsheet_other`: 1,428
- `forbidden_electrical_drawing`: 1,008
- `allowed_material_list_workbook`: 291
- `allowed_contract_workbook`: 223

This inventory is manifest evidence only. It does not approve any generator
bundle and does not start a real-project baseline.

Reusable library status:

- Canonical `ST-Block1` root was not found under the approved project root.
- `manifests/st_block_library_index.csv` records 27 project-local CAD files as
  `PROJECT_LOCAL_CAD_FILE_NOT_APPROVED_ST_BLOCK1`.
- Canonical vendor catalog root was not found under the approved project root.
- `manifests/vendor_catalog_index.csv` records 21 project-local catalog
  candidates as `PROJECT_LOCAL_CATALOG_CANDIDATE_NOT_PRODUCTION_KNOWLEDGE`.
