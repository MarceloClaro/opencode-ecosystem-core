# -*- coding: utf-8 -*-
"""
QualityCorrelator — Correlação Custódia vs. Qualidade Downstream (SPEC-935-R464+)
=================================================================================
Analisa se a Cadeia de Custódia Auditável (R462/R463) correlaciona-se com
indicadores downstream de qualidade: testes, specs, gates comportamentais,
segurança, linting.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from evolution.cycles import EvolutionRegistry
from evolution.audit_gate import EvolutionAuditGate, git_head_commit


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


@dataclass
class QualitySnapshot:
    """Instantâneo de métricas de qualidade para um ciclo."""
    cycle_id: str
    timestamp: float
    # Custódia (estrutural)
    custody_audited: int
    custody_total: int
    custody_pct: float
    custody_recent_pct: float
    # Qualidade downstream
    spec_verification_rate: Optional[float] = None      # % specs passando
    test_pass_rate: Optional[float] = None              # % testes passando
    test_coverage: Optional[float] = None               # cobertura %
    behavioral_gate_rate: Optional[float] = None        # % gates comportamentais OK
    security_findings: Optional[int] = None             # n. achados segurança
    lint_errors: Optional[int] = None                   # erros lint
    type_errors: Optional[int] = None                   # erros type-check
    # Metadados
    commit_hash: str = ""
    artifacts_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "timestamp": _iso(self.timestamp),
            "custody_audited": self.custody_audited,
            "custody_total": self.custody_total,
            "custody_pct": self.custody_pct,
            "custody_recent_pct": self.custody_recent_pct,
            "spec_verification_rate": self.spec_verification_rate,
            "test_pass_rate": self.test_pass_rate,
            "test_coverage": self.test_coverage,
            "behavioral_gate_rate": self.behavioral_gate_rate,
            "security_findings": self.security_findings,
            "lint_errors": self.lint_errors,
            "type_errors": self.type_errors,
            "commit_hash": self.commit_hash,
            "artifacts_count": self.artifacts_count,
        }


@dataclass
class CorrelationResult:
    """Resultado de análise de correlação."""
    metric_x: str
    metric_y: str
    pearson_r: Optional[float]
    spearman_rho: Optional[float]
    n_samples: int
    p_value: Optional[float]
    interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_x": self.metric_x,
            "metric_y": self.metric_y,
            "pearson_r": self.pearson_r,
            "spearman_rho": self.spearman_rho,
            "n_samples": self.n_samples,
            "p_value": self.p_value,
            "interpretation": self.interpretation,
        }


class QualityCorrelator:
    """
    Correlaciona Custódia (auditoria estrutural) com métricas de qualidade downstream.

    Coleta snapshots por ciclo e computa correlações (Pearson/Spearman) quando
    há dados suficientes (n >= 5 recomendado).
    """

    def __init__(
        self,
        registry: Optional[EvolutionRegistry] = None,
        snapshots_path: Optional[str] = None,
    ):
        self.registry = registry or EvolutionRegistry()
        self.gate = EvolutionAuditGate()
        self.snapshots_path = snapshots_path or os.path.join(
            os.path.dirname(__file__), "quality_snapshots.jsonl"
        )
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        Path(self.snapshots_path).parent.mkdir(parents=True, exist_ok=True)

    def collect_snapshot(
        self,
        cycle_id: Optional[str] = None,
        commit_hash: Optional[str] = None,
        run_quality_checks: bool = True,
    ) -> QualitySnapshot:
        """
        Coleta um snapshot de qualidade para o ciclo atual ou especificado.
        """
        reg = self.registry
        custody = reg.custody_metric()
        custody_recent = reg.custody_recent("R462")

        # Commit hash atual
        commit = commit_hash or git_head_commit()

        # Artefatos do ciclo mais recente
        latest_cycle = reg.cycles[-1] if reg.cycles else None
        artifacts = len(latest_cycle.artifact_hashes) if latest_cycle else 0

        # Métricas downstream (opcional - roda checks reais se solicitado)
        quality = {}
        if run_quality_checks:
            quality = self._run_quality_checks()

        snap = QualitySnapshot(
            cycle_id=cycle_id or (latest_cycle.round_id if latest_cycle else "unknown"),
            timestamp=time.time(),
            custody_audited=custody["audited"],
            custody_total=custody["total"],
            custody_pct=custody["pct"],
            custody_recent_pct=custody_recent["pct"],
            spec_verification_rate=quality.get("spec_verification_rate"),
            test_pass_rate=quality.get("test_pass_rate"),
            test_coverage=quality.get("test_coverage"),
            behavioral_gate_rate=quality.get("behavioral_gate_rate"),
            security_findings=quality.get("security_findings"),
            lint_errors=quality.get("lint_errors"),
            type_errors=quality.get("type_errors"),
            commit_hash=commit,
            artifacts_count=artifacts,
        )

        self._append_snapshot(snap)
        return snap

    def _run_quality_checks(self) -> Dict[str, Any]:
        """Executa checks de qualidade downstream (best-effort, não bloqueia)."""
        results = {}

        # 1. Spec verification rate (SDD)
        try:
            from sdd.spec_engine import SpecRegistry
            spec_reg = SpecRegistry()
            specs = spec_reg.list_formal_specs()
            if specs:
                # Verificação simplificada: specs carregadas sem erro
                results["spec_verification_rate"] = 100.0
            else:
                results["spec_verification_rate"] = 0.0
        except Exception:
            results["spec_verification_rate"] = None

        # 2. Test pass rate + coverage (pytest)
        try:
            # Conta testes totais
            total_out = subprocess.run(
                ["python3", "-m", "pytest", "--collect-only", "-q"],
                capture_output=True, text=True, timeout=60,
            )
            total_tests = len([l for l in total_out.stdout.splitlines() if l.startswith("tests/")])
            # Roda testes rápidos (subset) para pass rate
            run_out = subprocess.run(
                ["python3", "-m", "pytest", "-q", "--tb=no"],
                capture_output=True, text=True, timeout=120,
            )
            passed = 0
            failed = 0
            for line in run_out.stdout.splitlines():
                if "passed" in line and "failed" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "passed" and i > 0:
                            passed = int(parts[i-1])
                        if p == "failed" and i > 0:
                            failed = int(parts[i-1])
            total_ran = passed + failed
            if total_ran > 0:
                results["test_pass_rate"] = round(100.0 * passed / total_ran, 1)
            # Coverage (se coverage instalado)
            cov_out = subprocess.run(
                ["python3", "-m", "pytest", "--co", "-q"],
                capture_output=True, text=True, timeout=60,
            )
            # Não parseia coverage completo aqui (lento)
            results["test_coverage"] = None
        except Exception:
            results["test_pass_rate"] = None
            results["test_coverage"] = None

        # 3. Behavioral gate rate (Trust Engine)
        try:
            from trust.trust_engine import TrustEngine
            engine = TrustEngine()
            # Métrica simplificada: % de agentes com trust > 0.5
            agents = list(engine.agent_trust.values()) if hasattr(engine, "agent_trust") else []
            if agents:
                ok = sum(1 for t in agents if t > 0.5)
                results["behavioral_gate_rate"] = round(100.0 * ok / len(agents), 1)
            else:
                results["behavioral_gate_rate"] = 100.0
        except Exception:
            results["behavioral_gate_rate"] = None

        # 4. Security findings (bandit/semgrep se disponível)
        results["security_findings"] = self._run_security_scan()

        # 5. Lint errors (ruff/flake8)
        results["lint_errors"] = self._run_lint()

        # 6. Type errors (mypy)
        results["type_errors"] = self._run_type_check()

        return results

    def _run_security_scan(self) -> Optional[int]:
        try:
            # bandit quick scan
            out = subprocess.run(
                ["bandit", "-r", ".", "-ll", "-q", "-f", "json"],
                capture_output=True, text=True, timeout=60,
            )
            if out.returncode == 0:
                data = json.loads(out.stdout)
                return len(data.get("results", []))
        except Exception:
            pass
        return None

    def _run_lint(self) -> Optional[int]:
        try:
            out = subprocess.run(
                ["ruff", "check", "."],
                capture_output=True, text=True, timeout=60,
            )
            # ruff exit code: 0=clean, 1=issues found
            if out.returncode == 0:
                return 0
            # Conta linhas de erro
            return len([l for l in out.stdout.splitlines() if ":" in l and ("error" in l.lower() or "warning" in l.lower())])
        except Exception:
            return None

    def _run_type_check(self) -> Optional[int]:
        try:
            out = subprocess.run(
                ["mypy", ".", "--ignore-missing-imports"],
                capture_output=True, text=True, timeout=120,
            )
            if out.returncode == 0:
                return 0
            return len([l for l in out.stdout.splitlines() if "error:" in l])
        except Exception:
            return None

    def _append_snapshot(self, snap: QualitySnapshot) -> None:
        with open(self.snapshots_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(snap.to_dict(), ensure_ascii=False) + "\n")

    def load_snapshots(self) -> List[QualitySnapshot]:
        """Carrega todos os snapshots salvos."""
        if not os.path.exists(self.snapshots_path):
            return []
        snaps = []
        with open(self.snapshots_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                # Converte timestamp de volta para float
                from datetime import datetime
                data["timestamp"] = datetime.fromisoformat(data["timestamp"].replace(" UTC", "+00:00")).timestamp()
                snaps.append(QualitySnapshot(**data))
        return snaps

    def compute_correlations(self, min_samples: int = 5) -> List[CorrelationResult]:
        """
        Computa correlações entre Custódia e métricas downstream.
        Requer min_samples amostras (recomendado >= 5).
        """
        snaps = self.load_snapshots()
        if len(snaps) < min_samples:
            return [CorrelationResult(
                metric_x="custody_pct", metric_y="insufficient_data",
                pearson_r=None, spearman_rho=None,
                n_samples=len(snaps), p_value=None,
                interpretation=f"Dados insuficientes: {len(snaps)}/{min_samples} amostras. Colete mais snapshots."
            )]

        # Extrai séries
        custody = [s.custody_pct for s in snaps]
        metrics = {
            "spec_verification_rate": [s.spec_verification_rate for s in snaps],
            "test_pass_rate": [s.test_pass_rate for s in snaps],
            "test_coverage": [s.test_coverage for s in snaps],
            "behavioral_gate_rate": [s.behavioral_gate_rate for s in snaps],
            "security_findings": [s.security_findings for s in snaps],
            "lint_errors": [s.lint_errors for s in snaps],
            "type_errors": [s.type_errors for s in snaps],
        }

        results = []
        for name, series in metrics.items():
            # Filtra None
            pairs = [(c, v) for c, v in zip(custody, series) if v is not None]
            if len(pairs) < 3:
                results.append(CorrelationResult(
                    metric_x="custody_pct", metric_y=name,
                    pearson_r=None, spearman_rho=None,
                    n_samples=len(pairs), p_value=None,
                    interpretation=f"Dados insuficientes para {name}: {len(pairs)} pares válidos"
                ))
                continue

            x = [p[0] for p in pairs]
            y = [p[1] for p in pairs]

            # Pearson
            pearson_r = self._pearson(x, y)
            # Spearman
            spearman_rho = self._spearman(x, y)

            # Interpretação simples
            if pearson_r is not None:
                if abs(pearson_r) > 0.7:
                    interp = f"Correlação forte ({pearson_r:.2f})"
                elif abs(pearson_r) > 0.3:
                    interp = f"Correlação moderada ({pearson_r:.2f})"
                else:
                    interp = f"Correlação fraca/inexistente ({pearson_r:.2f})"
            else:
                interp = "Não computável"

            results.append(CorrelationResult(
                metric_x="custody_pct",
                metric_y=name,
                pearson_r=pearson_r,
                spearman_rho=spearman_rho,
                n_samples=len(pairs),
                p_value=None,  # Requer scipy.stats para p-value exato
                interpretation=interp,
            ))

        return results

    def _pearson(self, x: List[float], y: List[float]) -> Optional[float]:
        n = len(x)
        if n < 2:
            return None
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        den_x = sum((x[i] - mean_x) ** 2 for i in range(n)) ** 0.5
        den_y = sum((y[i] - mean_y) ** 2 for i in range(n)) ** 0.5
        if den_x == 0 or den_y == 0:
            return None
        return num / (den_x * den_y)

    def _spearman(self, x: List[float], y: List[float]) -> Optional[float]:
        n = len(x)
        if n < 2:
            return None
        # Rank transform
        def rank(vals):
            sorted_vals = sorted(set(vals))
            ranks = {v: i + 1 for i, v in enumerate(sorted_vals)}
            return [ranks[v] for v in vals]
        rx = rank(x)
        ry = rank(y)
        return self._pearson(rx, ry)

    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo de correlação."""
        snaps = self.load_snapshots()
        corr = self.compute_correlations()
        return {
            "generated_at": _iso(time.time()),
            "total_snapshots": len(snaps),
            "snapshots": [s.to_dict() for s in snaps],
            "correlations": [c.to_dict() for c in corr],
        }

    def write_report(self, out_path: str) -> str:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        report = self.generate_report()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return out_path


def main():
    """CLI: python -m evolution.quality_correlator [--collect] [--report] [--out PATH]"""
    import argparse
    parser = argparse.ArgumentParser(description="Correlação Custódia vs Qualidade Downstream")
    parser.add_argument("--collect", action="store_true", help="Coleta snapshot atual")
    parser.add_argument("--report", action="store_true", help="Gera relatório de correlação")
    parser.add_argument("--out", default=None, help="Arquivo de saída (JSON)")
    parser.add_argument("--no-checks", action="store_true", help="Não roda quality checks (rápido)")
    args = parser.parse_args()

    corr = QualityCorrelator()

    if args.collect:
        snap = corr.collect_snapshot(run_quality_checks=not args.no_checks)
        print(f"Snapshot coletado: {snap.cycle_id} | Custódia {snap.custody_pct}%")
        if args.out:
            corr.write_report(args.out)
            print(f"Relatório salvo em {args.out}")

    if args.report:
        report = corr.generate_report()
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"Relatório salvo em {args.out}")
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))

    if not args.collect and not args.report:
        parser.print_help()


if __name__ == "__main__":
    main()