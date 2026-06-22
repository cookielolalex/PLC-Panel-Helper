from __future__ import annotations

import argparse
from pathlib import Path

from harness_lib import sha256_json, write_json
from render_pdf_outputs import main as render_main
from validate_pdf_package import main as validate_pdf_main
from grade_project import main as grade_main


def create_synthetic_model(work_dir: Path) -> Path:
    job_spec = {
        "schema_version": "0.0.1",
        "project": {"project_id": "SYNTH-001", "customer": "Fixture", "project_name": "Valid minimal one-panel", "revision": "A"},
        "panels": [{"panel_id": "P1", "width": 600, "height": 800, "verification_status": "UNVERIFIED"}],
        "materials": [],
        "devices": [],
        "cutouts": [],
        "source_references": [],
        "conflicts": [],
        "unresolved_fields": []
    }
    job_path = work_dir / "job_spec_SYNTH-001.json"
    write_json(job_path, job_spec)
    model = {
        "schema_version": "0.0.1",
        "project_id": "SYNTH-001",
        "job_spec_hash": sha256_json(job_spec),
        "units": "mm",
        "model_version": "0.0.1",
        "panels": [{"panel_id": "P1", "width": 600, "height": 800, "material": None, "thickness": None, "devices": [], "cutouts": [], "verification_status": "UNVERIFIED"}],
        "renderer_visibility": {"production": ["P1"], "sheetmetal": ["P1"], "punch": ["P1"]},
        "unresolved_regions": [],
        "provenance": []
    }
    model_path = work_dir / "drawing_model_SYNTH-001.json"
    write_json(model_path, model)
    return model_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Phase 0 synthetic harness.")
    parser.add_argument("--work-dir", type=Path, default=Path("tmp/synthetic_harness"))
    args = parser.parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    model_path = create_synthetic_model(args.work_dir)

    import sys

    old_argv = sys.argv[:]
    try:
        sys.argv = ["render_pdf_outputs.py", str(model_path), "--output-dir", str(args.work_dir / "rendered"), "--run-id", "SYNTH-RUN-001"]
        render_main()
        sys.argv = ["validate_pdf_package.py", "--project-id", "SYNTH-001", "--pdf-dir", str(args.work_dir / "rendered"), "--run-id", "SYNTH-RUN-001", "--output", str(args.work_dir / "validation_results.json")]
        validate_pdf_main()
        sys.argv = ["grade_project.py", "--run-id", "SYNTH-RUN-001", "--validation", str(args.work_dir / "validation_results.json"), "--output", str(args.work_dir / "grading_result.json")]
        grade_main()
    finally:
        sys.argv = old_argv
    print(f"synthetic harness wrote {args.work_dir}")


if __name__ == "__main__":
    main()

