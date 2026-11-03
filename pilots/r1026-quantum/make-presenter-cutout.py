#!/usr/bin/env python3
"""R1030 — gera o retrato recortado da apresentadora para os cartões.

Extrai o frame neutro de 5,4 s do clipe, recorta 560×800 e separa a
apresentadora do fundo claro por limiar de luminosidade + morfologia.
Não é um modelo de segmentação: as bordas do cabelo podem ter artefatos.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import cv2
import numpy as np

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "source.mp4"
CARD = BASE / "presenter-card.png"
OUT = BASE / "presenter-cutout.png"


def extract_frame() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"fonte ausente: {SOURCE}")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            "5.4",
            "-i",
            str(SOURCE),
            "-frames:v",
            "1",
            "-vf",
            "crop=560:800:1180:130",
            str(CARD),
        ],
        check=True,
    )


def cutout() -> None:
    image = cv2.imread(str(CARD), cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f"não foi possível ler {CARD}")
    height, width = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # fundo claro: alta luminosidade e baixa saturação
    white = ((hsv[:, :, 2] > 150) & (hsv[:, :, 1] < 55)).astype(np.uint8) * 255
    alpha = cv2.bitwise_not(white)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel, iterations=3)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel, iterations=1)

    # mantém o maior componente (a apresentadora)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        (alpha > 0).astype(np.uint8), 8
    )
    if count > 1:
        index = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        alpha = (labels == index).astype(np.uint8) * 255

    # fecha buracos internos
    filled = alpha.copy()
    mask = np.zeros((height + 2, width + 2), np.uint8)
    cv2.floodFill(filled, mask, (0, 0), 255)
    alpha = cv2.bitwise_or(alpha, cv2.bitwise_not(filled))

    # remove a franja clara e suaviza a borda
    alpha = cv2.erode(alpha, np.ones((3, 3), np.uint8), iterations=3)
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0.8)

    # descontamina a cor de borda (o fundo era branco)
    a = (alpha.astype(np.float32) / 255.0)[..., None]
    source = image.astype(np.float32)
    foreground = (source - (1.0 - a) * 255.0) / np.maximum(a, 0.12)
    foreground = np.clip(foreground, 0, 255)
    edge = (a > 0.02) & (a < 0.98)
    clean = np.where(edge, foreground, source)

    rgba = cv2.cvtColor(clean.astype(np.uint8), cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = alpha
    cv2.imwrite(str(OUT), rgba)
    print(f"ok: {OUT} ({width}×{height}, alfa>20 em {(alpha > 20).mean():.1%})")


if __name__ == "__main__":
    extract_frame()
    cutout()
