# -*- coding: utf-8 -*-
"""RigorousEmpiricalValidator — estatística computada de dados brutos.

Diferente de mci.statistical_validator (que valida p-value/effect_size já
fornecidos), este módulo COMPUTA hipóteses a partir de amostras brutas via
contraprova por permutação (ataque de falsificação real, não decorado),
duas famílias de teste independentes (Welch-t e Mann-Whitney), validação
cruzada k-fold genérica e um relatório de "validade convergente".

Limite epistêmico: nenhuma função aqui prova uma hipótese. Convergência
significa que a alegação resistiu a tentativas independentes de
falsificação (permutação de rótulos, duas famílias de teste, validação
cruzada) — não que seja verdadeira, causal ou relevante. Interpretação
final é sempre humana.

Zero dependência de numpy/scipy: segue a convenção de
mci/statistical_validator.py (stdlib pura: statistics/math/random).

SPEC-935-R370.
"""

from __future__ import annotations

import math
import random
import statistics
from typing import Any, Callable, Dict, List, Sequence, Tuple

from mci.statistical_validator import validate_statistics

SCHEMA_VERSION = "1.0.0"

DEFAULT_SEED = 935370

DISCLAIMER = (
    "Convergência entre métodos estatísticos independentes NÃO PROVA a "
    "hipótese: significa que a alegação resistiu a tentativas de "
    "falsificação por permutação de rótulos sob duas famílias de teste "
    "(paramétrica e não-paramétrica). Não estabelece causalidade nem "
    "relevância no mundo real. Interpretação final é humana."
)

_LOW_DENOMINATOR_FLOOR = 1e-9


class ContractError(ValueError):
    """Entrada fora do contrato — falha fechada (SPEC-935-R373)."""


# ═══════════════════════════════════════════════════════════════════════
# 1. Contraprova por permutação (motor genérico)
# ═══════════════════════════════════════════════════════════════════════

