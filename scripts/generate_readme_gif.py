#!/usr/bin/env python3
"""Gera o GIF do pipeline científico R1051–R1054 para o README.

Requisitos: Pillow e ffmpeg. O script é determinístico, exceto pela codificação
do GIF. Ele não baixa nada e não altera o pipeline; apenas desenha o artefato
de documentação.

Uso:
    python3 scripts/generate_readme_gif.py
    python3 scripts/generate_readme_gif.py --out docs/images/research-pipeline-r1054.gif
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1000, 520
FPS = 15
DURATION = 8.0
STAGE_TIME = 0.55
FINAL_START = STAGE_TIME * 10
FADE = 0.35
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (8, 7, 15)
INK = (247, 245, 255)
MUTED = (185, 177, 206)
DIM = (143, 134, 168)
PURPLE = (167, 139, 250)
LIME = (163, 230, 53)
CARD = (23, 17, 38)
CARD_EDGE = (74, 58, 112)
GRID = (40, 30, 62)

STAGES = [
    ("Tema + pergunta", "explícita ou provisória"),
    ("Contrato", "fontes · filtros · budget"),
    ("Busca + dedupe", "9 plataformas nativas"),
    ("Triagem", "humana + conflitos"),
    ("Texto integral", "página + hash + aprovação"),
    ("Integridade", "retratações/correções"),
    ("Meta-análise", "REML/DL · I² · predição"),
    ("RoB + GRADE", "sugestão não autoritativa"),
    ("Manuscrito", "IMRaD + auditoria"),
    ("Submissão", "fail-closed + gate"),
]

CARD_W, CARD_H = 168, 88
GAP = 18
LEFT = 48
ROW_Y = (150, 270)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def text(draw: ImageDraw.ImageDraw, xy, value, *, size=14, bold=False,
         fill=INK, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def make_background() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    px = img.load()
    for y in range(H):
        for x in range(W):
            t = (x / W) * 0.55 + (y / H) * 0.45
            r = int(8 + 19 * t)
            g = int(7 + 11 * t)
            b = int(15 + 36 * t)
            px[x, y] = (r, g, b)
    draw = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 44):
        draw.line((x, 0, x, H), fill=(*GRID, 90), width=1)
    for y in range(0, H, 44):
        draw.line((0, y, W, y), fill=(*GRID, 90), width=1)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((760, -180, 1240, 300), fill=(124, 58, 237, 60))
    gd.ellipse((-180, 330, 320, 760), fill=(167, 139, 250, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    return img


def card_xy(index: int):
    row = index // 5
    col = index % 5
    return LEFT + col * (CARD_W + GAP), ROW_Y[row]


def draw_card(base: Image.Image, index: int, state: str, pulse: float):
    x, y = card_xy(index)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    active = state == "active"
    done = state == "done"
    if active:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.rounded_rectangle(
            (x - 4, y - 4, x + CARD_W + 4, y + CARD_H + 4),
            radius=16, fill=(163, 230, 53, int(45 + 25 * pulse)),
        )
        glow = glow.filter(ImageFilter.GaussianBlur(12))
        layer = Image.alpha_composite(layer, glow)
        draw = ImageDraw.Draw(layer)
    fill = (29, 22, 48) if active else CARD
    edge = LIME if active else (PURPLE if done else CARD_EDGE)
    width = 2 if active or done else 1
    draw.rounded_rectangle(
        (x, y, x + CARD_W, y + CARD_H), radius=13,
        fill=(*fill, 255), outline=(*edge, 255), width=width,
    )
    title_fill = INK if active or done else (205, 197, 222)
    text(draw, (x + 14, y + 16), STAGES[index][0], size=13, bold=True,
         fill=title_fill)
    text(draw, (x + 14, y + 42), STAGES[index][1], size=10, fill=DIM)
    if done:
        draw.ellipse((x + CARD_W - 25, y + 13, x + CARD_W - 11, y + 27),
                     fill=(*LIME, 255))
        text(draw, (x + CARD_W - 18, y + 19), "✓", size=10, bold=True,
             fill=(8, 7, 15), anchor="mm")
    elif active:
        draw.ellipse((x + CARD_W - 25, y + 13, x + CARD_W - 11, y + 27),
                     fill=(*LIME, 255))
        text(draw, (x + CARD_W - 18, y + 19), "›", size=14, bold=True,
             fill=(8, 7, 15), anchor="mm")
    base.alpha_composite(layer)


def render_frame(frame: int, background: Image.Image) -> Image.Image:
    t = frame / FPS
    active = min(9, int(t / STAGE_TIME)) if t < FINAL_START else 10
    pulse = 0.5 + 0.5 * math.sin(t * 7.0)
    img = background.convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    text(draw, (LEFT, 38), "OPENCODE ECOSYSTEM CORE", size=12, bold=True,
         fill=LIME)
    text(draw, (LEFT, 62), "Pesquisador científico", size=30, bold=True)
    text(draw, (LEFT, 102), "R1051–R1054 · do tema ao pacote de submissão",
         size=14, fill=MUTED)
    text(draw, (W - 48, 54), "EVIDENCE-FIRST", size=11, bold=True,
         fill=PURPLE, anchor="ra")
    text(draw, (W - 48, 74), "sem overclaim", size=11, fill=DIM, anchor="ra")

    for i in range(10):
        if i < active:
            state = "done"
        elif i == active and t < FINAL_START:
            state = "active"
        elif t >= FINAL_START:
            state = "done"
        else:
            state = "next"
        draw_card(img, i, state, pulse)

    progress = min(1.0, t / FINAL_START) if t < FINAL_START else 1.0
    bar_x, bar_y, bar_w = LEFT, 424, W - 2 * LEFT
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + 5),
                           radius=3, fill=(42, 33, 64, 255))
    fill_w = int(bar_w * progress)
    if fill_w > 0:
        draw.rounded_rectangle((bar_x, bar_y, bar_x + fill_w, bar_y + 5),
                               radius=3, fill=(*LIME, 255))
        dot_x = bar_x + fill_w
        draw.ellipse((dot_x - 5, bar_y - 2, dot_x + 5, bar_y + 8),
                     fill=(*LIME, 255))
    text(draw, (LEFT, 438), "progresso do pipeline", size=10, fill=DIM)
    text(draw, (W - 48, 438), f"{int(progress * 100):02d}%", size=10,
         bold=True, fill=LIME, anchor="ra")

    text(draw, (LEFT, 478), "github.com/MarceloClaro/opencode-ecosystem-core",
         size=11, fill=DIM)
    text(draw, (W - 48, 478), "410 tests · doctor 22/22", size=11, bold=True,
         fill=INK, anchor="ra")

    if t >= FINAL_START:
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle((LEFT, 364, W - LEFT, 410), radius=12,
                             fill=(12, 10, 20, 235), outline=(*LIME, 220),
                             width=2)
        text(od, (W // 2, 377), "EVIDENCE-FIRST · SEM ACEITE/PUBLICAÇÃO AUTOMÁTICA",
             size=12, bold=True, fill=LIME, anchor="ma")
        text(od, (W // 2, 396),
             "tema → evidência → meta-análise → manuscrito → gate humano",
             size=11, fill=MUTED, anchor="ma")
        img.alpha_composite(overlay)

    if t < FADE:
        alpha = int(255 * (1 - t / FADE))
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, alpha)))
    elif t > DURATION - FADE:
        alpha = int(255 * ((t - (DURATION - FADE)) / FADE))
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, alpha)))

    return img.convert("RGB")


def build(out: Path) -> Path:
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg não encontrado")
    out.parent.mkdir(parents=True, exist_ok=True)
    background = make_background()
    frames = int(DURATION * FPS)
    with tempfile.TemporaryDirectory(prefix="readme-gif-") as tmp:
        tmp_path = Path(tmp)
        for index in range(frames):
            render_frame(index, background).save(tmp_path / f"frame-{index:03d}.png")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(FPS),
            "-i", str(tmp_path / "frame-%03d.png"),
            "-vf",
            "split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=3",
            "-loop", "0", str(out),
        ], check=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=Path("docs/images/research-pipeline-r1054.gif"))
    args = parser.parse_args()
    path = build(args.out)
    print(f"GIF: {path} ({path.stat().st_size / 1024 / 1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
