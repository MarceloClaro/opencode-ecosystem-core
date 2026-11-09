#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scorecard híbrido de resiliência quântica (R1116/R1117).

Combina evidências de readout 4x4, tomografia SPAM, ZNE, PEC, incerteza e
comparação simétrica q0/q1 para recomendar a próxima técnica. Não executa
hardware e não declara vantagem.
"""
from __future__ import annotations

from typing import Any

REDUNDANCY_TOL = 1e-6
LAYOUT_COHERENCE_GATE = 0.99
READOUT_GATE = 0.05
COHERENCE_DELTA_GATE = 0.005


def _mitigated(case: dict[str, Any]) -> float | None:
    value = case.get("mitigated_tvd_vs_ideal")
    if value is None:
        value = case.get("mitigated_tvd_subspace")
    return None if value is None else float(value)


def _readout_summary(readout: dict[str, Any] | None) -> dict[str, Any] | None:
    if not readout:
        return None
    baseline = readout.get("baseline")
    optimized = readout.get("optimized")
    if not baseline or not optimized:
        return None
    b = _mitigated(baseline)
    o = _mitigated(optimized)
    return {
        "baseline_mitigated_tvd": b,
        "optimized_mitigated_tvd": o,
        "winner": (
            "baseline" if b is not None and o is not None and b <= o
            else "optimized" if b is not None and o is not None
            else None
        ),
    }


def _tomography_summary(fit: dict[str, Any] | None) -> dict[str, Any] | None:
    if not fit:
        return None
    fidelity = fit.get("prep_fidelity") or {}
    if not fidelity:
        return None
    r0 = fit.get("readout_p1_given_prep0")
    r1 = fit.get("readout_p0_given_prep1")
    fidelity = {k: float(v) for k, v in fidelity.items()}
    coherence_states = [state for state in ("+", "+i") if state in fidelity]
    coherence = (
        min(fidelity[state] for state in coherence_states)
        if coherence_states
        else None
    )
    redundancy = (
        r0 is not None
        and r1 is not None
        and "0" in fidelity
        and "1" in fidelity
        and abs(fidelity["0"] - (1.0 - float(r0))) < REDUNDANCY_TOL
        and abs(fidelity["1"] - (1.0 - float(r1))) < REDUNDANCY_TOL
    )
    min_state = min(fidelity, key=fidelity.get) if fidelity else None
    return {
        "min_prep_fidelity": min(fidelity.values()),
        "min_prep_state": min_state,
        "coherence_prep_fidelity": coherence,
        "prep_fidelity": fidelity,
        "r0": r0,
        "r1": r1,
        "prep_readout_redundant": redundancy,
    }


def _uncertainty_widths(bootstrap: dict[str, Any] | None) -> dict[str, float]:
    if not bootstrap:
        return {}
    widths = {}
    for state, item in (bootstrap.get("prep_fidelity") or {}).items():
        widths[f"prep_{state}"] = float(item["high"]) - float(item["low"])
    for key, item in (bootstrap.get("readout") or {}).items():
        widths[f"readout_{key}"] = float(item["high"]) - float(item["low"])
    return widths


def _comparison_summary(
    comparison: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if not comparison:
        return {}
    deltas = comparison.get("deltas") or {}
    summary = {}
    for key, item in deltas.items():
        if not isinstance(item, dict):
            continue
        summary[key] = {
            "delta": item.get("delta_q1_minus_q0"),
            "ci_overlap": item.get("ci_overlap"),
            "q0_set_spread": item.get("q0_set_spread"),
            "q1_set_spread": item.get("q1_set_spread"),
        }
    return summary


def _nonconclusive(item: dict[str, Any]) -> bool:
    delta = item.get("delta")
    if delta is None:
        return False
    spreads = [
        value
        for value in (item.get("q0_set_spread"), item.get("q1_set_spread"))
        if value is not None
    ]
    spread = max(spreads) if spreads else 0.0
    return bool(item.get("ci_overlap")) and abs(float(delta)) <= float(spread)


def resilience_scorecard(
    *,
    readout: dict[str, Any] | None = None,
    zne: dict[str, Any] | None = None,
    tomography_q0: dict[str, Any] | None = None,
    tomography_q1: dict[str, Any] | None = None,
    comparison: dict[str, Any] | None = None,
    pec: dict[str, Any] | None = None,
    uncertainty: dict[str, Any] | None = None,
    surface: dict[str, Any] | None = None,
    pulse_dd: dict[str, Any] | None = None,
) -> dict[str, Any]:
    findings: list[str] = []
    recommendations: list[dict[str, str]] = []
    blocked: list[dict[str, str]] = []

    readout_summary = _readout_summary(readout)
    if readout_summary:
        findings.append(
            "Readout 4x4 mitigado: baseline "
            f"{readout_summary['baseline_mitigated_tvd']}, otimizado "
            f"{readout_summary['optimized_mitigated_tvd']}; vencedor "
            f"{readout_summary['winner']}."
        )
        if readout_summary["winner"] == "baseline":
            recommendations.append(
                {
                    "priority": "alta",
                    "action": "não promover o layout otimizado; usar baseline como referência",
                    "reason": "o layout otimizado não venceu após mitigação 4x4",
                }
            )

    q0 = _tomography_summary(tomography_q0)
    q1 = _tomography_summary(tomography_q1)
    for label, item in (("q0", q0), ("q1", q1)):
        if not item:
            continue
        coherence = item.get("coherence_prep_fidelity")
        coherence_text = (
            f"{coherence:.4f}" if coherence is not None else "n/d"
        )
        findings.append(
            f"{label}: prep mínima {item['min_prep_fidelity']:.4f} "
            f"({item['min_prep_state']}); prep coerente {coherence_text}; "
            f"r0={item['r0']}, r1={item['r1']}."
        )
        if item.get("prep_readout_redundant"):
            findings.append(
                f"{label}: prep |0>/|1> e r0/r1 são a mesma contagem Z; "
                "não são duas evidências independentes."
            )

    deltas = _comparison_summary(comparison)
    if q0 and q1:
        coherence0 = q0.get("coherence_prep_fidelity")
        coherence1 = q1.get("coherence_prep_fidelity")
        if (
            coherence0 is not None
            and coherence1 is not None
            and coherence1 < coherence0 - COHERENCE_DELTA_GATE
        ):
            recommendations.append(
                {
                    "priority": "alta",
                    "action": "investigar erro coerente de preparação em q1",
                    "reason": (
                        "prep coerente de q1 é menor que a de q0 por mais de "
                        f"{COHERENCE_DELTA_GATE}; essa medida não depende do readout"
                    ),
                }
            )
        elif coherence0 is not None and coherence1 is not None:
            findings.append(
                "q0 vs q1 em prep coerente: diferença dentro do gate de "
                f"{COHERENCE_DELTA_GATE}; não atribuir a q1."
            )

        r1_nonconclusive = _nonconclusive(deltas.get("r1") or {})
        if r1_nonconclusive:
            findings.append(
                "Δ r1 entre q1 e q0 é menor ou igual ao spread entre conjuntos "
                "e os ICs se sobrepõem; a diferença não é conclusiva."
            )
            recommendations.append(
                {
                    "priority": "média",
                    "action": (
                        "medir mais conjuntos para leitura em q1 antes de "
                        "atribuir a diferença de r1 a q1"
                    ),
                    "reason": (
                        "Δ r1 dentro do spread entre conjuntos; "
                        "bootstrap não captura drift"
                    ),
                }
            )
        elif (q1.get("r1") or 0) > (q0.get("r1") or 0):
            recommendations.append(
                {
                    "priority": "alta",
                    "action": "aplicar/expandir mitigação de leitura em q1",
                    "reason": "r1 de q1 é maior que o de q0 e a diferença supera o spread",
                }
            )

        max_r1 = max(
            value for value in (q0.get("r1"), q1.get("r1")) if value is not None
        ) if any(value is not None for value in (q0.get("r1"), q1.get("r1"))) else None
        if max_r1 is not None and max_r1 > READOUT_GATE:
            recommendations.append(
                {
                    "priority": "alta",
                    "action": (
                        "aplicar/expandir mitigação de leitura em q0 e q1 "
                        f"(r1 até {max_r1:.4f})"
                    ),
                    "reason": f"r1 acima do gate {READOUT_GATE}",
                }
            )

        gate_values = [
            value
            for value in (coherence0, coherence1)
            if value is not None
        ]
        if gate_values and min(gate_values) < LAYOUT_COHERENCE_GATE:
            recommendations.append(
                {
                    "priority": "alta",
                    "action": (
                        "não comparar layouts antes de preparação coerente "
                        f"≥ {LAYOUT_COHERENCE_GATE} em ambos os qubits"
                    ),
                    "reason": (
                        "diferenças de layout da ordem de 1% ficam abaixo do "
                        "erro de preparação coerente atual"
                    ),
                }
            )

    if zne:
        applicability = zne.get("applicability") or {}
        if applicability.get("applicable") is False:
            blocked.append(
                {
                    "technique": "ZNE",
                    "reason": applicability.get("reason", "curva não monotônica"),
                }
            )
            findings.append("ZNE bloqueado: curva não monotônica; extrapolação inválida.")

    if pec:
        gamma = pec.get("gamma_total")
        samples = pec.get("samples_required")
        findings.append(f"PEC: gamma={gamma}, amostras={samples}.")
        if samples is not None and float(samples) > 1_000_000:
            blocked.append(
                {
                    "technique": "PEC 2q",
                    "reason": "orçamento de amostragem > 1e6",
                }
            )

    widths = _uncertainty_widths(uncertainty)
    if widths:
        max_width = max(widths.values())
        findings.append(f"Incerteza bootstrap: maior largura de IC = {max_width:.4f}.")
        if max_width > 0.01:
            recommendations.append(
                {
                    "priority": "média",
                    "action": "aumentar repetições antes de concluir",
                    "reason": "largura de IC acima de 0,01",
                }
            )

    if surface:
        blocked.append(
            {
                "technique": "QEC de superfície",
                "reason": "sem decodificador em tempo real no Baihua",
            }
        )
    if pulse_dd:
        blocked.append(
            {
                "technique": "DD pulse-level",
                "reason": "API GJQ sem controle de pulso",
            }
        )

    prepared = q1 or q0
    coherence_ref = (
        prepared.get("coherence_prep_fidelity") if prepared else None
    )
    if blocked:
        status = "partial"
    elif (
        coherence_ref is not None
        and coherence_ref >= LAYOUT_COHERENCE_GATE
        and not recommendations
    ):
        status = "ready"
    else:
        status = "partial"

    return {
        "schema_version": 2,
        "status": status,
        "readout": readout_summary,
        "tomography": {"q0": q0, "q1": q1},
        "comparison": deltas,
        "uncertainty_widths": widths,
        "findings": findings,
        "recommendations": recommendations,
        "blocked": blocked,
        "limits": (
            "Scorecard heurístico e local; não é prova de vantagem quântica. "
            "Combina técnicas diferentes sem somar créditos indevidos. "
            "Prep |0>/|1> e r0/r1 são a mesma medida neste desenho."
        ),
    }
