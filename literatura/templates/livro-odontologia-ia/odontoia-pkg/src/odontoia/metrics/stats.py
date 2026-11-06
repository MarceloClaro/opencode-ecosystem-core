"""
Módulo stats — Testes estatísticos e métricas de concordância para
avaliação de diagnóstico odontológico.

Funções:
    cohens_kappa : Kappa de Cohen (concordância inter-examinador)
    kappa_score  : Alias para cohens_kappa
    mcnemar_test : Teste de McNemar (comparação de pares)
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
from scipy import stats as scipy_stats


def cohens_kappa(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    weights: Optional[str] = None,
) -> float:
    """Calcula o Kappa de Cohen para concordância entre predições e verdade.

    O Kappa de Cohen mede a concordância entre duas avaliações, corrigindo
    a concordância esperada ao acaso.

    Interpretação (Landis & Koch, 1977):
        < 0.00:   Desacordo
        0.00-0.20:  Concordância leve
        0.21-0.40:  Concordância regular
        0.41-0.60:  Concordância moderada
        0.61-0.80:  Concordância substancial
        0.81-1.00:  Concordância quase perfeita

    Na odontologia, Kappa é usado para:
        - Concordância entre radiologistas e IA
        - Reprodutibilidade de diagnóstico (teste-reteste)
        - Calibração de examinadores

    Args:
        y_true: Avaliações de referência (1D)
        y_pred: Avaliações do modelo/examinador (1D)
        weights: Tipo de ponderação ('linear', 'quadratic' ou None)
            None   = Kappa simples (para dados nominais)
            linear = Kappa linear (para dados ordinais)
            quadratic = Kappa quadrático (para estágios)

    Returns:
        Kappa de Cohen no intervalo [-1, 1]

    Example:
        >>> rater1 = np.array([0, 1, 2, 1, 0, 2, 1, 0])
        >>> rater2 = np.array([0, 1, 1, 1, 0, 2, 1, 1])
        >>> kappa = cohens_kappa(rater1, rater2)
        >>> print(f"Kappa: {kappa:.3f}")
    """
    from sklearn.metrics import cohen_kappa_score
    return float(cohen_kappa_score(y_true, y_pred, weights=weights))


def mcnemar_test(
    y_true: np.ndarray,
    model_a: np.ndarray,
    model_b: np.ndarray,
) -> dict:
    """Teste de McNemar para comparar a performance de dois modelos.

    Teste estatístico pareado que compara as discordâncias entre dois
    classificadores. Útil para determinar se um modelo é significativamente
    melhor que outro.

    Hipóteses:
        H0: Os dois modelos têm a mesma taxa de erro
        H1: As taxas de erro diferem

    Args:
        y_true: Rótulos verdadeiros (1D)
        model1: Predições do modelo A (1D)
        model2: Predições do modelo B (1D)

    Returns:
        Dicionário com:
            - 'statistic': Estatística Qui-quadrado
            - 'p_value': Valor-p do teste
            - 'b': Modelo1 erros que Model2 acertou (Matriz[0,1])
            - 'c': Modelo2 erros que Model1 acertou (Matriz[1,0])
            - 'significant': True se p < 0.05

    Example:
        >>> y = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        >>> m1 = np.array([0, 0, 1, 1, 0, 1, 0, 0])
        >>> m2 = np.array([0, 0, 1, 0, 0, 1, 1, 1])
        >>> result = mcnemar_test(y, m1, m2)
        >>> if result['significant']:
        ...     print("Modelos diferem significativamente")
    """
    # Matriz de discordância
    # Matriz de discordância
    b = np.sum((model_a != y_true) & (model_b == y_true))  # M1 erra, M2 acerta
    c = np.sum((model_a == y_true) & (model_b != y_true))  # M1 acerta, M2 erra

    n_discordantes = b + c
    if n_discordantes < 10:
        # Correção de continuidade para amostras pequenas
        chi2 = (abs(b - c) - 1) ** 2 / n_discordantes if n_discordantes > 0 else 0.0
    else:
        chi2 = (b - c) ** 2 / n_discordantes if n_discordantes > 0 else 0.0

    p_value = 1.0 - scipy_stats.chi2.cdf(chi2, df=1)
    significant = p_value < 0.05

    return {
        "statistic": float(chi2),
        "p_value": float(p_value),
        "b": int(b),
        "c": int(c),
        "n_discordantes": int(n_discordantes),
        "significant": significant,
    }


def diagnostic_odds_ratio(tp: int, tn: int, fp: int, fn: int) -> float:
    """Calcula a razão de chances diagnóstica (DOR).

    DOR = (TP/FP) / (FN/TN) = (TP * TN) / (FP * FN)

    A DOR combina sensibilidade e especificidade em uma única métrica.
    Quanto maior, melhor o poder discriminatório do teste.
    DOR = 1 indica teste sem poder diagnóstico.

    Args:
        tp: Verdadeiros positivos
        tn: Verdadeiros negativos
        fp: Falsos positivos
        fn: Falsos negativos

    Returns:
        Razão de chances diagnóstica (float >= 0)

    Example:
        >>> dor = diagnostic_odds_ratio(tp=85, tn=90, fp=10, fn=15)
        >>> print(f"DOR: {dor:.2f}")
    """
    if fp == 0 or fn == 0:
        # Adiciona correção de continuidade de Haldane
        tp += 0.5
        tn += 0.5
        fp += 0.5
        fn += 0.5
    return float((tp * tn) / (fp * fn))