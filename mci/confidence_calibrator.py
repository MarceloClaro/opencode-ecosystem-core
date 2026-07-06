# -*- coding: utf-8 -*-
"""
ConfidenceCalibrator — Calibração de Confiança com Brier Score e ECE.

Upgrades vs SuperHuman:
- Brier Score (calibração + resolução)
- Expected Calibration Error (ECE)
- Calibração por binning adaptativo
- Abstention quando incerteza alta
- Atualização por feedback histórico
- Registro no EvidenceGraph
"""

import math
from typing import Dict, Any, List, Optional, Tuple


def _brier_score(
    predicted_prob: float,
    actual_outcome: int
) -> float:
    """
    Calcula o Brier Score para uma previsão.

    BS = (p - o)² onde p é a probabilidade prevista, o é o outcome (0 ou 1).

    Quanto menor, melhor. Range: [0, 1].
    Brier perfeito = 0
    """
    return (predicted_prob - actual_outcome) ** 2


def _expected_calibration_error(
    predictions: List[float],
    outcomes: List[int],
    n_bins: int = 10
) -> float:
    """
    Calcula o Expected Calibration Error (ECE).

    ECE = sum(bin_weight * |acc(bin) - conf(bin)|)

    Mede o quão bem as probabilidades previstas correspondem
    às frequências observadas.
    """
    if not predictions or len(predictions) != len(outcomes):
        return 0.0

    # Cria bins
    bin_edges = [i / n_bins for i in range(n_bins + 1)]
    bin_counts = [0] * n_bins
    bin_correct = [0] * n_bins
    bin_conf = [0.0] * n_bins

    for pred, outcome in zip(predictions, outcomes):
        bin_idx = min(int(pred * n_bins), n_bins - 1)
        bin_counts[bin_idx] += 1
        bin_correct[bin_idx] += outcome
        bin_conf[bin_idx] += pred

    ece = 0.0
    total = len(predictions)

    for i in range(n_bins):
        if bin_counts[i] == 0:
            continue
        acc = bin_correct[i] / bin_counts[i]
        conf = bin_conf[i] / bin_counts[i]
        weight = bin_counts[i] / total
        ece += weight * abs(acc - conf)

    return ece


