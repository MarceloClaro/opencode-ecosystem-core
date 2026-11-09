#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Engenharia de loop para comparação e mitigação GJQ (R1112).

Estágios:

    plan -> simulate -> execute -> score -> report

Gates:

    SDD (specs e testes existem) -> TDD (pytest) -> simulação -> hardware

O hardware só é chamado depois dos gates e com ``confirm``/``allow_hardware``.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .simulation import simulate_plan

ROOT = Path(__file__).resolve().parents[1]


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def new_state(
    *,
    backend: str | None,
    profile_file: str | None,
    circuit: str,
    shots: int,
    max_iterations: int,
    out_dir: Path,
) -> dict[str, Any]:
    timestamp = now()
    return {
        "schema_version": 1,
        "loop_id": f"gjq-loop-{datetime.now().strftime('%Y%m%dT%H%M%S')}",
        "backend": backend,
        "profile_file": profile_file,
        "circuit": circuit,
        "shots": int(shots),
        "max_iterations": int(max_iterations),
        "iteration": 1,
        "status": "created",
        "gates": {
            "sdd": None,
            "tdd": None,
            "simulation": None,
            "hardware": False,
        },
        "paths": {
            "out_dir": str(out_dir),
            "plan_dir": str(out_dir / "plan"),
            "plan": str(out_dir / "plan" / "plano_comparacao.json"),
            "simulation": str(out_dir / "simulacao.json"),
            "comparison": str(out_dir / "comparacao" / "comparacao.json"),
            "report": str(out_dir / "RELATORIO_LOOP.md"),
        },
        "history": [],
        "best": None,
        "lessons": [],
        "submissions_estimated": 0,
        "submissions_used": 0,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def load_state(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_state(state: dict[str, Any], path: Path) -> None:
    state["updated_at"] = now()
    Path(path).write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def append_log(out_dir: Path, event: dict[str, Any]) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "loop_log.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")


def run_sdd_gate(
    spec_paths: list[str],
    test_paths: list[str],
) -> dict[str, Any]:
    """Confere presença e conteúdo mínimo de specs e testes."""
    failures: list[str] = []
    specs = []
    for raw in spec_paths:
        path = Path(raw)
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        ok = (
            path.is_file()
            and len(text) > 400
            and "critérios de aceitação" in text.lower()
        )
        specs.append({"path": str(path), "ok": ok, "bytes": len(text)})
        if not ok:
            failures.append(f"spec inválida ou ausente: {path}")
    tests = []
    for raw in test_paths:
        path = Path(raw)
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        ok = path.is_file() and len(text) > 200 and "def test_" in text
        tests.append({"path": str(path), "ok": ok, "bytes": len(text)})
        if not ok:
            failures.append(f"teste inválido ou ausente: {path}")
    return {
        "ok": not failures,
        "specs": specs,
        "tests": tests,
        "failures": failures,
    }


def run_tdd_gate(
    test_paths: list[str],
    *,
    timeout: int = 900,
) -> dict[str, Any]:
    """Executa pytest nos testes indicados."""
    command = [sys.executable, "-m", "pytest", *test_paths, "-q"]
    try:
        result = subprocess.run(
            command,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "command": command,
            "returncode": None,
            "timeout": timeout,
            "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
            "failure": "timeout",
        }
    return {
        "ok": result.returncode == 0,
        "command": command,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }


def simulation_gate(
    plan: dict[str, Any],
    profile,
    *,
    shots: int,
    seed: int = 42,
) -> dict[str, Any]:
    result = simulate_plan(plan, profile, shots=shots, seed=seed)
    result["gate_ok"] = bool(result.get("gate_ok"))
    return result


def score_comparison(comparison: dict[str, Any]) -> dict[str, Any]:
    baseline = comparison["baseline"]
    optimized = comparison["optimized"]
    proxy_baseline = float(
        baseline["candidate"]["estimate"].get("error_budget_proxy", 1.0)
    )
    proxy_optimized = float(
        optimized["candidate"]["estimate"].get("error_budget_proxy", 1.0)
    )
    proxy_winner = "baseline" if proxy_baseline < proxy_optimized else "optimized"
    raw_winner = (
        "baseline"
        if baseline["raw_tvd_vs_ideal"] <= optimized["raw_tvd_vs_ideal"]
        else "optimized"
    )
    mitigated_winner = raw_winner
    if (
        baseline.get("mitigated_tvd_subspace") is not None
        and optimized.get("mitigated_tvd_subspace") is not None
    ):
        mitigated_winner = (
            "baseline"
            if baseline["mitigated_tvd_subspace"] <= optimized["mitigated_tvd_subspace"]
            else "optimized"
        )
    mitigated_available = (
        baseline.get("mitigated_tvd_subspace") is not None
        and optimized.get("mitigated_tvd_subspace") is not None
    )
    proxy_confirmed_raw = proxy_winner == raw_winner
    proxy_confirmed_mitigated = (
        proxy_winner == mitigated_winner if mitigated_available else None
    )
    proxy_confirmed = (
        proxy_confirmed_mitigated
        if proxy_confirmed_mitigated is not None
        else proxy_confirmed_raw
    )
    if proxy_confirmed_mitigated and mitigated_winner == "optimized":
        lesson = (
            "Proxy e resultado mitigado concordam no otimizado; o raw favoreceu "
            "o baseline. A diferença mitigada é pequena; repetir com mais shots "
            "e calibrar os 4 estados antes de qualquer conclusão."
        )
        next_action = "repetir com mais shots e calibração completa dos 4 estados"
    elif proxy_confirmed_mitigated is False and mitigated_winner == "baseline":
        lesson = (
            "O proxy não confirmou o hardware; o baseline venceu após a "
            "mitigação. A calibração declarada não foi suficiente para prever "
            "o Bell."
        )
        next_action = (
            "usar o layout baseline como referência e testar um candidato "
            "alternativo na próxima iteração"
        )
    elif proxy_confirmed_mitigated and mitigated_winner == "baseline":
        lesson = (
            "Proxy e mitigação concordam no baseline; manter o baseline como "
            "referência e testar outro candidato."
        )
        next_action = "manter o baseline como referência"
    else:
        lesson = (
            "O resultado mitigado favorece o otimizado, mas o proxy previa o "
            "baseline; a diferença é frágil. Repetir com mais shots."
        )
        next_action = "repetir com mais shots e calibrar os 4 estados"
    return {
        "proxy_baseline": proxy_baseline,
        "proxy_optimized": proxy_optimized,
        "proxy_winner": proxy_winner,
        "raw_winner": raw_winner,
        "mitigated_winner": mitigated_winner,
        "proxy_confirmed": proxy_confirmed,
        "proxy_confirmed_raw": proxy_confirmed_raw,
        "proxy_confirmed_mitigated": proxy_confirmed_mitigated,
        "baseline_raw_tvd": baseline["raw_tvd_vs_ideal"],
        "optimized_raw_tvd": optimized["raw_tvd_vs_ideal"],
        "baseline_mitigated_tvd": baseline.get("mitigated_tvd_subspace"),
        "optimized_mitigated_tvd": optimized.get("mitigated_tvd_subspace"),
        "score": (
            1.0 - float(optimized.get("mitigated_tvd_subspace") or optimized["raw_tvd_vs_ideal"])
        ),
        "lesson": lesson,
        "next_action": next_action,
        "limits": (
            "Uma execução não é estudo estatístico; o loop registra a lição, "
            "não promove confiança automaticamente."
        ),
    }


def render_loop_report(
    state: dict[str, Any],
    *,
    simulation: dict[str, Any] | None = None,
    comparison: dict[str, Any] | None = None,
    score: dict[str, Any] | None = None,
) -> str:
    gates = state.get("gates", {})
    lines = [
        "# Loop GJQ — plano, simulação, hardware e mitigação",
        "",
        f"Loop `{state.get('loop_id')}` · backend **{state.get('backend') or 'perfil offline'}** · "
        f"circuito **{state.get('circuit')}** · **{state.get('shots')} shots**.",
        "",
        "## Gates",
        "",
        "| Gate | Estado |",
        "|---|---|",
        f"| SDD | {gates.get('sdd')} |",
        f"| TDD | {gates.get('tdd')} |",
        f"| Simulação | {gates.get('simulation')} |",
        f"| Hardware | {gates.get('hardware')} |",
        "",
        f"Submissões estimadas: **{state.get('submissions_estimated')}** · usadas: "
        f"**{state.get('submissions_used')}**.",
        "",
    ]
    if simulation:
        lines += [
            "## Simulação",
            "",
            f"- Equivalência ideal (TVD): {simulation.get('ideal_equivalence_tvd'):.3e}.",
            f"- Gate: **{simulation.get('gate_ok')}** · vencedor simulado: "
            f"**{simulation.get('simulated_winner')}**.",
            f"- TVD ruidosa baseline: {simulation['baseline']['tvd_noisy_vs_ideal']:.4f}.",
            f"- TVD ruidosa otimizado: {simulation['optimized']['tvd_noisy_vs_ideal']:.4f}.",
            "",
            "> A simulação usa modelo depolarizante do perfil e não prevê o hardware.",
            "",
        ]
    if comparison:
        lines += [
            "## Hardware",
            "",
            "| Caso | Qubits | Raw 00/11 | TVD raw | TVD mitigada | Task ID |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for key, label in (("baseline", "baseline"), ("optimized", "otimizado")):
            case = comparison[key]
            lines.append(
                f"| {label} | {case['candidate']['used_physical']} | "
                f"{case['raw_correlation_00_11']:.4f} | "
                f"{case['raw_tvd_vs_ideal']:.4f} | "
                f"{case.get('mitigated_tvd_subspace', float('nan')):.4f} | "
                f"`{case.get('task_id')}` |"
            )
        lines.append("")
    if score:
        lines += [
            "## Score e reflexão",
            "",
            f"- Proxy: baseline {score['proxy_baseline']:.3e} · otimizado "
            f"{score['proxy_optimized']:.3e} · vencedor **{score['proxy_winner']}**.",
            f"- Raw: vencedor **{score['raw_winner']}** · mitigado: vencedor "
            f"**{score['mitigated_winner']}**.",
            f"- Proxy confirmado (raw): **{score.get('proxy_confirmed_raw')}** · "
            f"(mitigado): **{score.get('proxy_confirmed_mitigated')}**.",
            f"- Lição: {score['lesson']}",
            f"- Próxima ação: {score['next_action']}.",
            f"- Score (1 - TVD mitigada do otimizado): {score['score']:.4f}.",
            "",
        ]
    lines += [
        "## Limites",
        "",
        "- Simulação não é hardware; o modelo depolarizante não prevê fidelidade.",
        "- Uma execução por caso não é estudo estatístico.",
        "- A calibração |11> usa `rx(pi)` e inclui preparação do |1>.",
        "- A inversão 00/11 não corrige leakage para 01/10.",
        "- Não há ZNE, PEC, DD ou correção quântica de erro.",
        "- O loop registra lições; não promove confiança automaticamente.",
        "",
    ]
    return "\n".join(lines)


def export_loop(
    state: dict[str, Any],
    out_dir: Path,
    *,
    simulation: dict[str, Any] | None = None,
    comparison: dict[str, Any] | None = None,
    score: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    save_state(state, out_dir / "loop_state.json")
    report = render_loop_report(
        state, simulation=simulation, comparison=comparison, score=score
    )
    (out_dir / "RELATORIO_LOOP.md").write_text(report, encoding="utf-8")
    return {
        "out_dir": str(out_dir),
        "state": str(out_dir / "loop_state.json"),
        "report": str(out_dir / "RELATORIO_LOOP.md"),
    }
