from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

LEGACY_MANIFEST = ROOT / "evals" / "baseline-024" / "frozen_workflow_manifest.json"
LEGACY_ATTESTATION = ROOT / "evals" / "baseline-024" / "frozen_workflow_attestation.json"
ACTIVE_MANIFEST = ROOT / "evals" / "sheetmetal-v1" / "frozen_workflow_manifest.json"

TEMP_ROOT = ROOT / "tmp" / "frozen_workflow_verification"

LEGACY_SCOPE = "LEGACY_BASELINE_024"
ACTIVE_SCOPE = "SHEETMETAL_V1_ACTIVE"
ACTIVE_GOAL = "SHEETMETAL_FIRST_MODULAR_PANEL_MODEL_V1"

VERIFICATION_ALGORITHM = "sha256-file-v1;git-worktree-detached;core.autocrlf=false"

LEGACY_HASH_PATHS = {
    "master_spec": "CODEX_MASTER_CUSTOM_GPT_DRAWING_WORKFLOW.txt",
    "agents_md": "AGENTS.md",
    "instructions": "gpt-config/INSTRUCTIONS.md",
    "production_knowledge_readme": "knowledge/production/README.md",
    "job_spec_schema": "schemas/job_spec.schema.json",
    "drawing_model_schema": "schemas/drawing_model.schema.json",
    "renderer": "scripts/render_pdf_outputs.py",
    "validator_pdf": "scripts/validate_pdf_package.py",
    "grading_profile_v2": "evals/grading_profiles/plc_layout_v2.json",
    "evaluator_scoring": "scripts/evaluator_scoring.py",
    "tolerance_profile": "evals/tolerance_profiles/plc_layout_tolerances_v1.json",
    "source_guard_policy": "manifests/source_guard/source_guard_policy.json",
    "autonomous_source_approval_spec": "docs/specs/AUTONOMOUS_EVAL_SOURCE_APPROVAL.md",
    "sanitized_bundle_spec": "docs/specs/SANITIZED_GENERATOR_BUNDLE_SPEC.md",
    "baseline_protocol": "docs/specs/24_PROJECT_BASELINE_PROTOCOL.md",
}

