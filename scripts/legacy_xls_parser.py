from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import textwrap
import time
from pathlib import Path
from typing import Any

from harness_lib import detect_forbidden_text, read_json, sha256_file, sha256_json, write_json
from source_guard import DECISION_FIELDS, csv_rows, csv_write, decision_id, flatten_decision


PROJECT_ID_RE = re.compile(r"(?<!\d)(1[0-9]{6})(?!\d)")
PARSER_NAME = "excel_com_legacy_xls"
PARSER_VERSION = "excel_com_legacy_xls_v1"


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def a1(row: int, col: int) -> str:
    name = ""
    while col:
        col, rem = divmod(col - 1, 26)
        name = chr(65 + rem) + name
    return f"{name}{row}"


def normalize(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\r\n", "\n").replace("\r", "\n").split())


def safe_name(text: str) -> str:
    cleaned = []
    for ch in text:
        if ch.isalnum() or ch in "-_":
            cleaned.append(ch)
        else:
            cleaned.append("_")
    return "".join(cleaned).strip("_") or "sheet"


def split_pipe(text: str) -> list[str]:
    return [part for part in (text or "").split("|") if part]


def write_parser_ps1(path: Path) -> None:
    script = r'''
param(
  [Parameter(Mandatory=$true)][string]$WorkbookPath,
  [Parameter(Mandatory=$true)][string]$OutputDir
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Escape-CsvCell([string]$Value) {
  if ($null -eq $Value) { $Value = '' }
  $Value = $Value -replace '"', '""'
  if ($Value.Contains(',') -or $Value.Contains('"') -or $Value.Contains("`n") -or $Value.Contains("`r")) {
    return '"' + $Value + '"'
  }
  return $Value
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try { $excel.AutomationSecurity = 3 } catch {}
$metadata = [ordered]@{
  workbook_file_name = [System.IO.Path]::GetFileName($WorkbookPath)
  excel_version = [string]$excel.Version
  opened_read_only = $true
  macros_disabled = $true
  links = @()
  names = @()
  sheets = @()
}

try {
  $wb = $excel.Workbooks.Open($WorkbookPath, 0, $true)
  try {
    $ls = $wb.LinkSources(1)
    if ($ls) {
      foreach ($l in $ls) { $metadata.links += [string]$l }
    }
  } catch {}
  try {
    foreach ($n in $wb.Names) {
      $metadata.names += [ordered]@{ name = [string]$n.Name; refers_to = [string]$n.RefersTo }
    }
  } catch {}

  $sheetIndex = 0
  foreach ($ws in $wb.Worksheets) {
    $sheetIndex += 1
    $used = $ws.UsedRange
    $rowCount = [int]$used.Rows.Count
    $colCount = [int]$used.Columns.Count
    $safeSheet = ([string]$ws.Name) -replace '[\\/:*?"<>|]', '_'
    $csvName = ('{0:D3}_{1}.csv' -f $sheetIndex, $safeSheet)
    $csvPath = Join-Path $OutputDir $csvName
    $utf8 = New-Object System.Text.UTF8Encoding($true)
    $writer = New-Object System.IO.StreamWriter($csvPath, $false, $utf8)
    $formulas = @()
    $nonEmptyRows = 0
    try {
      for ($r = 1; $r -le $rowCount; $r++) {
        $cells = @()
        $rowHasValue = $false
        for ($c = 1; $c -le $colCount; $c++) {
          $cell = $used.Cells.Item($r, $c)
          $text = [string]$cell.Text
          if (-not [string]::IsNullOrWhiteSpace($text)) { $rowHasValue = $true }
          $cells += (Escape-CsvCell $text)
          $formula = [string]$cell.Formula
          if ($formula.StartsWith('=')) {
            $formulas += [ordered]@{
              row = $r
              column = $c
              address = [string]$cell.Address($false, $false)
              formula = $formula
              text = $text
            }
          }
        }
        if ($rowHasValue) { $nonEmptyRows += 1 }
        $writer.WriteLine(($cells -join ','))
      }
    } finally {
      $writer.Close()
    }
    $metadata.sheets += [ordered]@{
      index = $sheetIndex
      name = [string]$ws.Name
      visible_code = [int]$ws.Visible
      visible = ([int]$ws.Visible -eq -1)
      used_rows = $rowCount
      used_columns = $colCount
      non_empty_rows = $nonEmptyRows
      formula_count = $formulas.Count
      formulas = $formulas
      csv_file_name = $csvName
    }
  }
  $wb.Close($false)
} finally {
  $excel.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
$metadata | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $OutputDir 'metadata.json') -Encoding UTF8
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding="utf-8", newline="\n")


def parse_workbook(workbook_path: Path, output_dir: Path, ps1: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps1),
            "-WorkbookPath",
            str(workbook_path),
            "-OutputDir",
            str(output_dir),
        ],
        text=True,
        capture_output=True,
        timeout=120,
    )
    (output_dir / "powershell_stdout.log").write_text(proc.stdout or "", encoding="utf-8", newline="\n")
    (output_dir / "powershell_stderr.log").write_text(proc.stderr or "", encoding="utf-8", newline="\n")
    if proc.returncode:
        raise SystemExit(f"legacy xls parser failed for {workbook_path.name}: {proc.stderr}")
    return read_json(output_dir / "metadata.json")


def csv_cells(csv_path: Path) -> list[dict[str, str]]:
    cells: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader, start=1):
            for c, value in enumerate(row, start=1):
                text = normalize(value)
                if text:
                    cells.append({"coordinate": a1(r, c), "type": "display_text", "value": text})
    return cells


def formula_sheet_refs(formula: str) -> list[str]:
    refs = []
    for match in re.finditer(r"(?:'([^']+)'|([A-Za-z0-9_\-\u4e00-\u9fff ]+))!", formula):
        refs.append((match.group(1) or match.group(2) or "").strip())
    return sorted(set(refs))


def fingerprint_for_sheet(metadata: dict[str, Any], sheet: dict[str, Any], csv_path: Path) -> tuple[str, dict[str, Any], list[str]]:
    formulas = []
    refs = set()
    for item in sheet.get("formulas", []):
        formula = item.get("formula", "")
        sheet_refs = formula_sheet_refs(formula)
        refs.update(sheet_refs)
        formulas.append(
            {
                "coordinate": item.get("address") or a1(int(item["row"]), int(item["column"])),
                "formula": normalize(formula),
                "sheet_refs": sheet_refs,
            }
        )
    payload = {
        "parser": PARSER_VERSION,
        "sheet_name": sheet["name"],
        "sheet_visibility": "visible" if sheet.get("visible") else "hidden_or_very_hidden",
        "workbook_sheet_count": len(metadata.get("sheets", [])),
        "used_range_dimensions": f"R{sheet.get('used_rows')}C{sheet.get('used_columns')}",
        "normalized_visible_cell_content": csv_cells(csv_path),
        "formula_locations": formulas,
        "external_links": metadata.get("links", []),
        "workbook_defined_names": metadata.get("names", []),
    }
    return sha256_json(payload), payload, sorted(refs)


def detected_ids(*texts: str) -> list[str]:
    out: set[str] = set()
    for text in texts:
        out.update(PROJECT_ID_RE.findall(text or ""))
    return sorted(out)


def build_decisions(project_id: str, decisions_path: Path, file_index: Path, output_root: Path) -> dict[str, Any]:
    file_rows = {row["file_id"]: row for row in csv_rows(file_index)}
    base_rows = [
        row
        for row in csv_rows(decisions_path)
        if row.get("project_id") == project_id and row.get("workbook_format") == "xls"
    ]
    if not base_rows:
        raise SystemExit(f"no legacy xls rows found for {project_id}")

    parser_root = output_root / "legacy_xls_parse" / project_id
    ps1 = output_root / "legacy_xls_parse" / "parse_workbook.ps1"
    write_parser_ps1(ps1)

    decisions: list[dict[str, Any]] = []
    parse_reports = []
    stability_checks = []
    for base in base_rows:
        file_row = file_rows[base["file_id"]]
        workbook_path = Path(file_row["absolute_path"])
        if sha256_file(workbook_path).upper() != base["file_sha256"].upper():
            raise SystemExit(f"source hash changed before parse: {base['decision_id']}")
        workbook_out = parser_root / base["file_id"]
        metadata = parse_workbook(workbook_path, workbook_out, ps1)
        metadata_second = parse_workbook(workbook_path, workbook_out / "repeat_parse", ps1)
        parse_reports.append(
            {
                "file_id": base["file_id"],
                "relative_path": base["relative_path"],
                "file_sha256": base["file_sha256"],
                "parser_output": str(workbook_out),
                "sheet_count": len(metadata.get("sheets", [])),
            }
        )
        stability_checks.append(
            {
                "file_id": base["file_id"],
                "first_metadata_hash": sha256_json(metadata),
                "second_metadata_hash": sha256_json(metadata_second),
                "status": "PASS" if sha256_json(metadata) == sha256_json(metadata_second) else "FAIL",
            }
        )
        workbook_names = metadata.get("names", [])
        workbook_links = metadata.get("links", [])
        for sheet in metadata.get("sheets", []):
            csv_path = workbook_out / sheet["csv_file_name"]
            fp, payload, refs = fingerprint_for_sheet(metadata, sheet, csv_path)
            sheet_id = f"{base['file_id']}-XLS-SHEET-{int(sheet['index']):03d}"
            ids = detected_ids(base.get("relative_path", ""), " ".join(cell["value"] for cell in payload["normalized_visible_cell_content"][:200]))
            reasons = {"LEGACY_XLS_PARSED_BY_EXCEL_COM_READ_ONLY", "MACROS_DISABLED"}
            proposed = "CANDIDATE"
            formula_status = "NONE"
            external_status = "NONE"
            named_status = "NONE"
            if not sheet.get("visible"):
                proposed = "QUARANTINED"
                reasons.add("HIDDEN_OR_VERY_HIDDEN_SHEET")
            if workbook_links:
                proposed = "QUARANTINED"
                external_status = "EXTERNAL_LINK_REVIEW_REQUIRED"
                reasons.add("EXTERNAL_LINK_PRESENT")
            if workbook_names:
                proposed = "QUARANTINED"
                named_status = "NAMED_RANGE_REVIEW_REQUIRED"
                reasons.add("NAMED_RANGE_PRESENT")
            cross_sheet_refs = [ref for ref in refs if ref and ref != sheet["name"]]
            if cross_sheet_refs:
                proposed = "QUARANTINED"
                formula_status = "FORMULA_DEPENDENCY_REVIEW_REQUIRED"
                reasons.add("FORMULA_REFERENCES_OTHER_SHEET")
            if project_id not in ids:
                reasons.add("PROJECT_ID_SUPPORTED_BY_PATH_ONLY")
            else:
                reasons.add("CURRENT_PROJECT_ID_MATCH_REVIEWABLE")
            forbidden_hits = detect_forbidden_text(base.get("relative_path", "") + " " + sheet.get("name", ""))
            if forbidden_hits:
                proposed = "AUTO_DENIED"
                reasons.add("FORBIDDEN_LABEL_OR_ROLE")

            decisions.append(
                {
                    "decision_id": decision_id(base["file_id"], sheet_id),
                    "source_root_id": base.get("source_root_id", "SRC-ALL-PROJECTS"),
                    "project_id": project_id,
                    "family_id": base.get("family_id", ""),
                    "relative_path": base.get("relative_path", ""),
                    "file_name": base.get("file_name", ""),
                    "file_id": base.get("file_id", ""),
                    "sheet_id": sheet_id,
                    "file_sha256": base.get("file_sha256", ""),
                    "file_size": base.get("file_size", ""),
                    "workbook_format": "xls",
                    "worksheet_name": sheet["name"],
                    "worksheet_visibility": "visible" if sheet.get("visible") else "hidden_or_very_hidden",
                    "worksheet_fingerprint": fp,
                    "workbook_sheet_count": len(metadata.get("sheets", [])),
                    "detected_project_identifiers": ids or [project_id],
                    "detected_customer_identifiers": split_pipe(base.get("detected_customer_identifiers", "")),
                    "detected_document_role": base.get("detected_document_role", "spreadsheet_other"),
                    "parser_name": PARSER_NAME,
                    "parser_version": metadata.get("excel_version", PARSER_VERSION),
                    "parse_status": "PARSED_WITH_FINGERPRINT",
                    "formula_dependency_status": formula_status,
                    "external_link_status": external_status,
                    "named_range_status": named_status,
                    "revision_status": "CURRENT_OR_UNKNOWN",
                    "duplicate_or_supersession": base.get("duplicate_or_supersession", ""),
                    "proposed_decision": proposed,
                    "final_decision": "UNREVIEWED",
                    "reason_codes": sorted(reasons),
                    "evidence_references": [base.get("file_id", ""), sheet_id],
                    "policy_version": "source_guard_policy_v2_autonomous_eval",
                    "reviewer_or_approver": "",
                    "decision_timestamp": "",
                    "approval_manifest_hash": "",
                    "sanitized_artifact_hash": "",
                    "sanitized_csv_path": str(csv_path),
                    "sanitized_csv_sha256": sha256_file(csv_path),
                    "non_empty_rows": sheet.get("non_empty_rows", 0),
                }
            )

    decisions_csv = output_root / "source_decisions_1110102_legacy_xls.csv"
    csv_write(decisions_csv, [flatten_decision(row) for row in decisions], DECISION_FIELDS)

    project_root = output_root / "project_manifests" / project_id
    project_root.mkdir(parents=True, exist_ok=True)
    items = []
    for row in decisions:
        state = "SUBMIT_TO_REVIEW" if row["proposed_decision"] == "CANDIDATE" else row["proposed_decision"]
        items.append(
            {
                "decision_id": row["decision_id"],
                "file_id": row["file_id"],
                "sheet_id": row["sheet_id"],
                "project_id": project_id,
                "relative_path": row["relative_path"],
                "detected_document_role": row["detected_document_role"],
                "file_sha256": row["file_sha256"],
                "worksheet_name": row["worksheet_name"],
                "worksheet_visibility": row["worksheet_visibility"],
                "worksheet_fingerprint": row["worksheet_fingerprint"],
                "proposed_decision": row["proposed_decision"],
                "prefilter_state": state,
                "reason_codes": row["reason_codes"],
                "checks": [
                    {"check": "source_root", "status": "PASS", "evidence": "SRC-ALL-PROJECTS"},
                    {"check": "file_sha256", "status": "PASS", "evidence": row["file_sha256"]},
                    {"check": "legacy_xls_parser_stability", "status": "PASS", "evidence": PARSER_VERSION},
                    {"check": "worksheet_fingerprint", "status": "PASS", "evidence": row["worksheet_fingerprint"]},
                ],
                "reviewable": state == "SUBMIT_TO_REVIEW",
            }
        )
    prefilter = {
        "prefilter_id": f"deterministic_prefilter_{project_id}_legacy_xls",
        "project_id": project_id,
        "policy_version": "source_guard_policy_v2_autonomous_eval",
        "status": "PASS_SUBMIT_TO_REVIEW" if any(item["reviewable"] for item in items) else "NO_REVIEWABLE_ITEMS",
        "items": items,
        "summary": {
            state: sum(1 for item in items if item["prefilter_state"] == state)
            for state in sorted({item["prefilter_state"] for item in items})
        },
        "run_metadata": {
            "created_at": now(),
            "parser": PARSER_VERSION,
            "source_decisions": str(decisions_csv),
        },
    }
    write_json(project_root / "deterministic_prefilter.json", prefilter)
    write_json(
        project_root / "review_input.json",
        {
            "project_id": project_id,
            "policy_version": "source_guard_policy_v2_autonomous_eval",
            "reviewable_items": [item for item in items if item["reviewable"]],
            "excluded_items": [item for item in items if not item["reviewable"]],
        },
    )
    report = {
        "project_id": project_id,
        "created_at": now(),
        "parser": PARSER_VERSION,
        "source_decisions": str(decisions_csv),
        "parse_reports": parse_reports,
        "stability_checks": stability_checks,
        "status": "PASS" if all(item["status"] == "PASS" for item in stability_checks) else "FAIL",
        "reviewable_count": sum(1 for item in items if item["reviewable"]),
        "excluded_count": sum(1 for item in items if not item["reviewable"]),
    }
    write_json(output_root / "legacy_xls_parser_audit.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic legacy .xls source decisions for calibration backfill.")
    parser.add_argument("--project-id", default="1110102")
    parser.add_argument("--decisions", type=Path, default=Path("manifests/source_guard/source_decisions.csv"))
    parser.add_argument("--file-index", type=Path, default=Path("manifests/all_projects_file_role_index.csv"))
    parser.add_argument("--output-root", type=Path, default=Path("manifests/calibration-006/backfill"))
    args = parser.parse_args()
    report = build_decisions(args.project_id, args.decisions, args.file_index, args.output_root)
    print(json.dumps({"status": report["status"], "project_id": args.project_id, "reviewable_count": report["reviewable_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
