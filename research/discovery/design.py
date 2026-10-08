# -*- coding: utf-8 -*-
"""Desenho de estudo: PICO/PCC, hipóteses falsificáveis e poder (SPEC-935-R708, AC1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from scipy.stats import norm


@dataclass
class Hipotese:
    """H0/H1 com critério de falsificação explícito."""

    rotulo: str
    h0: str
    h1: str
    falsificacao: str
    teste_planejado: str = ""
    alfa: float = 0.05

    def __post_init__(self) -> None:
        for campo in ("rotulo", "h0", "h1", "falsificacao"):
            if not getattr(self, campo) or not getattr(self, campo).strip():
                raise ValueError(f"Hipotese exige {campo} não vazio.")
        if not 0 < self.alfa < 1:
            raise ValueError("alfa deve estar em (0,1).")


@dataclass
class Desenho:
    """PICO/PCC + hipóteses + confundidores declarados."""

    pergunta: str
    populacao: str
    intervencao_ou_exposicao: str
    comparador: str
    desfecho: str
    hipotese_list: list[Hipotese] = field(default_factory=list)
    confundidores: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        for campo in ("pergunta", "populacao", "intervencao_ou_exposicao",
                      "comparador", "desfecho"):
            if not getattr(self, campo) or not getattr(self, campo).strip():
                raise ValueError(f"Desenho exige {campo} não vazio.")
        if not self.hipotese_list:
            raise ValueError("Desenho exige ao menos uma hipótese registrada.")


def poder_t2(d: float, n_por_grupo: int, alfa: float = 0.05) -> float:
    """Poder aproximado (normal) do t de 2 amostras, bicaudal.

    Aproximação documentada, não cálculo exato de poder para Welch.
    d = diferença padronizada esperada (Cohen).
    """
    if d <= 0 or n_por_grupo < 2 or not 0 < alfa < 1:
        raise ValueError("Parâmetros inválidos para poder_t2.")
    z_alfa = norm.ppf(1 - alfa / 2)
    delta = d * sqrt(n_por_grupo / 2.0)
    return float(norm.cdf(delta - z_alfa) + norm.cdf(-delta - z_alfa))


def tamanho_amostra(d: float, poder_alvo: float = 0.8, alfa: float = 0.05,
                    n_max: int = 10000) -> int:
    """Menor n por grupo com poder >= alvo (busca binária, monótona em n)."""
    if d <= 0 or not 0 < poder_alvo < 1 or not 0 < alfa < 1:
        raise ValueError("Parâmetros inválidos para tamanho_amostra.")
    if poder_t2(d, n_max, alfa) < poder_alvo:
        raise ValueError("poder_alvo inalcançável até n_max.")
    lo, hi = 2, n_max
    while lo < hi:
        mid = (lo + hi) // 2
        if poder_t2(d, mid, alfa) >= poder_alvo:
            hi = mid
        else:
            lo = mid + 1
    return lo


def planejar(questao: dict) -> Desenho:
    """Constrói Desenho a partir de dicionário (falha fechada em campo ausente)."""
    try:
        hips = [Hipotese(**h) for h in questao["hipoteses"]]
        return Desenho(pergunta=questao["pergunta"], populacao=questao["populacao"],
                       intervencao_ou_exposicao=questao["exposicao"],
                       comparador=questao["comparador"], desfecho=questao["desfecho"],
                       hipotese_list=hips, confundidores=list(questao.get("confundidores", [])))
    except KeyError as exc:
        raise ValueError(f"Campo obrigatório ausente no desenho: {exc}.") from exc


__all__ = ["Hipotese", "Desenho", "poder_t2", "tamanho_amostra", "planejar"]
