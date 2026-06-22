from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from harness_lib import classify_path, read_json, repo_root, validate, validate_file
from harness_lib import write_json


ROOT = repo_root()
PY = sys.executable


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def test_json_schemas_parse() -> None:
    for path in (ROOT / "schemas").glob("*.schema.json"):
        read_json(path)


def test_declared_json_artifacts_validate() -> None:
    pairs = [
        ("manifests/source_manifest_initial.json", "schemas/source_manifest.schema.json"),
        ("manifests/workbook_sheet_adjudication_initial.json", "schemas/workbook_sheet_adjudication.schema.json"),
        ("manifests/generator_input_manifest_empty.json", "schemas/generator_input_manifest.schema.json"),
        ("rules/source_authority_profile.json", "schemas/source_authority_profile.schema.json"),
        ("rules/derivation_rules/bootstrap_dimension_rule.json", "schemas/derivation_rule.schema.json"),
        ("rules/constraint_rules/bootstrap_cross_pdf_rule.json", "schemas/constraint_rule.schema.json"),
        ("evals/grading_profiles/plc_layout_v1.json", "schemas/grading_result.schema.json"),
    ]
    # The grading profile has its own structure; check weights separately instead of grading_result schema.
    for instance, schema in pairs[:-1]:
        errors = validate_file(ROOT / instance, ROOT / schema)
        assert_true(not errors, f"{instance} failed {schema}: {errors}")


def test_utf8_fixture_labels() -> None:
    text = (ROOT / "evals/fixtures/utf8_labels.txt").read_text(encoding="utf-8")
    for label in ["合約", "材料清單", "生管文件", "生管課用圖", "生管用圖", "沖孔", "鈑金", "電機施工圖"]:
        assert_true(label in text, f"missing label {label}")


def test_forbidden_classification() -> None:
    forbidden = classify_path("案號/電機施工圖/01_生管課用圖_ABC.pdf")
    assert_true(forbidden["generator_eligibility"] == "FORBIDDEN", "target-like electrical drawing must be forbidden")
    allowedish = classify_path("案號/合約_ABC.xlsx")
    assert_true(allowedish["primary_role"] == "allowed_contract_workbook", "contract workbook label should classify")


def test_grading_weights() -> None:
    profile = read_json(ROOT / "evals/grading_profiles/plc_layout_v1.json")
    assert_true(sum(profile["weights"].values()) == 100, "grading weights must sum to 100")
    assert_true(profile["highest_automated_status"] == "READY_FOR_PRIVATE_PREVIEW", "highest automated status guard changed")


def test_synthetic_render_grade() -> None:
    work_dir = ROOT / "tmp" / "phase0_test_harness"
    run([PY, "scripts/eval_harness.py", "--work-dir", str(work_dir)])
    grading = read_json(work_dir / "grading_result.json")
    errors = validate(grading, read_json(ROOT / "schemas/grading_result.schema.json"))
    assert_true(not errors, f"grading_result schema errors: {errors}")
    assert_true(grading["validity"] == "PASS", "synthetic PDF package should pass")


def test_positive_bundle_and_contamination_scan() -> None:
    work_dir = ROOT / "tmp" / "bundle_test"
    work_dir.mkdir(parents=True, exist_ok=True)
    source_manifest = work_dir / "source_manifest.json"
    sheet_adjudication = work_dir / "sheet_adjudication.json"
    bundle_dir = work_dir / "bundle"
    generator_manifest = work_dir / "generator_input_manifest.json"
    contamination = work_dir / "contamination.json"
    write_json(source_manifest, {
        "manifest_id": "bundle-test-source",
        "files": [
            {
                "file_id": "FILE-ALLOWED",
                "relative_path": "1150101/合約_1150101.xlsx",
                "file_name": "合約_1150101.xlsx",
                "primary_role": "allowed_contract_workbook",
                "generator_eligibility": "ALLOWED"
            },
            {
                "file_id": "FILE-FORBIDDEN",
                "relative_path": "1150101/電機施工圖/target.pdf",
                "file_name": "target.pdf",
                "primary_role": "forbidden_electrical_drawing",
                "generator_eligibility": "FORBIDDEN"
            }
        ],
        "worksheets": []
    })
    write_json(sheet_adjudication, {
        "adjudication_id": "bundle-test-sheets",
        "worksheets": [
            {"sheet_id": "SHEET-ALLOWED", "generator_eligibility": "ALLOWED", "stale_template_status": "CURRENT_PROJECT_ID_MATCH"},
            {"sheet_id": "SHEET-STALE", "generator_eligibility": "FORBIDDEN", "stale_template_status": "STALE_TEMPLATE_SHEET"}
        ]
    })
    run([PY, "scripts/build_generator_bundle.py", "--source-manifest", str(source_manifest), "--sheet-adjudication", str(sheet_adjudication), "--bundle-dir", str(bundle_dir), "--output-manifest", str(generator_manifest), "--run-id", "BUNDLE-TEST", "--project-id", "1150101"])
    manifest = read_json(generator_manifest)
    assert_true(manifest["allowed_files"] == ["FILE-ALLOWED"], "only positive allowed file should enter manifest")
    assert_true(manifest["allowed_sheets"] == ["SHEET-ALLOWED"], "stale sheet must be excluded")
    run([PY, "scripts/scan_generator_contamination.py", "--bundle-dir", str(bundle_dir), "--manifest", str(generator_manifest), "--output", str(contamination)])
    scan = read_json(contamination)
    assert_true(scan["status"] == "PASS", "clean positive bundle should pass contamination scan")


