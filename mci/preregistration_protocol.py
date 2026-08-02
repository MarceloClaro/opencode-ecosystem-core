# -*- coding: utf-8 -*-
"""Protocolo de Pré-registro — declaração prévia + verificação de desvio.

Registra hipótese, método, critério de falsificação e alpha ANTES da
análise, e depois verifica se o que foi efetivamente usado bate com o
declarado. Não impede que alguém minta ao registrar (não há autoridade
externa de timestamp aqui) — impede a forma mais comum de p-hacking:
mudar silenciosamente hipótese/método/alpha depois de ver os dados
(HARKing). A comparação é textual exata (normalizada por case/espaços),
porque reformulação "só de forma" é como HARKing se disfarça.

SPEC-935-R372.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
import unicodedata
from typing import Any, Dict

SCHEMA_VERSION = "1.0.0"

DISCLAIMER = (
    "Verificação de pré-registro compara o que foi declarado ANTES da "
    "análise contra o que foi efetivamente usado. Não prova ausência de "
    "má-fé no registro — protege contra mudança silenciosa de hipótese, "
    "método ou alpha após ver os dados (HARKing). Interpretação final é "
    "sempre humana."
)


class ContractError(ValueError):
    """Entrada fora do contrato — falha fechada."""


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", str(text).casefold().strip())
    return " ".join(
        "".join(c for c in decomposed if not unicodedata.combining(c)).split()
    )


def _non_empty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} deve ser texto não vazio.")
    return value.strip()


def register_protocol(
    hypothesis: str, method: str, falsification_criterion: str, alpha: float = 0.05
) -> Dict[str, Any]:
    """Registra um protocolo ANTES da análise. protocol_id é determinístico
    (hash do conteúdo normalizado); registered_at é timestamp real."""
    hypothesis = _non_empty_text(hypothesis, "hypothesis")
    method = _non_empty_text(method, "method")
    falsification_criterion = _non_empty_text(
        falsification_criterion, "falsification_criterion"
    )
    if not isinstance(alpha, (int, float)) or not (0.0 < alpha < 1.0):
        raise ContractError("alpha deve estar em (0, 1).")

    canonical = {
        "hypothesis_norm": _normalize(hypothesis),
        "method_norm": _normalize(method),
        "falsification_criterion_norm": _normalize(falsification_criterion),
        "alpha": round(float(alpha), 6),
    }
    digest = hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:24]

    return {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": f"prereg-{digest}",
        "hypothesis": hypothesis,
        "method": method,
        "falsification_criterion": falsification_criterion,
        "alpha": float(alpha),
        "registered_at": time.time(),
    }


def _finding(field: str, declared: Any, actual: Any) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "code": "PROTOCOL_DEVIATION",
        "severity": "high",
        "detail": (
            f"campo {field!r} divergente: declarado={declared!r}, "
            f"efetivo={actual!r}"
        ),
        "requires_human_review": True,
    }


def verify_protocol(
    protocol: Dict[str, Any],
    actual_hypothesis: str,
    actual_method: str,
    actual_alpha: float,
) -> Dict[str, Any]:
    """Compara o protocolo declarado contra o que foi efetivamente usado."""
    if not isinstance(protocol, dict) or "protocol_id" not in protocol:
        raise ContractError("protocol inválido: precisa vir de register_protocol().")

    findings = []
    if _normalize(protocol["hypothesis"]) != _normalize(actual_hypothesis):
        findings.append(_finding("hypothesis", protocol["hypothesis"], actual_hypothesis))
    if _normalize(protocol["method"]) != _normalize(actual_method):
        findings.append(_finding("method", protocol["method"], actual_method))
    if abs(float(protocol["alpha"]) - float(actual_alpha)) >= 1e-9:
        findings.append(_finding("alpha", protocol["alpha"], actual_alpha))

    honored = len(findings) == 0
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": protocol["protocol_id"],
        "honored": honored,
        "findings": findings,
        "human_gate": "required" if findings else "recommended",
        "disclaimer": DISCLAIMER,
    }
