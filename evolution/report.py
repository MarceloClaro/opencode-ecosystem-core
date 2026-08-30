# -*- coding: utf-8 -*-
"""
EvolutionReport — Relatório de Evolução Auditável (SPEC-935-R462)
=================================================================
Gera um relatório Markdown (e, se um conversor estiver disponível, PDF) que
exibe, por ciclo de evolução, a CADEIA DE CUSTÓDIA: hashes de artefato,
veredito externo, identidade do verificador e trilha de evidência.

O relatório torna visível e auditável a distinção entre:
  - ciclos AUDITADOS (passaram no EvolutionAuditGate, gerador!=julgador, hash);
  - ciclos LEGADOS (pré-R462, sem auditoria formal — NÃO reescritos).
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from evolution.audit_gate import EvolutionAuditGate
from evolution.cycles import EvolutionRegistry


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )


class EvolutionReport:
    """Compila e renderiza o relatório de custódia auditável."""

    def __init__(self, registry: EvolutionRegistry,
                 gate: EvolutionAuditGate | None = None):
        self.registry = registry
        self.gate = gate or EvolutionAuditGate()

    def to_markdown(self, limit: int = 20) -> str:
        g = self.registry.custody_metric()
        r = self.registry.custody_recent()
        lines: List[str] = []
        lines.append("# Relatório de Evolução Auditável — R462")
        lines.append("")
        lines.append("> **SPEC-935-R462** · Cadeia de Custódia Auditável · "
                     "Gerado em " + _iso(__import__("time").time()) + "")
        lines.append("")
        lines.append("## Métricas de Custódia")
        lines.append("")
        lines.append("| Métrica | Valor |")
        lines.append("|---|---|")
        lines.append(f"| Custódia global | **{g['pct']}%** "
                     f"({g['audited']}/{g['total']} ciclos) |")
        lines.append(f"| Custódia recente (R462+) | **{r['pct']}%** "
                     f"({r['audited']}/{r['total']}) |")
        lines.append(f"| Rejeitados pelo gate | {g['rejected']} |")
        lines.append(f"| Tamper detectado | {g['tampered']} |")
        lines.append(f"| Ciclos legados (pré-R462, não reescritos) | {g['legacy']} |")
        lines.append("")
        lines.append("## Detalhe por ciclo (últimos %d)" % limit)
        lines.append("")
        lines.append("| Ciclo | Auditado | Verificador | Hash | Veredito |")
        lines.append("|---|---|---|---|---|")
        for c in self.registry.cycles[-limit:]:
            aud = "Sim" if c.audited else ("Legacy" if c.legacy else "Não")
            verif = c.verifier_identity or "—"
            n_hash = len(c.artifact_hashes)
            ok = (c.external_verdict or {}).get("passed")
            verdict = "APROVADO" if ok is True else ("Reprovado" if ok is False else "—")
            lines.append(
                f"| {c.round_id} | {aud} | {verif} | {n_hash} | {verdict} |"
            )
        lines.append("")
        lines.append("## Anti-Tamper (SHA-256 ancorado)")
        lines.append("")
        lines.append(
            "Cada artefato é ancorado por hash SHA-256 no momento da "
            "produção. Alterações posteriores são detectáveis via "
            "`EvolutionAuditGate.verify_tamper()`. O hash prova **ausência de "
            "alteração**, não **correção** do conteúdo."
        )
        return "\n".join(lines)

    def write(self, out_path: str, limit: int = 20) -> str:
        md = self.to_markdown(limit)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        return out_path


def generate_default(path: str | None = None) -> str:
    """Gera o relatório auditável para o registro real (default paths)."""
    reg = EvolutionRegistry()
    gate = EvolutionAuditGate()
    report = EvolutionReport(reg, gate)
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "evolution_audit_report.md",
        )
    return report.write(path)
