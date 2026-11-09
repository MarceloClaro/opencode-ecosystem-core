#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scorecard híbrido de resiliência quântica (R1116).

Combina evidências de readout 4x4, tomografia SPAM, ZNE, PEC e incerteza para
recomendar a próxima técnica. Não executa hardware e não declara vantagem.
"""
from __future__ import annotations

from typing import Any


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
    return {
        "min_prep_fidelity": min(float(v) for v in fidelity.values()),
        "prep_fidelity": {k: float(v) for k, v in fidelity.items()},
        "r0": fit.get("readout_p1_given_prep0"),
        "r1": fit.get("readout_p0_given_prep1"),
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


def resilience_scorecard(
    *,
    readout: dict[str, Any] | None = None,
    zne: dict[str, Any] | None = None,
    tomography_q0: dict[str, Any] | None = None,
    tomography_q1: dict[str, Any] | None = None,
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
    if q0:
        findings.append(
            f"q0: fidelidade mínima de preparação {q0['min_prep_fidelity']:.4f}; "
            f"r0={q0['r0']}, r1={q0['r1']}."
        )
    if q1:
        findings.append(
            f"q1: fidelidade mínima de preparação {q1['min_prep_fidelity']:.4f}; "
            f"r0={q1['r0']}, r1={q1['r1']}."
        )
    if q0 and q1:
        if q1["min_prep_fidelity"] < q0["min_prep_fidelity"]:
            recommendations.append(
                {
                    "priority": "alta",
                    "action": "priorizar state preparation em q1",
                    "reason": "q1 tem fidelidade de preparação menor que q0",
                }
            )
        if (q1.get("r1") or 0) > (q0.get("r1") or 0):
            recommendations.append(
                {
                    "priority": "alta",
                    "action": "aplicar/expandir mitigação de leitura em q1",
                    "reason": "r1 de q1 é maior que o de q0",
                }
            )
    combined = q1 or q0
    if combined and combined["min_prep_fidelity"] < 0.95:
        recommendations.append(
            {
                "priority": "alta",
                "action": "não comparar layouts antes de melhorar state preparation",
                "reason": "fidelidade mínima de preparação abaixo de 0,95",
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
        findings.append(
            f"PEC: gamma={gamma}, amostras={samples}."
        )
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

    if blocked:
        status = "partial"
    elif combined and combined["min_prep_fidelity"] >= 0.98 and not recommendations:
        status = "ready"
    else:
        status = "partial"

    return {
        "schema_version": 1,
        "status": status,
        "readout": readout_summary,
        "tomography": {"q0": q0, "q1": q1},
        "uncertainty_widths": widths,
        "findings": findings,
        "recommendations": recommendations,
        "blocked": blocked,
        "limits": (
            "Scorecard heurístico e local; não é prova de vantagem quântica. "
            "Combina técnicas diferentes sem somar créditos indevidos."
        ),
    }
