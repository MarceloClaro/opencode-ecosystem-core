#!/usr/bin/env python3
"""testes_aed_panoramicas.py — Testes TDD para análise exploratória."""
import numpy as np

def test_imagem_2d():
    from notebook_aed_panoramicas import carregar_imagem_sintetica
    img = carregar_imagem_sintetica()
    assert len(img.shape) == 2, "Imagem deve ser 2D (escala de cinza)"

def test_valores_no_range():
    from notebook_aed_panoramicas import carregar_imagem_sintetica
    img = carregar_imagem_sintetica()
    assert img.min() >= 0 and img.max() <= 255

def test_tamanho_correto():
    from notebook_aed_panoramicas import carregar_imagem_sintetica
    img = carregar_imagem_sintetica(256, 512)
    assert img.shape == (256, 512)

print("✅ Todos os testes AED passaram!")
