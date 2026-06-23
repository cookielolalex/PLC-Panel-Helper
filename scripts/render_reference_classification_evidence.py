from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TMP_ROOT = ROOT / "tmp" / "reference_detection_v3"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def bundled_poppler_tool(name: str) -> str | None:
    candidates = [
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "native"
        / "poppler"
        / "Library"
        / "bin"
        / f"{name}.exe",
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "bin"
        / f"{name}.exe",
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    found = shutil.which(name)
    return found


def render_with_pymupdf(pdf_path: Path, render_dir: Path) -> tuple[str, list[Path]]:
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local runtime
        raise RuntimeError(f"PyMuPDF unavailable: {exc}") from exc

    render_dir.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []
    doc = fitz.open(str(pdf_path))
    try:
        for page_index in range(len(doc)):
            pix = doc[page_index].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            out = render_dir / f"page-{page_index + 1:04d}.png"
            pix.save(str(out))
            pages.append(out)
    finally:
        doc.close()
    return "PYMUPDF", pages


def render_with_poppler(pdf_path: Path, render_dir: Path) -> tuple[str, list[Path]]:
    pdftoppm = bundled_poppler_tool("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("pdftoppm not found in bundled runtime or PATH")
    render_dir.mkdir(parents=True, exist_ok=True)
    prefix = render_dir / "page"
    subprocess.run([pdftoppm, "-png", "-r", "72", str(pdf_path), str(prefix)], cwd=ROOT, check=True)
    pages = sorted(render_dir.glob("page-*.png"))
    if not pages:
        raise RuntimeError("pdftoppm produced no page images")
    return "POPPLER_PDFTOPPM", pages


def render_pdf(pdf_path: Path, task_id: str) -> tuple[str, list[Path], Path]:
    task_dir = TMP_ROOT / task_id
    render_dir = task_dir / "renders" / pdf_path.stem
    try:
        renderer, pages = render_with_pymupdf(pdf_path, render_dir)
    except Exception:
        renderer, pages = render_with_poppler(pdf_path, render_dir)
    return renderer, pages, task_dir


def crop_title_region(page_image: Path) -> Path:
    crop_dir = page_image.parent.parent / "title_crops" / page_image.parent.name
    crop_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(page_image) as image:
        width, height = image.size
        left = int(width * 0.55)
        top = int(height * 0.68)
        crop = image.crop((left, top, width, height))
        out = crop_dir / page_image.name
        crop.save(out)
        return out


def neutral_visual_signature(image_path: Path) -> dict[str, Any]:
    with Image.open(image_path) as image:
        gray = image.convert("L")
        width, height = gray.size
        sample = gray.resize((32, 32))
        pixels = list(sample.getdata())
        dark = sum(1 for p in pixels if p < 220)
        ink_bucket = int(round((dark / len(pixels)) * 20) * 5)
        orientation = "LANDSCAPE" if width > height else "PORTRAIT" if height > width else "SQUARE_OR_UNKNOWN"
        signature_text = f"{orientation}:{width}x{height}:ink{ink_bucket}"
        return {
            "orientation": orientation,
            "width_px": width,
            "height_px": height,
            "coarse_ink_bucket": ink_bucket,
            "signature_id": hashlib.sha256(signature_text.encode("utf-8")).hexdigest().upper()[:16],
        }


def build_evidence(pdf_path: Path, task_id: str) -> dict[str, Any]:
    renderer, pages, task_dir = render_pdf(pdf_path, task_id)
    page_records = []
    for page_number, page_image in enumerate(pages, start=1):
        crop = crop_title_region(page_image)
        page_records.append(
            {
                "page_number": page_number,
                "page_image": str(page_image),
                "title_crop": str(crop),
                "page_signature": neutral_visual_signature(page_image),
                "title_crop_signature": neutral_visual_signature(crop),
            }
        )
    return {
        "task_id": task_id,
        "pdf_sha256": sha256_file(pdf_path),
        "renderer": renderer,
        "task_dir": str(task_dir),
        "page_count": len(page_records),
        "pages": page_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render temporary reference-classification evidence.")
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.output, build_evidence(args.pdf, args.task_id))


if __name__ == "__main__":
    main()
