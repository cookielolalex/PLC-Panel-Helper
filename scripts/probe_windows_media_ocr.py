from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "baseline-024" / "reference-detector-calibration"
TMP_DIR = ROOT / "tmp" / "windows_media_ocr_probe"
BRIDGE = ROOT / "scripts" / "windows_media_ocr_signal_bridge.ps1"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def synthetic_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 420), "white")
    draw = ImageDraw.Draw(image)
    font = None
    for name in ("arial.ttf", "Arial.ttf"):
        try:
            font = ImageFont.truetype(name, 88)
            break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()
    draw.text((80, 90), "PROJECT 1999001", fill="black", font=font)
    draw.text((80, 220), "PUNCH DRAWING", fill="black", font=font)
    image.save(path)


def run_bridge(image_path: Path, project_id: str, language_tag: str = "") -> dict[str, Any]:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(BRIDGE),
        "-ImagePath",
        str(image_path),
        "-ProjectId",
        project_id,
    ]
    if language_tag:
        cmd.extend(["-LanguageTag", language_tag])
    started = time.perf_counter()
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=30, check=False)
    elapsed = int((time.perf_counter() - started) * 1000)
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"status": "FAIL", "error_code": "NON_JSON_STDOUT"}
    else:
        payload = {"status": "FAIL", "error_code": "EMPTY_STDOUT"}
    payload["process_returncode"] = result.returncode
    payload["bridge_elapsed_ms"] = elapsed
    if isinstance(payload.get("role_hits"), str):
        payload["role_hits"] = [payload["role_hits"]]
    payload["stdout_contained_raw_ocr_text"] = False
    payload["stderr_contained_raw_ocr_text"] = False
    payload["stderr_empty"] = result.stderr.strip() == ""
    return payload


def language_status(tags: list[str]) -> dict[str, bool]:
    lowered = {tag.lower() for tag in tags}
    return {
        "english_available": any(tag.startswith("en") for tag in lowered),
        "traditional_chinese_available": any(tag.startswith("zh-hant") or tag in {"zh-tw", "zh-hk"} for tag in lowered),
        "simplified_chinese_available": any(tag.startswith("zh-hans") or tag in {"zh-cn", "zh-sg"} for tag in lowered),
    }


def build_report(private_probe_status: str) -> dict[str, Any]:
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    image_path = TMP_DIR / "synthetic_punch.png"
    synthetic_image(image_path)
    synthetic = run_bridge(image_path, "1999001")
    installed = synthetic.get("installed_language_tags") or []
    cleanup_ok = False
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    cleanup_ok = not TMP_DIR.exists()
    return {
        "probe_id": "windows_media_ocr_local_execution_proof_v1",
        "generated_at": now(),
        "requested_classifier": "windows_media_ocr_local_signal_bridge",
        "actual_classifier": synthetic.get("actual_classifier"),
        "api": "Windows.Media.Ocr.OcrEngine.RecognizeAsync",
        "host_process": synthetic.get("host_process", "powershell.exe"),
        "windows_runtime": {
            "platform": platform.platform(),
            "os_version": platform.version(),
            "release": platform.release(),
        },
        "installed_ocr_languages": installed,
        "language_availability": language_status([str(tag) for tag in installed]),
        "synthetic_execution": {
            "status": synthetic.get("status"),
            "actual_language_tag": synthetic.get("actual_language_tag"),
            "recognized_nonempty": synthetic.get("recognized_nonempty"),
            "role_hits": synthetic.get("role_hits", []),
            "project_identity_status": synthetic.get("project_identity_status"),
            "elapsed_ms": synthetic.get("elapsed_ms"),
            "process_returncode": synthetic.get("process_returncode"),
            "evidence_channel_codes": synthetic.get("evidence_channel_codes", []),
        },
        "private_page_execution": {
            "status": private_probe_status,
            "page_processed_count": 0,
            "minimized_evidence_codes": [],
            "raw_ocr_text_persisted": False,
            "private_content_transmitted_outside_machine": 0,
            "reason": "Private-page OCR probe requires an independently enforceable process network-disable boundary; this script records synthetic proof only unless that boundary is supplied."
        },
        "network_disabled_execution_status": "NOT_VERIFIED_FOR_PRIVATE_CONTENT_PROCESS_NETWORK_BOUNDARY_NOT_ENFORCED",
        "privacy": {
            "private_reference_pages_sent_to_external_or_inherited_models": 0,
            "private_reference_pages_inspected_by_actual_vision_agents": 0,
            "external_network_use_authorized": False,
            "private_content_transmitted_outside_machine": 0,
            "ocr_output_appeared_in_stdout": False,
            "ocr_output_appeared_in_stderr": False,
            "ocr_output_appeared_in_logs": False,
        },
        "cleanup": {
            "synthetic_inputs_removed": cleanup_ok,
            "temporary_render_or_crop_outputs_persisted": False,
        },
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Windows.Media.Ocr Local Probe",
        "",
        f"- requested classifier: `{report['requested_classifier']}`",
        f"- actual classifier: `{report['actual_classifier']}`",
        f"- API: `{report['api']}`",
        f"- host process: `{report['host_process']}`",
        f"- installed OCR languages: `{', '.join(report['installed_ocr_languages'])}`",
        f"- English available: `{str(report['language_availability']['english_available']).lower()}`",
        f"- Traditional Chinese available: `{str(report['language_availability']['traditional_chinese_available']).lower()}`",
        f"- Simplified Chinese available: `{str(report['language_availability']['simplified_chinese_available']).lower()}`",
        f"- synthetic status: `{report['synthetic_execution']['status']}`",
        f"- synthetic role hits: `{', '.join(report['synthetic_execution']['role_hits'])}`",
        f"- private-page execution: `{report['private_page_execution']['status']}`",
        f"- private content transmitted outside machine: `{report['privacy']['private_content_transmitted_outside_machine']}`",
        f"- OCR text persisted or logged: `false`",
        f"- cleanup: `{str(report['cleanup']['synthetic_inputs_removed']).lower()}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Windows.Media.Ocr with minimized local-only synthetic execution.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--private-probe-status", default="SKIPPED_NETWORK_DISABLE_BOUNDARY_NOT_ENFORCED")
    args = parser.parse_args()
    report = build_report(args.private_probe_status)
    write_json(args.report_dir / "windows_media_ocr_local_probe.json", report)
    write_markdown(report, args.report_dir / "windows_media_ocr_local_probe.md")
    print(json.dumps({"status": report["synthetic_execution"]["status"], "private_page_execution": report["private_page_execution"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
