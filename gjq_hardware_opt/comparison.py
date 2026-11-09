#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comparação baseline vs otimizado e relatório de mitigação (R1110)."""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from qiskit import QuantumCircuit, qasm2, qasm3, transpile

from quantum_efficiency.metrics import circuit_metrics

from .estimator import estimate_success
from .execution import audit_counts
from .mitigation import correlation, tvd_vs_ideal
from .optimizer import Candidate, compact_to_used_physical
from .profile import HardwareProfile


def build_baseline_candidate(
    circuit: QuantumCircuit,
    profile: HardwareProfile,
    target,
    *,
    seed: int = 42,
) -> Candidate:
    """Baseline trivial-operacional, mesma porta base e mesmo target."""
    layout = list(profile.operational_qubits)[: circuit.num_qubits]
    if len(layout) < circuit.num_qubits:
        raise ValueError("perfil sem qubits operacionais suficientes para o baseline")
    transpiled = transpile(
        circuit,
        target=target,
        optimization_level=1,
        initial_layout=layout,
        routing_method="basic",
        seed_transpiler=int(seed),
    )
    compact = compact_to_used_physical(transpiled)
    used = sorted(
        {
            compact.find_bit(qubit).index
            for instruction in compact.data
            for qubit in instruction.qubits
        }
    )
    return Candidate(
        layout_kind="trivial",
        optimization_level=1,
        layout_method=None,
        routing_method="basic",
        seed=int(seed),
        initial_layout=layout,
        circuit=compact,
        metrics=circuit_metrics(compact),
        estimate=estimate_success(compact, profile),
        transpile_seconds=0.0,
        used_physical=used,
        status="pass",
    )


