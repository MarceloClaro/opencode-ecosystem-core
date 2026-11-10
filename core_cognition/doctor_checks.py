# -*- coding: utf-8 -*-
"""Checks de cognição para o doctor (SPEC-935-R1132).

Três checks estruturais: mapa de funções cognitivas, risco epistêmico e
contestabilidade/saída. Retornam objetos simples para evitar import circular
com ``marceloclaro.doctor``.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import cognitive_function_map, contestability, epistemic_risk


@dataclass(frozen=True)
class CognitionCheck:
    name: str
    status: str
    detail: str


def _root(repo_root: str | Path | None) -> Path:
    if repo_root is not None:
        return Path(repo_root)
    return Path(__file__).resolve().parents[1]


def run_cognition_checks(repo_root: str | Path | None = None) -> list[CognitionCheck]:
    root = _root(repo_root)
    checks: list[CognitionCheck] = []

    try:
        report = cognitive_function_map.audit(root)
        detail = (
            f"{report['total']} funções mapeadas; "
            f"faltantes={report['missing_functions']}; "
            f"módulos ausentes={report['missing_modules']}."
        )
        checks.append(CognitionCheck("cognitive_function_map", report["status"], detail))
    except Exception as exc:  # pragma: no cover - defensive
        checks.append(
            CognitionCheck(
                "cognitive_function_map",
                "warn",
                f"Mapa cognitivo indisponível: {type(exc).__name__}.",
            )
        )

    try:
        report = epistemic_risk.audit_repository(root)
        checks.append(
            CognitionCheck(
                "epistemic_risk",
                report["status"],
                f"{report['counts']}; achados={len(report['findings'])}.",
            )
        )
    except Exception as exc:  # pragma: no cover - defensive
        checks.append(
            CognitionCheck(
                "epistemic_risk",
                "warn",
                f"Auditoria de risco indisponível: {type(exc).__name__}.",
            )
        )

    try:
        report = contestability.audit(root)
        status = "pass" if report.score >= 0.8 else "warn"
        checks.append(
            CognitionCheck(
                "contestability",
                status,
                f"score={report.score}; lacunas={report.gaps}.",
            )
        )
    except Exception as exc:  # pragma: no cover - defensive
        checks.append(
            CognitionCheck(
                "contestability",
                "warn",
                f"Auditoria de contestabilidade indisponível: {type(exc).__name__}.",
            )
        )

    return checks
