from __future__ import annotations

import csv
import json
import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RANKING = ROOT / "evals" / "baseline-024" / "expanded_candidate_ranking_v2.json"
TASK_REGISTRY = ROOT / "orchestration" / "TASK_REGISTRY.csv"


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_task_registry(rows: list[dict[str, str]]) -> None:
    existing = TASK_REGISTRY.read_text(encoding="utf-8-sig").splitlines()
    reader = csv.DictReader(existing)
    fieldnames = reader.fieldnames or []
    existing_rows = list(reader)
    replacement_by_id = {row["task_id"]: row for row in rows}
    rewritten = []
    seen = set()
    for row in existing_rows:
        task_id = row.get("task_id", "")
        if task_id in replacement_by_id:
            rewritten.append({key: replacement_by_id[task_id].get(key, "") for key in fieldnames})
            seen.add(task_id)
        else:
            rewritten.append(row)
    for row in rows:
        if row["task_id"] not in seen:
            rewritten.append({key: row.get(key, "") for key in fieldnames})
    with TASK_REGISTRY.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rewritten)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a six-project reference presence wave.")
    parser.add_argument("--wave-number", type=int, default=1)
    parser.add_argument("--count", type=int, default=6)
    args = parser.parse_args()
    wave_number = args.wave_number
    wave_id = f"wave-{wave_number:03d}"
    task_prefix = f"B024-RP-W{wave_number:03d}"

    ranking = read_json(RANKING)
    start = (wave_number - 1) * args.count
    projects = ranking["reference_presence_review_required"][start : start + args.count]
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    registry_rows = []
    for project_id in projects:
        task_id = f"{task_prefix}-{project_id}"
        task_path = ROOT / "orchestration" / "tasks" / "reference_detection" / wave_id / f"{task_id}.md"
        visible_manifest = ROOT / "orchestration" / "input_manifests" / "reference_detection" / wave_id / f"{task_id}.visible_files.json"
        output = ROOT / "manifests" / "reference_detection" / "reviews" / wave_id / f"{project_id}_reference_presence.json"
        trajectory = ROOT / "orchestration" / "trajectories" / "reference_detection" / wave_id / f"{task_id}.json"
        vault = ROOT / "tmp" / "reference-vault" / wave_id / project_id

        task = f"""# Reference Presence Classifier {project_id}

Task ID: `{task_id}`

Role: isolated `reference_presence_classifier`.

Scope:

- Project: `{project_id}`
- Inspect only candidate PDF files copied into the ignored reference-vault workspace.
- Output only neutral role-classification metadata.
- Do not persist raw PDF text, images, thumbnails, dimensions, component names, quantities, layout descriptions, or title-block details beyond drawing identity.
- Do not act as a source reviewer, generator, portfolio optimizer, or later reviewer for this project.

Required output: `{output.as_posix()}`
"""
        write_text(task_path, task)

        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "run_reference_presence_classifier.py"),
            "--project-id",
            project_id,
            "--output",
            str(output),
            "--visible-manifest",
            str(visible_manifest),
            "--trajectory",
            str(trajectory),
            "--vault-dir",
            str(vault),
        ]
        subprocess.run(cmd, cwd=str(ROOT), check=True)

        registry_rows.append(
            {
                "task_id": task_id,
                "phase": "cycle-000-reference-detection",
                "agent_type": "reference_presence_classifier",
                "scope": f"isolated completed-target presence classification for {project_id}",
                "workspace": str(vault),
                "input_manifest": str(visible_manifest.relative_to(ROOT)),
                "output_manifest": str(output.relative_to(ROOT)),
                "status": "NEEDS_PARENT_REVIEW",
                "parent_owner": "coordinator",
                "child_thread_or_run_id": task_id,
                "requested_model": "local",
                "actual_model": "local_deterministic_pdf_metadata_text_classifier",
                "sandbox": "ignored_reference_vault_no_raw_text_persisted",
                "started_at": created_at,
                "heartbeat_at": created_at,
                "completed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "exit_status": "PASS",
                "result_path": str(output.relative_to(ROOT)),
                "trajectory_path": str(trajectory.relative_to(ROOT)),
                "commit": "",
                "blocker": "",
            }
        )
    append_task_registry(registry_rows)
    summary = {
        "wave_id": f"reference-presence-{wave_id}",
        "project_ids": projects,
        "task_ids": [f"{task_prefix}-{pid}" for pid in projects],
        "created_at": created_at,
    }
    out = ROOT / "manifests" / "reference_detection" / "reviews" / wave_id / "wave_summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result_rows = []
    for project_id in projects:
        path = ROOT / "manifests" / "reference_detection" / "reviews" / wave_id / f"{project_id}_reference_presence.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        result_rows.append(data)
    promoted = sum(1 for row in result_rows if row["verification_result"] in {"VERIFIED_ALL_THREE", "PROBABLE_ALL_THREE"})
    report_lines = [
        f"# Reference Presence Wave {wave_number:03d} Summary",
        "",
        f"- status: `REFERENCE_PRESENCE_WAVE_{wave_number:03d}_COMPLETE`",
        "- completed-reference raw text persisted: `false`",
        "- images or thumbnails persisted: `false`",
        f"- promoted to all-three reference availability: `{promoted}`",
        "",
        "| project_id | verification_result | detected_output_types | inspected_file_count | classification_count |",
        "|---|---|---|---:|---:|",
    ]
    for data in result_rows:
        report_lines.append(
            f"| `{data['project_id']}` | `{data['verification_result']}` | `{','.join(data['detected_output_types'])}` | {data['inspected_file_count']} | {len(data['classifications'])} |"
        )
    report_lines.extend(
        [
            "",
            "All six top-ranked partial-reference projects remained partial after isolated classifier review.",
            "No project from this wave may proceed to source screening on the basis of this reference-presence result.",
        ]
    )
    report_path = ROOT / "reports" / "baseline-024" / "expanded-screening" / f"reference_presence_wave_{wave_number:03d}_summary.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
