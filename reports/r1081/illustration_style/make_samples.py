#!/usr/bin/env python3
"""Provas determinísticas de direção de arte Piranesi/Pencz.

Não gera arte nova e não usa IA generativa: aplica linha, hachura, duotone,
textura e marca de placa sobre pranchas existentes. O resultado é referência
visual, não arte final.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075/figures/immersao"
OUT = Path(__file__).resolve().parent / "samples"
PAPER = (242, 232, 207)
INK = (43, 33, 23)
ACCENT = (155, 27, 27)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_gray(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"imagem ilegível: {path}")
    return image


def line_art(gray: np.ndarray, block: int = 15, c: int = 6) -> np.ndarray:
    smooth = cv2.bilateralFilter(gray, 7, 45, 45)
    equalized = cv2.equalizeHist(smooth)
    edges = cv2.adaptiveThreshold(
        equalized, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block, c
    )
    lines = 255 - edges
    shade = cv2.GaussianBlur(equalized, (0, 0), 1.6)
    out = cv2.addWeighted(lines, 0.82, shade, 0.18, 0)
    out = cv2.normalize(out, None, 18, 242, cv2.NORM_MINMAX)
    return out.astype(np.uint8)


def hatch(gray: np.ndarray, step: int = 8) -> np.ndarray:
    smooth = cv2.bilateralFilter(gray, 7, 45, 45)
    equalized = cv2.equalizeHist(smooth)
    height, width = equalized.shape
    canvas = np.full((height, width), 255, np.uint8)
    for y in range(0, height, step):
        for x in range(0, width, step):
            value = int(equalized[y, x])
            if value >= 150:
                continue
            length = max(2, int((150 - value) / 150 * step * 1.7))
            cv2.line(
                canvas, (x, y),
                (min(width - 1, x + length), max(0, y - length)),
                0, 1, cv2.LINE_AA,
            )
    edges = cv2.adaptiveThreshold(
        equalized, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 6
    )
    lines = 255 - edges
    out = cv2.min(canvas, lines)
    return cv2.normalize(out, None, 18, 242, cv2.NORM_MINMAX).astype(np.uint8)


def duotone(gray: np.ndarray, paper=PAPER, ink=INK) -> np.ndarray:
    gray = cv2.normalize(gray, None, 18, 242, cv2.NORM_MINMAX)
    t = gray.astype(np.float32) / 255.0
    out = np.zeros((*gray.shape, 3), np.float32)
    for channel in range(3):
        out[..., channel] = ink[channel] + (paper[channel] - ink[channel]) * t
    return np.clip(out, 0, 255).astype(np.uint8)


def texture(gray: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(42)
    noise = rng.normal(0, 3.2, gray.shape)
    return np.clip(gray.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def vignette(gray: np.ndarray, strength: float = 0.32) -> np.ndarray:
    height, width = gray.shape
    yy, xx = np.ogrid[:height, :width]
    cx, cy = width / 2, height / 2
    distance = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    mask = np.clip(1.08 - strength * distance, 0.55, 1.0)
    return np.clip(gray.astype(np.float32) * mask, 0, 255).astype(np.uint8)


def plate_mark(rgb: np.ndarray, accent: bool = False) -> Image.Image:
    image = Image.fromarray(rgb, "RGB")
    margin = 26
    canvas = Image.new("RGB", (image.width + margin * 2, image.height + margin * 2), PAPER)
    canvas.paste(image, (margin, margin))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(
        [margin - 9, margin - 9, image.width + margin + 8, image.height + margin + 8],
        outline=INK, width=1,
    )
    draw.rectangle(
        [margin - 15, margin - 15, image.width + margin + 14, image.height + margin + 14],
        outline=INK, width=1,
    )
    if accent:
        draw.rectangle(
            [margin - 15, canvas.height - margin + 2, image.width + margin + 14, canvas.height - margin + 5],
            fill=ACCENT,
        )
    return canvas


def process(source: Path, mode: str) -> Image.Image:
    gray = load_gray(source)
    if mode == "pencz_line":
        art = line_art(gray, block=15, c=6)
        art = vignette(art, 0.18)
    elif mode == "piranesi_hatch":
        art = hatch(gray, step=8)
        art = vignette(art, 0.32)
    elif mode == "hybrid":
        base = line_art(gray, block=17, c=6)
        hatched = hatch(gray, step=9)
        art = cv2.min(base, hatched)
        art = vignette(art, 0.26)
    else:
        raise ValueError(mode)
    art = texture(art)
    rgb = duotone(art)
    return plate_mark(rgb, accent=(mode == "hybrid"))


def contact_sheet(items, path: Path) -> None:
    width = 360
    pad = 24
    header = 54
    font = ImageFont.truetype(FONT_PATH, 13)
    font_header = ImageFont.truetype(FONT_PATH, 16)
    tiles = []
    for label, image in items:
        ratio = width / image.width
        thumb = image.resize((width, max(1, round(image.height * ratio))), Image.LANCZOS)
        tile = Image.new("RGB", (width, thumb.height + 52), PAPER)
        tile.paste(thumb, (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((6, thumb.height + 14), label, fill=INK, font=font)
        tiles.append(tile)
    total_w = sum(t.width for t in tiles) + pad * (len(tiles) + 1)
    total_h = max(t.height for t in tiles) + header + pad * 2
    sheet = Image.new("RGB", (total_w, total_h), PAPER)
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 18), "MOLAMBUDOS - DIRECAO DE ARTE PIRANESI/PENCZ - PROVA",
              fill=INK, font=font_header)
    x = pad
    for tile in tiles:
        sheet.paste(tile, (x, header))
        x += tile.width + pad
    sheet.save(path, optimize=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("placa_00.png", "pencz_line", "placa_00_pencz_line.png", "Pencz - linha"),
        ("placa_01.png", "piranesi_hatch", "placa_01_piranesi_hatch.png", "Piranesi - hachura"),
        ("placa_03.png", "hybrid", "placa_03_hybrid.png", "Hibrido - linha + hachura"),
    ]
    manifest = {
        "schema_version": 1,
        "status": "visual_reference_only",
        "source": str(SOURCE),
        "note": "Provas determinísticas; não são arte final, não são prova histórica e não usam IA generativa.",
        "items": [],
    }
    sheet_items = []
    for source_name, mode, output_name, label in jobs:
        source = SOURCE / source_name
        if not source.is_file():
            raise SystemExit(f"origem ausente: {source}")
        image = process(source, mode)
        target = OUT / output_name
        image.save(target, optimize=True)
        manifest["items"].append({
            "source": source_name,
            "mode": mode,
            "output": output_name,
            "label": label,
            "pixels": [image.width, image.height],
            "source_sha256": sha256(source),
            "output_sha256": sha256(target),
            "bytes": target.stat().st_size,
        })
        sheet_items.append((label, image))
    contact_sheet(sheet_items, OUT / "contact_sheet.png")
    manifest["contact_sheet"] = {
        "path": "contact_sheet.png",
        "sha256": sha256(OUT / "contact_sheet.png"),
    }
    manifest["limits"] = [
        "Não é arte final; é prova de direção.",
        "Não há upscale; as dimensões são as das pranchas de origem.",
        "Não substitui desenhista, revisão de sensibilidade ou prova de impressão.",
        "Piranesi e Pencz são domínio público; a prova não copia uma prancha específica.",
    ]
    (OUT.parent / "samples_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:2500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
