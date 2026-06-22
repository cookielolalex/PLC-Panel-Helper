# Harness Scripts

Use the bundled Python runtime recorded by `codex_app.load_workspace_dependencies`
when system Python is unavailable.

Phase 0 commands:

```powershell
$py='C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py scripts/run_tests.py
```

Important scripts:

- `inventory_sources.py` creates read-only source manifests.
- `inspect_workbook_sheets.py` inventories visible/hidden workbook sheets.
- `build_generator_bundle.py` creates positive generator bundles.
- `scan_generator_contamination.py` rejects forbidden labels/sentinels.
- `render_pdf_outputs.py` renders the three required PDFs from one model.
- `validate_pdf_package.py` verifies PDF presence/readability.
- `grade_project.py` creates validity/score/coverage/confidence results.