def create_source_guard_fixture(root: Path):
    from openpyxl import Workbook

    root.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "核准輸入"
    ws["A1"] = "工程編號"
    ws["B1"] = "1159999"
    ws["A2"] = "客戶"
    ws["B2"] = "目前客戶"
    ws["A3"] = "公式"
    ws["B3"] = "=DeniedSheet!A1"
    denied = wb.create_sheet("DeniedSheet")
    denied["A1"] = "denied"
    hidden = wb.create_sheet("hidden舊資料")
    hidden.sheet_state = "hidden"
    hidden["A1"] = "1140001 舊客戶"
    sentinel = wb.create_sheet("veryHidden完成圖")
    sentinel.sheet_state = "veryHidden"
    sentinel["A1"] = "生管課用圖 completed target sentinel"
    try:
        from openpyxl.workbook.defined_name import DefinedName

        wb.defined_names.add(DefinedName("DeniedRange", attr_text="'DeniedSheet'!$A$1"))
    except Exception:
        pass
    path = root / "合約_1159999.xlsx"
    wb.save(path)
    macro_path = root / "合約_1159999.xlsm"
    wb.save(macro_path)
    legacy_path = root / "舊格式_1159999.xls"
    legacy_path.write_bytes(b"legacy xls placeholder")
    return path, macro_path, legacy_path


