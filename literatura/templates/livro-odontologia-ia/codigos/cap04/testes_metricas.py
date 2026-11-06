#!/usr/bin/env python3
"""testes_metricas.py — Testes TDD para métricas clínicas odontológicas."""
from calculadora_metricas_tdd import sensibilidade, especificidade, acuracia, vpp, f1_score

def test_sensibilidade_perfeita():
    assert sensibilidade(100, 0) == 1.0

def test_especificidade_zero_casos():
    assert especificidade(0, 0) == 0.0

def test_acuracia_50_pct():
    assert abs(acuracia(50, 50, 50, 50) - 0.5) < 0.01

def test_f1_perfeito():
    assert f1_score(100, 0, 0) == 1.0

print("✅ Todos os testes de métricas passaram!")
