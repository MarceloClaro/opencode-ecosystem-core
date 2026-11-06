#!/usr/bin/env python3
"""Monta 6 pranchas de prova com duotone, acento carmim e proveniência.

Não gera arte nova: usa as artes existentes do pacote R1082 e a prancha
`placa_00`. As pranchas ficam a 300 DPI no tamanho final de 86 mm; não há
2x a 300 DPI com as fontes atuais.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
CAPAS = ROOT / "literatura/molambudos/capas"
PIRANESI = CAPAS / "piranesi_pencz_2026-11-05/fontes"
FINAL = CAPAS / "molambudos_final/fontes"
PLACA = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075/figures/immersao"
OUT = Path(__file__).resolve().parent / "plate_proof" / "plates"
PAPER = (242, 232, 207)
INK = (43, 33, 23)
ACCENT = (155, 27, 27)
FINAL_WIDTH_MM = 86.0
MARGIN = 24


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duotone(image: Image.Image, contrast: float = 1.05) -> Image.Image:
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    if contrast != 1.0:
        gray = gray.point(lambda value: min(255, max(0, int((value - 128) * contrast + 128))))
    t = np.asarray(gray, dtype=np.float32) / 255.0
    rgb = np.zeros((*t.shape, 3), dtype=np.float32)
    for channel in range(3):
        rgb[..., channel] = INK[channel] + (PAPER[channel] - INK[channel]) * t
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


def plate(image: Image.Image, accent: str) -> Image.Image:
    width, height = image.width + MARGIN * 2, image.height + MARGIN * 2
    canvas = Image.new("RGB", (width, height), PAPER)
    canvas.paste(image, (MARGIN, MARGIN))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([MARGIN - 8, MARGIN - 8, width - MARGIN + 7, height - MARGIN + 7],
                   outline=INK, width=1)
    draw.rectangle([MARGIN - 14, MARGIN - 14, width - MARGIN + 13, height - MARGIN + 13],
                   outline=INK, width=1)
    if accent == "stamp":
        draw.rectangle([width - MARGIN - 22, height - MARGIN + 4,
                        width - MARGIN - 2, height - MARGIN + 14], fill=ACCENT)
    elif accent == "seal":
        cx, cy = width - MARGIN - 12, height - MARGIN + 9
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=ACCENT)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=PAPER)
    elif accent == "rule":
        draw.rectangle([MARGIN - 14, height - MARGIN + 4, width - MARGIN + 13,
                        height - MARGIN + 7], fill=ACCENT)
    elif accent == "cross":
        cx, cy = width - MARGIN - 12, height - MARGIN + 9
        draw.rectangle([cx - 9, cy - 2, cx + 9, cy + 2], fill=ACCENT)
        draw.rectangle([cx - 2, cy - 9, cx + 2, cy + 9], fill=ACCENT)
    return canvas


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("carceri-colonia", "Carceri do Colônia", PIRANESI / "arte_confinamento.png",
         "stamp", "arquitetura opressiva; figura pequena; hachura", "ai_generated"),
        ("paisagem-erodida", "Paisagem Erodida", PIRANESI / "arte_sertao.png",
         "rule", "seca; mulher e criança; arcos", "ai_generated"),
        ("arquivo-doente", "Arquivo Doente", PIRANESI / "arte_arquivo.png",
         "seal", "estantes; livros; selo", "ai_generated"),
        ("retrato-emblematico", "Retrato Emblemático", PLACA / "placa_00.png",
         "rule", "criança; figura espectral", "existing_plate"),
        ("tabela-alegorica", "Tabela Alegórica", FINAL / "arte_frontal_original.png",
         "seal", "diário; coruja; foto; caatinga", "ai_generated"),
        ("anatomia-contaminacao", "Anatomia da Contaminação", PLACA / "placa_00.png",
         "cross", "detalhe do rosto; alto contraste", "existing_plate"),
    ]
    manifest = {
        "schema_version": 1,
        "status": "proof_only",
        "final_width_mm": FINAL_WIDTH_MM,
        "two_x_width_mm": FINAL_WIDTH_MM * 2,
        "two_x_300dpi": False,
        "note": ("As fontes têm 1024-1122 px de largura: 300 DPI no tamanho final "
                 "de 86 mm, mas ~151-173 DPI a 2x. Não houve upscale."),
        "items": [],
    }
    for plate_id, title, source, accent, description, source_type in jobs:
        if not source.is_file():
            raise SystemExit(f"origem ausente: {source}")
        with Image.open(source) as raw:
            raw = raw.convert("RGB")
            if plate_id == "anatomia-contaminacao":
                raw = raw.crop((49, 37, 1073, 1402))
            art = duotone(raw, contrast=1.10 if plate_id == "anatomia-contaminacao" else 1.03)
        output = plate(art, accent)
        dpi = round(output.width / (FINAL_WIDTH_MM / 25.4), 2)
        target = OUT / f"{plate_id}.png"
        quantized = output.quantize(colors=16, method=Image.MEDIANCUT)
        quantized.save(target, dpi=(dpi, dpi), optimize=True)
        manifest["items"].append({
            "id": plate_id,
            "title": title,
            "description": description,
            "source": str(source.relative_to(ROOT)),
            "source_type": source_type,
            "source_sha256": sha256(source),
            "output": target.name,
            "output_sha256": sha256(target),
            "pixels": [output.width, output.height],
            "final_width_mm": FINAL_WIDTH_MM,
            "effective_dpi": dpi,
            "two_x_effective_dpi": round(output.width / (FINAL_WIDTH_MM * 2 / 25.4), 2),
            "required_width_px_for_2x_300dpi": math.ceil(FINAL_WIDTH_MM * 2 / 25.4 * 300),
            "two_x_300dpi": False,
        })
    (OUT.parent / "plates_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
