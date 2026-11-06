#!/usr/bin/env python3
"""notebook_aed_panoramicas.py — Análise exploratória de radiografias panorâmicas."""
import numpy as np
import matplotlib.pyplot as plt

def carregar_imagem_sintetica(h=256, w=512):
    """Gera radiografia panorâmica sintética para demonstração didática."""
    img = np.zeros((h, w), dtype=np.uint8)
    # Simular arcada dentária
    for x in range(50, w-50, 40):
        yy, xx = np.ogrid[:h, :w]
        mask = ((xx - x)**2 / 15**2 + (yy - h//2)**2 / 20**2) <= 1
        img[mask] = 180 + np.random.randint(-20, 20, size=np.sum(mask))
    return np.clip(img, 0, 255).astype(np.uint8)

def test_shape():
    img = carregar_imagem_sintetica()
    assert img.shape == (256, 512)
    assert img.dtype == np.uint8

if __name__ == "__main__":
    img = carregar_imagem_sintetica()
    plt.imshow(img, cmap='gray')
    plt.title("Radiografia Panorâmica Sintética")
    plt.show()
    test_shape()
    print("✅ AED concluída")