def calibrate_confidence(
    claim: Dict[str, Any],
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Calibra a confiança de uma ScientificClaim usando múltiplos critérios.

    Args:
        claim: ScientificClaim dict
        context: Contexto com parâmetros de calibração

    Returns:
        ScientificClaim com calibrated_confidence calculado
    """
    if context is None:
        context = {}

    # Fatores de calibração
    base = 0.5

    # 1. p-valor
    p_value = claim.get("p_value_corrected") or claim.get("p_value")
    if p_value is not None:
        if p_value < 0.001:
            base += 0.30
        elif p_value < 0.01:
            base += 0.20
        elif p_value < 0.05:
            base += 0.10
        elif p_value < 0.10:
            base += 0.05
        else:
            base -= 0.20

    # 2. Tamanho de efeito
    effect_size = claim.get("effect_size")
    if effect_size is not None:
        es = abs(effect_size)
        if es >= 0.8:
            base += 0.15
        elif es >= 0.5:
            base += 0.10
        elif es >= 0.2:
            base += 0.05
        else:
            base -= 0.10

    # 3. Bayes Factor
    bf = claim.get("bayes_factor", {})
    bf10 = bf.get("BF10", 0) if isinstance(bf, dict) else 0
    if bf10 >= 100:
        base += 0.20
    elif bf10 >= 30:
        base += 0.15
    elif bf10 >= 10:
        base += 0.10
    elif bf10 >= 3:
        base += 0.05
    elif bf10 < 0.33:  # BF01 > 3
        base -= 0.20

    # 4. Poder estatístico
    statistical_power = claim.get("statistical_power", 0.5)
    if statistical_power >= 0.95:
        base += 0.10
    elif statistical_power >= 0.80:
        base += 0.05
    elif statistical_power < 0.50:
        base -= 0.15

    # 5. Reprodutibilidade
    reproducibility = context.get("reproducibility_score", claim.get("reproducibility_score", 0.85))
    if reproducibility >= 0.95:
        base += 0.10
    elif reproducibility >= 0.80:
        base += 0.05
    elif reproducibility < 0.50:
        base -= 0.20

    # 6. Achados adversariais (penalizam confiança)
    findings = claim.get("adversarial_findings", [])
    n_alerts = sum(1 for f in findings if f.startswith("ALERTA:"))
    n_confounders = sum(1 for f in findings if f.startswith("CONFOUNDER"))
    base -= min(0.30, n_alerts * 0.08)
    base -= min(0.20, n_confounders * 0.05)

    # 7. Penalidade adicional por adversarial override
    if claim.get("adversarial_overridden", False):
        base -= 0.15

    # 8. Veredito consistente?
    if claim.get("final_verdict") == "refuted":
        base = max(base, 0.3)  # Confiança mínima mesmo em refutação

    # Clampa entre [0, 1]
    calibrated = max(0.0, min(1.0, round(base, 4)))

    # Decisão de abstention
    should_abstain = calibrated < 0.20
    abstention_reason = None
    if should_abstain:
        abstention_reason = (
            f"Confiança calibrada muito baixa ({calibrated:.2f}). "
            "Recomenda-se abster-se de conclusões definitivas. "
            "Coletar mais dados ou revisar o desenho experimental."
        )

    claim["calibrated_confidence"] = calibrated
    claim["should_abstain"] = should_abstain
    claim["abstention_reason"] = abstention_reason

    # Brier Score (se houver outcome real)
    actual_outcome = context.get("actual_outcome")
    if actual_outcome is not None:
        # Converte veredito para outcome binário
        verdict_to_outcome = {
            "supported": 1,
            "inconclusive": 0,
            "refuted": 0,
        }
        outcome = verdict_to_outcome.get(
            context.get("actual_verdict", claim.get("final_verdict", "inconclusive")),
            0
        )
        brier = _brier_score(calibrated, outcome)
        claim["brier_score"] = round(brier, 4)
    else:
        claim["brier_score"] = None

    claim["reproducibility_score"] = float(reproducibility)

    return claim


def calculate_ece_from_history(
    confidence_history: List[float],
    outcome_history: List[int],
    n_bins: int = 10
) -> float:
    """
    Calcula o ECE a partir do histórico de confianças e outcomes.

    Útil para monitoramento contínuo da calibração do sistema.
    """
    if not confidence_history or len(confidence_history) != len(outcome_history):
        return 0.0
    return _expected_calibration_error(
        confidence_history, outcome_history, n_bins
    )


def update_calibration_from_feedback(
    claim: Dict[str, Any],
    feedback: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Atualiza a calibração com base em feedback externo (humano ou validação).

    Args:
        claim: ScientificClaim original
        feedback: Dict com 'verified_verdict' (str) e 'confidence' (float)

    Returns:
        ScientificClaim atualizado com novo Brier score
    """
    verified_verdict = feedback.get("verified_verdict")
    feedback_confidence = feedback.get("confidence")

    if verified_verdict and feedback_confidence is not None:
        outcome = 1 if verified_verdict == "supported" else 0
        brier = _brier_score(claim.get("calibrated_confidence", 0.5), outcome)

        if "brier_history" not in claim:
            claim["brier_history"] = []

        claim["brier_history"].append({
            "brier_score": round(brier, 4),
            "feedback_confidence": feedback_confidence,
            "verified_verdict": verified_verdict,
        })

        # Média móvel dos Brier scores
        brier_values = [b["brier_score"] for b in claim["brier_history"]]
        claim["average_brier_score"] = round(
            sum(brier_values) / len(brier_values), 4
        )

    return claim
