#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera 100 ícones de conceito (hanzi) para o cabeçalho das laudas."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LIVRO = Path(__file__).resolve().parents[1]
RAIZ = LIVRO.parent
sys.path.insert(0, str(LIVRO))

from base.base_conceitos import CONCEITOS  # noqa: E402
from gerar_secoes import PARTES  # noqa: E402

SAIDA = LIVRO / "sprites_conceitos"
SAIDA.mkdir(parents=True, exist_ok=True)
FONTE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

TAM = 48


def main() -> None:
    for i, c in enumerate(CONCEITOS, 1):
        letra = c["titulo"][0].upper()
        cor = "#" + PARTES[c["parte"]][2]
        img = Image.new("RGBA", (TAM, TAM), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([1, 1, TAM - 2, TAM - 2], radius=6,
                            fill=(11, 18, 32, 255), outline=cor, width=2)
        try:
            fonte = ImageFont.truetype(str(FONTE), 30)
        except Exception:
            fonte = ImageFont.load_default()
        bbox = d.textbbox((0, 0), letra, font=fonte)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text(((TAM - w) / 2 - bbox[0], (TAM - h) / 2 - bbox[1] + 1),
               letra, font=fonte, fill=cor)
        img.save(SAIDA / f"C{i:03d}.png")
    print(f"Ícones: {len(list(SAIDA.glob('C*.png')))}")


if __name__ == "__main__":
    main()
