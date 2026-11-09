#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Varredura de níveis de otimização e de ruído depolarizante."""
from __future__ import annotations

from statistics import mean

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from .experiment_benchmarks import benchmarks_experimentos
from .metrics import circuit_metrics, dist_ideal, transpile_measured, tvd

TVD_TOL = 1e-9
SEED_PADRAO = 42
NIVEIS_PADRAO = (0, 1, 2, 3)
RUIDOS_PADRAO = (0.0, 0.001, 0.005, 0.01)


def _reducao(base: int, opt: int) -> float:
    return 0.0 if base == 0 else (base - opt) / base


def _modelo_ruido(p: float):
    if p <= 0:
        return None
    modelo = NoiseModel()
    modelo.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["u"])
    modelo.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
    return modelo


def _contagens(qc, level: int, seed: int, p: float, shots: int) -> dict[str, int]:
    backend = AerSimulator(noise_model=_modelo_ruido(p))
    qc_t = transpile(
        qc,
        backend=backend,
        optimization_level=level,
        seed_transpiler=seed,
    )
    resultado = backend.run(
        qc_t, shots=shots, seed_simulator=seed
    ).result()
    return {str(k): int(v) for k, v in resultado.get_counts().items()}


def varrer_circuito(
    qc,
    nome: str,
    experimento: str,
    descricao: str,
    coupling_map=None,
    seed: int = SEED_PADRAO,
    niveis=NIVEIS_PADRAO,
    ruidos=RUIDOS_PADRAO,
    shots: int = 2048,
) -> dict:
    base, t_base = transpile_measured(qc, 0, seed, coupling_map=coupling_map)
    mb = circuit_metrics(base)
    db = dist_ideal(base)
    niveis_saida = []
    for level in niveis:
        opt, t_opt = transpile_measured(qc, level, seed, coupling_map=coupling_map)
        mo = circuit_metrics(opt)
        do = dist_ideal(opt)
        diff = tvd(db, do)
        niveis_saida.append({
            "level": int(level),
            "metrics": {**mo, "transpile_seconds": t_opt},
            "tvd": diff,
            "reducao": {
                "num_2q": _reducao(mb["num_2q"], mo["num_2q"]),
                "depth": _reducao(mb["depth"], mo["depth"]),
                "size": _reducao(mb["size"], mo["size"]),
            },
            "gates": {
                "tvd": diff <= TVD_TOL,
                "num_2q": mo["num_2q"] <= mb["num_2q"],
                "depth": mo["depth"] <= mb["depth"],
            },
            "status": (
                "pass"
                if diff <= TVD_TOL
                and mo["num_2q"] <= mb["num_2q"]
                and mo["depth"] <= mb["depth"]
                else "fail"
            ),
        })

    ruido_saida = []
    for p in ruidos:
        for level in (0, max(niveis)):
            counts = _contagens(qc, level, seed, p, shots)
            total = sum(counts.values())
            dist = {k: v / total for k, v in counts.items()}
            ruido_saida.append({
                "p": float(p),
                "level": int(level),
                "shots": int(shots),
                "tvd": tvd(dist, db),
            })

    aprovados = [n for n in niveis_saida if n["status"] == "pass"]
    melhor = min(
        aprovados or niveis_saida,
        key=lambda n: (n["metrics"]["num_2q"], n["metrics"]["depth"], n["level"]),
    )
    return {
        "name": nome,
        "experiment": experimento,
        "description": descricao,
        "seed": seed,
        "baseline": {**mb, "transpile_seconds": t_base},
        "niveis": niveis_saida,
        "melhor": melhor,
        "ruido": ruido_saida,
        "hardware": False,
        "network": False,
    }


