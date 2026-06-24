from __future__ import annotations

import json
import shutil
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


def test_evaluator_sensitivity_monotonicity() -> None:
    from evaluator_scoring import compute_score

    base = {
        "run_id": "SENS-BASE",
        "validity_inputs": {"required_outputs_present": True, "hard_gate_failures": []},
        "coverage": {"scorable_elements": 38, "total_elements": 100},
        "dimension_items": {
            "source_selection_provenance_conflict": [
                {"item_id": "source_bundle", "score": 14, "max_score": 20, "classification": "EXPLICIT_IN_ALLOWED_INPUT"}
            ],
            "panel_schedule_enclosure_facts": [
                {"item_id": "panel_facts", "score": 5, "max_score": 15, "classification": "UNAVAILABLE_IN_ALLOWED_INPUT"}
            ],
            "device_bom_quantity_tag_fidelity": [
                {"item_id": "device_fidelity", "score": 8, "max_score": 20, "classification": "UNAVAILABLE_IN_ALLOWED_INPUT"}
            ],
            "shared_geometry_cross_pdf_consistency": [
                {"item_id": "cross_pdf", "score": 8, "max_score": 15, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
            "production_drawing_quality": [
                {"item_id": "production", "score": 3, "max_score": 10, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
            "punch_drawing_quality": [
                {"item_id": "punch", "score": 2, "max_score": 10, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
            "sheetmetal_drawing_quality": [
                {"item_id": "sheetmetal", "score": 2, "max_score": 10, "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"}
            ],
        },
        "findings": [
            {"finding_id": "F1", "severity": "HIGH", "dedupe_key": "missing_exact_dimensions", "classification": "UNAVAILABLE_IN_ALLOWED_INPUT"},
            {"finding_id": "F2", "severity": "HIGH", "dedupe_key": "reference_layout_unavailable", "classification": "UNAVAILABLE_IN_ALLOWED_INPUT"},
            {"finding_id": "F3", "severity": "HIGH", "dedupe_key": "schematic_minimal", "classification": "DESIGN_CHOICE_WITH_CONSTRAINTS"},
        ],
    }

    baseline = compute_score(base)
    assert_true(baseline["quality_score"] == 42, "baseline score should be arithmetic sum of dimension items")
    assert_true(baseline["scorable_coverage"] == 38, "coverage should come from the explicit denominator")

    missing = json.loads(json.dumps(base))
    missing["validity_inputs"]["required_outputs_present"] = False
    assert_true(compute_score(missing)["validity"] == "FAIL", "missing output must fail validity")

    corrected = json.loads(json.dumps(base))
    corrected["dimension_items"]["panel_schedule_enclosure_facts"][0]["score"] = 9
    assert_true(compute_score(corrected)["quality_score"] > baseline["quality_score"], "proven correction must improve score")

    worse = json.loads(json.dumps(base))
    worse["dimension_items"]["device_bom_quantity_tag_fidelity"][0]["score"] = 4
    assert_true(compute_score(worse)["quality_score"] < baseline["quality_score"], "new high defect must worsen score")

    unsupported = json.loads(json.dumps(base))
    unsupported["validity_inputs"]["hard_gate_failures"] = ["INVENTED_CRITICAL_VALUE"]
    gated = compute_score(unsupported)
    assert_true(gated["validity"] == "FAIL" and gated["quality_score"] == 0, "hard gate must override numerical score")

    no_scorable = json.loads(json.dumps(base))
    no_scorable["coverage"] = {"scorable_elements": 0, "total_elements": 0}
    low = compute_score(no_scorable)
    assert_true(low["evidence_strength"] == "INSUFFICIENT_COVERAGE", "zero scorable elements must not look like an ordinary score")

    duplicate = json.loads(json.dumps(base))
    duplicate["findings"].append(dict(duplicate["findings"][0], finding_id="F1_DUP"))
    deduped = compute_score(duplicate)
    assert_true(deduped["high_findings"] == baseline["high_findings"], "duplicate findings must not add accidental penalties")

    same_total = json.loads(json.dumps(base))
    same_total["dimension_items"]["production_drawing_quality"][0]["score"] = 4
    same_total["dimension_items"]["punch_drawing_quality"][0]["score"] = 1
    alt = compute_score(same_total)
    assert_true(alt["quality_score"] == baseline["quality_score"], "fixture should preserve same total")
    assert_true(alt["dimension_scores"] != baseline["dimension_scores"], "same total must preserve different dimension vectors")


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


def create_reference_v3_pdf(path: Path, page_texts: list[str]) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    for index, text in enumerate(page_texts, start=1):
        c.setFont("Helvetica", 14)
        c.drawString(72, height - 72, text)
        c.setFont("Helvetica", 8)
        c.drawString(width - 240, 48, f"TITLE BLOCK {index}")
        c.showPage()
    c.save()


def reference_v3_manifest(path: Path, project_id: str, files: list[dict[str, str]]) -> None:
    rows = []
    for item in files:
        pdf = Path(item["path"])
        rows.append({
            "project_id": project_id,
            "neutral_reference_file_id": item["file_id"],
            "path": str(pdf),
            "sha256": __import__("hashlib").sha256(pdf.read_bytes()).hexdigest().upper(),
            "role_hint": item.get("role_hint", "supporting_document_non_generator"),
            "metadata_text": item.get("metadata_text", pdf.name),
        })
    write_json(path, {"project_id": project_id, "files": rows})


def test_reference_detection_v3_boundary_and_page_level_sets() -> None:
    project_id = "1999001"
    work = ROOT / "tmp" / "reference_detection_v3_tests" / "boundary"
    if work.exists():
        shutil.rmtree(work)
    fixture = read_json(ROOT / "evals" / "fixtures" / "reference_detection_v3" / "fixture_manifest.json")
    cases = {case["case_id"]: case for case in fixture["cases"]}

    production = work / "forbidden_production_control" / "synthetic_production.pdf"
    electrical = work / "electrical" / "synthetic_electrical.pdf"
    combined = work / "combined" / "synthetic_combined.pdf"
    create_reference_v3_pdf(production, cases["target_under_production_control"]["pages"])
    create_reference_v3_pdf(electrical, cases["ordinary_electrical_under_electrical"]["pages"])
    create_reference_v3_pdf(combined, cases["combined_all_three"]["pages"])

    candidate_manifest = work / "candidate_manifest.json"
    reference_v3_manifest(candidate_manifest, project_id, [
        {"file_id": "REF-PROD-FORBIDDEN-FOLDER", "path": str(production), "role_hint": "forbidden_production_control_file", "metadata_text": "production-control-folder"},
        {"file_id": "REF-ELECTRICAL", "path": str(electrical), "role_hint": "forbidden_electrical_drawing", "metadata_text": "electrical-folder"},
        {"file_id": "REF-COMBINED-CJK-合併", "path": str(combined), "role_hint": "supporting_document_non_generator", "metadata_text": "合併 package"},
    ])
    output_dir = work / "out"
    run([PY, "scripts/detect_reference_presence_v3.py", "--project-id", project_id, "--candidate-manifest", str(candidate_manifest), "--output-dir", str(output_dir), "--task-id", "TEST-REFDET-V3-BOUNDARY"])
    run([PY, "scripts/verify_reference_detection_output.py", "--output-dir", str(output_dir)])

    effective = read_json(output_dir / "effective_reference_set.json")
    pages = read_json(output_dir / "reference_page_classifications.json")["page_classifications"]
    audit = read_json(output_dir / "reference_detection_audit.json")
    assert_true(effective["status"] == "VERIFIED_ALL_THREE_COMBINED_PACKAGE", "combined package with all three page types must verify")
    assert_true(audit["temporary_workspace_removed"], "temporary reference renders must be deleted")
    assert_true(any(row["neutral_reference_file_id"] == "REF-PROD-FORBIDDEN-FOLDER" and row["page_classification"] == "PRODUCTION_DRAWING" for row in pages), "target under production-control folder must qualify as reviewer evidence by content")
    assert_true(any(row["neutral_reference_file_id"] == "REF-ELECTRICAL" and row["page_classification"] == "ELECTRICAL_DRAWING" for row in pages), "ordinary electrical drawing must stay non-target")

    source_manifest = work / "source_manifest.json"
    sheet_adjudication = work / "sheet_adjudication.json"
    generator_manifest = work / "generator_input_manifest.json"
    write_json(source_manifest, {
        "manifest_id": "ref-v3-boundary-source",
        "files": [
            {
                "file_id": "REF-PROD-FORBIDDEN-FOLDER",
                "relative_path": "forbidden_production_control/synthetic_production.pdf",
                "file_name": "synthetic_production.pdf",
                "primary_role": "forbidden_production_control_file",
                "generator_eligibility": "FORBIDDEN",
                "absolute_path": str(production),
            }
        ],
        "worksheets": [],
    })
    write_json(sheet_adjudication, {"adjudication_id": "ref-v3-boundary-sheets", "worksheets": []})
    run([PY, "scripts/build_generator_bundle.py", "--source-manifest", str(source_manifest), "--sheet-adjudication", str(sheet_adjudication), "--bundle-dir", str(work / "generator_bundle"), "--output-manifest", str(generator_manifest), "--run-id", "REF-V3-BOUNDARY", "--project-id", project_id])
    generator = read_json(generator_manifest)
    assert_true(generator["allowed_files"] == [], "reviewer-reference PDF must not enter generator bundle")
    assert_true("REF-PROD-FORBIDDEN-FOLDER" not in json.dumps(generator, ensure_ascii=False), "generator manifest must not expose reference file IDs")


def test_reference_detection_v3_duplicates_identity_and_missing_types() -> None:
    project_id = "1999001"
    work = ROOT / "tmp" / "reference_detection_v3_tests" / "duplicates"
    if work.exists():
        shutil.rmtree(work)
    fixture = read_json(ROOT / "evals" / "fixtures" / "reference_detection_v3" / "fixture_manifest.json")
    cases = {case["case_id"]: case for case in fixture["cases"]}

    production = work / "production.pdf"
    duplicate = work / "duplicate_named_punch.pdf"
    sheetmetal = work / "sheetmetal.pdf"
    wrong_project = work / "wrong_project_punch.pdf"
    near_duplicate = work / "production_near_duplicate.pdf"
    create_reference_v3_pdf(production, cases["missing_third_with_duplicate"]["pages"])
    shutil.copy2(production, duplicate)
    create_reference_v3_pdf(sheetmetal, cases["sheetmetal_only"]["pages"])
    create_reference_v3_pdf(wrong_project, cases["mismatched_project_identity"]["pages"])
    create_reference_v3_pdf(near_duplicate, ["PROJECT 1999001 PRODUCTION_DRAWING NEAR DUPLICATE"])

    candidate_manifest = work / "candidate_manifest.json"
    reference_v3_manifest(candidate_manifest, project_id, [
        {"file_id": "REF-PROD", "path": str(production), "metadata_text": "production"},
        {"file_id": "REF-DUP-PUNCH-NAME", "path": str(duplicate), "metadata_text": "punch filename but exact duplicate"},
        {"file_id": "REF-SHEETMETAL", "path": str(sheetmetal), "metadata_text": "sheetmetal"},
        {"file_id": "REF-WRONG-PROJECT", "path": str(wrong_project), "metadata_text": "punch wrong project"},
        {"file_id": "REF-NEAR-DUP-PROD", "path": str(near_duplicate), "metadata_text": "production near duplicate"},
    ])
    output_dir = work / "out"
    run([PY, "scripts/detect_reference_presence_v3.py", "--project-id", project_id, "--candidate-manifest", str(candidate_manifest), "--output-dir", str(output_dir), "--task-id", "TEST-REFDET-V3-DUP"])
    run([PY, "scripts/verify_reference_detection_output.py", "--output-dir", str(output_dir)])
    effective = read_json(output_dir / "effective_reference_set.json")
    docs = read_json(output_dir / "reference_document_classifications.json")["document_classifications"]
    pages = read_json(output_dir / "reference_page_classifications.json")["page_classifications"]
    assert_true(effective["status"] == "PARTIAL_REFERENCE_SET", "duplicate or wrong-project punch must not create false all-three set")
    assert_true(set(effective["target_types_present"]) == {"PRODUCTION_DRAWING", "SHEETMETAL_DRAWING"}, "only confirmed production and sheetmetal should count")
    assert_true(any(doc["neutral_reference_file_id"] == "REF-DUP-PUNCH-NAME" and doc["duplicate_of"] == "REF-PROD" for doc in docs), "exact duplicate must be recorded")
    assert_true(any(row["neutral_reference_file_id"] == "REF-WRONG-PROJECT" and row["project_identity_status"] == "CONFLICT" for row in pages), "mismatched project identity must be marked conflict")
    assert_true(any(row["neutral_reference_file_id"] == "REF-NEAR-DUP-PROD" and row["page_classification"] == "PRODUCTION_DRAWING" for row in pages), "near duplicate should remain same target type, not a missing third output")


def test_reference_detector_v3_known_positive_recall_gate() -> None:
    summary_path = ROOT / "reports" / "baseline-024" / "reference-detector-calibration" / "known_positive_replay_summary.json"
    summary = read_json(summary_path)
    expected_projects = {
        "1110101",
        "1110103",
        "1110104",
        "1110203",
        "1110204",
        "1110205",
        "1110405",
        "1110410",
        "1110704",
        "1110801",
        "1120207",
        "1120305",
        "1120308",
    }
    project_results = {row["project_id"]: row for row in summary["project_results"]}
    assert_true(summary["detector_version"] == "target_output_detection_v3_page_content_isolated", "unexpected detector under v3 replay gate")
    assert_true(summary["status"] == "DETECTOR_V3_RECALL_FAIL", "v3 known-positive replay must remain a failed gate until superseded")
    assert_true(set(summary["known_positive_projects"]) == expected_projects, "known-positive control set changed")
    assert_true(set(project_results) == expected_projects, "known-positive replay result set changed")
    assert_true(summary["positive_projects_detected_all_three"] == 0, "v3 must not be recorded as detecting any all-three known positive")
    assert_true(summary["false_negative_output_type_count"] == 31, "v3 false-negative count changed without a new detector version")
    assert_true(summary["project_identity_mismatch_count"] == 0, "project identity mismatch count changed")
    assert_true(summary["per_type_recall"]["PRODUCTION_DRAWING"]["detected"] == 0, "v3 production recall unexpectedly changed")
    assert_true(summary["per_type_recall"]["SHEETMETAL_DRAWING"]["detected"] == 8, "v3 sheetmetal recall unexpectedly changed")
    assert_true(summary["per_type_recall"]["PUNCH_DRAWING"]["detected"] == 0, "v3 punch recall unexpectedly changed")
    assert_true(summary["actual_vision_agents"]["image_only_pages_inspected_by_actual_vision_agents"] == 0, "local v3 replay must not masquerade as actual vision classification")
    assert_true(summary["classifier_models"][0]["actual_model"] == "local_poppler_pypdf_deterministic_reference_detector_v3", "v3 replay model provenance changed")
    for project_id in expected_projects:
        result = project_results[project_id]
        assert_true(result["missed_output_types"], f"{project_id} must remain a recorded v3 missed-positive regression case")
        assert_true("IMAGE_OR_NO_TARGET_TEXT_WITHOUT_REAL_VISION_CLASSIFICATION" in result["failure_reason"], f"{project_id} missing real-vision failure reason")


def test_qualification_recovery_controller_state() -> None:
    work = ROOT / "tmp" / "qualification_recovery_controller_test"
    if work.exists():
        shutil.rmtree(work)
    report_dir = work / "reports"
    queue_path = work / "queue.json"
    run([
        PY,
        "scripts/run_qualification_recovery.py",
        "--report-dir",
        str(report_dir),
        "--queue-path",
        str(queue_path),
        "--skip-capability-probe",
    ])
    state_path = report_dir / "recovery_state.json"
    state = read_json(state_path)
    errors = validate(state, read_json(ROOT / "schemas/qualification_recovery_state.schema.json"))
    assert_true(not errors, f"qualification recovery state schema errors: {errors}")
    assert_true(state["decision_id"] == "D-0021", "recovery state must bind to accepted decision D-0021")
    assert_true(state["current_allowed_eval"]["current_count"] == 13, "current ALLOWED_EVAL count must remain 13")
    assert_true(state["current_allowed_eval"]["deficit"] == 11, "deficit must remain 11")
    assert_true(state["privacy"]["approval_status"] == "NOT_APPROVED", "privacy approval must remain NOT_APPROVED")
    assert_true(state["privacy"]["private_reference_pages_inspected_by_actual_vision_agents"] == 0, "private vision inspection count must stay zero")
    assert_true(state["detector_calibration"]["regression_gate_behavior_status"] == "PASS_BLOCKS_KNOWN_FAILING_DETECTOR", "gate behavior must be reported separately")
    assert_true(state["detector_calibration"]["detector_performance_status"] == "FAIL", "v3 detector performance must remain failed")
    assert_true("RECOVERABLE_DETECTOR_LIMITATION" in state["blocker_taxonomy"], "recoverable detector blocker class missing")
    assert_true(state["next_selected_action"]["action_id"] == "RUN_LOCAL_CAPABILITY_DISCOVERY", "test-mode next action should be capability discovery")
    assert_true(queue_path.exists(), "qualification recovery queue must be written")
    queue = read_json(queue_path)
    assert_true(queue["privacy_minimization"]["stores_private_paths"] is False, "queue must not store private paths")
    assert_true(queue["privacy_minimization"]["stores_reference_content"] is False, "queue must not store reference content")


def main() -> None:
    tests = [
        test_json_schemas_parse,
        test_declared_json_artifacts_validate,
        test_utf8_fixture_labels,
        test_forbidden_classification,
        test_grading_weights,
        test_evaluator_sensitivity_monotonicity,
        test_synthetic_render_grade,
        test_positive_bundle_and_contamination_scan,
        test_source_guard_fail_closed_decisions,
        test_source_approval_and_bundle_fail_closed,
        test_bundle_verifier_rejects_leaks_and_traversal,
        test_reference_detection_v3_boundary_and_page_level_sets,
        test_reference_detection_v3_duplicates_identity_and_missing_types,
        test_reference_detector_v3_known_positive_recall_gate,
        test_qualification_recovery_controller_state,
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
