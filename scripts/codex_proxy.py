from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from harness_lib import read_json, sha256_file, sha256_json, validate, validate_file, write_json


CODEX_CLI = Path(r"C:\Users\alex1\AppData\Local\OpenAI\Codex\bin\8e55c2dd143b6354\codex.exe")
PYTHON = Path(r"C:\Users\alex1\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
SUPPORTED_FEATURE_DISABLES = ["plugins", "apps", "browser_use", "image_generation"]
REQUIRED_FLAGS = [
    "--config",
    "--enable",
    "--disable",
    "--strict-config",
    "--model",
    "--sandbox",
    "--cd",
    "--add-dir",
    "--skip-git-repo-check",
    "--ephemeral",
    "--ignore-user-config",
    "--ignore-rules",
    "--output-schema",
    "--json",
    "--output-last-message",
]


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_process(cmd: list[str], cwd: Path, timeout: int, stdout_path: Path, stderr_path: Path) -> dict[str, Any]:
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        timed_out = False
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(stdout or "", encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr or "", encoding="utf-8", newline="\n")
    return {
        "command": cmd,
        "returncode": returncode,
        "timed_out": timed_out,
        "duration_seconds": round(time.time() - start, 2),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }


def probe_cli(root: Path, output_dir: Path) -> dict[str, Any]:
    version = subprocess.run([str(CODEX_CLI), "--version"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()
    help_text = subprocess.run([str(CODEX_CLI), "exec", "--help"], cwd=root, text=True, capture_output=True, check=True).stdout
    help_path = output_dir / "codex_exec_help.txt"
    help_path.parent.mkdir(parents=True, exist_ok=True)
    help_path.write_text(help_text, encoding="utf-8", newline="\n")
    missing = [flag for flag in REQUIRED_FLAGS if flag not in help_text]
    if missing:
        raise SystemExit(f"codex exec missing required flags: {missing}")
    return {
        "path": str(CODEX_CLI),
        "version": version,
        "exec_help_sha256": sha256_file(help_path),
        "supported_flags": REQUIRED_FLAGS,
        "disabled_features_for_tests": SUPPORTED_FEATURE_DISABLES,
    }


def codex_command(root: Path, out_dir: Path, role: str, prompt: str, requested_model: str = "default") -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    last_message = out_dir / "last_message.json"
    stdout = out_dir / "stdout.jsonl"
    stderr = out_dir / "stderr.log"
    cmd = [
        str(CODEX_CLI),
        "exec",
        "--ephemeral",
        "--cd",
        str(root),
        "--sandbox",
        "read-only",
    ]
    for feature in SUPPORTED_FEATURE_DISABLES:
        cmd.extend(["--disable", feature])
    cmd.extend([
        "--json",
        "--output-schema",
        str(root / "schemas" / "codex_proxy_child_output.schema.json"),
        "--output-last-message",
        str(last_message),
    ])
    if requested_model != "default":
        cmd.extend(["--model", requested_model])
    cmd.append(prompt)
    meta = run_process(cmd, root, 180, stdout, stderr)
    parsed: Any = None
    validation_errors: list[str] = []
    if last_message.exists():
        text = last_message.read_text(encoding="utf-8-sig").strip()
        try:
            parsed = json.loads(text)
            validation_errors = validate(parsed, read_json(root / "schemas" / "codex_proxy_child_output.schema.json"))
        except Exception as exc:
            validation_errors = [f"FINAL_OUTPUT_PARSE_ERROR:{type(exc).__name__}:{exc}"]
    else:
        validation_errors = ["MISSING_LAST_MESSAGE"]
    meta.update({
        "role": role,
        "requested_model": requested_model,
        "actual_model": parsed.get("actual_model") if isinstance(parsed, dict) else "NOT_REPORTED",
        "actual_model_recording_status": "RECORDED_FROM_CHILD_OUTPUT" if isinstance(parsed, dict) else "NOT_REPORTED",
        "last_message_path": str(last_message),
        "parsed_output": parsed,
        "validation_errors": validation_errors,
    })
    write_json(out_dir / "process_metadata.json", meta)
    return meta


def write_synthetic_job_and_model(root: Path, output_dir: Path) -> dict[str, Path]:
    job_spec = {
        "schema_version": "job_spec_v0",
        "project": {
            "project_id": "SYNTH-CJK-001",
            "customer": "合成客戶",
            "project_name": "合成校驗盤",
            "revision": "synthetic"
        },
        "panels": [{"panel_id": "P1", "width": 600, "height": 800}],
        "materials": [],
        "devices": [],
        "cutouts": [],
        "source_references": [{"source_id": "SYNTH", "kind": "fixture"}],
        "conflicts": [],
        "unresolved_fields": [{"field": "material", "status": "TBD"}],
    }
    job_path = output_dir / "合成路徑" / "job_spec_SYNTH-CJK-001.json"
    write_json(job_path, job_spec)
    model = {
        "schema_version": "drawing_model_v0",
        "project_id": "SYNTH-CJK-001",
        "job_spec_hash": sha256_json(job_spec),
        "units": "mm",
        "model_version": "synthetic",
        "panels": [
            {
                "panel_id": "P1",
                "width": 600,
                "height": 800,
                "material": None,
                "thickness": None,
                "devices": [],
                "cutouts": [],
                "verification_status": "TBD"
            }
        ],
        "renderer_visibility": {"production": ["P1"], "sheetmetal": ["P1"], "punch": ["P1"]},
        "unresolved_regions": [],
        "provenance": [{"source_id": "SYNTH"}],
    }
    model_path = output_dir / "合成路徑" / "drawing_model_SYNTH-CJK-001.json"
    write_json(model_path, model)
    subprocess.run([str(PYTHON), "scripts/validate_job_spec.py", str(job_path)], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run([str(PYTHON), "scripts/validate_drawing_model.py", str(model_path)], cwd=root, check=True, capture_output=True, text=True)
    pdf_dir = output_dir / "合成路徑" / "pdfs"
    subprocess.run([str(PYTHON), "scripts/render_pdf_outputs.py", str(model_path), "--output-dir", str(pdf_dir), "--run-id", "CODEX-PROXY-SYNTH"], cwd=root, check=True, capture_output=True, text=True)
    validation_path = output_dir / "合成路徑" / "pdf_validation.json"
    subprocess.run([str(PYTHON), "scripts/validate_pdf_package.py", "--project-id", "SYNTH-CJK-001", "--pdf-dir", str(pdf_dir), "--run-id", "CODEX-PROXY-SYNTH", "--output", str(validation_path)], cwd=root, check=True, capture_output=True, text=True)
    return {"job_spec": job_path, "drawing_model": model_path, "pdf_dir": pdf_dir, "pdf_validation": validation_path}


def detect_sentinel_or_escape(path: Path, frozen_hashes: dict[str, str] | None = None) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for file in path.rglob("*"):
        if file.is_symlink():
            errors.append(f"SYMLINK:{file}")
        if file.is_file():
            rel = file.relative_to(path)
            if ".." in rel.parts:
                errors.append(f"PATH_TRAVERSAL:{rel}")
            try:
                text = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = ""
            if "reference_only_sentinel" in text or "completed_target" in text:
                errors.append(f"REFERENCE_SENTINEL:{rel}")
            if r"C:\Users\alex1\OneDrive\Desktop\All Projects" in text:
                errors.append(f"ABSOLUTE_SOURCE_PATH:{rel}")
            if frozen_hashes and str(rel) in frozen_hashes and sha256_file(file) != frozen_hashes[str(rel)]:
                errors.append(f"POST_FREEZE_MUTATION:{rel}")
    return (not errors, errors)


def synthetic_suite(args: argparse.Namespace) -> None:
    root = Path.cwd()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    cli = probe_cli(root, out)
    tests: list[dict[str, Any]] = []

    def add_test(name: str, ok: bool, evidence: str, artifacts: list[Path] | None = None) -> None:
        tests.append({
            "name": name,
            "status": "PASS" if ok else "FAIL",
            "evidence": evidence,
            "artifacts": [str(p) for p in (artifacts or [])],
        })

    generator_prompt = (
        "Synthetic fixture only. Return exactly one JSON object with keys role,status,project_id,outputs,actual_model,notes. "
        "Use role mock_case_generator, status PASS, project_id SYNTH-CJK-001, outputs [\"production\",\"sheetmetal\",\"punch\"], actual_model unknown."
    )
    gen_meta = codex_command(root, out / "successful_generator_run", "mock_case_generator", generator_prompt)
    add_test(
        "successful generator run",
        gen_meta["returncode"] == 0 and not gen_meta["validation_errors"] and gen_meta["parsed_output"]["role"] == "mock_case_generator",
        f"returncode={gen_meta['returncode']} validation_errors={gen_meta['validation_errors']}",
        [Path(gen_meta["stdout_path"]), Path(gen_meta["stderr_path"]), Path(gen_meta["last_message_path"]), out / "successful_generator_run" / "process_metadata.json"],
    )

    reviewer_prompt = (
        "Synthetic fixture only. Return exactly one JSON object with keys role,status,project_id,outputs,actual_model,notes. "
        "Use role project_reviewer, status PASS, project_id SYNTH-CJK-001, outputs [\"review\"], actual_model unknown."
    )
    review_meta = codex_command(root, out / "successful_reviewer_run", "project_reviewer", reviewer_prompt)
    add_test(
        "successful independent reviewer run",
        review_meta["returncode"] == 0 and not review_meta["validation_errors"] and review_meta["parsed_output"]["role"] == "project_reviewer",
        f"returncode={review_meta['returncode']} validation_errors={review_meta['validation_errors']}",
        [Path(review_meta["stdout_path"]), Path(review_meta["stderr_path"]), Path(review_meta["last_message_path"]), out / "successful_reviewer_run" / "process_metadata.json"],
    )

    malformed_dir = out / "malformed_final_output"
    malformed_dir.mkdir(parents=True, exist_ok=True)
    malformed = malformed_dir / "last_message.txt"
    malformed.write_text("not json", encoding="utf-8")
    try:
        json.loads(malformed.read_text(encoding="utf-8"))
        malformed_ok = False
    except json.JSONDecodeError:
        malformed_ok = True
    add_test("malformed final output", malformed_ok, "Synthetic malformed final output rejected.", [malformed])

    schema_dir = out / "schema_failure"
    schema_dir.mkdir(parents=True, exist_ok=True)
    schema_file = schema_dir / "bad_output.json"
    write_json(schema_file, {"role": "mock_case_generator", "status": "PASS"})
    schema_errors = validate_file(schema_file, root / "schemas" / "codex_proxy_child_output.schema.json")
    add_test("schema failure", bool(schema_errors), f"schema_errors={schema_errors}", [schema_file])

    timeout_meta = run_process([str(PYTHON), "-c", "import time; time.sleep(2)"], root, 1, out / "timeout" / "stdout.log", out / "timeout" / "stderr.log")
    write_json(out / "timeout" / "process_metadata.json", timeout_meta)
    add_test("timeout", timeout_meta["timed_out"], f"timed_out={timeout_meta['timed_out']}", [out / "timeout" / "process_metadata.json"])

    nonzero_meta = run_process([str(PYTHON), "-c", "raise SystemExit(7)"], root, 10, out / "nonzero_exit" / "stdout.log", out / "nonzero_exit" / "stderr.log")
    write_json(out / "nonzero_exit" / "process_metadata.json", nonzero_meta)
    add_test("nonzero exit", nonzero_meta["returncode"] == 7, f"returncode={nonzero_meta['returncode']}", [out / "nonzero_exit" / "process_metadata.json"])

    sentinel_dir = out / "reference_sentinel_exposure"
    sentinel_dir.mkdir(parents=True, exist_ok=True)
    (sentinel_dir / "visible.txt").write_text("reference_only_sentinel", encoding="utf-8")
    ok, errors = detect_sentinel_or_escape(sentinel_dir)
    add_test("reference sentinel exposure", not ok and any("REFERENCE_SENTINEL" in e for e in errors), f"errors={errors}", [sentinel_dir / "visible.txt"])

    escape_dir = out / "path_escape"
    escape_dir.mkdir(parents=True, exist_ok=True)
    (escape_dir / "path.txt").write_text(r"C:\Users\alex1\OneDrive\Desktop\All Projects\secret", encoding="utf-8")
    ok, errors = detect_sentinel_or_escape(escape_dir)
    add_test("path escape", not ok and any("ABSOLUTE_SOURCE_PATH" in e for e in errors), f"errors={errors}", [escape_dir / "path.txt"])

    freeze_dir = out / "post_freeze_mutation"
    freeze_dir.mkdir(parents=True, exist_ok=True)
    frozen = freeze_dir / "artifact.txt"
    frozen.write_text("before", encoding="utf-8")
    frozen_hashes = {"artifact.txt": sha256_file(frozen)}
    frozen.write_text("after", encoding="utf-8")
    ok, errors = detect_sentinel_or_escape(freeze_dir, frozen_hashes)
    add_test("post-freeze mutation", not ok and any("POST_FREEZE_MUTATION" in e for e in errors), f"errors={errors}", [frozen])

    pdf_artifacts = write_synthetic_job_and_model(root, out / "pdf_generation_and_cjk_paths")
    pdf_validation = read_json(pdf_artifacts["pdf_validation"])
    add_test(
        "CJK file paths",
        "合成路徑" in str(pdf_artifacts["job_spec"]) and pdf_artifacts["job_spec"].exists(),
        f"job_spec={pdf_artifacts['job_spec']}",
        [pdf_artifacts["job_spec"], pdf_artifacts["drawing_model"]],
    )
    add_test(
        "PDF generation and validation",
        pdf_validation.get("validity") == "PASS",
        f"validity={pdf_validation.get('validity')} failures={pdf_validation.get('hard_gate_failures')}",
        [pdf_artifacts["pdf_validation"]],
    )

    add_test(
        "requested versus actual model recording",
        all("requested_model" in meta and "actual_model" in meta for meta in [gen_meta, review_meta]),
        f"generator={gen_meta.get('requested_model')}->{gen_meta.get('actual_model')} reviewer={review_meta.get('requested_model')}->{review_meta.get('actual_model')}",
        [out / "successful_generator_run" / "process_metadata.json", out / "successful_reviewer_run" / "process_metadata.json"],
    )

    status = "CODEX_PROXY_READY_FOR_ONE_PROJECT_CALIBRATION" if all(t["status"] == "PASS" for t in tests) else "CODEX_PROXY_NOT_READY"
    result = {
        "gate_id": "codex_proxy_synthetic_gate_v1",
        "status": status,
        "created_at": now(),
        "cli": cli,
        "tests": tests,
        "summary": {
            "pass_count": sum(1 for t in tests if t["status"] == "PASS"),
            "fail_count": sum(1 for t in tests if t["status"] == "FAIL"),
            "network_or_external_data_note": "Only synthetic prompts and fixtures were sent through codex exec.",
        },
    }
    write_json(out / "codex_proxy_synthetic_gate.json", result)
    errors = validate_file(out / "codex_proxy_synthetic_gate.json", root / "schemas" / "codex_proxy_gate.schema.json")
    if errors:
        raise SystemExit(f"codex proxy gate schema errors: {errors}")
    print(json.dumps({"status": status, "pass_count": result["summary"]["pass_count"], "fail_count": result["summary"]["fail_count"]}, ensure_ascii=False))
    if status != "CODEX_PROXY_READY_FOR_ONE_PROJECT_CALIBRATION":
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local codex exec proxy and synthetic gate.")
    sub = parser.add_subparsers(dest="command", required=True)
    suite = sub.add_parser("synthetic-suite")
    suite.add_argument("--output-dir", type=Path, default=Path("reports/codex_proxy_synthetic"))
    suite.set_defaults(func=synthetic_suite)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