def test_source_guard_fail_closed_decisions() -> None:
    import source_guard

    fixture_root = ROOT / "tmp" / "source_guard_fixtures" / "SRC"
    workbook, macro_workbook, legacy = create_source_guard_fixture(fixture_root)
    old_root = source_guard.SOURCE_ROOT_PATH
    source_guard.SOURCE_ROOT_PATH = fixture_root
    try:
        file_row = {
            "file_id": "FILE-1",
            "source_root": "SRC-ALL-PROJECTS",
            "project_id": "1159999",
            "project_name": "1159999測試-目前客戶",
            "customer": "目前客戶",
            "relative_path": workbook.name,
            "file_name": workbook.name,
            "extension": ".xlsx",
            "size_bytes": str(workbook.stat().st_size),
            "sha256": __import__("hashlib").sha256(workbook.read_bytes()).hexdigest().upper(),
            "primary_role": "allowed_contract_workbook",
            "generator_eligibility": "HUMAN_REVIEW_REQUIRED",
            "parse_status": "PARSED",
            "absolute_path": str(workbook),
            "duplicate_of": "",
        }
        visible_sheet = {
            "sheet_id": "SHEET-1",
            "sheet_name": "核准輸入",
            "visibility": "visible",
            "stale_template_status": "CURRENT_PROJECT_ID_MATCH",
            "stale_evidence": "1159999 目前客戶",
            "generator_eligibility": "HUMAN_REVIEW_REQUIRED",
            "external_links": "external.xlsx",
            "named_ranges": "DeniedRange",
            "parse_status": "PARSED",
        }
        hidden_sheet = dict(visible_sheet, sheet_id="SHEET-2", sheet_name="hidden舊資料", visibility="hidden", stale_template_status="INSUFFICIENT_IDENTITY", stale_evidence="1140001 舊客戶")
        sentinel_sheet = dict(visible_sheet, sheet_id="SHEET-3", sheet_name="veryHidden完成圖", visibility="veryHidden", stale_template_status="FORBIDDEN_SOURCE", stale_evidence="生管課用圖")
        visible_decision = source_guard.decide_source_item(file_row, visible_sheet)
        hidden_decision = source_guard.decide_source_item(file_row, hidden_sheet)
        sentinel_decision = source_guard.decide_source_item(file_row, sentinel_sheet)
        assert_true(visible_decision["proposed_decision"] == "QUARANTINED", "formula/external/named-range dependencies must quarantine")
        assert_true("FORMULA_REFERENCES_OTHER_SHEET" in visible_decision["reason_codes"], "formula dependency reason missing")
        assert_true(hidden_decision["proposed_decision"] == "QUARANTINED", "hidden sheet must not be approved")
        assert_true(sentinel_decision["proposed_decision"] == "AUTO_DENIED", "completed-reference sentinel must auto-deny")
        assert_true(visible_decision["worksheet_fingerprint"], "visible supported sheet must have deterministic fingerprint")
        again = source_guard.decide_source_item(file_row, visible_sheet)
        assert_true(again["worksheet_fingerprint"] == visible_decision["worksheet_fingerprint"], "worksheet fingerprint must be deterministic")

        macro_row = dict(file_row, file_id="FILE-MACRO", relative_path=macro_workbook.name, file_name=macro_workbook.name, extension=".xlsm", size_bytes=str(macro_workbook.stat().st_size), sha256=__import__("hashlib").sha256(macro_workbook.read_bytes()).hexdigest().upper(), absolute_path=str(macro_workbook))
        macro_decision = source_guard.decide_source_item(macro_row, dict(visible_sheet, external_links="", named_ranges=""))
        assert_true(macro_decision["proposed_decision"] in {"QUARANTINED", "AUTO_DENIED"}, "macro-enabled workbook must fail closed")

        legacy_row = dict(file_row, file_id="FILE-XLS", relative_path=legacy.name, file_name=legacy.name, extension=".xls", size_bytes=str(legacy.stat().st_size), sha256=__import__("hashlib").sha256(legacy.read_bytes()).hexdigest().upper(), absolute_path=str(legacy))
        legacy_decision = source_guard.decide_source_item(legacy_row, None)
        assert_true(legacy_decision["proposed_decision"] == "PARSER_REQUIRED", "legacy xls must be parser-required")

        tampered = dict(file_row, sha256="0" * 64)
        tampered_decision = source_guard.decide_source_item(tampered, visible_sheet)
        assert_true(tampered_decision["proposed_decision"] == "AUTO_DENIED", "source hash mutation must deny")
    finally:
        source_guard.SOURCE_ROOT_PATH = old_root