def varrer_experimentos(
    seed: int = SEED_PADRAO,
    niveis=NIVEIS_PADRAO,
    ruidos=RUIDOS_PADRAO,
    shots: int = 2048,
    apenas: list[str] | None = None,
) -> dict:
    benchmarks = benchmarks_experimentos()
    if apenas:
        alvo = set(apenas)
        benchmarks = [b for b in benchmarks if b["experiment"] in alvo or b["name"] in alvo]
    resultados = [
        varrer_circuito(
            b["circuit"],
            b["name"],
            b["experiment"],
            b["description"],
            b.get("coupling_map"),
            seed,
            niveis,
            ruidos,
            shots,
        )
        for b in benchmarks
    ]
    resumo = {
        "circuitos": len(resultados),
        "experimentos": len({r["experiment"] for r in resultados}),
        "pass": sum(1 for r in resultados if r["melhor"]["status"] == "pass"),
        "fail": sum(1 for r in resultados if r["melhor"]["status"] != "pass"),
        "reducao_media_2q": mean(r["melhor"]["reducao"]["num_2q"] for r in resultados) if resultados else 0.0,
        "reducao_media_depth": mean(r["melhor"]["reducao"]["depth"] for r in resultados) if resultados else 0.0,
        "tvd_medio_melhor": mean(r["melhor"]["tvd"] for r in resultados) if resultados else 0.0,
    }
    return {
        "schema_version": 1,
        "seed": seed,
        "niveis": list(niveis),
        "ruidos": list(ruidos),
        "shots_ruido": shots,
        "resumo": resumo,
        "circuitos": resultados,
        "limites": (
            "Simulação e distribuição ideal; não é hardware. A TVD com ruído é "
            "um proxy do efeito do modelo depolarizante, não uma previsão de "
            "fidelidade de um backend real."
        ),
    }


def escrever_relatorio_experimentos(dados: dict, out_dir: Path) -> tuple[Path, Path]:
    import json
    from pathlib import Path

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "resultados_experimentos.json"
    json_path.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")

    linhas = [
        "# Eficiência nos experimentos E01–E18",
        "",
        f"Seed {dados['seed']} · níveis {dados['niveis']} · ruído {dados['ruidos']} · "
        f"{dados['shots_ruido']} tiros por ponto de ruído.",
        "",
        "## Protocolo",
        "",
        "- Baseline: `optimization_level=0`.",
        "- Varredura: níveis de otimização declarados.",
        "- Gate de correção: TVD ≤ `1e-9` entre as distribuições ideais.",
        "- Ruído: modelo depolarizante de porta (`u` 1q, `cx` 2q), sem hardware.",
        "",
        "## Resumo",
        "",
        f"- Circuitos: **{dados['resumo']['circuitos']}** em "
        f"**{dados['resumo']['experimentos']}** experimentos.",
        f"- Pass: **{dados['resumo']['pass']}** · Fail: **{dados['resumo']['fail']}**.",
        f"- Redução média de 2q: **{dados['resumo']['reducao_media_2q']:.1%}**.",
        f"- Redução média de profundidade: **{dados['resumo']['reducao_media_depth']:.1%}**.",
        f"- TVD médio do melhor nível: **{dados['resumo']['tvd_medio_melhor']:.3e}**.",
        "",
        "## Por circuito",
        "",
        "| Circuito | Exp. | Melhor nível | 2q base | 2q melhor | Δ2q | depth base | depth melhor | Δdepth | TVD | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for c in dados["circuitos"]:
        b = c["baseline"]
        m = c["melhor"]
        linhas.append(
            f"| {c['name']} | {c['experiment']} | {m['level']} | "
            f"{b['num_2q']} | {m['metrics']['num_2q']} | {m['reducao']['num_2q']:.1%} | "
            f"{b['depth']} | {m['metrics']['depth']} | {m['reducao']['depth']:.1%} | "
            f"{m['tvd']:.2e} | {m['status']} |"
        )

    linhas += [
        "",
        "## Ruído depolarizante",
        "",
        "| p | TVD baseline | TVD melhor nível | Δ |",
        "|---:|---:|---:|---:|",
    ]
    for p in dados["ruidos"]:
        t0 = [x["tvd"] for c in dados["circuitos"] for x in c["ruido"] if x["p"] == p and x["level"] == 0]
        t3 = [
            x["tvd"]
            for c in dados["circuitos"]
            for x in c["ruido"]
            if x["p"] == p and x["level"] == c["melhor"]["level"]
        ]
        if not t0 or not t3:
            continue
        m0 = sum(t0) / len(t0)
        m3 = sum(t3) / len(t3)
        linhas.append(f"| {p:g} | {m0:.4f} | {m3:.4f} | {(m3 - m0):+.4f} |")

    linhas += [
        "",
        f"> Em p = 0, a TVD reflete apenas o ruído de amostragem "
        f"({dados['shots_ruido']} tiros), não erro de porta.",
        "",
        "## Limites",
        "",
        "- Simulação e distribuição ideal; não é hardware.",
        "- A TVD com ruído é um proxy do modelo depolarizante, não uma previsão de fidelidade.",
        "- O resultado depende da versão do Qiskit, do seed e do conjunto de portas.",
        "- Redução de portas não é vantagem quântica.",
        "",
    ]
    md_path = out_dir / "RELATORIO_EXPERIMENTOS.md"
    md_path.write_text("\n".join(linhas), encoding="utf-8")
    return json_path, md_path