def case_payload(
    name: str,
    candidate: Candidate,
    counts: dict[str, int],
    shots: int,
    *,
    task_id: str | None = None,
    calibration_task_ids: dict[str, str] | None = None,
    calibration_counts: dict[str, dict[str, int]] | None = None,
    mitigation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    total = sum(int(v) for v in counts.values())
    probabilities = {
        str(k): int(v) / total for k, v in counts.items()
    } if total else {}
    payload: dict[str, Any] = {
        "name": name,
        "task_id": task_id,
        "shots": int(shots),
        "candidate": candidate.to_dict(),
        "counts": counts,
        "audit": audit_counts(counts, shots),
        "probabilities": probabilities,
        "raw_correlation_00_11": correlation(probabilities),
        "raw_tvd_vs_ideal": tvd_vs_ideal(probabilities),
        "calibration_task_ids": calibration_task_ids or {},
        "calibration_counts": calibration_counts or {},
        "mitigation": mitigation,
    }
    if mitigation and "probabilities" in mitigation:
        mitigated = mitigation["probabilities"]
        if "00" in mitigated and "11" in mitigated:
            p00 = float(mitigated["00"])
            p11 = float(mitigated["11"])
            payload["mitigated_correlation_00_11"] = p00 + p11
            payload["mitigated_tvd_subspace"] = 0.5 * (
                abs(p00 - 0.5) + abs(p11 - 0.5)
            )
    return payload


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def render_comparison_markdown(data: dict[str, Any]) -> str:
    baseline = data["baseline"]
    optimized = data["optimized"]
    lines = [
        "# Comparação baseline vs otimizado — GJQ / Baihua",
        "",
        f"Gerado em {data['generated_at']} · {data['shots']} shots por circuito.",
        "",
        "## Protocolo",
        "",
        "- Mesmo circuito E05/Bell, mesmo target, mesma seed e mesmas portas base.",
        "- Baseline: layout trivial-operacional, roteamento basic, nível 1.",
        "- Otimizado: layout noise-aware, roteamento sabre, candidato escolhido.",
        "- Submissão com `transpile=False`; nenhuma dupla transpilação.",
        "- Calibração de leitura: |00> e |11> nos mesmos qubits físicos.",
        "",
        "## Resultados",
        "",
        "| Caso | Qubits | Erro proxy | Raw 00+11 | Raw TVD | Mitigado 00 | Mitigado 11 | TVD mitigada | Task ID |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for case in (baseline, optimized):
        mitigation = case.get("mitigation") or {}
        probabilities = mitigation.get("probabilities") or {}
        lines.append(
            f"| {case['name']} | {case['candidate']['used_physical']} | "
            f"{case['candidate']['estimate'].get('error_budget_proxy', 0):.4e} | "
            f"{case['raw_correlation_00_11']:.4f} | {case['raw_tvd_vs_ideal']:.4f} | "
            f"{_fmt(probabilities.get('00'))} | {_fmt(probabilities.get('11'))} | "
            f"{_fmt(case.get('mitigated_tvd_subspace'))} | `{case.get('task_id')}` |"
        )
    improvement = data["comparison"]
    lines += [
        "",
        "## Diferença (otimizado − baseline)",
        "",
        "| Métrica | Δ |",
        "|---|---:|",
        f"| Correlação raw 00/11 | {improvement['delta_raw_correlation']:+.4f} |",
        f"| TVD raw vs ideal | {improvement['delta_raw_tvd']:+.4f} |",
        f"| TVD mitigada | {_fmt(improvement.get('delta_mitigated_tvd'), 4)} |",
        "",
        "## Interpretação",
        "",
    ]
    proxy_baseline = baseline["candidate"]["estimate"].get("error_budget_proxy")
    proxy_optimized = optimized["candidate"]["estimate"].get("error_budget_proxy")
    proxy_rank = (
        "otimizado" if proxy_optimized < proxy_baseline else "baseline"
    )
    observed_rank = (
        "otimizado"
        if optimized["raw_tvd_vs_ideal"] < baseline["raw_tvd_vs_ideal"]
        else "baseline"
    )
    proxy_confirmed = proxy_rank == observed_rank
    lines += [
        f"- O proxy previa erro menor para **{proxy_rank}** "
        f"(baseline {proxy_baseline:.4e}; otimizado {proxy_optimized:.4e}).",
        f"- No hardware, a correlação raw 00/11 foi "
        f"{baseline['raw_correlation_00_11']:.4f} no baseline e "
        f"{optimized['raw_correlation_00_11']:.4f} no otimizado.",
        f"- O ranking do proxy **{'confirmou' if proxy_confirmed else 'não confirmou'}** "
        f"o resultado observado; o caso com menor TVD raw foi **{observed_rank}**.",
    ]
    if "delta_mitigated_tvd" in improvement:
        mitigated_rank = (
            "otimizado" if improvement["delta_mitigated_tvd"] < 0 else "baseline"
        )
        lines.append(
            f"- Após a mitigação de leitura, a TVD foi "
            f"{baseline.get('mitigated_tvd_subspace', float('nan')):.4f} no baseline "
            f"e {optimized.get('mitigated_tvd_subspace', float('nan')):.4f} no "
            f"otimizado; o caso com menor TVD mitigada foi **{mitigated_rank}**."
        )
    leakage_baseline = (baseline.get("mitigation") or {}).get("leakage_by_prepared") or {}
    leakage_optimized = (optimized.get("mitigation") or {}).get("leakage_by_prepared") or {}
    if leakage_baseline or leakage_optimized:
        lines.append(
            f"- Leakage de |11>: {leakage_baseline.get('11', 0):.1%} no baseline e "
            f"{leakage_optimized.get('11', 0):.1%} no otimizado. A inversão 00/11 "
            "não corrige a população que sai para 01/10."
        )
    lines += [
        "- Uma execução por caso, com 4096 shots, não é estudo estatístico; "
        "diferenças pequenas não sustentam vantagem.",
        "",
        "## Calibração de leitura",
        "",
    ]
    for case in (baseline, optimized):
        calibration = case.get("mitigation") or {}
        matrix = calibration.get("matrix")
        lines += [
            f"### {case['name']}",
            "",
            f"- Matriz de leitura: `{matrix}`.",
            f"- Leakage por estado preparado: `{calibration.get('leakage_by_prepared')}`.",
            f"- Condição da matriz: {_fmt(calibration.get('condition_number'), 3)}.",
            f"- Massa negativa clipada: {_fmt(calibration.get('negative_mass_clipped'), 6)}.",
            "",
        ]
    lines += [
        "## Limites",
        "",
        "- Uma execução por caso não é estudo estatístico nem prova de vantagem.",
        "- A calibração de leitura mede |00> e |11> nos mesmos qubits; |11> "
        "usa rx(pi) e inclui preparação do |1>, então não separa completamente "
        "readout de state preparation. Crosstalk, deriva e leakage fora do "
        "subespaço também não são capturados.",
        "- A TVD mitigada é uma estimativa dentro do subespaço 00/11; não é "
        "fidelidade de estado.",
        "- O proxy de erro é um produto de `(1 - erro)` por porta e leitura; não "
        "é fidelidade.",
        "- Custo, fila e calibração podem mudar.",
        "",
    ]
    return "\n".join(lines)


def export_comparison(data: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    (out_dir / "comparacao.json").write_text(payload, encoding="utf-8")
    (out_dir / "RELATORIO_COMPARACAO.md").write_text(
        render_comparison_markdown(data), encoding="utf-8"
    )
    for name, case in (("baseline", data["baseline"]), ("otimizado", data["optimized"])):
        case_dir = out_dir / name
        case_dir.mkdir(exist_ok=True)
        circuit = case.get("qasm2")
        if circuit:
            (case_dir / "circuito.qasm2").write_text(circuit, encoding="utf-8")
        if case.get("qasm3"):
            (case_dir / "circuito.qasm3").write_text(case["qasm3"], encoding="utf-8")
        (case_dir / "counts.json").write_text(
            json.dumps(case["counts"], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (case_dir / "caso.json").write_text(
            json.dumps(case, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return {
        "out_dir": str(out_dir),
        "files": [
            str(out_dir / "comparacao.json"),
            str(out_dir / "RELATORIO_COMPARACAO.md"),
        ],
    }


def summary_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0
