#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exportação de resultados, QASM e relatórios do otimizador GJQ (R1109)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from qiskit import qasm2, qasm3

from .optimizer import OptimizationResult


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write(path: Path, text: str) -> dict[str, Any]:
    path.write_text(text, encoding="utf-8")
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(text),
    }


def _candidate_rows(result: OptimizationResult) -> list[str]:
    rows = [
        "| Candidato | Nível | Seed | Layout | Roteamento | 2q | Depth | Size | Erro proxy | Sucesso | Status |",
        "|---|---:|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for candidate in result.candidates:
        marker = " **escolhido**" if candidate is result.chosen else ""
        metrics = candidate.metrics
        estimate = candidate.estimate
        rows.append(
            f"| {candidate.layout_kind}{marker} | {candidate.optimization_level} | "
            f"{candidate.seed} | {candidate.layout_method or 'initial_layout'} | "
            f"{candidate.routing_method} | {metrics.get('num_2q', '-')} | "
            f"{metrics.get('depth', '-')} | {metrics.get('size', '-')} | "
            f"{estimate.get('error_budget_proxy', 0):.3e} | "
            f"{estimate.get('success_proxy', 0):.3e} | {candidate.status} |"
        )
    return rows


def render_result_markdown(result: OptimizationResult) -> str:
    summary = result.profile.summary()
    baseline = result.baseline
    chosen = result.chosen
    improvement = result.selection.get("improvement", {})
    lines = [
        "# Otimização para hardware GJQ — resultado",
        "",
        f"Perfil **{summary['name']}** · tipo `{summary['profile_kind']}` · "
        f"fingerprint `{summary['target_fingerprint'][:16]}…`.",
        "",
        "## Protocolo",
        "",
        "- Baseline: layout trivial, roteamento basic, nível 1.",
        "- Candidatos: layout noise-aware, Sabre e Dense; níveis e seeds declarados.",
        "- Seleção: erro proxy, profundidade, 2q e tamanho, conforme a estratégia.",
        "- Gate de correção: o circuito escolhido usa apenas portas base e arestas do perfil.",
        "- Nenhum job foi submetido por este relatório.",
        "",
        "## Perfil",
        "",
        f"- Qubits: **{summary['num_qubits']}** · arestas: **{summary['edges']}**.",
        f"- Portas 1q: {', '.join(summary['oneq_gates']) or '—'}.",
        f"- Portas 2q: {', '.join(summary['twoq_gates']) or '—'}.",
        f"- Erro 1q médio: {summary['oneq_error_mean']:.3e} · máximo: {summary['oneq_error_max']:.3e}.",
        f"- Erro 2q médio: {summary['twoq_error_mean']:.3e} · máximo: {summary['twoq_error_max']:.3e}.",
        f"- Erro de leitura médio: {summary['readout_error_mean']:.3e} · máximo: {summary['readout_error_max']:.3e}.",
        f"- Calibração: `{summary['calibration_source']}` · atualização: {summary['last_update_date'] or '—'}.",
        "",
        "## Layout",
        "",
        f"- Método: `{result.layout.method}`.",
        f"- Layout lógico → físico: `{result.layout.layout}`.",
        f"- Região física conectada: `{result.layout.physical_region}`.",
        f"- Custo do layout: {result.layout.cost:.3e} · custo trivial: {result.layout.trivial_cost:.3e}.",
        "",
        "## Baseline vs escolhido",
        "",
        "| Métrica | Baseline | Escolhido | Δ |",
        "|---|---:|---:|---:|",
        f"| Erro proxy | {baseline.estimate.get('error_budget_proxy', 0):.3e} | "
        f"{chosen.estimate.get('error_budget_proxy', 0):.3e} | "
        f"{improvement.get('error_budget_abs', 0):+.3e} |",
        f"| Sucesso proxy | {baseline.estimate.get('success_proxy', 0):.3e} | "
        f"{chosen.estimate.get('success_proxy', 0):.3e} | "
        f"{improvement.get('success_proxy_ratio') or 0:.3f}× |",
        f"| 2q | {baseline.metrics.get('num_2q', 0)} | {chosen.metrics.get('num_2q', 0)} | "
        f"{improvement.get('num_2q_abs', 0):+d} |",
        f"| Profundidade | {baseline.metrics.get('depth', 0)} | {chosen.metrics.get('depth', 0)} | "
        f"{improvement.get('depth_abs', 0):+d} |",
        f"| Size | {baseline.metrics.get('size', 0)} | {chosen.metrics.get('size', 0)} | "
        f"{improvement.get('size_abs', 0):+d} |",
        "",
        f"Estratégia: `{result.selection.get('strategy')}` · candidato escolhido: "
        f"`{chosen.layout_kind}` nível {chosen.optimization_level}, seed {chosen.seed}.",
        "",
        "## Candidatos",
        "",
        *_candidate_rows(result),
        "",
        "## Limites",
        "",
        "- Métricas de compilação e proxy de erro; não é execução física.",
        "- O proxy não mede fidelidade de estado, crosstalk, leakage ou deriva.",
        "- A calibração muda; releia `backend.properties` antes de comparar execuções.",
        "- Redução de portas ou de erro proxy não é vantagem quântica.",
        "- Nenhum job foi submetido por este relatório.",
        "",
    ]
    return "\n".join(lines)


def export_result(result: OptimizationResult, out_dir: Path) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    qasm2_text = qasm2.dumps(result.chosen.circuit)
    qasm3_text = qasm3.dumps(result.chosen.circuit)
    baseline_qasm2 = qasm2.dumps(result.baseline.circuit)
    payload = result.to_dict()
    files = {
        "otimizado.qasm2": _write(out_dir / "otimizado.qasm2", qasm2_text),
        "otimizado.qasm3": _write(out_dir / "otimizado.qasm3", qasm3_text),
        "baseline.qasm2": _write(out_dir / "baseline.qasm2", baseline_qasm2),
        "perfil.json": _write(
            out_dir / "perfil.json",
            json.dumps(result.profile.to_dict(), indent=2, ensure_ascii=False),
        ),
    }
    payload["files"] = files
    payload["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    _write(
        out_dir / "resultado.json",
        json.dumps(payload, indent=2, ensure_ascii=False),
    )
    report = _write(out_dir / "RELATORIO.md", render_result_markdown(result))
    return {
        "out_dir": str(out_dir),
        "files": files,
        "report": report,
        "chosen": result.chosen.to_dict(),
        "baseline": result.baseline.to_dict(),
        "selection": result.selection,
    }


def render_benchmark_markdown(data: dict[str, Any]) -> str:
    summary = data["summary"]
    lines = [
        "# Otimização GJQ — benchmark",
        "",
        f"Gerado em {data['generated_at']} · seed {data['seed']} · estratégia "
        f"`{data['strategy']}` · modo {'rápido' if data['quick'] else 'completo'}.",
        "",
        "## Resumo",
        "",
        f"- Circuitos: **{summary['circuits']}** · pass: **{summary['pass']}** · "
        f"fail: **{summary['fail']}**.",
        f"- Erro proxy médio: baseline **{summary['mean_error_baseline']:.3e}** · "
        f"escolhido **{summary['mean_error_chosen']:.3e}**.",
        f"- Redução relativa média do erro proxy: **{summary['mean_error_reduction_rel']:.1%}**.",
        f"- Profundidade média: baseline **{summary['mean_depth_baseline']:.1f}** · "
        f"escolhido **{summary['mean_depth_chosen']:.1f}**.",
        f"- 2q médio: baseline **{summary['mean_2q_baseline']:.2f}** · "
        f"escolhido **{summary['mean_2q_chosen']:.2f}**.",
        f"- Circuitos com erro proxy menor: **{summary['improved_error']}** · "
        f"com profundidade menor: **{summary['improved_depth']}**.",
        "",
        "## Por circuito",
        "",
        "| Circuito | Erro base | Erro escolhido | Δrel | Depth base | Depth escolhido | 2q base | 2q escolhido | Candidato |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in data["results"]:
        if row["status"] != "pass":
            lines.append(
                f"| {row['circuit']} | — | — | — | — | — | — | — | fail: {row.get('error', '')} |"
            )
            continue
        baseline = row["baseline"]
        chosen = row["chosen"]
        improvement = row["improvement"]
        lines.append(
            f"| {row['circuit']} | {baseline['estimate']['error_budget_proxy']:.3e} | "
            f"{chosen['estimate']['error_budget_proxy']:.3e} | "
            f"{improvement['error_budget_rel']:.1%} | "
            f"{baseline['metrics']['depth']} | {chosen['metrics']['depth']} | "
            f"{baseline['metrics']['num_2q']} | {chosen['metrics']['num_2q']} | "
            f"{chosen['layout_kind']}/L{chosen['optimization_level']} |"
        )
    lines += [
        "",
        "## Limites",
        "",
        "- Métricas de compilação e proxy de erro; não é execução física.",
        "- O proxy não mede fidelidade de estado, crosstalk, leakage ou deriva.",
        "- A calibração muda; releia as propriedades antes de comparar execuções.",
        "- Nenhum job foi submetido por este benchmark.",
        "",
    ]
    return "\n".join(lines)


def export_benchmark(data: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "benchmark.json": _write(
            out_dir / "benchmark.json",
            json.dumps(data, indent=2, ensure_ascii=False),
        ),
        "RELATORIO_BENCHMARK.md": _write(
            out_dir / "RELATORIO_BENCHMARK.md",
            render_benchmark_markdown(data),
        ),
    }
    return {"out_dir": str(out_dir), "files": files, "summary": data["summary"]}


def render_execution_markdown(record: dict[str, Any]) -> str:
    audit = record.get("counts_audit") or {}
    wait = record.get("wait") or {}
    status = wait.get("task_status") or wait.get("status") or record.get("task_status") or "—"
    observed = record.get("observed") or {}
    lines = [
        "# Execução GJQ — proveniência",
        "",
        f"Task ID: **{record.get('task_id')}** · backend **{record.get('backend')}** · "
        f"hardware: **{record.get('hardware')}** · shots: **{record.get('shots')}**.",
        "",
        "## Circuito",
        "",
        f"- Perfil: `{record.get('profile_name')}` (`{record.get('profile_kind')}`).",
        f"- Fingerprint: `{record.get('profile_fingerprint')}`.",
        f"- Estratégia: `{record.get('strategy')}` · candidato: "
        f"`{record.get('chosen_layout_kind')}` nível {record.get('chosen_optimization_level')} "
        f"seed {record.get('chosen_seed')}.",
        f"- QASM2 SHA-256: `{record.get('qasm2_sha256')}`.",
        f"- QASM3 SHA-256: `{record.get('qasm3_sha256')}`.",
        f"- Submetido em: {record.get('submitted_at')}.",
        "",
        "## Resultado",
        "",
        f"- Status: `{status}`.",
        f"- Soma dos counts: {audit.get('total', '—')} · esperado: {audit.get('shots_expected', '—')}.",
        f"- Auditoria: {'ok' if audit.get('ok') else audit.get('alert', 'sem counts')}.",
        "",
        "## Limites",
        "",
        "- Uma execução não prova fidelidade, emaranhamento, vantagem quântica ou "
        "interpretação de Bohm.",
        "- O proxy de erro não é calibração e não prevê o resultado desta execução.",
        "- Não reenvie o mesmo circuito sem necessidade; reutilize o task_id.",
        "",
    ]
    if observed:
        lines += [
            "## Métricas observadas",
            "",
            "| Métrica | Valor |",
            "|---|---:|",
            f"| Fração 00/11 | {observed.get('correlated_00_11', 0):.4f} |",
            f"| Erro padrão de 00/11 | {observed.get('correlated_standard_error') or 0:.4f} |",
        ]
        if "tvd_vs_ideal" in observed:
            lines.append(f"| TVD vs ideal | {observed['tvd_vs_ideal']:.4f} |")
        lines += [
            "",
            "> A fração 00/11 é uma taxa de outcomes correlacionados, não "
            "fidelidade de estado nem prova de emaranhamento.",
            "",
        ]
    if audit.get("probabilities"):
        lines += ["## Probabilidades", "", "| Bitstring | Probabilidade | Erro padrão |", "|---|---:|---:|"]
        for key, probability in audit["probabilities"].items():
            lines.append(
                f"| `{key}` | {probability:.6f} | {audit['standard_error'].get(key, 0):.6f} |"
            )
        lines.append("")
    return "\n".join(lines)


def export_execution(record: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "execucao.json": _write(
            out_dir / "execucao.json",
            json.dumps(record, indent=2, ensure_ascii=False),
        ),
        "RELATORIO_EXECUCAO.md": _write(
            out_dir / "RELATORIO_EXECUCAO.md",
            render_execution_markdown(record),
        ),
    }
    if record.get("counts") is not None:
        files["counts.json"] = _write(
            out_dir / "counts.json",
            json.dumps(record["counts"], indent=2, ensure_ascii=False),
        )
    return {"out_dir": str(out_dir), "files": files}
