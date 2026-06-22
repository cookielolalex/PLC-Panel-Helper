from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from harness_lib import classify_path, read_json, repo_root, validate, validate_file


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


def main() -> None:
    tests = [
        test_json_schemas_parse,
        test_declared_json_artifacts_validate,
        test_utf8_fixture_labels,
        test_forbidden_classification,
        test_grading_weights,
        test_synthetic_render_grade,
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

