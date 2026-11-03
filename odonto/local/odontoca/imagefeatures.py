"""Extrator determinístico de features clássicas de imagem — SPEC-935-R898 §3.

Sem torch/TF: usa OpenCV + NumPy. Alvo é o rótulo da pasta (caries/healthy).
Saída é dado para o pipeline tabular (comparação empírica, revisão humana).
"""
from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
RESIZE = 128


def _entropy(gray: np.ndarray) -> float:
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    total = hist.sum()
    if total <= 0:
        return 0.0
    p = hist / total
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def extract_image_features(path: str | Path) -> dict[str, float]:
    """Features de cor, textura e forma (determinístico para o mesmo arquivo)."""
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"imagem ilegível: {path}")
    h0, w0 = img.shape[:2]
    small = cv2.resize(img, (RESIZE, RESIZE), interpolation=cv2.INTER_AREA)
    feats: dict[str, float] = {
        "width": float(w0),
        "height": float(h0),
        "aspect": float(w0) / float(h0) if h0 else 0.0,
    }
    # BGR
    for i, name in enumerate(("b", "g", "r")):
        ch = small[:, :, i].astype(np.float32)
        feats[f"mean_{name}"] = float(ch.mean() / 255.0)
        feats[f"std_{name}"] = float(ch.std() / 255.0)
    # HSV
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    for i, name in enumerate(("h", "s", "v")):
        ch = hsv[:, :, i].astype(np.float32)
        feats[f"mean_hsv_{name}"] = float(
            ch.mean() / (179.0 if name == "h" else 255.0)
        )
        feats[f"std_hsv_{name}"] = float(ch.std() / (179.0 if name == "h" else 255.0))
    # histogramas normalizados
    for name, ch, bins, rng in (
        ("h", hsv[:, :, 0], 8, (0, 180)),
        ("s", hsv[:, :, 1], 4, (0, 256)),
        ("v", hsv[:, :, 2], 4, (0, 256)),
    ):
        hist = cv2.calcHist([ch], [0], None, [bins], list(rng)).ravel()
        hist = hist / max(hist.sum(), 1.0)
        for b in range(bins):
            feats[f"hist_{name}_{b}"] = float(hist[b])
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 180)
    feats["edge_density"] = float((edges > 0).mean())
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    feats["sobel_mag_mean"] = float(mag.mean() / 255.0)
    feats["sobel_mag_std"] = float(mag.std() / 255.0)
    feats["laplacian_var"] = float(cv2.Laplacian(gray, cv2.CV_32F).var() / (255.0 ** 2))
    thr, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    feats["otsu_threshold"] = float(thr / 255.0)
    feats["dark_fraction"] = float((gray < thr).mean())
    feats["entropy"] = _entropy(gray)
    return {k: (v if math.isfinite(v) else 0.0) for k, v in feats.items()}


def build_image_dataset(root: str | Path) -> "np.ndarray":
    """Varre ``root`` por pastas-rótulo e devolve DataFrame de features.

    Requer ``pandas`` (import tardio para manter o extrator leve).
    """
    import pandas as pd

    root_p = Path(root)
    rows: list[dict] = []
    for label_dir in sorted(p for p in root_p.iterdir() if p.is_dir()):
        label = label_dir.name
        for img in sorted(label_dir.rglob("*")):
            if img.suffix.lower() not in IMAGE_EXTS:
                continue
            try:
                feats = extract_image_features(img)
            except ValueError:
                continue
            feats["label"] = label
            feats["path"] = str(img.relative_to(root_p))
            rows.append(feats)
    if not rows:
        raise ValueError(f"nenhuma imagem rotulada encontrada em {root_p}")
    return pd.DataFrame(rows)
