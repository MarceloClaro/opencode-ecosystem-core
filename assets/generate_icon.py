# -*- coding: utf-8 -*-
"""
Gerador de ícone — OpenCode Ecosystem Core / marceloclaro (SPEC-935-R116)
==========================================================================
Gera um ícone original e simples, sem depender de nenhum material de arte
externo: um nó central "M" (o orquestrador marceloclaro) conectado a
quatro nós satélite (os agentes/CLIs que ele coordena), sobre um
círculo de fundo.

Uso:
    python3 assets/generate_icon.py

Gera:
    assets/icon.png   — 256x256, fonte única
    assets/icon.ico   — multi-resolução (16/32/48/256), para atalhos Windows

Para macOS (.icns), que exige `iconutil`/`sips` rodando em macOS real,
ver `installer/macos/build_icns.sh` — este script prepara o iconset de
PNGs necessário; a conversão final precisa ser feita em hardware Apple.
"""

from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

SIZE = 256
BG_COLOR = (17, 24, 39, 255)        # slate-900 — fundo escuro neutro
ACCENT_COLOR = (56, 189, 248, 255)  # sky-400 — cor de destaque (conexões/nós)
CORE_COLOR = (248, 250, 252, 255)   # quase-branco — nó central / letra M


def _draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size / 2
    margin = size * 0.06

    # Círculo de fundo
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=BG_COLOR,
    )

    # 4 nós satélite (agentes/CLIs coordenados) + linhas de conexão
    satellite_radius = size * 0.34
    node_r = size * 0.045
    core_r = size * 0.16

    for i in range(4):
        angle = math.pi / 4 + i * (math.pi / 2)  # 45°, 135°, 225°, 315°
        sx = center + satellite_radius * math.cos(angle)
        sy = center + satellite_radius * math.sin(angle)
        draw.line([center, center, sx, sy], fill=ACCENT_COLOR, width=max(2, int(size * 0.012)))
        draw.ellipse(
            [sx - node_r, sy - node_r, sx + node_r, sy + node_r],
            fill=ACCENT_COLOR,
        )

    # Nó central (orquestrador)
    draw.ellipse(
        [center - core_r, center - core_r, center + core_r, center + core_r],
        fill=CORE_COLOR,
        outline=ACCENT_COLOR,
        width=max(2, int(size * 0.01)),
    )

    # Letra "M" no nó central
    font = None
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if os.path.exists(candidate):
            font = ImageFont.truetype(candidate, int(core_r * 1.3))
            break
    if font is None:
        font = ImageFont.load_default()

    text = "M"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (center - tw / 2 - bbox[0], center - th / 2 - bbox[1]),
        text, fill=BG_COLOR, font=font,
    )

    return img


def generate() -> None:
    icon = _draw_icon(SIZE)

    png_path = os.path.join(HERE, "icon.png")
    icon.save(png_path, format="PNG")

    ico_path = os.path.join(HERE, "icon.ico")
    icon.save(
        ico_path, format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)],
    )

    # Iconset de PNGs para quem for gerar o .icns num Mac real
    iconset_dir = os.path.join(HERE, "icon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)
    for px, name in (
        (16, "icon_16x16.png"), (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"), (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"), (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"), (512, "icon_256x256@2x.png"),
    ):
        _draw_icon(px).save(os.path.join(iconset_dir, name), format="PNG")

    print(f"Gerado: {png_path} ({os.path.getsize(png_path)} bytes)")
    print(f"Gerado: {ico_path} ({os.path.getsize(ico_path)} bytes)")
    print(f"Gerado: {iconset_dir}/ (8 PNGs para build_icns.sh)")


if __name__ == "__main__":
    generate()
