#!/usr/bin/env python3
"""calculadora_metricas_tdd.py — Calculadora de métricas clínicas com TDD.
Autor: Edson Laranjeiras — OdontoIA"""

def sensibilidade(vp, fn):
    """Sensibilidade = VP / (VP + FN)"""
    if vp + fn == 0:
        return 0.0
    return vp / (vp + fn)

def especificidade(vn, fp):
    """Especificidade = VN / (VN + FP)"""
    if vn + fp == 0:
        return 0.0
    return vn / (vn + fp)

def acuracia(vp, vn, fp, fn):
    """Acurácia = (VP + VN) / Total"""
    total = vp + vn + fp + fn
    if total == 0:
        return 0.0
    return (vp + vn) / total

def vpp(vp, fp):
    """Valor Preditivo Positivo"""
    if vp + fp == 0:
        return 0.0
    return vp / (vp + fp)

def f1_score(vp, fp, fn):
    """F1 = 2*VP / (2*VP + FP + FN)"""
    denom = 2*vp + fp + fn
    if denom == 0:
        return 0.0
    return 2*vp / denom

# TDD embutido
if __name__ == "__main__":
    assert sensibilidade(90, 10) == 0.9
    assert especificidade(85, 15) == 0.85
    assert abs(acuracia(90, 85, 15, 10) - 0.875) < 0.01
    print("✅ Calculadora de métricas — TDD aprovado!")
