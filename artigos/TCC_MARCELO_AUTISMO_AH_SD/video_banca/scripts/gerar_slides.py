#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os 14 slides (PNG 1920x1080) do vídeo de banca.

Área segura: todo o conteúdo fica acima de y=920; a faixa inferior é
reservada às legendas queimadas pelo ffmpeg.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from roteiro import SCENES  # noqa: E402

W, H = 1920, 1080
NAVY = (11, 31, 58)
NAVY_TOP = (17, 44, 78)
CARD = (18, 41, 74)
BORDER = (35, 69, 107)
TEAL = (91, 192, 190)
AMBER = (242, 184, 75)
CORAL = (217, 95, 57)
OFF = (245, 241, 232)
MUTED = (168, 184, 200)

FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

OUT = BASE / "slides"
OUT.mkdir(exist_ok=True)
CHARTS = BASE / "charts"

_F: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _F:
        _F[key] = ImageFont.truetype(path, size)
    return _F[key]


def mix(fg, bg, a: float):
    """Mistura opaca (PIL ignora alfa ao desenhar sobre imagem RGB)."""
    return tuple(int(fg[i] * a + bg[i] * (1 - a)) for i in range(3))


def fundo() -> Image.Image:
    col = Image.new("RGB", (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(
            int(NAVY_TOP[i] * (1 - t * 0.75) + NAVY[i] * (t * 0.75)) for i in range(3)
        )
    img = col.resize((W, H)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([W - 560, -300, W + 260, 520], outline=(91, 192, 190, 20), width=2)
    od.ellipse([W - 440, -180, W + 140, 400], outline=(91, 192, 190, 12), width=2)
    return Image.alpha_composite(img, ov).convert("RGB")


def tracked(d: ImageDraw.ImageDraw, xy, texto, f, fill, spacing=3) -> float:
    x, y = xy
    for ch in texto:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing
    return x


def wrap(d, texto: str, f, largura: int) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if d.textlength(teste, font=f) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def cabecalho(d, cena, idx, size=58, max_w=1650):
    tracked(d, (120, 96), cena["eyebrow"].upper(), font(FR, 21), TEAL, 3.2)
    d.rectangle([120, 136, 176, 141], fill=AMBER)
    f = font(FB, size)
    y = 166
    for linha in wrap(d, cena["title"], f, max_w):
        d.text((120, y), linha, font=f, fill=OFF)
        y += int(size * 1.14)
    # contador de cena
    cont = f"{idx:02d} / {len(SCENES):02d}"
    cf = font(FR, 20)
    d.text((W - 120 - d.textlength(cont, font=cf), 100), cont, font=cf, fill=MUTED)
    # barra de progresso no topo (não colide com as legendas)
    d.rectangle([0, 0, max(6, int(W * idx / len(SCENES))), 4],
                fill=mix(TEAL, NAVY_TOP, 0.80))
    return y


def cartao(d, box, raio=26, fill=CARD, borda=BORDER, largura=2):
    d.rounded_rectangle(box, radius=raio, fill=fill, outline=borda, width=largura)


def pilula(d, x, y, texto, cor, f, altura=58):
    largura = d.textlength(texto, font=f) + 64
    d.rounded_rectangle([x, y, x + largura, y + altura], radius=altura // 2,
                        fill=mix(cor, CARD, 0.10), outline=cor, width=2)
    d.text((x + 32, y + (altura - f.size) // 2 - 4), texto, font=f, fill=OFF)
    return largura


# ---------------------------------------------------------------- layouts

def layout_title(cena, idx):
    img = fundo()
    d = ImageDraw.Draw(img, "RGBA")
    tracked(d, (120, 110), cena["eyebrow"].upper(), font(FR, 22), TEAL, 3.4)
    d.rectangle([120, 152, 200, 157], fill=AMBER)

    f = font(FB, 84)
    y = 250
    for linha in wrap(d, cena["title"], f, 1560):
        d.text((120, y), linha, font=f, fill=OFF)
        y += 96

    fsub = font(FR, 38)
    y += 24
    for linha in wrap(d, cena["subtitle"], fsub, 1380):
        d.text((120, y), linha, font=fsub, fill=MUTED)
        y += 50

    # chip do recorte temporal
    fchip = font(FB, 24)
    larg = d.textlength(cena["meta"], font=fchip) + 56
    d.rounded_rectangle([120, y + 34, 120 + larg, y + 92], radius=29,
                        fill=mix(AMBER, NAVY, 0.10), outline=AMBER, width=2)
    d.text((148, y + 51), cena["meta"], font=fchip, fill=AMBER)

    # bloco de autoria
    d.rectangle([120, 800, 1800, 802], fill=(35, 69, 107))
    d.text((120, 836), cena["author"], font=font(FB, 34), fill=OFF)
    inst = wrap(d, cena["institution"], font(FR, 21), 1500)
    yy = 886
    for linha in inst[:2]:
        d.text((120, yy), linha, font=font(FR, 21), fill=MUTED)
        yy += 29
    d.text((120, yy + 6), "Brasília · 2026", font=font(FR, 21), fill=MUTED)

    # marca discreta
    fm = font(FB, 300)
    d.text((1500, 330), "2e", font=fm, fill=mix(TEAL, NAVY, 0.09))
    return img


def layout_cards3(cena, idx):
    img = fundo()
    d = ImageDraw.Draw(img, "RGBA")
    cabecalho(d, cena, idx, size=60)

    topo, altura = 380, 360
    largura = (1680 - 2 * 40) // 3
    cores = [TEAL, AMBER, CORAL]
    for i, (num, titulo, corpo) in enumerate(cena["cards"]):
        x = 120 + i * (largura + 40)
        cartao(d, [x, topo, x + largura, topo + altura])
        d.rectangle([x + 34, topo + 44, x + 34 + 44, topo + 48], fill=cores[i])
        d.text((x + 34, topo + 70), num, font=font(FB, 62), fill=cores[i])
        ft = font(FB, 33)
        y = topo + 168
        for linha in wrap(d, titulo, ft, largura - 68):
            d.text((x + 34, y), linha, font=ft, fill=OFF)
            y += 40
        fb = font(FR, 25)
        y += 14
        for linha in wrap(d, corpo, fb, largura - 68):
            d.text((x + 34, y), linha, font=fb, fill=MUTED)
            y += 34
    return img


def layout_split(cena, idx):
    img = fundo()
    d = ImageDraw.Draw(img, "RGBA")
    cabecalho(d, cena, idx, size=58)

    topo, altura = 360, 230
    largura = 810
    for i, (titulo, texto, cor) in enumerate([
        (cena["left_title"], cena["left_text"], TEAL),
        (cena["right_title"], cena["right_text"], AMBER),
    ]):
        x = 120 + i * (largura + 60)
        cartao(d, [x, topo, x + largura, topo + altura])
        d.rectangle([x, topo + 28, x + 6, topo + altura - 28], fill=cor)
        d.text((x + 42, topo + 38), titulo.upper(), font=font(FB, 22), fill=cor)
        ft = font(FR, 31)
        y = topo + 92
        for linha in wrap(d, texto, ft, largura - 96):
            d.text((x + 42, y), linha, font=ft, fill=OFF)
            y += 44

    # pílulas
    f = font(FR, 24)
    x = 120
    y = 660
    for item in cena.get("bullets", []):
        larg = d.textlength(item, font=f) + 64
        if x + larg > 1800:
            x, y = 120, y + 76
        pilula(d, x, y, item, MUTED, f)
        x += larg + 18
    return img


def layout_content(cena, idx):
    img = fundo()
    d = ImageDraw.Draw(img, "RGBA")
    y = cabecalho(d, cena, idx, size=58)

    if cena.get("subtitle"):
        f = font(FR, 33)
        linhas = wrap(d, cena["subtitle"], f, 1540)
        topo = max(y + 30, 330)
        altura = 46 + len(linhas) * 46 + 26
        cartao(d, [120, topo, 1800, topo + altura])
        d.rounded_rectangle([140, topo + 26, 146, topo + altura - 26], radius=3, fill=AMBER)
        if cena.get("lead_label"):
            d.text((164, topo + 20), cena["lead_label"].upper(),
                   font=font(FB, 19), fill=AMBER)
            yy = topo + 56
        else:
            yy = topo + 32
        for linha in linhas:
            d.text((164, yy), linha, font=f, fill=OFF)
            yy += 46
        y = topo + altura + 54

    f = font(FR, 32)
    yy = max(y, 560)
    if cena.get("footnote"):
        d.rectangle([120, 842, 148, 845], fill=MUTED)
        d.text((162, 830), cena["footnote"], font=font(FR, 20), fill=MUTED)

    for item in cena.get("bullets", []):
        d.rounded_rectangle([120, yy + 14, 132, yy + 26], radius=3, fill=TEAL)
        linhas = wrap(d, item, f, 1590)
        for linha in linhas:
            d.text((162, yy), linha, font=f, fill=OFF)
            yy += 42
        yy += 26
    return img


def layout_chart(cena, idx):
    img = fundo()
    d = ImageDraw.Draw(img, "RGBA")
    cabecalho(d, cena, idx, size=52)

    # KPIs à esquerda
    mapa = {"teal": TEAL, "amber": AMBER, "coral": CORAL}
    cores = [mapa[c] for c in cena.get("big_colors", ["teal", "amber"])]
    for i, (valor, rotulo) in enumerate([cena["big_left"], cena["big_right"]]):
        topo = 350 + i * 200
        cartao(d, [120, topo, 680, topo + 168])
        d.text((152, topo + 26), valor, font=font(FB, 62), fill=cores[i])
        d.text((154, topo + 112), rotulo.upper(), font=font(FR, 19), fill=MUTED)

    # nota de fonte
    nota = cena.get(
        "source",
        "Fonte: INEP. Sinopses Estatísticas da Educação Básica (2021–2024). "
        "Elaboração própria.",
    )
    fnota = font(FR, 17)
    yy = 790
    for linha in wrap(d, nota, fnota, 540):
        d.text((120, yy), linha, font=fnota, fill=MUTED)
        yy += 24

    # gráfico dentro de um cartão
    caminho = CHARTS / cena["chart"]
    grafico = Image.open(caminho).convert("RGB")
    larg = 980
    alt = int(grafico.height * larg / grafico.width)
    grafico = grafico.resize((larg, alt), Image.LANCZOS)
    x0, y0 = 760, 320
    cartao(d, [x0 - 18, y0 - 18, x0 + larg + 18, y0 + alt + 18], raio=22)
    img.paste(grafico, (x0, y0))
    return img


def layout_conclusion(cena, idx):
    img = fundo()
    d = ImageDraw.Draw(img, "RGBA")
    cabecalho(d, cena, idx, size=58)

    cores = [TEAL, AMBER, CORAL]
    topo = 330
    for i, (num, titulo, corpo) in enumerate(cena["cards"]):
        y = topo + i * 178
        cartao(d, [120, y, 1800, y + 158])
        d.ellipse([154, y + 43, 226, y + 115], fill=mix(cores[i], CARD, 0.18),
                  outline=cores[i], width=2)
        nf = font(FB, 32)
        d.text((190 - d.textlength(num, font=nf) / 2, y + 59), num, font=nf, fill=cores[i])
        d.text((262, y + 32), titulo, font=font(FB, 34), fill=OFF)
        fb = font(FR, 24)
        yy = y + 84
        for linha in wrap(d, corpo, fb, 1440):
            d.text((262, yy), linha, font=fb, fill=MUTED)
            yy += 32
    return img


def layout_closing(cena, idx):
    img = fundo()
    d = ImageDraw.Draw(img, "RGBA")
    tracked(d, (120, 110), cena["eyebrow"].upper(), font(FR, 21), TEAL, 3.2)
    d.rectangle([120, 148, 176, 153], fill=AMBER)

    f = font(FB, 124)
    texto = cena["title"]
    d.text(((W - d.textlength(texto, font=f)) / 2, 288), texto, font=f, fill=OFF)

    fsub = font(FR, 42)
    d.text(((W - d.textlength(cena["subtitle"], font=fsub)) / 2, 452),
           cena["subtitle"], font=fsub, fill=TEAL)

    d.rectangle([760, 546, 1160, 548], fill=BORDER)

    # autor em destaque
    faut = font(FB, 46)
    d.text(((W - d.textlength(cena["author"], font=faut)) / 2, 590),
           cena["author"], font=faut, fill=OFF)

    finst = font(FR, 21)
    linhas = wrap(d, cena["institution"], finst, 1180)
    yy = 664
    for linha in linhas:
        d.text(((W - d.textlength(linha, font=finst)) / 2, yy), linha, font=finst, fill=MUTED)
        yy += 29

    fmeta = font(FR, 24)
    d.text(((W - d.textlength(cena["meta"], font=fmeta)) / 2, yy + 8),
           cena["meta"], font=fmeta, fill=MUTED)

    fnota = font(FR, 22)
    larg = d.textlength(cena["note"], font=fnota) + 72
    x = (W - larg) / 2
    d.rounded_rectangle([x, 828, x + larg, 884], radius=28,
                        fill=mix(AMBER, NAVY, 0.10), outline=AMBER, width=2)
    d.text((x + 36, 846), cena["note"], font=fnota, fill=AMBER)
    return img


LAYOUTS = {
    "title": layout_title,
    "cards3": layout_cards3,
    "split": layout_split,
    "content": layout_content,
    "chart": layout_chart,
    "conclusion": layout_conclusion,
    "closing": layout_closing,
}


def main() -> int:
    for i, cena in enumerate(SCENES, 1):
        fn = LAYOUTS[cena["layout"]]
        img = fn(cena, i)
        destino = OUT / f"{cena['id']}.png"
        img.save(destino, optimize=True)
        print(f"[{i:02d}/{len(SCENES)}] {destino.name} ({img.size[0]}x{img.size[1]})")
    print("OK:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
