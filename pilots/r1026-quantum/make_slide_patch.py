#!/usr/bin/env python3
"""Gera o patch PT-BR do slide e a máscara de composição (R1027)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 935, 864
BG = (245, 243, 255)
INK = (22, 22, 22)
MUTED = (82, 82, 82)
PURPLE = (105, 41, 196)
ACCENT = (139, 92, 246)
CARD = (255, 255, 255)
BORDER = (208, 208, 216)
CALLOUT = (240, 234, 251)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def chip_eagle(image: Image.Image, cx: int, cy: int) -> None:
    # Losango com malha recortada pela silhueta, inspirado no chip Eagle.
    layer = Image.new("RGBA", (180, 140), (0, 0, 0, 0))
    points = [(90, 10), (170, 70), (90, 130), (10, 70)]
    ImageDraw.Draw(layer).polygon(points, fill=(232, 232, 242, 255), outline=(74, 74, 85, 255), width=2)
    grid = Image.new("RGBA", (180, 140), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    for offset in range(-3, 4):
        grid_draw.line(
            [(90 + offset * 20, 10 + abs(offset) * 10),
             (90 + offset * 20, 130 - abs(offset) * 10)],
            fill=(120, 120, 135, 255), width=1,
        )
    for offset in range(-2, 3):
        grid_draw.line(
            [(10 + abs(offset) * 20, 70 + offset * 16),
             (170 - abs(offset) * 20, 70 + offset * 16)],
            fill=(120, 120, 135, 255), width=1,
        )
    mask = Image.new("L", (180, 140), 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    grid.putalpha(ImageChops.multiply(grid.getchannel("A"), mask))
    layer.alpha_composite(grid)
    image.paste(layer, (cx - 90, cy - 70), layer)


def chip_heron(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    # Escada de três blocos, inspirada no chip Heron.
    for index, (dx, dy) in enumerate(((-58, 22), (-10, -4), (38, -30))):
        box = (cx + dx, cy + dy - 24, cx + dx + 48, cy + dy + 24)
        draw.rounded_rectangle(box, radius=4, fill=(232, 232, 242),
                               outline=(74, 74, 85), width=2)
        for step in range(1, 4):
            draw.line([(box[0] + step * 12, box[1]), (box[0] + step * 12, box[3])],
                      fill=(120, 120, 135), width=1)
        for step in range(1, 3):
            draw.line([(box[0], box[1] + step * 16), (box[2], box[1] + step * 16)],
                      fill=(120, 120, 135), width=1)


def build() -> None:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)

    draw.text((36, 30), "QISKIT  •  FUNDAMENTOS", font=font(16, True), fill=PURPLE)
    draw.text((36, 58), "Computação quântica na prática", font=font(38, True), fill=INK)
    draw.text((36, 108), "Processadores IBM com mais de 100 qubits", font=font(21), fill=MUTED)
    draw.rectangle((36, 146, 116, 151), fill=ACCENT)

    # Cards Eagle / Heron.
    for x, title, subtitle in ((36, "Eagle", "127 qubits"), (484, "Heron", "133 qubits × p")):
        draw.rounded_rectangle((x, 178, x + 415, 478), radius=12, fill=CARD, outline=BORDER, width=2)
        draw.text((x + 24, 200), title, font=font(30, True), fill=INK)
        draw.text((x + 24, 242), subtitle, font=font(21), fill=MUTED)
        draw.text((x + 24, 438), "processador", font=font(14), fill=MUTED)
    chip_eagle(image, 243, 355)
    chip_heron(draw, 692, 355)

    # Callout didático.
    draw.rounded_rectangle((36, 506, 899, 764), radius=12, fill=CALLOUT, outline=ACCENT, width=2)
    draw.text((58, 526), "Por que a mudança?", font=font(23, True), fill=PURPLE)
    body = (
        "Alguns números de qubits ainda podem ser simulados classicamente. "
        "Os chips maiores abrem espaço para problemas que a simulação não alcança. "
        "É por isso que os processadores menores saíram de linha."
    )
    y = 562
    for line in wrap(draw, body, font(19), 800):
        draw.text((58, y), line, font=font(19), fill=INK)
        y += 28
    draw.text(
        (58, 700),
        "Menos processadores menores  →  mais capacidade de 100+ qubits",
        font=font(17, True), fill=PURPLE,
    )

    draw.text((36, 812), "Fonte: Qiskit  •  tradução para estudo", font=font(14), fill=MUTED)
    image.save(ROOT / "slide-patch.png")

    mask = Image.new("L", (W, H), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((2, 2, W - 2, H - 2), radius=10, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(18))
    mask.save(ROOT / "slide-patch-mask.png")
    print("ok", image.size, (ROOT / "slide-patch.png").stat().st_size)


if __name__ == "__main__":
    build()
