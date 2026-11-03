"""FR-013 (derivado) — features clássicas de imagem para dataset Kaggle rotulado.

Sem torch/TF: usa OpenCV (disponível) para um extrator determinístico.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from odontoca import imagefeatures as ifeat


def _make_image(path: Path, color: tuple[int, int, int], size: int = 96):
    img = np.full((size, size, 3), color, dtype=np.uint8)
    img[size // 4 : size // 2, size // 4 : size // 2] = 20  # região escura (lesão)
    cv2.imwrite(str(path), img)


def test_extract_image_features(tmp_path: Path):
    p = tmp_path / "a.png"
    _make_image(p, (200, 180, 160), size=120)
    f = ifeat.extract_image_features(p)
    assert f["width"] == 120 and f["height"] == 120
    assert 0.0 <= f["edge_density"] <= 1.0
    assert 0.0 <= f["dark_fraction"] <= 1.0
    assert len([k for k in f if k.startswith("hist_h_")]) == 8
    assert len([k for k in f if k.startswith("hist_s_")]) == 4
    assert len([k for k in f if k.startswith("hist_v_")]) == 4
    assert all(np.isfinite(v) for v in f.values())


def test_build_image_dataset(tmp_path: Path):
    for label, color in (("caries", (60, 60, 60)), ("healthy", (220, 210, 200))):
        d = tmp_path / label
        d.mkdir()
        for i in range(3):
            _make_image(d / f"{label}_{i}.png", color)
    df = ifeat.build_image_dataset(tmp_path)
    assert set(df["label"].unique()) == {"caries", "healthy"}
    assert "width" in df.columns and "edge_density" in df.columns
    assert len(df) == 6


def test_dataset_deterministic(tmp_path: Path):
    p = tmp_path / "x.png"
    _make_image(p, (128, 128, 128))
    a = ifeat.extract_image_features(p)
    b = ifeat.extract_image_features(p)
    assert a == b