DYNAMIC_EVIDENCE_FILES = {
    "docs/01_CURRENT_STATE.md",
    "docs/06_EVAL_LEDGER.md",
    "docs/07_CHANGELOG.md",
    "docs/SESSION_CHECKPOINT.md",
    "orchestration/TASK_REGISTRY.csv",
    "orchestration/NEXT_THREAD_PROMPT.txt",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def bundled_dependency_root() -> Path:
    return Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"


def bundled_git() -> Path:
    return bundled_dependency_root() / "native" / "git" / "cmd" / "git.exe"


def git_executable() -> str:
    bundled = bundled_git()
    if bundled.exists():
        return str(bundled)
    found = shutil.which("git")
    return found or str(bundled)


def run_git(args: list[str], *, cwd: Path = ROOT, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [git_executable(), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git command failed")
    return result


def commit_exists(commit: str) -> bool:
    if not commit:
        return False
    result = run_git(["cat-file", "-e", f"{commit}^{{commit}}"])
    return result.returncode == 0


def current_head() -> str:
    return run_git(["rev-parse", "HEAD"], check=True).stdout.strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    result = run_git(["merge-base", "--is-ancestor", ancestor, descendant])
    return result.returncode == 0


def tracked_path(rel_path: str) -> bool:
    result = run_git(["ls-files", "--error-unmatch", "--", rel_path])
    return result.returncode == 0


def normalize_rel(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def hash_checks_in_directory(root: Path, expected_hashes: dict[str, str], path_map: dict[str, str]) -> list[dict[str, str]]:
    checks = []
    for key, rel_path in path_map.items():
        expected = str(expected_hashes.get(key, "")).upper()
        path = root / rel_path
        actual = sha256_file(path) if path.exists() else ""
        status = "PASS" if expected and actual == expected else "FAIL"
        checks.append(
            {
                "key": key,
                "path": rel_path,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "status": status,
            }
        )
    return checks


def cleanup_temp_root() -> bool:
    if TEMP_ROOT.exists() and not any(TEMP_ROOT.iterdir()):
        TEMP_ROOT.rmdir()
    return not TEMP_ROOT.exists()


def long_path(path: Path) -> str:
    resolved = str(path.resolve(strict=False))
    if sys.platform == "win32" and not resolved.startswith("\\\\?\\"):
        return "\\\\?\\" + resolved
    return resolved


def remove_owned_temp_tree(path: Path) -> bool:
    temp_root = TEMP_ROOT.resolve(strict=False)
    target = path.resolve(strict=False)
    try:
        target.relative_to(temp_root)
    except ValueError:
        return False
    if not target.exists():
        return True
    shutil.rmtree(long_path(target))
    return not target.exists()


def verify_hashes_at_commit(
    commit: str,
    manifest: dict[str, Any],
    path_map: dict[str, str],
    *,
    worktree_name: str = "legacy-baseline-024",
) -> dict[str, Any]:
    worktree_path = TEMP_ROOT / worktree_name
    cleanup = {
        "worktree_path": str(worktree_path.relative_to(ROOT)),
        "worktree_removed": False,
        "git_worktree_prune_status": "NOT_RUN",
        "verification_root_removed": False,
        "remaining_path_exists": False,
    }
    if worktree_path.exists():
        cleanup["remaining_path_exists"] = True
        return {
            "status": "FAIL",
            "error": "TEMP_WORKTREE_PATH_ALREADY_EXISTS",
            "verified_file_count": 0,
            "hashes": [],
            "temporary_worktree_cleanup": cleanup,
        }
    if not commit_exists(commit):
        cleanup["verification_root_removed"] = cleanup_temp_root()
        return {
            "status": "FAIL",
            "error": "MISSING_ANCHOR_COMMIT",
            "verified_file_count": 0,
            "hashes": [],
            "temporary_worktree_cleanup": cleanup,
        }

    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    added = False
    checks: list[dict[str, str]] = []
    error = ""
    try:
        add = run_git(
            [
                "-c",
                "core.longpaths=true",
                "-c",
                "core.autocrlf=false",
                "worktree",
                "add",
                "--detach",
                str(worktree_path),
                commit,
            ]
        )
        if add.returncode != 0:
            error = add.stderr.strip() or add.stdout.strip() or "git worktree add failed"
        else:
            added = True
            checks = hash_checks_in_directory(worktree_path, manifest.get("hashes", {}), path_map)
    finally:
        if added:
            remove = run_git(["worktree", "remove", "--force", str(worktree_path)])
            if worktree_path.exists():
                remove_owned_temp_tree(worktree_path)
            cleanup["worktree_removed"] = not worktree_path.exists()
        prune = run_git(["worktree", "prune"])
        cleanup["git_worktree_prune_status"] = "PASS" if prune.returncode == 0 else "FAIL"
        cleanup["remaining_path_exists"] = worktree_path.exists()
        cleanup["verification_root_removed"] = cleanup_temp_root()

    failures = [row for row in checks if row["status"] != "PASS"]
    status = "PASS" if checks and not failures and not error and cleanup["worktree_removed"] and not cleanup["remaining_path_exists"] else "FAIL"
    result = {
        "status": status,
        "verified_file_count": len(checks),
        "hashes": checks,
        "temporary_worktree_cleanup": cleanup,
    }
    if error:
        result["error"] = error
    return result


def build_legacy_attestation(
    *,
    manifest_path: Path = LEGACY_MANIFEST,
    anchor_commit: str = "fac44321491633181f1fa53a062084d072b0b582",
    output_path: Path | None = None,
    worktree_name: str = "legacy-baseline-024",
) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    reproduced = verify_hashes_at_commit(anchor_commit, manifest, LEGACY_HASH_PATHS, worktree_name=worktree_name)
    attestation = {
        "manifest_path": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
        "manifest_sha256": sha256_file(manifest_path),
        "resolved_historical_anchor_commit": anchor_commit,
        "verification_algorithm": VERIFICATION_ALGORITHM,
        "verified_file_count": reproduced["verified_file_count"],
        "status": reproduced["status"],
        "hashes": reproduced["hashes"],
        "temporary_worktree_cleanup": reproduced["temporary_worktree_cleanup"],
        "verification_timestamp": now(),
    }
    if output_path is not None:
        write_json(output_path, attestation)
    return attestation


def compare_hash_rows(left: list[dict[str, str]], right: list[dict[str, str]]) -> bool:
    keys = ["key", "path", "expected_sha256", "actual_sha256", "status"]
    left_norm = [{key: row.get(key, "") for key in keys} for row in left]
    right_norm = [{key: row.get(key, "") for key in keys} for row in right]
    return left_norm == right_norm


def verify_legacy_scope(
    *,
    manifest_path: Path = LEGACY_MANIFEST,
    attestation_path: Path = LEGACY_ATTESTATION,
    attestation: dict[str, Any] | None = None,
    worktree_name: str = "legacy-baseline-024",
) -> dict[str, Any]:
    if attestation is None:
        if not attestation_path.exists():
            return {"scope": LEGACY_SCOPE, "status": "FAIL", "error": "LEGACY_ATTESTATION_MISSING"}
        attestation = read_json(attestation_path)

    manifest = read_json(manifest_path)
    manifest_hash = sha256_file(manifest_path)
    failures = []
    expected_manifest_path = str(manifest_path.relative_to(ROOT)).replace("\\", "/")
    if attestation.get("manifest_path") != expected_manifest_path:
        failures.append("MANIFEST_PATH_MISMATCH")
    if str(attestation.get("manifest_sha256", "")).upper() != manifest_hash:
        failures.append("MANIFEST_HASH_MISMATCH")
    if attestation.get("verification_algorithm") != VERIFICATION_ALGORITHM:
        failures.append("VERIFICATION_ALGORITHM_MISMATCH")
    anchor = str(attestation.get("resolved_historical_anchor_commit", ""))
    if not commit_exists(anchor):
        failures.append("MISSING_ANCHOR_COMMIT")
        return {
            "scope": LEGACY_SCOPE,
            "status": "FAIL",
            "manifest_sha256": manifest_hash,
            "resolved_historical_anchor_commit": anchor,
            "failures": failures,
        }

    reproduced = verify_hashes_at_commit(anchor, manifest, LEGACY_HASH_PATHS, worktree_name=worktree_name)
    if reproduced["status"] != "PASS":
        failures.append("HISTORICAL_HASH_REPRODUCTION_FAIL")
    if int(attestation.get("verified_file_count", -1)) != reproduced["verified_file_count"]:
        failures.append("VERIFIED_FILE_COUNT_MISMATCH")
    if str(attestation.get("status", "")) != reproduced["status"]:
        failures.append("ATTESTED_STATUS_MISMATCH")
    if not compare_hash_rows(attestation.get("hashes", []), reproduced["hashes"]):
        failures.append("ATTESTED_HASH_ROWS_MISMATCH")
    cleanup = reproduced["temporary_worktree_cleanup"]
    if cleanup.get("remaining_path_exists") or cleanup.get("git_worktree_prune_status") != "PASS":
        failures.append("TEMP_WORKTREE_CLEANUP_FAIL")

    return {
        "scope": LEGACY_SCOPE,
        "status": "PASS" if not failures else "FAIL",
        "manifest_sha256": manifest_hash,
        "resolved_historical_anchor_commit": anchor,
        "verified_file_count": reproduced["verified_file_count"],
        "failures": failures,
        "hashes": reproduced["hashes"],
        "temporary_worktree_cleanup": cleanup,
    }


def verify_active_manifest_data(manifest: dict[str, Any], *, manifest_path: Path = ACTIVE_MANIFEST) -> dict[str, Any]:
    failures = []
    if manifest.get("scope") != ACTIVE_SCOPE:
        failures.append("SCOPE_MISMATCH")
    if manifest.get("active_goal") != ACTIVE_GOAL:
        failures.append("ACTIVE_GOAL_MISMATCH")
    if str(manifest.get("hash_algorithm", "")).upper() not in {"SHA-256", "SHA256"}:
        failures.append("HASH_ALGORITHM_MISMATCH")
    if manifest.get("supersedes_historical_manifest") is not False:
        failures.append("HISTORICAL_SUPERSESSION_NOT_FALSE")

    anchor = str(manifest.get("anchor_commit", ""))
    head = current_head()
    if not commit_exists(anchor):
        failures.append("MISSING_ANCHOR_COMMIT")
    elif not is_ancestor(anchor, head):
        failures.append("ANCHOR_NOT_IN_CURRENT_LINEAGE")

    file_checks = []
    for row in manifest.get("files", []):
        rel_path = normalize_rel(str(row.get("path", "")))
        expected = str(row.get("sha256", "")).upper()
        check = {"path": rel_path, "expected_sha256": expected, "actual_sha256": "", "status": "FAIL", "tracked": False}
        if rel_path in DYNAMIC_EVIDENCE_FILES or rel_path.startswith("reports/") or rel_path.endswith("_queue.json"):
            check["status"] = "FAIL"
            check["reason"] = "DYNAMIC_EVIDENCE_FILE_IN_ACTIVE_FREEZE"
            failures.append(f"DYNAMIC_FILE_INCLUDED:{rel_path}")
        elif not tracked_path(rel_path):
            check["reason"] = "UNTRACKED_OR_MISSING_FROM_GIT"
            failures.append(f"UNTRACKED_FILE:{rel_path}")
        else:
            path = ROOT / rel_path
            check["tracked"] = True
            if path.exists():
                check["actual_sha256"] = sha256_file(path)
                check["status"] = "PASS" if expected and check["actual_sha256"] == expected else "FAIL"
                if check["status"] != "PASS":
                    failures.append(f"HASH_MISMATCH:{rel_path}")
            else:
                check["reason"] = "MISSING_FILE"
                failures.append(f"MISSING_FILE:{rel_path}")
        file_checks.append(check)

    if not file_checks:
        failures.append("NO_FILES_IN_ACTIVE_MANIFEST")

    return {
        "scope": ACTIVE_SCOPE,
        "status": "PASS" if not failures else "FAIL",
        "manifest_path": str(manifest_path.relative_to(ROOT)).replace("\\", "/") if manifest_path.is_absolute() else str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path) if manifest_path.exists() else "",
        "anchor_commit": anchor,
        "current_head": head,
        "verified_file_count": len(file_checks),
        "failures": failures,
        "files": file_checks,
    }


def verify_active_scope(*, manifest_path: Path = ACTIVE_MANIFEST) -> dict[str, Any]:
    if not manifest_path.exists():
        return {"scope": ACTIVE_SCOPE, "status": "FAIL", "error": "ACTIVE_MANIFEST_MISSING"}
    manifest = read_json(manifest_path)
    return verify_active_manifest_data(manifest, manifest_path=manifest_path)


def resolve_unique_legacy_anchor(candidate_results: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [row for row in candidate_results if row.get("status") == "PASS"]
    if len(passing) == 1:
        return {"status": "PASS", "resolved_historical_anchor_commit": passing[0].get("commit", "")}
    if not passing:
        return {"status": "FAIL", "error": "LEGACY_FROZEN_WORKFLOW_ANCHOR_UNRESOLVED"}
    return {"status": "FAIL", "error": "AMBIGUOUS_LEGACY_ANCHOR", "passing_candidates": [row.get("commit", "") for row in passing]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify scoped frozen workflow manifests.")
    parser.add_argument("--scope", required=True, choices=["legacy-baseline-024", "sheetmetal-v1-active"])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--attestation", type=Path)
    parser.add_argument("--write-attestation", action="store_true")
    args = parser.parse_args()

    if args.scope == "legacy-baseline-024":
        manifest_path = args.manifest or LEGACY_MANIFEST
        attestation_path = args.attestation or LEGACY_ATTESTATION
        if args.write_attestation:
            result = build_legacy_attestation(manifest_path=manifest_path, output_path=attestation_path)
        else:
            result = verify_legacy_scope(manifest_path=manifest_path, attestation_path=attestation_path)
    else:
        if args.write_attestation:
            result = {"scope": ACTIVE_SCOPE, "status": "FAIL", "error": "ACTIVE_SCOPE_DOES_NOT_WRITE_ATTESTATION"}
        else:
            result = verify_active_scope(manifest_path=args.manifest or ACTIVE_MANIFEST)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.get("status") == "PASS" else 1)


if __name__ == "__main__":
    main()
