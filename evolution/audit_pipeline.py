# -*- coding: utf-8 -*-
"""
Pipeline de Auditoria Contínua da Cadeia de Custódia (SPEC-935-R462+)
=====================================================================
Monitora a integridade do registro de evolução e a métrica de Custódia,
emitindo relatórios e alertas para integração contínua.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from evolution.audit_gate import EvolutionAuditGate
from evolution.cycles import EvolutionRegistry


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


@dataclass
class AuditAlert:
    level: str          # "info" | "warn" | "critical"
    code: str           # código de identificação
    message: str        # mensagem legível
    details: Dict[str, Any]


@dataclass
class AuditReport:
    timestamp: str
    registry_path: str
    total_cycles: int
    custody_global: Dict[str, Any]
    custody_recent: Dict[str, Any]
    integrity_checks: List[Dict[str, Any]]
    alerts: List[AuditAlert]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "registry_path": self.registry_path,
            "total_cycles": self.total_cycles,
            "custody_global": self.custody_global,
            "custody_recent": self.custody_recent,
            "integrity_checks": self.integrity_checks,
            "alerts": [asdict(a) for a in self.alerts],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_markdown(self) -> str:
        lines = []
        lines.append("# Relatório de Auditoria Contínua — Cadeia de Custódia")
        lines.append(f"\n**Gerado em:** {self.timestamp}")
        lines.append(f"**Registro:** {self.registry_path}")
        lines.append(f"**Total de ciclos:** {self.total_cycles}")
        lines.append("")
        lines.append("## Métricas de Custódia")
        lines.append("")
        g = self.custody_global
        r = self.custody_recent
        lines.append(f"- **Global:** {g['pct']}% ({g['audited']}/{g['total']}) · Âncoras: {g['anchored']} · Legados: {g['legacy']}")
        lines.append(f"- **Recente (R462+):** {r['pct']}% ({r['audited']}/{r['total']})")
        lines.append("")
        lines.append("## Verificações de Integridade")
        lines.append("")
        for ck in self.integrity_checks:
            status = "✅" if ck["passed"] else "❌"
            lines.append(f"- {status} {ck['name']}: {ck['detail']}")
        lines.append("")
        lines.append("## Alertas")
        lines.append("")
        if not self.alerts:
            lines.append("_(nenhum)_")
        else:
            for a in self.alerts:
                icon = {"info": "ℹ️", "warn": "⚠️", "critical": "🚨"}.get(a.level, "•")
                lines.append(f"- {icon} **[{a.code}]** {a.message}")
                if a.details:
                    lines.append(f"  - Detalhes: {a.details}")
        return "\n".join(lines)


class AuditPipeline:
    """Pipeline de auditoria contínua do registro de evolução."""

    # Thresholds configuráveis
    CUSTODY_RECENT_MIN_PCT = 80.0      # alerta se Custódia recente < 80%
    INTEGRITY_MAX_MISMATCH = 0         # tolerância zero para perda silenciosa
    ANCHOR_MIN_RECENT = 1              # mínimo de ciclos recentes com âncora merkle

    def __init__(
        self,
        registry_path: Optional[str] = None,
        custody_recent_min_pct: Optional[float] = None,
    ):
        self.registry_path = registry_path or os.environ.get(
            "EVOLUTION_STATE_PATH",
            os.path.join(os.path.dirname(__file__), "cycles.json"),
        )
        self.custody_recent_min_pct = (
            custody_recent_min_pct
            if custody_recent_min_pct is not None
            else self.CUSTODY_RECENT_MIN_PCT
        )
        self.registry = EvolutionRegistry(self.registry_path)
        self.gate = EvolutionAuditGate()

    def run(self) -> AuditReport:
        """Executa o pipeline completo e retorna o relatório."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1) Métricas de Custódia
        custody_global = self.registry.custody_metric()
        custody_recent = self.registry.custody_recent("R462")

        # 2) Verificações de integridade estrutural
        integrity_checks = self._run_integrity_checks()

        # 3) Gerar alertas baseados em thresholds
        alerts = self._generate_alerts(custody_global, custody_recent, integrity_checks)

        return AuditReport(
            timestamp=now,
            registry_path=self.registry_path,
            total_cycles=len(self.registry.cycles),
            custody_global=custody_global,
            custody_recent=custody_recent,
            integrity_checks=integrity_checks,
            alerts=alerts,
        )

    def _run_integrity_checks(self) -> List[Dict[str, Any]]:
        """Verifica integridade estrutural do registro."""
        checks = []

        # (a) Carregamento completo — sem perda silenciosa
        raw_count = 0
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    raw_count = len(json.load(f).get("cycles", []))
            except Exception as exc:
                checks.append({
                    "name": "raw_json_readable",
                    "passed": False,
                    "detail": f"Falha ao ler JSON bruto: {exc}",
                })
        loaded_count = len(self.registry.cycles)
        checks.append({
            "name": "no_silent_loss",
            "passed": loaded_count == raw_count,
            "detail": f"Carregados {loaded_count}/{raw_count} ciclos",
        })

        # (b) Âncoras merkle em ciclos recentes (R462+)
        recent = [c for c in self.registry.cycles
                  if self.registry._round_num(c.round_id) >= 462]
        anchored_recent = sum(1 for c in recent if c.merkle_root)
        checks.append({
            "name": "anchors_recent",
            "passed": anchored_recent >= self.ANCHOR_MIN_RECENT,
            "detail": f"{anchored_recent}/{len(recent)} ciclos recentes com merkle_root",
        })

        # (c) Verificação de tamper nos ciclos auditados
        tampered = 0
        for c in self.registry.cycles:
            if c.audited and c.artifact_hashes and c.external_verdict:
                if c.external_verdict.get("tampered") is True:
                    tampered += 1
        checks.append({
            "name": "tamper_free",
            "passed": tampered == 0,
            "detail": f"{tampered} ciclo(s) auditado(s) marcado(s) como tampered",
        })

        # (d) Verificação de âncoras compostas (merkle_root == gate.merkle_root(hashes))
        merkle_mismatch = 0
        for c in self.registry.cycles:
            if c.audited and c.merkle_root and c.artifact_hashes:
                computed = self.gate.merkle_root(c.artifact_hashes)
                if computed != c.merkle_root:
                    merkle_mismatch += 1
        checks.append({
            "name": "merkle_consistency",
            "passed": merkle_mismatch == 0,
            "detail": f"{merkle_mismatch} ciclo(s) com merkle_root inconsistente",
        })

        # (e) origin_commit válido (hash git 40 hex) onde presente
        invalid_commits = 0
        for c in self.registry.cycles:
            if c.origin_commit and (len(c.origin_commit) != 40 or not all(ch in "0123456789abcdef" for ch in c.origin_commit)):
                invalid_commits += 1
        checks.append({
            "name": "origin_commit_valid",
            "passed": invalid_commits == 0,
            "detail": f"{invalid_commits} ciclo(s) com origin_commit inválido",
        })

        return checks

    def _generate_alerts(
        self,
        custody_global: Dict[str, Any],
        custody_recent: Dict[str, Any],
        integrity_checks: List[Dict[str, Any]],
    ) -> List[AuditAlert]:
        """Gera alertas baseados em thresholds."""
        alerts = []

        # Alerta: Custódia recente abaixo do threshold
        if custody_recent["pct"] < self.custody_recent_min_pct:
            alerts.append(AuditAlert(
                level="critical",
                code="CUSTODY_RECENT_LOW",
                message=f"Custódia recente ({custody_recent['pct']}%) abaixo do mínimo ({self.custody_recent_min_pct}%)",
                details={"current_pct": custody_recent["pct"], "threshold": self.custody_recent_min_pct},
            ))

        # Alerta: Integridade comprometida
        for ck in integrity_checks:
            if not ck["passed"]:
                level = "critical" if ck["name"] in ("no_silent_loss", "merkle_consistency", "tamper_free") else "warn"
                alerts.append(AuditAlert(
                    level=level,
                    code=f"INTEGRITY_{ck['name'].upper()}",
                    message=f"Falha na verificação: {ck['name']}",
                    details={"check": ck},
                ))

        # Info: Custódia global baixa (esperado enquanto houver muitos legados)
        if custody_global["pct"] < 5.0 and custody_global["legacy"] > 100:
            alerts.append(AuditAlert(
                level="info",
                code="CUSTODY_GLOBAL_LEGACY_DOMINANT",
                message="Custódia global baixa — dominada por ciclos legados não reescritos (não é erro)",
                details={"global_pct": custody_global["pct"], "legacy_count": custody_global["legacy"]},
            ))

        # Info: Nenhum ciclo auditado
        if custody_global["audited"] == 0:
            alerts.append(AuditAlert(
                level="warn",
                code="NO_AUDITED_CYCLES",
                message="Nenhum ciclo auditado no registro",
                details={"total": custody_global["total"]},
            ))

        return alerts

    def write_report(self, out_path: str, fmt: str = "json") -> str:
        """Executa o pipeline e grava relatório (json|md)."""
        report = self.run()
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if fmt == "md":
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report.to_markdown())
        else:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report.to_json())
        return out_path

    def cli_exit_code(self) -> int:
        """Retorna código de saída para uso em CI/CD: 0=OK, 1=warn, 2=critical."""
        report = self.run()
        has_critical = any(a.level == "critical" for a in report.alerts)
        has_warn = any(a.level == "warn" for a in report.alerts)
        if has_critical:
            return 2
        if has_warn:
            return 1
        return 0


def main() -> int:
    """Entry point CLI: python -m evolution.audit_pipeline [--json|--md] [out]"""
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline de Auditoria Contínua — Cadeia de Custódia")
    parser.add_argument("--json", dest="fmt", action="store_const", const="json", default="json",
                        help="Saída JSON (padrão)")
    parser.add_argument("--md", dest="fmt", action="store_const", const="md",
                        help="Saída Markdown")
    parser.add_argument("out", nargs="?", default=None,
                        help="Caminho do arquivo de saída (padrão: stdout)")
    parser.add_argument("--custody-min", type=float, default=None,
                        help="Threshold minimo Custodia recente (default 80%%)")
    args = parser.parse_args()

    pipeline = AuditPipeline(custody_recent_min_pct=args.custody_min)
    report = pipeline.run()

    if args.out:
        pipeline.write_report(args.out, args.fmt)
        print(f"Relatório gravado em {args.out} ({args.fmt})", file=sys.stderr)
    else:
        if args.fmt == "md":
            print(report.to_markdown())
        else:
            print(report.to_json())

    return pipeline.cli_exit_code()


if __name__ == "__main__":
    sys.exit(main())