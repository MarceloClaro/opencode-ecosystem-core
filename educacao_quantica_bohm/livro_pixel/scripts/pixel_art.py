#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arte pixel para a edição de 1000 laudas."""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
SPRITES = RAIZ / "sprites"
SPRITES.mkdir(parents=True, exist_ok=True)

FUNDO = (7, 11, 18)
NOITE = (11, 18, 30)
GRAMA = (62, 124, 58)
TERRA = (107, 74, 47)
PEDRA = (58, 63, 70)
CIANO = (94, 234, 212)
OURO = (251, 191, 36)
VERMELHO = (251, 113, 133)
ROXO = (167, 139, 250)
VERDE = (52, 211, 153)
BRANCO = (232, 240, 255)
CINZA = (148, 163, 184)


def _px(d: ImageDraw.ImageDraw, x: int, y: int, cor, tam: int = 4) -> None:
    d.rectangle([x, y, x + tam - 1, y + tam - 1], fill=cor)


def icone(nome: str, cor) -> None:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # contorno pixelado comum
    if nome == "ideia":
        d.rectangle([5, 1, 10, 2], fill=cor)
        d.rectangle([4, 3, 11, 6], fill=cor)
        d.rectangle([5, 7, 10, 9], fill=cor)
        d.rectangle([6, 10, 9, 11], fill=CINZA)
        d.rectangle([6, 12, 9, 13], fill=CINZA)
        d.rectangle([7, 7, 8, 8], fill=BRANCO)
    elif nome == "analogia":
        for k in range(3):
            d.rectangle([1, 6 + k * 2, 4, 7 + k * 2], fill=CIANO)
            d.rectangle([11, 4 + k * 2, 14, 5 + k * 2], fill=OURO)
        d.rectangle([5, 8, 10, 9], fill=cor)
    elif nome == "pratica":
        d.rectangle([2, 9, 12, 13], fill=cor)
        d.rectangle([4, 5, 7, 9], fill=cor)
        d.rectangle([7, 3, 8, 9], fill=cor)
        d.rectangle([9, 5, 11, 7], fill=cor)
    elif nome == "laboratorio":
        d.rectangle([6, 1, 9, 3], fill=CINZA)
        d.rectangle([5, 4, 10, 6], fill=cor)
        d.rectangle([4, 7, 11, 12], fill=cor)
        d.rectangle([3, 13, 12, 14], fill=cor)
        d.rectangle([6, 9, 7, 10], fill=BRANCO)
    elif nome == "erro":
        d.polygon([(8, 1), (15, 14), (1, 14)], fill=cor)
        d.rectangle([7, 5, 8, 9], fill=NOITE)
        d.rectangle([7, 11, 8, 12], fill=NOITE)
    elif nome == "alem":
        d.rectangle([2, 2, 12, 13], fill=cor)
        d.rectangle([3, 3, 6, 12], fill=NOITE)
        d.rectangle([7, 3, 11, 12], fill=NOITE)
        d.rectangle([2, 2, 12, 3], fill=BRANCO)
    elif nome == "dialogo":
        d.rectangle([1, 3, 9, 8], fill=cor)
        d.rectangle([6, 7, 14, 12], fill=OURO)
        d.rectangle([3, 9, 4, 9], fill=cor)
        d.rectangle([10, 13, 11, 13], fill=OURO)
    elif nome == "etica":
        d.rectangle([7, 2, 8, 13], fill=cor)
        d.rectangle([3, 4, 12, 5], fill=cor)
        d.rectangle([2, 6, 5, 9], fill=cor)
        d.rectangle([10, 6, 13, 9], fill=cor)
    elif nome == "vida":
        d.rectangle([2, 8, 13, 13], fill=cor)
        d.polygon([(1, 8), (8, 2), (14, 8)], fill=OURO)
        d.rectangle([7, 10, 8, 13], fill=NOITE)
    elif nome == "checkpoint":
        d.rectangle([3, 1, 4, 14], fill=CINZA)
        d.rectangle([5, 2, 12, 8], fill=cor)
        d.rectangle([5, 2, 12, 3], fill=BRANCO)
    else:
        d.rectangle([2, 2, 13, 13], fill=cor)

    img = img.resize((128, 128), Image.Resampling.NEAREST)
    img.save(SPRITES / f"{nome}.png")


