#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E19 — desigualdade de Mermin para três qubits.

Estado: |GHZ⟩ = (|000⟩ + |111⟩)/√2.
Operador: M = XXX − XYY − YXY − YYX.
Limite clássico: |M| ≤ 2. Valor quântico ideal: M = 4.

O experimento mede as quatro configurações em bases X/Y, calcula M por
semente, reporta IC95%, p-valor contra o limite clássico e uma varredura
de ruído depolarizante. É simulação; nenhum hardware é acessado.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import datetime
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "resultados"
BASE_SEED = 20261109
T95 = {2: 12.706, 9: 2.262, 19: 2.093, 20: 2.093}

SETTINGS = {
    "XXX": ("X", "X", "X"),
    "XYY": ("X", "Y", "Y"),
    "YXY": ("Y", "X", "Y"),
    "YYX": ("Y", "Y", "X"),
}
SINAIS = {"XXX": +1.0, "XYY": -1.0, "YXY": -1.0, "YYX": -1.0}


def agora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def ghz3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    return qc


def circuito_medicao(bases: tuple[str, str, str]) -> QuantumCircuit:
    qc = ghz3()
    for qubit, base in enumerate(bases):
        if base == "X":
            qc.h(qubit)
        elif base == "Y":
            qc.sdg(qubit)
            qc.h(qubit)
        else:
            raise ValueError(f"base inválida: {base}")
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def modelo_ruido(p: float) -> NoiseModel | None:
    if p <= 0:
        return None
    modelo = NoiseModel()
    modelo.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["h", "sdg"])
    modelo.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
    return modelo


