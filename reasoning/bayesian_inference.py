# -*- coding: utf-8 -*-
"""R830 — bayesian_inference: atualização conjugada com prior explícito.

Inspiração: mathkernel (trust por evidência, prior explícito), reasoning
BayesianEngine. Corpus keywords: bayesian, bayes, probabilistic,
bayesian_inference. Categoria: bayesian_inference. Sem prior oculto.
"""
from __future__ import annotations

def update_beta_binomial(a0: float, b0: float, sucessos: int, tentativas: int) -> dict:
    """bayesian_inference Beta-Binomial: posterior = prior + dados (bayes)."""
    a0, b0 = float(a0), float(b0)
    if a0 <= 0 or b0 <= 0:
        raise ValueError("prior Beta exige a0,b0>0")
    if not (0 <= sucessos <= tentativas):
        raise ValueError("sucessos inconsistentes")
    a1, b1 = a0 + sucessos, b0 + (tentativas - sucessos)
    mean = a1 / (a1 + b1)
    # intervalo crível aproximado (normal approx, probabilístico)
    import math
    var = (a1 * b1) / (((a1 + b1) ** 2) * (a1 + b1 + 1))
    sd = math.sqrt(var)
    return {"engine": "bayesian_inference", "prior": [a0, b0],
            "posterior": [a1, b1], "posterior_mean": mean,
            "credible_95": [max(0.0, mean - 1.96 * sd), min(1.0, mean + 1.96 * sd)],
            "bayesian": True, "probabilistic": True}
