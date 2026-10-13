# -*- coding: utf-8 -*-
"""Contraprova numérica do _softmax real (float) vs teoria (Real).

Tenta REFUTAR, em 20k vetores aleatórios (magnitudes até ±1000, tamanhos
1..50): soma=1, pesos em [0,1], invariância à subtração do máximo,
preservação de argmax, singleton=[1.0], vazio=[]. Qualquer violação acima
da tolerância é reportada e falha (exit 1).
"""
from __future__ import annotations

import random
import sys

sys.path.insert(0, "/home/marceloclaro/opencode-ecosystem-core")

from transformer.attention import _softmax  # noqa: E402

TOL_SUM = 1e-9
TOL_SHIFT = 1e-12


def main(n: int = 20000, seed: int = 7):
    rng = random.Random(seed)
    viol = {"soma": 0, "limites": 0, "invariancia": 0, "argmax": 0,
            "singleton": 0, "vazio": 0}
    worst_sum = 0.0
    worst_shift = 0.0
    for k in range(n):
        m = rng.choice([1, 2, 3, 5, 8, 13, 25, 50])
        mag = rng.choice([1.0, 10.0, 100.0, 1000.0])
        xs = [rng.uniform(-mag, mag) for _ in range(m)]
        w = _softmax(xs)
        if len(w) != m:
            viol["soma"] += 1
            continue
        s = sum(w)
        worst_sum = max(worst_sum, abs(s - 1.0))
        if abs(s - 1.0) > TOL_SUM:
            viol["soma"] += 1
        if any(not (0.0 <= v <= 1.0) for v in w):
            viol["limites"] += 1
        if m == 1 and w != [1.0]:
            viol["singleton"] += 1
        mu = max(xs)
        w2 = _softmax([x - mu for x in xs])
        d = max(abs(a - b) for a, b in zip(w, w2))
        worst_shift = max(worst_shift, d)
        if d > TOL_SHIFT:
            viol["invariancia"] += 1
        amax_w = max(w)
        if max(xs[i] for i in range(m) if w[i] == amax_w) < max(xs):
            viol["argmax"] += 1
    if _softmax([]) != []:
        viol["vazio"] += 1
    total = sum(viol.values())
    print(f"vetores={n} violacoes={total} {viol}")
    print(f"pior_soma={worst_sum:.2e} pior_shift={worst_shift:.2e}")
    print("CONTRAPROVA_OK" if total == 0 else "CONTRAPROVA_FALHOU")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