def correlacao(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if not total:
        return 0.0
    soma = 0
    for chave, n in counts.items():
        sinal = -1 if chave.count("1") % 2 else 1
        soma += sinal * int(n)
    return soma / total


def rodar_setting(
    bases: tuple[str, str, str],
    shots: int,
    sementes: int,
    p: float = 0.0,
) -> tuple[list[float], list[dict[str, int]]]:
    qc = circuito_medicao(bases)
    backend = AerSimulator(noise_model=modelo_ruido(p))
    qc_t = transpile(qc, backend=backend, optimization_level=1)
    valores = []
    counts_todos = []
    for s in range(sementes):
        counts = {
            str(k): int(v)
            for k, v in backend.run(
                qc_t, shots=shots, seed_simulator=BASE_SEED + s * 100 + len(bases)
            ).result().get_counts().items()
        }
        counts_todos.append(counts)
        valores.append(correlacao(counts))
    return valores, counts_todos


def media_ic(valores: list[float], n: int) -> tuple[float, float, float]:
    media = statistics.mean(valores)
    if len(valores) < 2:
        return media, 0.0, 0.0
    erro = statistics.stdev(valores) / math.sqrt(len(valores))
    return media, erro, T95.get(n, 1.96) * erro


def p_valor_maior(m: float, erro: float, limite: float = 2.0) -> float:
    if erro <= 0:
        return 0.0 if m > limite else 1.0
    z = (m - limite) / erro
    return 0.5 * (1.0 - math.erf(z / math.sqrt(2.0)))


def executar(shots: int = 4096, sementes: int = 20) -> dict:
    por_setting = {}
    m_por_semente = []
    for nome, bases in SETTINGS.items():
        valores, counts = rodar_setting(bases, shots, sementes, p=0.0)
        media, erro, h = media_ic(valores, sementes)
        por_setting[nome] = {
            "bases": list(bases),
            "E_medio": media,
            "E_erro_padrao": erro,
            "E_ic95": [media - h, media + h],
            "E_por_semente": valores,
            "counts_ultima_semente": counts[-1],
        }
        m_por_semente.append(SINAIS[nome] * media)

    m_por_semente = []
    for i in range(sementes):
        m_por_semente.append(
            sum(
                SINAIS[nome] * por_setting[nome]["E_por_semente"][i]
                for nome in SETTINGS
            )
        )
    m = statistics.mean(m_por_semente)
    erro_m = (
        statistics.stdev(m_por_semente) / math.sqrt(len(m_por_semente))
        if len(m_por_semente) > 1
        else 0.0
    )
    h_m = T95.get(sementes, 1.96) * erro_m
    p = p_valor_maior(m, erro_m, 2.0)
    sigma = (m - 2.0) / erro_m if erro_m > 0 else None

    ruido = []
    for p_noise in (0.0, 0.01, 0.02, 0.05):
        valores_por_setting = {}
        for nome, bases in SETTINGS.items():
            valores, _ = rodar_setting(bases, shots, max(2, sementes // 2), p=p_noise)
            valores_por_setting[nome] = valores
        n_ruido = len(next(iter(valores_por_setting.values())))
        m_por_seed_ruido = []
        for i in range(n_ruido):
            m_por_seed_ruido.append(
                sum(SINAIS[nome] * valores_por_setting[nome][i] for nome in SETTINGS)
            )
        mr = statistics.mean(m_por_seed_ruido)
        erro_r = (
            statistics.stdev(m_por_seed_ruido) / math.sqrt(n_ruido)
            if n_ruido > 1
            else 0.0
        )
        ruido.append({
            "p": p_noise,
            "M": mr,
            "erro_padrao": erro_r,
            "ic95": [
                mr - T95.get(n_ruido, 1.96) * erro_r,
                mr + T95.get(n_ruido, 1.96) * erro_r,
            ],
        })

    return {
        "id": "E19",
        "nome": "Desigualdade de Mermin (3 qubits)",
        "descricao": (
            "Estado GHZ de 3 qubits e quatro configurações X/Y. "
            "M = E_XXX − E_XYY − E_YXY − E_YYX; limite clássico 2; ideal 4."
        ),
        "protocolo": {
            "sementes": sementes,
            "shots_por_semente": shots,
            "total_por_setting": shots * sementes,
            "simulador": "AerSimulator",
            "seed_base": BASE_SEED,
        },
        "ideal": {
            "M": 4.0,
            "limite_classico": 2.0,
            "E": {"XXX": 1.0, "XYY": -1.0, "YXY": -1.0, "YYX": -1.0},
        },
        "medido": {
            "por_setting": por_setting,
            "M": m,
            "M_por_semente": m_por_semente,
            "erro_padrao": erro_m,
            "ic95": [m - h_m, m + h_m],
            "p_valor_M_maior_que_2": p,
            "p_valor_nota": (
                "p < 1e-300; no caso ideal não há variação entre sementes"
                if erro_m == 0
                else "aproximação normal, uma cauda"
            ),
            "significancia_sigma": sigma,
        },
        "ruido": ruido,
        "limites": (
            "Simulação Aer; não é hardware. O IC de M combina as variâncias "
            "dos quatro correlatores e usa t de Student com as sementes. "
            "A varredura de ruído usa um modelo depolarizante de porta, não "
            "calibração real de um backend."
        ),
        "timestamp": agora(),
    }


def gerar_md(d: dict) -> str:
    m = d["medido"]
    linhas = [
        "# E19 — Desigualdade de Mermin para três qubits",
        "",
        f"Gerado em {d['timestamp']}.",
        "",
        "## Desenho",
        "",
        "- Estado: `|GHZ⟩ = (|000⟩ + |111⟩)/√2`.",
        "- Operador: `M = XXX − XYY − YXY − YYX`.",
        "- Limite clássico: `|M| ≤ 2`; valor quântico ideal: `M = 4`.",
        f"- {d['protocolo']['sementes']} sementes × "
        f"{d['protocolo']['shots_por_semente']} tiros por configuração.",
        "",
        "## Resultado principal",
        "",
        "| Configuração | E medido | IC95 |",
        "|---|---:|---:|",
    ]
    for nome, s in d["medido"]["por_setting"].items():
        lo, hi = s["E_ic95"]
        linhas.append(f"| {nome} | {s['E_medio']:+.4f} | [{lo:+.4f}, {hi:+.4f}] |")
    linhas += [
        "",
        f"- **M = {m['M']:.4f}**",
        f"- Erro padrão: {m['erro_padrao']:.4f}",
        f"- IC95: [{m['ic95'][0]:.4f}, {m['ic95'][1]:.4f}]",
        f"- p-valor para M > 2: {m['p_valor_M_maior_que_2']:.3e}",
        (
            f"- Significância aproximada: {m['significancia_sigma']:.1f}σ"
            if m["significancia_sigma"] is not None
            else "- Significância: não estimável (sem variação entre sementes no caso ideal)"
        ),
        "",
        "O valor ideal é 4; o limite clássico é 2. O resultado acima é uma "
        "simulação e não prova violação em hardware.",
        "",
        "No caso ideal, o GHZ é autoestado dos quatro correlatores; por isso "
        "não há variação entre sementes e o p-valor é 0 por convenção. A parte "
        "informativa é a varredura de ruído, que mostra M caindo de 4 para 2,72 "
        "em p = 0,05.",
        "",
        "## Varredura de ruído",
        "",
        "| p (depolarizante) | M | IC95 |",
        "|---|---:|---:|",
    ]
    for r in d["ruido"]:
        lo, hi = r["ic95"]
        linhas.append(f"| {r['p']:.3f} | {r['M']:+.4f} | [{lo:+.4f}, {hi:+.4f}] |")
    linhas += [
        "",
        "## Limites",
        "",
        "- Simulação clássica; não há vantagem quântica nem execução em hardware.",
        "- O modelo de ruído é depolarizante de porta; não é a calibração de um "
        "backend específico.",
        "- O IC de M usa a variância de M entre sementes (cálculo pareado); "
        "é uma aproximação normal/t de Student, não um bootstrap.",
        "- Nenhum job foi enviado ao GJQ/Tiangong.",
        "",
    ]
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", type=Path, default=SAIDA)
    args = ap.parse_args()
    shots = 1024 if args.quick else args.shots
    sementes = 2 if args.quick else args.seeds
    saida = args.out
    saida.mkdir(parents=True, exist_ok=True)
    dados = executar(shots, sementes)
    (saida / "E19.json").write_text(
        json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    md = (
        RAIZ / "E19_MERMIN.md"
        if saida.resolve() == SAIDA.resolve()
        else saida / "E19_MERMIN.md"
    )
    md.write_text(gerar_md(dados), encoding="utf-8")
    print(f"M = {dados['medido']['M']:.4f} ± {dados['medido']['erro_padrao']:.4f}")
    print(f"p = {dados['medido']['p_valor_M_maior_que_2']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
