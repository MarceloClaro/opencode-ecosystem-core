"""R1148 — coordenação vs. warrant epistêmico, Brier/ECE e abstenção.

Separa duas perguntas:

- **coordenação**: o agente executa, entrega e mantém taxa de sucesso?
- **warrant epistêmico**: as probabilidades declaradas são calibradas?

Um agente pode coordenar bem e ser epistemicamente frágil. Sem histórico
suficiente, o relatório diz `calibration_insufficient_data` e recomenda
abstenção; não inventa confiança.
"""
from __future__ import annotations

import math
from datetime import datetime

LIMITS = (
    "Brier/ECE medem calibração em resultados observados; não provam verdade, "
    "causalidade ou generalização. Coordination score não é warrant epistêmico. "
    "Sem histórico suficiente, a única saída honesta é abstenção."
)


def _validate(predictions, outcomes) -> tuple[list[float], list[int]]:
    predictions = [float(value) for value in predictions]
    outcomes = [int(value) for value in outcomes]
    if len(predictions) != len(outcomes):
        raise ValueError("predictions e outcomes devem ter o mesmo tamanho")
    if not predictions:
        raise ValueError("histórico vazio")
    if any(not 0.0 <= value <= 1.0 for value in predictions):
        raise ValueError("predictions devem estar em [0,1]")
    if any(value not in (0, 1) for value in outcomes):
        raise ValueError("outcomes devem ser 0/1")
    return predictions, outcomes


def brier_score(predictions, outcomes) -> float:
    predictions, outcomes = _validate(predictions, outcomes)
    return float(
        sum(
            (prediction - outcome) ** 2
            for prediction, outcome in zip(predictions, outcomes)
        )
        / len(predictions)
    )


def expected_calibration_error(
    predictions,
    outcomes,
    *,
    n_bins: int = 10,
) -> dict:
    predictions, outcomes = _validate(predictions, outcomes)
    n_bins = int(n_bins)
    if n_bins < 1:
        raise ValueError("n_bins deve ser >= 1")
    bins = []
    ece = 0.0
    total = len(predictions)
    for index in range(n_bins):
        low = index / n_bins
        high = (index + 1) / n_bins
        members = [
            (prediction, outcome)
            for prediction, outcome in zip(predictions, outcomes)
            if (low <= prediction < high)
            or (index == n_bins - 1 and prediction == 1.0)
        ]
        if not members:
            continue
        count = len(members)
        mean_prediction = sum(value for value, _ in members) / count
        mean_outcome = sum(value for _, value in members) / count
        gap = abs(mean_prediction - mean_outcome)
        ece += (count / total) * gap
        bins.append({
            "bin_low": low,
            "bin_high": high,
            "n": count,
            "mean_prediction": float(mean_prediction),
            "mean_outcome": float(mean_outcome),
            "gap": float(gap),
        })
    return {
        "ece": float(ece),
        "n_bins": n_bins,
        "n": total,
        "bins": bins,
        "method": "ECE por bins iguais de probabilidade prevista",
    }


def _recency_weighted_success(history: list[dict]) -> float:
    items = []
    for item in history:
        timestamp = item.get("timestamp")
        parsed = None
        if timestamp:
            try:
                parsed = datetime.fromisoformat(str(timestamp))
            except ValueError:
                parsed = None
        items.append((parsed, float(item["outcome"])))
    if all(parsed is None for parsed, _ in items):
        return sum(value for _, value in items) / len(items)
    items.sort(
        key=lambda pair: pair[0] or datetime.min,
        reverse=True,
    )
    weights = [math.exp(-index / 10.0) for index in range(len(items))]
    denominator = sum(weights)
    return float(
        sum(weight * value for weight, (_, value) in zip(weights, items))
        / denominator
    )


def coordination_score(history: list[dict]) -> dict:
    if not history:
        return {
            "schema_version": 1,
            "coordination_score": 0.0,
            "n": 0,
            "status": "no_history",
        }
    outcomes = [int(item["outcome"]) for item in history]
    if any(value not in (0, 1) for value in outcomes):
        raise ValueError("outcomes devem ser 0/1")
    success_rate = sum(outcomes) / len(outcomes)
    recency = _recency_weighted_success(history)
    volume = 1.0 - math.exp(-len(outcomes) / 20.0)
    score = 0.5 * success_rate + 0.3 * recency + 0.2 * volume
    return {
        "schema_version": 1,
        "coordination_score": float(max(0.0, min(1.0, score))),
        "success_rate": float(success_rate),
        "recency_weighted_success": float(recency),
        "volume_factor": float(volume),
        "n": len(outcomes),
        "status": "observed",
    }


def epistemic_warrant(
    history: list[dict],
    *,
    min_samples: int = 20,
    warrant_threshold: float = 0.6,
    ece_threshold: float = 0.15,
    n_bins: int = 10,
) -> dict:
    if not history:
        return {
            "schema_version": 1,
            "status": "calibration_insufficient_data",
            "warrant": None,
            "abstain": True,
            "n": 0,
            "recommendation": "abster; sem outcomes observados",
            "limits": LIMITS,
        }
    predictions = [float(item["prediction"]) for item in history]
    outcomes = [int(item["outcome"]) for item in history]
    brier = brier_score(predictions, outcomes)
    ece = expected_calibration_error(
        predictions, outcomes, n_bins=n_bins
    )
    n = len(outcomes)
    if n < int(min_samples):
        return {
            "schema_version": 1,
            "status": "calibration_insufficient_data",
            "warrant": None,
            "abstain": True,
            "n": n,
            "brier": float(brier),
            "ece": float(ece["ece"]),
            "min_samples": int(min_samples),
            "recommendation": "abster; amostra insuficiente para calibrar",
            "limits": LIMITS,
        }
    calibration = 1.0 - brier
    reliability = 1.0 - ece["ece"]
    warrant = 0.7 * calibration + 0.3 * reliability
    bias = sum(predictions) / n - sum(outcomes) / n
    if bias > 0.1:
        status = "overconfident"
    elif bias < -0.1:
        status = "underconfident"
    else:
        status = "calibrated"
    abstain = warrant < float(warrant_threshold) or ece["ece"] > float(ece_threshold)
    return {
        "schema_version": 1,
        "status": status,
        "warrant": float(max(0.0, min(1.0, warrant))),
        "abstain": bool(abstain),
        "n": n,
        "brier": float(brier),
        "ece": float(ece["ece"]),
        "bias": float(bias),
        "calibration_component": float(calibration),
        "reliability_component": float(reliability),
        "ece_bins": ece["bins"],
        "warrant_threshold": float(warrant_threshold),
        "ece_threshold": float(ece_threshold),
        "recommendation": (
            "abster; calibração insuficiente"
            if abstain
            else "usar com monitoramento e revisão humana"
        ),
        "limits": LIMITS,
    }


def trust_report(
    history: list[dict],
    *,
    min_samples: int = 20,
    warrant_threshold: float = 0.6,
    ece_threshold: float = 0.15,
) -> dict:
    coordination = coordination_score(history)
    warrant = epistemic_warrant(
        history,
        min_samples=min_samples,
        warrant_threshold=warrant_threshold,
        ece_threshold=ece_threshold,
    )
    return {
        "schema_version": 1,
        "coordination": coordination,
        "epistemic_warrant": warrant,
        "separation_note": (
            "coordenação alta não implica warrant alto; "
            "coordenação mede entrega, warrant mede calibração"
        ),
        "limits": LIMITS,
        "hardware_executed": False,
    }
