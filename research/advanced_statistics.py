"""Inferência avançada selecionada para pesquisa — SPEC-935-R1256.

Os métodos retornam estimativas e premissas; não validam desenho amostral,
independência, proveniência, representatividade ou interpretação causal.
"""
from __future__ import annotations

import math
from statistics import mean
from typing import Sequence

from scipy import stats

from .quantitative_calculators import _confidence_z, _finite_real


def _finite_vector(values, field: str, minimum: int = 1) -> list[float]:
    if isinstance(values, (str, bytes)) or not isinstance(values, (list, tuple)) or len(values) < minimum:
        raise ValueError(f"{field} deve ser sequência numérica com pelo menos {minimum} valores.")
    result = [_finite_real(value, f"{field}[{index}]") for index, value in enumerate(values)]
    return result


def _count(value, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} deve ser inteiro não negativo.")
    return value


def one_way_anova(groups: Sequence[Sequence[float]]) -> dict:
    """ANOVA clássica de uma via entre grupos independentes.

    Reporta eta-quadrado como tamanho de efeito. Homocedasticidade, normalidade
    e independência são premissas declaradas, não diagnósticos executados.
    """
    if isinstance(groups, (str, bytes)) or not isinstance(groups, (list, tuple)) or len(groups) < 2:
        raise ValueError("ANOVA de uma via exige ao menos dois grupos.")
    cleaned = [_finite_vector(group, f"groups[{index}]", minimum=2) for index, group in enumerate(groups)]
    sample_count = sum(len(group) for group in cleaned)
    df_between = len(cleaned) - 1
    df_within = sample_count - len(cleaned)
    grand_mean = mean(value for group in cleaned for value in group)
    ss_between = math.fsum(len(group) * (mean(group) - grand_mean) ** 2 for group in cleaned)
    ss_within = math.fsum(math.fsum((value - mean(group)) ** 2 for value in group) for group in cleaned)
    ss_total = ss_between + ss_within
    if df_within <= 0 or ss_within <= 0 or ss_total <= 0:
        raise ValueError("ANOVA requer variação residual positiva e graus de liberdade residuais.")
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    statistic = ms_between / ms_within
    p_value = float(stats.f.sf(statistic, df_between, df_within))
    return {
        "statistic": statistic,
        "p_value": p_value,
        "df_between": df_between,
        "df_within": df_within,
        "sum_squares_between": ss_between,
        "sum_squares_within": ss_within,
        "eta_squared": ss_between / ss_total,
        "group_sizes": [len(group) for group in cleaned],
        "group_means": [mean(group) for group in cleaned],
        "method": "classical one-way ANOVA",
        "null_hypothesis": "All population group means are equal.",
        "assumptions": [
            "Independent observations and groups.",
            "Approximately normal residuals within groups.",
            "Equal within-group variances; no diagnostic was executed.",
        ],
    }


def spearman_correlation(x: Sequence[float], y: Sequence[float]) -> dict:
    """Correlação de postos de Spearman com teste bilateral assintótico."""
    left = _finite_vector(x, "x", minimum=3)
    right = _finite_vector(y, "y", minimum=3)
    if len(left) != len(right):
        raise ValueError("x e y devem ter o mesmo número de observações pareadas.")
    if len(set(left)) < 2 or len(set(right)) < 2:
        raise ValueError("Spearman requer variação em ambas as variáveis.")
    result = stats.spearmanr(left, right, alternative="two-sided")
    return {
        "estimate": float(result.statistic),
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "n": len(left),
        "method": "Spearman rank correlation; asymptotic two-sided p-value",
        "null_hypothesis": "Population rank correlation equals zero.",
        "assumptions": [
            "Pairs are independent and measurements are at least ordinal.",
            "The reported p-value is asymptotic; small-sample exact inference is not implemented.",
            "Ties are handled by SciPy's rank-based implementation.",
        ],
    }


def cochrans_q_meta_analysis(effect_sizes: Sequence[float], variances: Sequence[float]) -> dict:
    """Q de Cochran para heterogeneidade entre estimativas independentes.

    As estimativas devem estar na mesma escala e suas variâncias amostrais serem
    positivas. A referência qui-quadrado com k-1 graus de liberdade é uma
    aproximação; dependência entre estudos não é modelada.
    """
    effects = _finite_vector(effect_sizes, "effect_sizes", minimum=2)
    vars_ = _finite_vector(variances, "variances", minimum=2)
    if len(effects) != len(vars_):
        raise ValueError("effect_sizes e variances devem ter o mesmo comprimento.")
    if any(value <= 0 for value in vars_):
        raise ValueError("Todas as variâncias amostrais devem ser positivas.")
    weights = [1.0 / value for value in vars_]
    total_weight = math.fsum(weights)
    weighted_mean = math.fsum(weight * effect for weight, effect in zip(weights, effects)) / total_weight
    statistic = math.fsum(weight * (effect - weighted_mean) ** 2 for weight, effect in zip(weights, effects))
    degrees = len(effects) - 1
    p_value = float(stats.chi2.sf(statistic, degrees))
    i_squared = max(0.0, (statistic - degrees) / statistic) * 100.0 if statistic > 0 else 0.0
    return {
        "statistic": statistic,
        "p_value": p_value,
        "df": degrees,
        "degrees_of_freedom": degrees,
        "i_squared_percent": min(100.0, i_squared),
        "weighted_mean": weighted_mean,
        "study_count": len(effects),
        "method": "Cochran's Q for meta-analysis",
        "formula": "Q=sum(w_i*(y_i-weighted_mean)^2); w_i=1/v_i",
        "null_hypothesis": "All studies share one common effect size.",
        "assumptions": [
            "Study effect estimates are independent and on a common scale.",
            "Input variances are sampling variances, not standard errors or standard deviations.",
            "The chi-square reference distribution is an approximation; low power is possible with few studies.",
        ],
    }


