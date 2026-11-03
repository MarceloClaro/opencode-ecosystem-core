#!/usr/bin/env python3
"""R1031 — compõe a apresentadora falando no cartão escuro.

Recebe um vídeo 1080p com a boca sincronizada, recorta a região da
apresentadora (560×800), calcula a matte por frame (fundo claro), compõe sobre
o gradiente do cartão e grava um MP4 560×800 a 30 fps.

Uso:
  python3 compose-presenter-card.py --video presenter-intro-1080.mp4 \
      --duration 14.187 --label intro
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

BASE = Path(__file__).resolve().parent
CROP_X, CROP_Y, CROP_W, CROP_H = 1180, 100, 560, 700
FPS = 30


def make_background(path: Path) -> np.ndarray:
    """Gera o gradiente do cartão em BGR, 560×800."""
    height, width = CROP_H, CROP_W
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    cx, cy = 0.50 * width, 0.40 * height
    dx = (xx - cx) / (0.50 * width)
    dy = (yy - cy) / (0.50 * height)
    distance = np.sqrt(dx * dx + dy * dy)

    c0 = np.array([69, 33, 43], dtype=np.float32)   # #2B2145 em BGR
    c1 = np.array([34, 16, 23], dtype=np.float32)   # #171022
    c2 = np.array([15, 11, 11], dtype=np.float32)   # #0B0B0F

    t = np.clip(distance / 1.25, 0.0, 1.0)
    image = np.empty((height, width, 3), dtype=np.float32)
    low = t < 0.55
    image[low] = c0 + (c1 - c0) * (t[low] / 0.55)[:, None]
    image[~low] = c1 + (c2 - c1) * ((t[~low] - 0.55) / 0.45)[:, None]

    # glow roxo atrás da cabeça
    gx, gy = 0.52 * width, 0.26 * height
    gd = np.sqrt(((xx - gx) / (0.55 * width)) ** 2 + ((yy - gy) / (0.55 * height)) ** 2)
    ga = 0.40 * np.clip(1.0 - gd, 0.0, 1.0) ** 2
    purple = np.array([246, 92, 139], dtype=np.float32)  # #8B5CF6 em BGR
    image = image * (1.0 - ga[..., None]) + purple * ga[..., None]

    # brilho elíptico na base, para separar a blusa do fundo
    bx, by = 0.50 * width, 0.95 * height
    bd = np.sqrt(((xx - bx) / (0.45 * width)) ** 2 + ((yy - by) / (0.225 * height)) ** 2)
    ba = 0.26 * np.clip(1.0 - bd, 0.0, 1.0) ** 2
    image = image * (1.0 - ba[..., None]) + purple * ba[..., None]

    # escurece a base para o rótulo
    bottom = np.clip((yy / height - 0.55) / 0.45, 0.0, 1.0) * 0.35
    image = image * (1.0 - bottom[..., None])

    output = np.clip(image, 0, 255).astype(np.uint8)
    cv2.imwrite(str(path), output)
    return output


def matte(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Separa a apresentadora do fundo claro e devolve (RGB limpo, alfa).

    A matte é suave: usa V*(1-S) para dar alfa parcial às bordas do cabelo,
    em vez de um corte binário. O fundo claro tem escore alto e alfa zero;
    cabelo, pele e blusa têm escore baixo e alfa cheio.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    value = hsv[:, :, 2].astype(np.float32) / 255.0
    saturation = hsv[:, :, 1].astype(np.float32) / 255.0
    score = value * (1.0 - saturation)
    alpha = (np.clip((0.93 - score) / 0.18, 0.0, 1.0) * 255.0).astype(np.uint8)

    height, width = alpha.shape
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel, iterations=2)
    alpha = cv2.erode(alpha, np.ones((3, 3), np.uint8), iterations=2)
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0.8)

    # remove o fundo claro que sobra na borda esquerda (mancha em "M")
    yy, xx = np.mgrid[0:height, 0:width]
    left_bg = (
        (xx < 180)
        & (yy > 300)
        & (yy < 540)
        & (value > 0.80)
        & (saturation < 0.20)
    ).astype(np.uint8) * 255
    left_bg = cv2.dilate(left_bg, np.ones((5, 5), np.uint8), iterations=2)
    alpha = (alpha.astype(np.float32) * (255 - left_bg) / 255.0).astype(np.uint8)
    alpha[:, :12] = 0
    alpha[:, -12:] = 0

    # descontamina a cor de borda (o fundo era branco)
    a = (alpha.astype(np.float32) / 255.0)[..., None]
    source = frame.astype(np.float32)
    foreground = (source - (1.0 - a) * 255.0) / np.maximum(a, 0.15)
    foreground = np.clip(foreground, 0, 255)
    edge = (a > 0.02) & (a < 0.98)
    clean = np.where(edge, foreground, source).astype(np.uint8)

    # fade inferior: funde a base no cartão e elimina restos da borda
    fade = np.clip(
        (height - 1 - np.arange(height, dtype=np.float32)) / 24.0, 0.0, 1.0
    )[:, None]
    alpha = (alpha.astype(np.float32) * fade).astype(np.uint8)
    # remove o último fio da borda inferior
    alpha[-20:, :] = 0
    return clean, alpha


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--duration", required=True, type=float)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--background", type=Path, default=BASE / "card-bg-560x700.png")
    args = parser.parse_args()

    if not args.video.is_file():
        raise SystemExit(f"vídeo ausente: {args.video}")

    background = make_background(args.background)
    output = args.out or (BASE / f"presenter-{args.label}-card.mp4")
    target_frames = int(round(args.duration * FPS))

    capture = cv2.VideoCapture(str(args.video))
    if not capture.isOpened():
        raise SystemExit(f"não foi possível abrir {args.video}")

    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "bgr24",
        "-s",
        f"{CROP_W}x{CROP_H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-movflags",
        "+faststart",
        str(output),
    ]
    writer = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert writer.stdin is not None

    last_frame = None
    written = 0
    try:
        for index in range(target_frames):
            ok, frame = capture.read()
            if ok:
                crop = frame[CROP_Y : CROP_Y + CROP_H, CROP_X : CROP_X + CROP_W]
                if crop.shape[0] != CROP_H or crop.shape[1] != CROP_W:
                    raise SystemExit(f"recorte inesperado: {crop.shape}")
                last_frame = crop.copy()
            elif last_frame is not None:
                crop = last_frame
            else:
                break

            clean, alpha = matte(crop)
            a = (alpha.astype(np.float32) / 255.0)[..., None]
            composed = clean.astype(np.float32) * a + background.astype(np.float32) * (1.0 - a)
            writer.stdin.write(np.clip(composed, 0, 255).astype(np.uint8).tobytes())
            written += 1
            if written % 30 == 0 or written == target_frames:
                print(f"{args.label}: {written}/{target_frames} frames", flush=True)
    finally:
        capture.release()
        writer.stdin.close()
        code = writer.wait()
        if code != 0:
            raise SystemExit(f"ffmpeg terminou com código {code}")

    print(f"ok: {output} ({written} frames, {args.duration:.3f}s)")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit("ffmpeg encerrou o pipe antes do fim")
