# -*- coding: utf-8 -*-
"""
EvolutionAuditGate — Cadeia de Custódia Auditável (SPEC-935-R462)
================================================================
Fecha o gargalo "produzir IA com IA" (R461) impondo tres condicoes por ciclo:

  (i)   imutabilidade  : cada artefato tem hash SHA-256 registrado no momento
                         da producao (anti-tamper);
  (ii)  verificacao    : todo ciclo precisa de um `external_verdict` aprovado
                         por uma instancia DISTINTA do gerador (quebra
                         gerador=julgador);
  (iii) rastreabilidade: trilha de evidencia (spec, testes, scans) sustenta
                         cada alegacao.

Fail-closed: a verificacao so passa se TODAS as condicoes forem satisfeitas.
Se `verifier_identity == generator_identity`, o ciclo e rejeitado.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


@dataclass
class AuditResult:
    passed: bool = False
    reason: str = ""
    tampered: bool = False
    hashes: Dict[str, str] = field(default_factory=dict)
    verifier: str = ""


class EvolutionAuditGate:
    """Gate fail-closed de auditoria externa sobre um ciclo de evolucao."""

    def _sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def verify_cycle(
        self,
        *,
        objective: str,
        changes: List[str],
        artifact_files: Mapping[str, bytes],
        verifier_identity: str,
        generator_identity: str,
        evidence_trail: Optional[List[str]] = None,
    ) -> AuditResult:
        """Valida um ciclo antes da persistencia. Fail-closed: recusa se
        qualquer condicao de custodio falhar."""
        # (ii) verificacao externa: gerador != verificador
        if not verifier_identity:
            return AuditResult(passed=False,
                               reason="sem identidade de verificador externo")
        if verifier_identity == generator_identity:
            return AuditResult(
                passed=False,
                reason="verificador == gerador: viola condicao (ii) "
                       "(gerador nao pode julgar a si mesmo)",
            )
        if not artifact_files:
            return AuditResult(passed=False,
                               reason="sem artefatos para ancorar hash")

        # (i) calcular hashes SHA-256
        hashes = {name: self._sha256(data) for name, data in artifact_files.items()}
        # (iii) trilha de evidencia
        if not evidence_trail:
            return AuditResult(
                passed=False,
                reason="sem trilha de evidencia (spec/teste/scan) que sustente "
                       "as mudancas",
                tampered=False, hashes=hashes, verifier=verifier_identity,
            )
        return AuditResult(
            passed=True,
            reason="auditoria externa aprovada",
            tampered=False, hashes=hashes, verifier=verifier_identity,
        )

    def verify_tamper(
        self,
        *,
        artifact_files: Mapping[str, bytes],
        registered_hashes: Mapping[str, str],
    ) -> AuditResult:
        """Compara os hashes reais com os registrados. Se divergem =>
        tampered=True (imutabilidade violada)."""
        real = {name: self._sha256(data) for name, data in artifact_files.items()}
        mismatches = [
            name for name in real
            if name not in registered_hashes
            or registered_hashes[name] != real[name]
        ]
        if mismatches:
            return AuditResult(
                passed=False,
                tampered=True,
                reason=f"tamper detectado em: {', '.join(mismatches)}",
                hashes=real,
            )
        return AuditResult(
            passed=True,
            tampered=False,
            reason="hashes conferem, sem tamper",
            hashes=real,
        )
