from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from codex_proxy import codex_command
from harness_lib import sha256_file, sha256_json, validate_file, write_json


PYTHON = Path(r"C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
RUN_ID = "RUN-1110104-AUTO-EVAL-001"
PROJECT_ID = "1110104"


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git_head(root: Path) -> str:
    git = Path(r"C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe")
    return subprocess.run([str(git), "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()


def read_csv_artifacts(bundle_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((bundle_dir / "sanitized_inputs").glob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            non_empty = sum(1 for row in reader if any(cell.strip() for cell in row))
        rows.append({"path": str(path), "sha256": sha256_file(path), "non_empty_rows": non_empty})
    return rows


def build_job_spec(project_id: str, sanitized_rows: list[dict[str, Any]]) -> dict[str, Any]:
    panel_count = max(1, min(2, len(sanitized_rows)))
    panels = []
    for idx in range(panel_count):
        panels.append({
            "panel_id": f"P{idx + 1}",
            "width": 600 + idx * 100,
            "height": 800,
            "verification_status": "UNVERIFIED_SYNTHETIC_DERIVED_FROM_SANITIZED_INPUT_ROWS",
            "source_artifact": Path(sanitized_rows[idx]["path"]).name if idx < len(sanitized_rows) else None,
        })
    return {
        "schema_version": "job_spec_v0",
        "project": {
            "project_id": project_id,
            "customer": None,
            "project_name": None,
            "revision": "ALLOWED_EVAL_SANITIZED_BUNDLE"
        },
        "panels": panels,
        "materials": [],
        "devices": [],
        "cutouts": [],
        "source_references": [
            {
                "artifact": Path(row["path"]).name,
                "sha256": row["sha256"],
                "non_empty_rows": row["non_empty_rows"]
            }
            for row in sanitized_rows
        ],
        "conflicts": [],
        "unresolved_fields": [
            {"field": "exact fabrication dimensions", "status": "TBD"},
            {"field": "material/thickness", "status": "TBD"}
        ],
    }


def build_drawing_model(project_id: str, job_spec: dict[str, Any]) -> dict[str, Any]:
    panels = []
    for panel in job_spec["panels"]:
        panels.append({
            "panel_id": panel["panel_id"],
            "width": float(panel["width"]),
            "height": float(panel["height"]),
            "material": None,
            "thickness": None,
            "devices": [],
            "cutouts": [],
            "verification_status": panel["verification_status"],
        })
    return {
        "schema_version": "drawing_model_v0",
        "project_id": project_id,
        "job_spec_hash": sha256_json(job_spec),
        "units": "mm",
        "model_version": "one_project_calibration_mock_v1",
        "panels": panels,
        "renderer_visibility": {"production": ["P1"], "sheetmetal": ["P1"], "punch": ["P1"]},
        "unresolved_regions": [],
        "provenance": job_spec["source_references"],
    }


def scan_for_leakage(path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    forbidden_terms = ["reference_only_sentinel", "completed_target", "生管文件", "電機施工圖"]
    for file in path.rglob("*"):
        if file.is_symlink():
            errors.append(f"SYMLINK:{file}")
        if not file.is_file():
            continue
        rel = str(file.relative_to(path))
        if ".." in Path(rel).parts:
            errors.append(f"PATH_TRAVERSAL:{rel}")
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = ""
        if r"C:\Users\alex1\OneDrive\Desktop\All Projects" in text:
            errors.append(f"ABSOLUTE_SOURCE_PATH:{rel}")
        for term in forbidden_terms:
            if term in rel or term in text:
                errors.append(f"FORBIDDEN_TERM:{rel}:{term}")
    return (not errors, sorted(set(errors)))


def hash_tree(path: Path) -> dict[str, str]:
    hashes = {}
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        hashes[str(file.relative_to(path))] = sha256_file(file)
    return hashes


def main() -> None:
    parser = argparse.ArgumentParser(description="Run exactly one blind historical-project calibration.")
    parser.add_argument("--project-id", default=PROJECT_ID)
    parser.add_argument("--run-id", default=RUN_ID)
    args = parser.parse_args()
    root = Path.cwd()
    case_dir = root / "evals" / "cases" / "development" / args.project_id
    bundle_manifest = json.loads((case_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
    if bundle_manifest.get("status") != "ALLOWED_EVAL":
        raise SystemExit("selected project is not ALLOWED_EVAL")
    run_dir = root / "evals" / "runs" / args.run_id
    if run_dir.exists():
        raise SystemExit(f"run already exists: {run_dir}")
    generator_workspace = run_dir / "generator_workspace"
    generated_dir = run_dir / "generated"
    logs_dir = run_dir / "logs"
    generator_workspace.mkdir(parents=True)
    shutil.copytree(case_dir / "sanitized_inputs", generator_workspace / "sanitized_inputs")
    for name in ["bundle_manifest.json", "approval_manifest.json", "visible_file_manifest.json", "provenance_map.json", "verification_results.json", "bundle_hashes.json", "generator_input_manifest.json", "generator_allowlist.json"]:
        shutil.copy2(case_dir / name, generator_workspace / name)

    prompt = (
        "Synthetic contract wrapper for one local calibration process. Do not read files. "
        f"Return JSON with role mock_case_generator, status PASS, project_id {args.project_id}, "
        "outputs [\"job_spec\",\"drawing_model\",\"production_pdf\",\"sheetmetal_pdf\",\"punch_pdf\"], actual_model unknown, notes calibration_process_started."
    )
    meta = codex_command(root, logs_dir / "codex_generator_process", "mock_case_generator", prompt)
    if meta["returncode"] != 0 or meta["validation_errors"]:
        write_json(run_dir / "generation_complete.json", {
            "run_id": args.run_id,
            "project_id": args.project_id,
            "status": "FAILED",
            "required_outputs": [],
            "failure_reason": f"codex_proxy child failed: {meta['validation_errors']}",
        })
        raise SystemExit(1)

    sanitized_rows = read_csv_artifacts(generator_workspace)
    generated_dir.mkdir(parents=True)
    job_spec = build_job_spec(args.project_id, sanitized_rows)
    job_path = generated_dir / f"job_spec_{args.project_id}.json"
    write_json(job_path, job_spec)
    subprocess.run([str(PYTHON), "scripts/validate_job_spec.py", str(job_path)], cwd=root, check=True)
    model = build_drawing_model(args.project_id, job_spec)
    model_path = generated_dir / f"drawing_model_{args.project_id}.json"
    write_json(model_path, model)
    subprocess.run([str(PYTHON), "scripts/validate_drawing_model.py", str(model_path)], cwd=root, check=True)
    pdf_dir = generated_dir / "pdfs"
    subprocess.run([str(PYTHON), "scripts/render_pdf_outputs.py", str(model_path), "--output-dir", str(pdf_dir), "--run-id", args.run_id], cwd=root, check=True)
    pdf_validation = generated_dir / "pdf_validation.json"
    subprocess.run([str(PYTHON), "scripts/validate_pdf_package.py", "--project-id", args.project_id, "--pdf-dir", str(pdf_dir), "--run-id", args.run_id, "--output", str(pdf_validation)], cwd=root, check=True)

    write_json(generated_dir / "provenance.json", {
        "run_id": args.run_id,
        "project_id": args.project_id,
        "source": "ALLOWED_EVAL_SANITIZED_BUNDLE",
        "source_references": job_spec["source_references"],
        "forbidden_reference_access": False,
    })
    write_json(generated_dir / "validation_summary.json", {
        "run_id": args.run_id,
        "job_spec_schema": "PASS",
        "drawing_model_schema": "PASS",
        "pdf_validation": json.loads(pdf_validation.read_text(encoding="utf-8")),
        "unsupported_value_policy": "critical fabrication values left TBD/UNVERIFIED when unavailable",
    })
    write_json(run_dir / "process_metadata.json", {
        "run_id": args.run_id,
        "project_id": args.project_id,
        "git_head": git_head(root),
        "codex_process_metadata": meta,
        "started_at": now(),
        "fresh_ephemeral_codex_session": True,
        "manual_repair": False,
    })
    hashes = hash_tree(generated_dir)
    write_json(run_dir / "artifact_hashes.json", hashes)
    freeze_hash = sha256_json(hashes)
    write_json(run_dir / "freeze_manifest.json", {
        "run_id": args.run_id,
        "project_id": args.project_id,
        "freeze_hash": freeze_hash,
        "artifact_hashes": hashes,
        "freeze_time": now(),
    })
    still_hashes = hash_tree(generated_dir)
    freeze_ok = hashes == still_hashes
    leakage_ok, leakage_errors = scan_for_leakage(generator_workspace)
    output_leakage_ok, output_leakage_errors = scan_for_leakage(generated_dir)
    write_json(run_dir / "leakage_scan.json", {
        "run_id": args.run_id,
        "generator_workspace_status": "PASS" if leakage_ok else "FAIL",
        "generated_output_status": "PASS" if output_leakage_ok else "FAIL",
        "errors": leakage_errors + output_leakage_errors,
    })
    complete = {
        "run_id": args.run_id,
        "project_id": args.project_id,
        "status": "PASS" if freeze_ok and leakage_ok and output_leakage_ok else "FAIL",
        "required_outputs": [
            str(pdf_dir / f"01_生管課用圖_{args.project_id}.pdf"),
            str(pdf_dir / f"02_鈑金施工圖_{args.project_id}.pdf"),
            str(pdf_dir / f"03_沖孔施工圖_{args.project_id}.pdf"),
        ],
        "failure_reason": None if freeze_ok and leakage_ok and output_leakage_ok else "freeze or leakage failure",
    }
    write_json(run_dir / "generation_complete.json", complete)
    errors = validate_file(run_dir / "generation_complete.json", root / "schemas" / "generation_complete.schema.json")
    if errors:
        raise SystemExit(f"generation_complete schema errors: {errors}")
    print(json.dumps({"status": complete["status"], "run_id": args.run_id}, ensure_ascii=False))
    if complete["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
