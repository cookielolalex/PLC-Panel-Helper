from __future__ import annotations

import argparse
import csv
from pathlib import Path

from harness_lib import TARGET_OUTPUT_TYPES, read_json, sha256_json, write_json


RENDERER_VERSION = "bootstrap_renderer_v0"


def render_one(output_path: Path, title: str, project_id: str, model_hash: str, panel_rows: list[dict], run_id: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfgen import canvas

    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        font_name = "STSong-Light"
    except Exception:
        font_name = "Helvetica"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setTitle(title)
    c.setAuthor("PLC Panels Generation Helper")
    width, height = A4
    c.setFont(font_name, 16)
    c.drawString(36, height - 48, title)
    c.setFont(font_name, 10)
    c.drawString(36, height - 72, f"Project: {project_id}")
    c.drawString(36, height - 88, f"Run: {run_id}")
    c.drawString(36, height - 104, f"Drawing model SHA-256: {model_hash}")
    c.drawString(36, height - 120, f"Renderer: {RENDERER_VERSION}")
    y = height - 152
    c.setFont(font_name, 11)
    for panel in panel_rows:
        c.drawString(36, y, f"Panel {panel.get('panel_id')}: {panel.get('width')} x {panel.get('height')} {panel.get('verification_status', '')}")
        y -= 18
        if y < 72:
            c.showPage()
            c.setFont(font_name, 11)
            y = height - 72
    c.showPage()
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the three required PDFs from one drawing_model.")
    parser.add_argument("drawing_model", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", default="RUN")
    parser.add_argument("--index", type=Path)
    args = parser.parse_args()

    model = read_json(args.drawing_model)
    project_id = model["project_id"]
    model_hash = sha256_json(model)
    rendered = []
    titles = {
        "production": "生管課用圖",
        "sheetmetal": "鈑金施工圖",
        "punch": "沖孔施工圖",
    }
    for output_type, pattern in TARGET_OUTPUT_TYPES.items():
        filename = pattern.format(project_id=project_id)
        path = args.output_dir / filename
        render_one(path, titles[output_type], project_id, model_hash, model["panels"], args.run_id)
        rendered.append({
            "output_type": output_type,
            "path": str(path),
            "project_id": project_id,
            "drawing_model_hash": model_hash,
            "renderer_version": RENDERER_VERSION,
            "run_id": args.run_id
        })
    index_path = args.index or args.output_dir / f"drawing_index_{project_id}.csv"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rendered[0].keys()))
        writer.writeheader()
        writer.writerows(rendered)
    write_json(args.output_dir / f"render_manifest_{project_id}.json", {
        "project_id": project_id,
        "run_id": args.run_id,
        "drawing_model_hash": model_hash,
        "renderer_version": RENDERER_VERSION,
        "outputs": rendered
    })
    print(f"rendered {len(rendered)} PDFs")


if __name__ == "__main__":
    main()

