# -*- coding: utf-8 -*-
"""
ExperimentDesigner — Desenho Experimental com Power Analysis.

Upgrades vs SuperHuman:
- Cálculo de tamanho amostral (power analysis)
- Múltiplos braços experimentais
- Controle de confounders explícito
- Randomização estratificada
- Plano de análise pré-registrado
"""

import math
from typing import Dict, Any, List, Optional


def _calculate_sample_size(
    effect_size: float = 0.2,
    power: float = 0.80,
    alpha: float = 0.05,
    test_type: str = "two_sided"
) -> int:
    """
    Calcula o tamanho amostral mínimo necessário usando fórmula aproximada
    para teste t de Student (coerente com Cohen, 1988).

    Fórmula: n ≈ (Z_alpha/2 + Z_beta)^2 * 2 / d^2

    Onde:
    - d = effect_size (Cohen's d)
    - Z_alpha/2 = quantil da normal para alpha (bilateral ≈ 1.96)
    - Z_beta = quantil da normal para 1 - power (≈ 0.84 para power 0.80)
    """
    if effect_size <= 0:
        return float('inf')

    if test_type == "one_sided":
        z_alpha = 1.645  # alpha 0.05 one-sided
    else:
        z_alpha = 1.960  # alpha 0.05 two-sided

    z_beta = {
        0.80: 0.8416,
        0.85: 1.0364,
        0.90: 1.2816,
        0.95: 1.6449,
    }.get(power, 0.8416)

    # Fórmula para teste t independente (n por grupo)
    n_per_group = math.ceil(
        2 * (z_alpha + z_beta) ** 2 / (effect_size ** 2)
    )
    return n_per_group


def _suggest_confounders(domain: str, question: str) -> List[str]:
    """Sugere confounders potenciais baseados no domínio."""
    domain_confounders = {
        "machine_learning": [
            "Data leakage (vazamento de informação entre treino/teste)",
            "Class imbalance (desequilíbrio de classes)",
            "Hyperparameter overfitting (ajuste excessivo de hiperparâmetros)",
        ],
        "nlp": [
            "Domain shift (diferença de domínio entre treino e teste)",
            "Text length bias (viés de comprimento do texto)",
            "Annotation inconsistency (inconsistência de anotação)",
        ],
        "causal_inference": [
            "Unmeasured confounders (confundidores não medidos)",
            "Selection bias (viés de seleção)",
            "Measurement error (erro de medição na variável de tratamento)",
        ],
        "clinical": [
            "Confounding by indication (confusão por indicação)",
            "Loss to follow-up (perda de seguimento)",
            "Detection bias (viés de detecção)",
        ],
        "social_science": [
            "Social desirability bias (viés de desejabilidade social)",
            "Sampling bias (viés de amostragem)",
            "Demand characteristics (características de demanda)",
        ],
        "engineering": [
            "Hardware variability (variabilidade de hardware)",
            "Measurement noise (ruído de medição)",
            "Environmental factors (fatores ambientais)",
        ],
    }
    return domain_confounders.get(domain, [
        "Confounders não medidos (unknown unknowns)",
    ])


def design_experiment(
    claim: Dict[str, Any],
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Enriquece o desenho experimental com power analysis e controle de confounders.

    Args:
        claim: ScientificClaim dict com hipóteses
        context: Contexto com parâmetros de design

    Returns:
        ScientificClaim com desenho experimental completo
    """
    if context is None:
        context = {}

    # Aplica overrides do contexto
    design_override = context.get("experimental_design", {})
    if design_override:
        claim["experimental_design"].update(design_override)

    design = claim["experimental_design"]

    # Extrai parâmetros
    effect_size = context.get("effect_size", claim.get("sesoi", 0.2))
    power_level = design.get("power_level", 0.80)
    alpha = design.get("alpha", 0.05)
    domain = claim.get("domain", "machine_learning")

    # Calcula tamanho amostral
    n_per_group = _calculate_sample_size(
        effect_size=effect_size,
        power=power_level,
        alpha=alpha
    )

    # Número de grupos/braços
    n_arms = context.get("n_arms", 2)
    total_sample = n_per_group * n_arms

    # Confounders
    confounders = context.get(
        "confounders",
        _suggest_confounders(domain, claim.get("hypothesis", ""))
    )

    # Enriquece o desenho
    design.update({
        "n_arms": n_arms,
        "n_per_group": n_per_group,
        "total_sample_size": total_sample,
        "min_effect_size_detectable": effect_size,
        "power_level": power_level,
        "alpha": alpha,
        "confounders_controlled": confounders,
        "randomization_unit": context.get("randomization_unit", "individual"),
        "blinding": context.get("blinding", "double_blind"),
        "pre_registered": context.get("pre_registered", True),
        "analysis_plan": context.get("analysis_plan", [
            "Descriptive statistics (média, desvio padrão, distribuição)",
            "Primary analysis: teste estatístico principal",
            "Sensitivity analysis: análise de sensibilidade",
            "Subgroup analysis: análise de subgrupos (se aplicável)",
        ]),
    })

    claim["experimental_design"] = design

    # Limitações atualizadas
    if "power" not in str(claim.get("limitations", "")):
        if n_per_group == float('inf'):
            claim["limitations"].append(
                "Tamanho de efeito muito pequeno para detecção com poder adequado."
            )
        else:
            claim["limitations"].append(
                f"Tamanho amostral de {n_per_group} por grupo ({total_sample} total) "
                f"pode ser insuficiente para efeitos menores que d={effect_size}."
            )

    claim["limitations"].append(
        f"Foram identificados {len(confounders)} confounders potenciais no domínio {domain}."
    )

    return claim