def test_source_approval_and_bundle_fail_closed() -> None:
    fixture_root = ROOT / "tmp" / "source_guard_approval"
    workbook, _, _ = create_source_guard_fixture(fixture_root)
    file_sha = __import__("hashlib").sha256(workbook.read_bytes()).hexdigest().upper()
    import source_guard

    old_root = source_guard.SOURCE_ROOT_PATH
    source_guard.SOURCE_ROOT_PATH = fixture_root
    try:
        file_row = {
            "file_id": "FILE-APPROVE",
            "source_root": "SRC-ALL-PROJECTS",
            "project_id": "1159999",
            "project_name": "1159999測試-目前客戶",
            "customer": "目前客戶",
            "relative_path": workbook.name,
            "file_name": workbook.name,
            "extension": ".xlsx",
            "size_bytes": str(workbook.stat().st_size),
            "sha256": file_sha,
            "primary_role": "allowed_contract_workbook",
            "generator_eligibility": "HUMAN_REVIEW_REQUIRED",
            "parse_status": "PARSED",
            "absolute_path": str(workbook),
            "duplicate_of": "",
        }
        sheet_row = {
            "sheet_id": "SHEET-APPROVE",
            "sheet_name": "核准輸入",
            "visibility": "visible",
            "stale_template_status": "CURRENT_PROJECT_ID_MATCH",
            "stale_evidence": "1159999 目前客戶",
            "generator_eligibility": "HUMAN_REVIEW_REQUIRED",
            "external_links": "",
            "named_ranges": "",
            "parse_status": "PARSED",
        }
        decision = source_guard.decide_source_item(file_row, sheet_row)
    finally:
        source_guard.SOURCE_ROOT_PATH = old_root
    decision["proposed_decision"] = "CANDIDATE"
    decisions_csv = fixture_root / "decisions.csv"
    fields = ["decision_id", "project_id", "file_id", "sheet_id", "file_sha256", "worksheet_fingerprint", "proposed_decision"]
    import csv

    with decisions_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(decision.keys()), extrasaction="ignore")
        writer.writeheader()
        writer.writerow({k: "|".join(v) if isinstance(v, list) else v for k, v in decision.items()})
    blank_decisions = fixture_root / "blank_human_decisions.csv"
    with blank_decisions.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["decision_id", "project_id", "file_id", "sheet_id", "file_sha256", "worksheet_fingerprint", "human_decision", "reviewer", "notes"])
        writer.writeheader()
        writer.writerow({"decision_id": decision["decision_id"], "project_id": "1159999", "file_id": "FILE-APPROVE", "sheet_id": "SHEET-APPROVE", "file_sha256": file_sha, "worksheet_fingerprint": decision["worksheet_fingerprint"], "human_decision": "", "reviewer": "", "notes": ""})
    failed = subprocess.run([PY, "scripts/validate_source_approval.py", "--decisions", str(decisions_csv), "--human-decisions", str(blank_decisions), "--output", str(fixture_root / "approval_fail.json")], cwd=ROOT)
    assert_true(failed.returncode != 0, "blank human decision must fail")

    approve_csv = fixture_root / "approve.csv"
    with approve_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["decision_id", "project_id", "file_id", "sheet_id", "file_sha256", "worksheet_fingerprint", "human_decision", "reviewer", "notes"])
        writer.writeheader()
        writer.writerow({"decision_id": decision["decision_id"], "project_id": "1159999", "file_id": "FILE-APPROVE", "sheet_id": "SHEET-APPROVE", "file_sha256": file_sha, "worksheet_fingerprint": "bad", "human_decision": "HUMAN_APPROVED", "reviewer": "tester", "notes": ""})
    tamper = subprocess.run([PY, "scripts/validate_source_approval.py", "--decisions", str(decisions_csv), "--human-decisions", str(approve_csv), "--output", str(fixture_root / "approval_tamper.json")], cwd=ROOT)
    assert_true(tamper.returncode != 0, "tampered worksheet fingerprint must fail")


def test_bundle_verifier_rejects_leaks_and_traversal() -> None:
    bundle = ROOT / "tmp" / "bad_bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    write_json(bundle / "bundle_manifest.json", {"bundle_id": "bad", "project_id": "P", "policy_version": "source_guard_policy_v1", "status": "BUILT", "artifacts": [{"artifact_id": "A", "path": "sanitized_inputs/01_生管課用圖_bad.csv", "sha256": "0" * 64, "source_decision_id": "D"}]})
    write_json(bundle / "approval_manifest.json", {"status": "PASS", "decisions": [{"decision_id": "D", "human_decision": "HUMAN_APPROVED"}]})
    write_json(bundle / "provenance_map.json", {"rows": []})
    write_json(bundle / "visible_file_manifest.json", {"files": []})
    write_json(bundle / "verification_results.json", {"status": "PENDING_VERIFICATION", "errors": ["BUNDLE_NOT_VERIFIED"], "warnings": []})
    write_json(bundle / "bundle_hashes.json", {"files": []})
    leak = bundle / "sanitized_inputs" / "01_生管課用圖_bad.csv"
    leak.parent.mkdir(parents=True, exist_ok=True)
    leak.write_text("C:\\Users\\alex1\\OneDrive\\Desktop\\All Projects\\secret", encoding="utf-8")
    result = subprocess.run([PY, "scripts/verify_generator_bundle.py", "--bundle-dir", str(bundle), "--output", str(bundle / "verification.json")], cwd=ROOT)
    assert_true(result.returncode != 0, "bundle verifier must reject source path and target-output leaks")


def main() -> None:
    tests = [
        test_json_schemas_parse,
        test_declared_json_artifacts_validate,
        test_utf8_fixture_labels,
        test_forbidden_classification,
        test_grading_weights,
        test_synthetic_render_grade,
        test_positive_bundle_and_contamination_scan,
        test_source_guard_fail_closed_decisions,
        test_source_approval_and_bundle_fail_closed,
        test_bundle_verifier_rejects_leaks_and_traversal,
    ]
    failures = []
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:
            failures.append((test.__name__, str(exc)))
            print(f"FAIL {test.__name__}: {exc}")
    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps({"status": "PASS", "tests": [t.__name__ for t in tests]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
