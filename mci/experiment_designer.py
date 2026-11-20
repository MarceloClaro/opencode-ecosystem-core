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

    # Pré-registro (SPEC-935-R372): corrige bug de overclaim onde
    # "pre_registered" tinha default True sem qualquer verificação. Agora
    # só é True quando um protocolo real (mci.preregistration_protocol)
    # foi registrado ANTES da análise e verificado como honrado.
    registered_protocol = context.get("registered_protocol")
    protocol_verification = None
    if registered_protocol is not None and all(
        k in context for k in ("actual_hypothesis", "actual_method", "actual_alpha")
    ):
        from mci.preregistration_protocol import verify_protocol

        protocol_verification = verify_protocol(
            registered_protocol,
            actual_hypothesis=context["actual_hypothesis"],
            actual_method=context["actual_method"],
            actual_alpha=context["actual_alpha"],
        )
        pre_registered = protocol_verification["honored"]
    else:
        pre_registered = False

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
        "pre_registered": pre_registered,
        "analysis_plan": context.get("analysis_plan", [
            "Descriptive statistics (média, desvio padrão, distribuição)",
            "Primary analysis: teste estatístico principal",
            "Sensitivity analysis: análise de sensibilidade",
            "Subgroup analysis: análise de subgrupos (se aplicável)",
        ]),
    })

    # Cálculo por precisão e power analysis respondem perguntas diferentes.
    # Só calcular a primeira modalidade quando o usuário fornece parâmetros
    # explícitos; não assumir erro, confiança, população ou variabilidade.
    sample_parameters = context.get("sample_size_parameters")
    if sample_parameters is not None:
        if not isinstance(sample_parameters, dict):
            raise ValueError("sample_size_parameters deve ser um objeto.")
        outcome_type = sample_parameters.get("outcome_type")
        common = {"population_size", "margin_error", "confidence_level", "design_effect", "nonresponse_rate"}
        if outcome_type == "proportion":
            allowed = common | {"outcome_type", "expected_proportion"}
            if not {"margin_error", "confidence_level"} <= set(sample_parameters):
                raise ValueError("Cálculo amostral de proporção requer margin_error e confidence_level explícitos.")
            if set(sample_parameters) - allowed:
                raise ValueError("Parâmetro desconhecido para cálculo amostral de proporção.")
            from research.quantitative_calculators import calculate_sample_size_proportion
            result = calculate_sample_size_proportion(
                population_size=sample_parameters.get("population_size"),
                margin_error=sample_parameters["margin_error"],
                confidence_level=sample_parameters["confidence_level"],
                expected_proportion=sample_parameters.get("expected_proportion", 0.5),
                design_effect=sample_parameters.get("design_effect", 1.0),
                nonresponse_rate=sample_parameters.get("nonresponse_rate", 0.0),
            )
        elif outcome_type == "mean":
            allowed = common | {"outcome_type", "standard_deviation"}
            if not {"standard_deviation", "margin_error", "confidence_level"} <= set(sample_parameters):
                raise ValueError("Cálculo amostral de média requer desvio-padrão, erro e confiança explícitos.")
            if set(sample_parameters) - allowed:
                raise ValueError("Parâmetro desconhecido para cálculo amostral de média.")
            from research.quantitative_calculators import calculate_sample_size_mean
            result = calculate_sample_size_mean(
                population_size=sample_parameters.get("population_size"),
                standard_deviation=sample_parameters["standard_deviation"],
                margin_error=sample_parameters["margin_error"],
                confidence_level=sample_parameters["confidence_level"],
                design_effect=sample_parameters.get("design_effect", 1.0),
                nonresponse_rate=sample_parameters.get("nonresponse_rate", 0.0),
            )
        else:
            raise ValueError("outcome_type deve ser 'proportion' ou 'mean'.")
        design["sample_size_calculation"] = {
            **result,
            "outcome_type": outcome_type,
            "execution_authorized": False,
            "distinction": "Precision-based minimum sample size; separate from effect-size power approximation.",
        }

    if protocol_verification is not None:
        design["protocol_verification"] = protocol_verification

    claim["experimental_design"] = design

    if not pre_registered:
        claim.setdefault("limitations", []).append(
            "Pré-registro não declarado; nenhum protocolo formal foi "
            "verificado antes da análise."
            if registered_protocol is None else
            "Protocolo pré-registrado apresentou desvio na verificação "
            "(ver protocol_verification)."
        )

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
