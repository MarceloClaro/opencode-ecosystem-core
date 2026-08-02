# -*- coding: utf-8 -*-
"""Triangulação Multidisciplinar — gate de convergência entre domínios.

Uma alegação só é tratada como bem sustentada quando ≥2 domínios/
disciplinas independentes trazem evidência concordante e NENHUM domínio a
contesta. Design deliberadamente aditivo: não modifica EvidenceGraph (R102)
nem DataKnowledgeHub (R52/R55) — o contrato de entrada é uma lista simples
de itens de evidência que qualquer chamador pode popular.

Limite epistêmico: triangulação não decide verdade — decide se a alegação
tem corroboração estruturalmente independente. Discordância real entre
disciplinas nunca é resolvida por maioria de votos: um único domínio
contestando bloqueia a triangulação.

Domínios sugeridos (texto livre, não um enum fechado): os 5 já existentes
no DataKnowledgeHub (financeiro, oficial, conhecimento, dataset, academico)
mais disciplinas acadêmicas quando a evidência vier de literatura
(medicina, direito, ciencia_dados, ...).

SPEC-935-R371.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List

SCHEMA_VERSION = "1.0.0"

_VALID_STANCES = frozenset({"supports", "contradicts", "neutral"})

DISCLAIMER = (
    "Triangulação não decide verdade — decide se a alegação tem corroboração "
    "estruturalmente independente entre domínios. Contestação de qualquer "
    "domínio bloqueia a triangulação (nunca resolvida por maioria de votos). "
    "Interpretação final é sempre humana."
)


class ContractError(ValueError):
    """Entrada fora do contrato — falha fechada."""


def _normalize_domain(domain: str) -> str:
    return domain.strip().casefold()


def _validate_items(evidence_items: List[Any]) -> List[Dict[str, str]]:
    validated: List[Dict[str, str]] = []
    for i, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            raise ContractError(f"evidence_items[{i}] deve ser um dict.")
        source = item.get("source")
        domain = item.get("domain")
        stance = item.get("stance")
        if not isinstance(source, str) or not source.strip():
            raise ContractError(f"evidence_items[{i}].source deve ser texto não vazio.")
        if not isinstance(domain, str) or not domain.strip():
            raise ContractError(f"evidence_items[{i}].domain deve ser texto não vazio.")
        if stance not in _VALID_STANCES:
            raise ContractError(
                f"evidence_items[{i}].stance inválido: {stance!r} "
                f"(deve ser um de {sorted(_VALID_STANCES)})."
            )
        validated.append({
            "source": source.strip(),
            "domain": _normalize_domain(domain),
            "stance": stance,
        })
    return validated


def _domain_verdict(stances: List[str]) -> str:
    has_supports = "supports" in stances
    has_contradicts = "contradicts" in stances
    if has_supports and has_contradicts:
        return "mixed"
    if has_supports:
        return "supports"
    if has_contradicts:
        return "contradicts"
    return "neutral"


def _finding(code: str, severity: str, detail: str) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "code": code,
        "severity": severity,
        "detail": detail,
        "requires_human_review": True,
    }


def multidisciplinary_triangulation(
    claim_text: str, evidence_items: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Gate de triangulação multidisciplinar. Função pura, determinística."""
    claim_display = str(claim_text)[:200]

    if not evidence_items:
        return {
            "schema_version": SCHEMA_VERSION,
            "claim_text": claim_display,
            "analysis_status": "insufficient_context",
            "triangulated": False,
            "supporting_domains": [],
            "contesting_domains": [],
            "domain_verdicts": {},
            "findings": [],
            "human_gate": "recommended",
            "disclaimer": DISCLAIMER,
        }

    validated = _validate_items(evidence_items)

    by_domain: Dict[str, List[str]] = {}
    for item in validated:
        by_domain.setdefault(item["domain"], []).append(item["stance"])

    domain_verdicts = {
        domain: _domain_verdict(stances) for domain, stances in by_domain.items()
    }

    supporting_domains = sorted(
        d for d, v in domain_verdicts.items() if v == "supports"
    )
    contesting_domains = sorted(
        d for d, v in domain_verdicts.items() if v in ("contradicts", "mixed")
    )

    triangulated = len(contesting_domains) == 0 and len(supporting_domains) >= 2

    findings: List[Dict[str, Any]] = []
    for domain in contesting_domains:
        findings.append(_finding(
            "CONTESTED_MULTIDISCIPLINARY", "high",
            f"domínio {domain!r} contesta a alegação (veredito: "
            f"{domain_verdicts[domain]}) — controvérsia real, não resolvida "
            f"por maioria",
        ))
    if not contesting_domains and len(supporting_domains) < 2:
        findings.append(_finding(
            "SINGLE_DOMAIN_EVIDENCE", "medium",
            f"apenas {len(supporting_domains)} domínio(s) favorável(is) "
            f"({', '.join(supporting_domains) or 'nenhum'}) — corroboração "
            f"multidisciplinar exige >= 2 domínios independentes",
        ))

    high = any(f["severity"] == "high" for f in findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "claim_text": claim_display,
        "analysis_status": "complete",
        "triangulated": triangulated,
        "supporting_domains": supporting_domains,
        "contesting_domains": contesting_domains,
        "domain_verdicts": domain_verdicts,
        "findings": findings,
        "human_gate": "required" if high else "recommended",
        "disclaimer": DISCLAIMER,
    }