def benjamini_hochberg(p_values: Sequence[float]) -> dict:
    """Ajuste Benjamini–Hochberg para controlar FDR sob condições apropriadas."""
    values = _finite_vector(p_values, "p_values", minimum=1)
    if any(value < 0 or value > 1 for value in values):
        raise ValueError("p_values devem estar entre 0 e 1.")
    count = len(values)
    order = sorted(range(count), key=lambda index: (values[index], index))
    adjusted = [0.0] * count
    running_minimum = 1.0
    for rank_index in range(count - 1, -1, -1):
        original_index = order[rank_index]
        rank = rank_index + 1
        candidate = values[original_index] * count / rank
        running_minimum = min(running_minimum, candidate)
        adjusted[original_index] = min(1.0, running_minimum)
    return {
        "adjusted_p_values": adjusted,
        "rank_order": order,
        "method": "Benjamini-Hochberg step-up adjustment",
        "family_size": count,
        "assumptions": ["FDR control requires independence or specified positive-dependence conditions; dependence is not assessed."],
    }


def risk_ratio(events_exposed: int, n_exposed: int, events_unexposed: int, n_unexposed: int,
               confidence_level: float = 0.95) -> dict:
    """Razão de riscos com IC log-Wald; células zero são rejeitadas, sem correção oculta."""
    a = _count(events_exposed, "events_exposed")
    n1 = _count(n_exposed, "n_exposed")
    c = _count(events_unexposed, "events_unexposed")
    n0 = _count(n_unexposed, "n_unexposed")
    if n1 <= 0 or n0 <= 0 or a <= 0 or c <= 0 or a > n1 or c > n0:
        raise ValueError("Risk ratio log-Wald exige amostras positivas e eventos entre 1 e o tamanho de cada grupo.")
    level, z = _confidence_z(confidence_level)
    estimate = (a / n1) / (c / n0)
    se_log = math.sqrt(1.0 / a - 1.0 / n1 + 1.0 / c - 1.0 / n0)
    interval = [math.exp(math.log(estimate) - z * se_log), math.exp(math.log(estimate) + z * se_log)]
    return {"estimate": estimate, "confidence_interval": interval, "confidence_level": level,
            "method": "risk ratio with log-Wald interval", "zero_cell_correction": "none; zero cells are rejected"}


def odds_ratio(a: int, b: int, c: int, d: int, confidence_level: float = 0.95) -> dict:
    """Odds ratio de tabela 2×2 com IC log-Wald, sem correção automática de células."""
    cells = [_count(value, name) for value, name in zip((a, b, c, d), ("a", "b", "c", "d"))]
    if any(value == 0 for value in cells):
        raise ValueError("Odds ratio log-Wald exige quatro células positivas; nenhuma correção é aplicada automaticamente.")
    level, z = _confidence_z(confidence_level)
    estimate = cells[0] * cells[3] / (cells[1] * cells[2])
    se_log = math.sqrt(sum(1.0 / value for value in cells))
    interval = [math.exp(math.log(estimate) - z * se_log), math.exp(math.log(estimate) + z * se_log)]
    return {"estimate": estimate, "confidence_interval": interval, "confidence_level": level,
            "method": "odds ratio with log-Wald interval", "zero_cell_correction": "none; zero cells are rejected"}


def diagnostic_accuracy(*, tp: int, fn: int, tn: int, fp: int) -> dict:
    """Métricas pontuais de uma tabela de classificação diagnóstica 2×2."""
    true_positive = _count(tp, "tp")
    false_negative = _count(fn, "fn")
    true_negative = _count(tn, "tn")
    false_positive = _count(fp, "fp")
    positive_total = true_positive + false_negative
    negative_total = true_negative + false_positive
    predicted_positive = true_positive + false_positive
    predicted_negative = true_negative + false_negative
    total = positive_total + negative_total
    if min(positive_total, negative_total, predicted_positive, predicted_negative, total) <= 0:
        raise ValueError("A tabela deve permitir denominadores positivos para todas as métricas.")
    return {
        "sensitivity": true_positive / positive_total,
        "specificity": true_negative / negative_total,
        "positive_predictive_value": true_positive / predicted_positive,
        "negative_predictive_value": true_negative / predicted_negative,
        "accuracy": (true_positive + true_negative) / total,
        "counts": {"tp": true_positive, "fn": false_negative, "tn": true_negative, "fp": false_positive},
        "limitations": ["Métricas pontuais; intervalos e calibração do teste não são calculados.",
                        "Valores preditivos dependem da prevalência na amostra/população-alvo."],
    }