def capa() -> None:
    rng = random.Random(42)
    img = Image.new("RGB", (900, 1350), FUNDO)
    d = ImageDraw.Draw(img)

    # estrelas
    for _ in range(120):
        x = rng.randrange(0, 900, 4)
        y = rng.randrange(0, 820, 4)
        cor = rng.choice([BRANCO, CIANO, CINZA])
        _px(d, x, y, cor, rng.choice([2, 2, 4]))

    # lua pixelada
    d.ellipse([690, 110, 810, 230], fill=(242, 201, 76))
    d.ellipse([720, 140, 750, 170], fill=(214, 170, 55))
    d.ellipse([760, 180, 780, 200], fill=(214, 170, 55))

    # montanhas
    d.polygon([(0, 900), (120, 720), (240, 900)], fill=NOITE)
    d.polygon([(180, 900), (340, 650), (500, 900)], fill=(15, 26, 44))
    d.polygon([(440, 900), (620, 700), (800, 900)], fill=NOITE)
    d.polygon([(700, 900), (820, 760), (900, 900)], fill=(15, 26, 44))

    # chão
    d.rectangle([0, 900, 900, 1350], fill=TERRA)
    d.rectangle([0, 900, 900, 940], fill=GRAMA)
    for x in range(0, 900, 40):
        d.rectangle([x, 940, x + 20, 960], fill=(48, 98, 46))
    for _ in range(40):
        x = rng.randrange(0, 900, 20)
        y = rng.randrange(980, 1330, 20)
        _px(d, x, y, PEDRA, 12)

    # caminho de pixels
    for i in range(0, 260, 12):
        x = 300 + i
        y = 1040 - int(i * 0.55)
        _px(d, x, y, (150, 120, 80), 8)

    # cubo quântico isométrico
    cx, cy = 470, 760
    s = 90
    topo = [(cx, cy - s), (cx + s, cy - s // 2), (cx, cy), (cx - s, cy - s // 2)]
    esq = [(cx - s, cy - s // 2), (cx, cy), (cx, cy + s), (cx - s, cy + s // 2)]
    dir_ = [(cx, cy), (cx + s, cy - s // 2), (cx + s, cy + s // 2), (cx, cy + s)]
    d.polygon(topo, fill=(143, 247, 232))
    d.polygon(esq, fill=(47, 176, 164))
    d.polygon(dir_, fill=(28, 128, 122))
    for i in range(-3, 4):
        _px(d, cx + i * 18, cy - s + 20, BRANCO, 4)
    # brilho
    for r in range(1, 5):
        d.rectangle([cx - s - r * 12, cy - s - r * 12,
                     cx + s + r * 12, cy + s + r * 12],
                    outline=(94, 234, 212, 20), width=2)

    # tochas
    for x in (180, 740):
        d.rectangle([x, 900, x + 12, 1020], fill=(92, 64, 38))
        d.rectangle([x - 8, 860, x + 20, 900], fill=OURO)
        d.rectangle([x - 4, 840, x + 16, 870], fill=VERMELHO)
        d.rectangle([x, 828, x + 12, 848], fill=(255, 230, 120))

    # personagem
    px, py = 320, 1020
    d.rectangle([px, py, px + 24, py + 40], fill=(30, 41, 59))
    d.rectangle([px + 4, py - 24, px + 20, py], fill=(217, 154, 108))
    d.rectangle([px + 2, py - 28, px + 22, py - 18], fill=(20, 24, 32))
    d.rectangle([px + 8, py + 40, px + 12, py + 64], fill=(30, 41, 59))
    d.rectangle([px + 16, py + 40, px + 20, py + 64], fill=(30, 41, 59))

    # partículas
    for _ in range(30):
        x = rng.randrange(380, 560, 8)
        y = rng.randrange(620, 900, 8)
        _px(d, x, y, CIANO, 2)

    img.save(RAIZ / "capa_pixel.png")
    print("  ✓ capa_pixel.png")


def banners() -> None:
    cores = [CIANO, OURO, VERDE, ROXO, VERMELHO, (96, 165, 250),
             (244, 114, 182), (251, 146, 60), (45, 212, 191), (163, 230, 53)]
    for i, cor in enumerate(cores, 1):
        img = Image.new("RGB", (900, 240), NOITE)
        d = ImageDraw.Draw(img)
        # blocos de terreno
        d.rectangle([0, 190, 900, 240], fill=TERRA)
        d.rectangle([0, 190, 900, 205], fill=GRAMA)
        for x in range(0, 900, 30):
            d.rectangle([x, 205, x + 15, 220], fill=(48, 98, 46))
        # número grande
        d.rectangle([40, 40, 160, 160], fill=cor)
        d.rectangle([60, 60, 140, 140], fill=NOITE)
        # "número" em blocos
        if i == 1:
            d.rectangle([85, 75, 115, 85], fill=cor)
            d.rectangle([105, 85, 115, 125], fill=cor)
            d.rectangle([85, 125, 115, 135], fill=cor)
        else:
            # barras simples representando o número
            for k in range(i):
                d.rectangle([72 + k * 9, 110, 78 + k * 9, 135], fill=cor)
        # linhas de circuito
        for k in range(3):
            d.rectangle([220, 80 + k * 30, 840, 84 + k * 30], fill=(42, 54, 64))
            d.rectangle([300 + k * 60, 68 + k * 30, 340 + k * 60, 96 + k * 30], fill=cor)
        img.save(RAIZ / f"banner_{i:02d}.png")
    print("  ✓ banners 01-10")


def grade() -> None:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (15, 0)], fill=(30, 41, 59, 90))
    d.line([(0, 0), (0, 15)], fill=(30, 41, 59, 90))
    img.save(RAIZ / "grade.png")
    print("  ✓ grade.png")


def main() -> None:
    print("Gerando arte pixel…")
    for nome, cor in [("ideia", OURO), ("analogia", CIANO), ("pratica", VERDE),
                      ("laboratorio", ROXO), ("erro", VERMELHO), ("alem", (96, 165, 250)),
                      ("dialogo", (244, 114, 182)), ("etica", (251, 146, 60)),
                      ("vida", (45, 212, 191)), ("checkpoint", (163, 230, 53))]:
        icone(nome, cor)
        print("  ✓ sprite", nome)
    capa()
    banners()
    grade()
    print(f"Pronto: {SPRITES}")


if __name__ == "__main__":
    main()