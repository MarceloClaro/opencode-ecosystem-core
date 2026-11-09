#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Harness de eficiência: baseline vs otimização, com gate de correção."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import mean

from .benchmarks import BENCHMARKS
from .metrics import circuit_metrics, dist_ideal, transpile_measured, tvd

TVD_TOL = 1e-9
SEED_PADRAO = 42


def _reducao(base: int, opt: int) -> float:
    if base == 0:
        return 0.0
    return (base - opt) / base


def rodar_benchmark(nome: str, qc, coupling_map=None, seed: int = SEED_PADRAO) -> dict:
    base, t_base = transpile_measured(qc, 0, seed, coupling_map=coupling_map)
    opt, t_opt = transpile_measured(qc, 3, seed, coupling_map=coupling_map)
    mb = circuit_metrics(base)
    mo = circuit_metrics(opt)
    db = dist_ideal(base)
    do = dist_ideal(opt)
    diferenca = tvd(db, do)
    gates = {
        "tvd": diferenca <= TVD_TOL,
        "num_2q": mo["num_2q"] <= mb["num_2q"],
        "depth": mo["depth"] <= mb["depth"],
    }
    return {
        "benchmark": nome,
        "seed": seed,
        "coupling_map": coupling_map,
        "baseline": {**mb, "transpile_seconds": t_base},
        "otimizado": {**mo, "transpile_seconds": t_opt},
        "reducao": {
            "size": _reducao(mb["size"], mo["size"]),
            "depth": _reducao(mb["depth"], mo["depth"]),
            "num_2q": _reducao(mb["num_2q"], mo["num_2q"]),
            "num_1q": _reducao(mb["num_1q"], mo["num_1q"]),
        },
        "tvd": diferenca,
        "tvd_tolerancia": TVD_TOL,
        "gates": gates,
        "status": "pass" if all(gates.values()) else "fail",
        "hardware": False,
        "network": False,
    }


def rodar_tudo(seed: int = SEED_PADRAO, apenas: list[str] | None = None) -> dict:
    ids = {b["name"] for b in BENCHMARKS}
    if apenas:
        desconhecidos = sorted(set(apenas) - ids)
        if desconhecidos:
            raise ValueError(f"benchmarks desconhecidos: {desconhecidos}")
    resultados = []
    for b in BENCHMARKS:
        if apenas and b["name"] not in apenas:
            continue
        resultados.append(
            rodar_benchmark(b["name"], b["circuit"], b.get("coupling_map"), seed)
        )
    passou = sum(1 for r in resultados if r["status"] == "pass")
    total = len(resultados)
    return {
        "schema_version": 1,
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "seed": seed,
        "software": {
            "transpilador": "qiskit",
            "optimization_level_baseline": 0,
            "optimization_level_otimizado": 3,
            "basis_gates": ["u", "cx"],
        },
        "resumo": {
            "benchmarks": total,
            "pass": passou,
            "fail": total - passou,
            "tvd_medio": mean(r["tvd"] for r in resultados) if resultados else 0.0,
            "reducao_media_2q": mean(r["reducao"]["num_2q"] for r in resultados) if resultados else 0.0,
            "reducao_media_depth": mean(r["reducao"]["depth"] for r in resultados) if resultados else 0.0,
        },
        "benchmarks": resultados,
        "limites": (
            "Métricas de transpilação e distribuição ideal; não é execução em hardware, "
            "não mede fidelidade de estado e não prova vantagem quântica. O resultado "
            "depende da versão do Qiskit, do seed e do conjunto de portas base."
        ),
    }


def escrever_relatorio(dados: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "resultados.json"
    json_path.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    linhas = [
        "# Eficiência de código quântico — relatório",
        "",
        f"Gerado em {dados['timestamp']} · seed {dados['seed']}.",
        "",
        "## Protocolo",
        "",
        "- Baseline: `transpile(..., optimization_level=0)`.",
        "- Otimizado: `transpile(..., optimization_level=3)`.",
        "- Portas base: `u`, `cx`; roteamento quando o benchmark tem coupling map.",
        f"- Gate de correção: TVD ≤ {TVD_TOL:g} entre as distribuições ideais.",
        "- Sem hardware e sem rede.",
        "",
        "## Resumo",
        "",
        f"- Benchmarks: **{dados['resumo']['benchmarks']}**",
        f"- Pass: **{dados['resumo']['pass']}** · Fail: **{dados['resumo']['fail']}**",
        f"- TVD médio: **{dados['resumo']['tvd_medio']:.3e}**",
        f"- Redução média de 2q: **{dados['resumo']['reducao_media_2q']:.1%}**",
        f"- Redução média de profundidade: **{dados['resumo']['reducao_media_depth']:.1%}**",
        "",
        "## Benchmarks",
        "",
        "| Benchmark | 2q base | 2q opt | Δ2q | depth base | depth opt | Δdepth | TVD | Status |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in dados["benchmarks"]:
        b, o = r["baseline"], r["otimizado"]
        linhas.append(
            f"| {r['benchmark']} | {b['num_2q']} | {o['num_2q']} | "
            f"{r['reducao']['num_2q']:.1%} | {b['depth']} | {o['depth']} | "
            f"{r['reducao']['depth']:.1%} | {r['tvd']:.2e} | {r['status']} |"
        )
    linhas += [
        "",
        "## Limites",
        "",
        "- Métricas de transpilação e distribuição ideal; não é hardware.",
        "- Não mede fidelidade de estado, calibração ou tempo de parede em backend.",
        "- O resultado depende da versão do Qiskit, do seed e do conjunto de portas.",
        "- Redução de portas não é, por si só, vantagem quântica.",
        "",
    ]
    md_path = out_dir / "RELATORIO.md"
    md_path.write_text("\n".join(linhas), encoding="utf-8")
    return json_path, md_path