def permutation_counter_proof(
    group_a: Sequence[float],
    group_b: Sequence[float],
    statistic_fn: Callable[[Sequence[float], Sequence[float]], float],
    n_permutations: int = 2000,
    seed: int = DEFAULT_SEED,
) -> Dict[str, Any]:
    """Tentativa de falsificação por permutação de rótulos.

    Embaralha os grupos combinados `n_permutations` vezes e recalcula a
    estatística sob a hipótese nula (rótulos trocados ao acaso). O p-value
    é a fração de permutações tão ou mais extremas que a observada.
    Determinístico: mesma entrada + mesmo seed -> mesmo resultado.
    """
    group_a = list(group_a)
    group_b = list(group_b)
    n_a, n_b = len(group_a), len(group_b)
    observed = statistic_fn(group_a, group_b)

    rng = random.Random(seed)
    pooled = group_a + group_b
    null_stats: List[float] = []
    for _ in range(n_permutations):
        shuffled = pooled[:]
        rng.shuffle(shuffled)
        perm_a, perm_b = shuffled[:n_a], shuffled[n_a:n_a + n_b]
        null_stats.append(statistic_fn(perm_a, perm_b))

    # Teste bilateral genérico: centra pela média da própria distribuição
    # nula, pois estatísticas como Mann-Whitney U não são simétricas em
    # torno de zero sob H0 (ao contrário de Welch-t). Usar |observado| como
    # referência fixa subestimaria a extremidade de estatísticas deslocadas.
    null_mean = statistics.mean(null_stats)
    observed_deviation = abs(observed - null_mean)
    extreme_count = sum(
        1 for stat in null_stats if abs(stat - null_mean) >= observed_deviation
    )
    p_value = (1 + extreme_count) / (n_permutations + 1)

    return {
        "observed_statistic": observed,
        "p_value": p_value,
        "n_permutations": n_permutations,
        "seed": seed,
        "null_distribution_summary": {
            "min": min(null_stats),
            "max": max(null_stats),
            "mean": statistics.mean(null_stats),
            "stdev": statistics.pstdev(null_stats),
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# 2. Estatísticas de teste (paramétrica e não-paramétrica)
# ═══════════════════════════════════════════════════════════════════════

def _welch_t_statistic(a: Sequence[float], b: Sequence[float]) -> float:
    mean_a, mean_b = statistics.mean(a), statistics.mean(b)
    var_a = statistics.variance(a) if len(a) > 1 else 0.0
    var_b = statistics.variance(b) if len(b) > 1 else 0.0
    n_a, n_b = len(a), len(b)
    denom = ((var_a / n_a) + (var_b / n_b)) ** 0.5
    return (mean_a - mean_b) / denom if denom > 0 else 0.0


def _mann_whitney_u_a(a: Sequence[float], b: Sequence[float]) -> float:
    """U_a: soma de postos de `a` menos o mínimo possível (empates por média)."""
    combined = sorted(
        [(v, "a") for v in a] + [(v, "b") for v in b], key=lambda item: item[0]
    )
    n = len(combined)
    ranks: Dict[int, float] = {}
    i = 0
    while i < n:
        j = i
        while j < n and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # postos 1-indexados
        for idx in range(i, j):
            ranks[idx] = avg_rank
        i = j
    rank_sum_a = sum(ranks[idx] for idx, (_, g) in enumerate(combined) if g == "a")
    n_a = len(a)
    return rank_sum_a - n_a * (n_a + 1) / 2.0


def _bootstrap_ci_cohens_d(
    group_a: Sequence[float], group_b: Sequence[float],
    n_resamples: int = 2000, seed: int = DEFAULT_SEED,
) -> Tuple[float, float]:
    rng = random.Random(seed)
    n_a, n_b = len(group_a), len(group_b)
    samples: List[float] = []
    for _ in range(n_resamples):
        resample_a = [group_a[rng.randrange(n_a)] for _ in range(n_a)]
        resample_b = [group_b[rng.randrange(n_b)] for _ in range(n_b)]
        samples.append(_cohens_d(resample_a, resample_b))
    samples.sort()
    lo_idx = int(0.025 * n_resamples)
    hi_idx = int(0.975 * n_resamples) - 1
    hi_idx = min(hi_idx, n_resamples - 1)
    return samples[lo_idx], samples[hi_idx]


def _cohens_d(group_a: Sequence[float], group_b: Sequence[float]) -> float:
    mean_a, mean_b = statistics.mean(group_a), statistics.mean(group_b)
    n_a, n_b = len(group_a), len(group_b)
    var_a = statistics.variance(group_a) if n_a > 1 else 0.0
    var_b = statistics.variance(group_b) if n_b > 1 else 0.0
    pooled_var = ((n_a - 1) * var_a + (n_b - 1) * var_b) / max(1, (n_a + n_b - 2))
    pooled_sd = pooled_var ** 0.5
    return (mean_a - mean_b) / pooled_sd if pooled_sd > 0 else 0.0


def two_sample_hypothesis_test(
    group_a: Sequence[float],
    group_b: Sequence[float],
    seed: int = DEFAULT_SEED,
    n_permutations: int = 2000,
) -> Dict[str, Any]:
    """Duas lentes independentes (Welch-t + Mann-Whitney) via permutação,
    mais Cohen's d com IC 95% via bootstrap."""
    group_a = list(group_a)
    group_b = list(group_b)
    if len(group_a) < 3 or len(group_b) < 3:
        raise ValueError(
            "amostra insuficiente para permutação significativa "
            "(mínimo 3 por grupo)."
        )

    welch = permutation_counter_proof(
        group_a, group_b, _welch_t_statistic, n_permutations=n_permutations, seed=seed
    )
    mann_whitney = permutation_counter_proof(
        group_a, group_b, _mann_whitney_u_a, n_permutations=n_permutations, seed=seed
    )
    cohens_d = _cohens_d(group_a, group_b)
    ci = _bootstrap_ci_cohens_d(group_a, group_b, n_resamples=n_permutations, seed=seed)

    return {
        "schema_version": SCHEMA_VERSION,
        "welch_t": welch,
        "mann_whitney": mann_whitney,
        "cohens_d": cohens_d,
        "cohens_d_ci_95": ci,
        "sample_size": {"n_a": len(group_a), "n_b": len(group_b)},
    }


# ═══════════════════════════════════════════════════════════════════════
# 3. Validação cruzada k-fold (harness genérico)
# ═══════════════════════════════════════════════════════════════════════

def k_fold_cross_validate(
    data: Sequence[Any],
    k: int,
    scorer_fn: Callable[[List[int], List[int]], float],
    seed: int = DEFAULT_SEED,
) -> Dict[str, Any]:
    """Validação cruzada k-fold genérica. Partição exaustiva e disjunta."""
    n = len(data)
    if n == 0:
        raise ValueError("data não pode ser vazio.")
    if k < 2 or k > n:
        raise ValueError(f"k deve estar em [2, {n}]; recebido k={k}.")

    indices = list(range(n))
    rng = random.Random(seed)
    rng.shuffle(indices)

    # Partição o mais equilibrada possível
    fold_sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    folds: List[List[int]] = []
    cursor = 0
    for size in fold_sizes:
        folds.append(indices[cursor:cursor + size])
        cursor += size

    fold_scores: List[float] = []
    for i in range(k):
        test_idx = folds[i]
        train_idx = [idx for j, fold in enumerate(folds) if j != i for idx in fold]
        fold_scores.append(scorer_fn(train_idx, test_idx))

    mean = statistics.mean(fold_scores)
    stdev = statistics.pstdev(fold_scores) if len(fold_scores) > 1 else 0.0
    low_mean_denominator = abs(mean) < _LOW_DENOMINATOR_FLOOR
    denominator = max(abs(mean), _LOW_DENOMINATOR_FLOOR)
    coefficient_of_variation = stdev / denominator

    return {
        "schema_version": SCHEMA_VERSION,
        "fold_scores": fold_scores,
        "mean": mean,
        "stdev": stdev,
        "coefficient_of_variation": coefficient_of_variation,
        "stable": coefficient_of_variation <= 0.5,
        "low_mean_denominator": low_mean_denominator,
        "k": k,
        "seed": seed,
    }


# ═══════════════════════════════════════════════════════════════════════
# 4. Relatório de validade convergente
# ═══════════════════════════════════════════════════════════════════════

def convergent_validity_report(
    group_a: Sequence[float],
    group_b: Sequence[float],
    alpha: float = 0.05,
    seed: int = DEFAULT_SEED,
    n_permutations: int = 2000,
) -> Dict[str, Any]:
    """Relatório honesto de convergência entre métodos independentes.

    convergent=True somente quando: Welch-t significante E Mann-Whitney
    significante E IC bootstrap do effect size exclui zero. Reaproveita
    mci.statistical_validator.validate_statistics para o veredito final
    (Bayes factor, evidence_strength) sem duplicar essa lógica.
    """
    tests = two_sample_hypothesis_test(
        group_a, group_b, seed=seed, n_permutations=n_permutations
    )

    welch_significant = tests["welch_t"]["p_value"] < alpha
    mw_significant = tests["mann_whitney"]["p_value"] < alpha
    ci_low, ci_high = tests["cohens_d_ci_95"]
    ci_excludes_zero = (ci_low > 0) or (ci_high < 0)
    sign_agrees = True  # por construção: Cohen's d e a diferença de médias sempre concordam

    convergent = bool(
        welch_significant and mw_significant and ci_excludes_zero and sign_agrees
    )

    verdict = validate_statistics(
        claim={},
        context={
            "p_value": tests["welch_t"]["p_value"],
            "effect_size": tests["cohens_d"],
            "confidence_interval": [ci_low, ci_high],
            "sample_size": tests["sample_size"]["n_a"] + tests["sample_size"]["n_b"],
        },
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "convergent": convergent,
        "welch_significant": welch_significant,
        "mann_whitney_significant": mw_significant,
        "ci_excludes_zero": ci_excludes_zero,
        "tests": tests,
        "verdict": verdict,
        "human_gate": True,
        "disclaimer": DISCLAIMER,
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. Contraverificação de estatísticas já reportadas (SPEC-935-R373)
# ═══════════════════════════════════════════════════════════════════════
#
# Motivação: manuscritos publicados reportam apenas r/p/n já calculados,
# nunca os dados brutos que two_sample_hypothesis_test exige. Esta seção
# recalcula a significância de Pearson de forma independente a partir de
# (r, n) — via distribuição t de Student em Python puro (função beta
# incompleta regularizada por fração contínua, sem numpy/scipy) — e
# compara de forma ASSIMÉTRICA: nenhuma correção metodológica legítima
# (cointegração, autocorrelação, tamanho efetivo de amostra) jamais torna
# um resultado artificialmente MAIS significativo do que a fórmula
# ingênua sustenta; só torna mais conservador. Por isso, só é sinalizado
# o caso em que o p reportado é MENOR que o p ingênuo.

CROSSCHECK_DISCLAIMER = (
    "Ausência de achado NÃO VALIDA a correção metodológica aplicada pelo "
    "autor — apenas confirma que a significância reportada não é mais "
    "forte do que os números brutos (r, n) sustentariam sem correção "
    "alguma. Correções legítimas de séries temporais (cointegração, "
    "autocorrelação) tornam o p mais conservador, nunca mais forte; só "
    "esse segundo caso é sinalizado."
)


def _log_beta(a: float, b: float) -> float:
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _betacf(x: float, a: float, b: float) -> float:
    """Fração contínua da função beta incompleta (Numerical Recipes)."""
    max_iter, eps, fpmin = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_bt = -_log_beta(a, b) + a * math.log(x) + b * math.log(1.0 - x)
    bt = math.exp(log_bt)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(x, a, b) / a
    return 1.0 - bt * _betacf(1.0 - x, b, a) / b


def pearson_naive_significance(r: float, n: int) -> float:
    """P-value bilateral de Pearson a partir de (r, n), via t de Student
    em Python puro. Validado contra scipy.stats.t.cdf (dev-time) com
    diff <= 1e-12 em 8 casos de referência; scipy não é importado aqui.
    """
    if not isinstance(n, int) or n < 3:
        raise ContractError("n deve ser inteiro >= 3.")
    if not isinstance(r, (int, float)) or abs(r) >= 1.0:
        raise ContractError("r deve estar em (-1, 1).")

    df = n - 2
    t = r * math.sqrt(df) / math.sqrt(1 - r ** 2)
    x = df / (df + t * t)
    return _regularized_incomplete_beta(x, df / 2.0, 0.5)


def crosscheck_reported_correlation(
    r: float, n: int, reported_p: float, tolerance: float = 1e-3
) -> Dict[str, Any]:
    """Contraverificação assimétrica: só sinaliza quando o p reportado é
    MAIS FORTE (menor) do que a fórmula ingênua a partir de (r, n)
    sustenta — nunca quando é igual ou mais conservador (correção
    metodológica legítima de série temporal)."""
    naive_p = pearson_naive_significance(r, n)
    overstated = reported_p < (naive_p - tolerance)

    findings: List[Dict[str, Any]] = []
    if overstated:
        findings.append({
            "schema_version": SCHEMA_VERSION,
            "code": "OVERSTATED_SIGNIFICANCE",
            "severity": "high",
            "detail": (
                f"p reportado ({reported_p:.6f}) é mais forte que o p "
                f"ingênuo calculado de (r={r}, n={n}) = {naive_p:.6f} — "
                f"nenhuma correção metodológica legítima produz esse "
                f"efeito"
            ),
            "requires_human_review": True,
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "naive_p": naive_p,
        "reported_p": reported_p,
        "overstated": overstated,
        "findings": findings,
        "human_gate": "required" if overstated else "recommended",
        "disclaimer": CROSSCHECK_DISCLAIMER,
    }
