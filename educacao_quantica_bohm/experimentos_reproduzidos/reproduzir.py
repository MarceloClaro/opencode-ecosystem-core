#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduz E01–E18 com protocolo estatístico mais forte.

Para cada experimento:
- executa os circuitos em AerSimulator com N sementes × S tiros;
- calcula a distribuição ideal por statevector, marginalizada nos bits
  clássicos efetivamente medidos;
- agrega os counts de todas as sementes;
- compara com o JSON simulado e o JSON real arquivados;
- registra TVD (distância de variação total), IC95% e leitura agregada.

Uso:
    python reproduzir.py
    python reproduzir.py --quick
    python reproduzir.py --only E01 E07 E10
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

from qiskit import transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro_pixel"
DADOS = RAIZ / "dados_experimentos"
SAIDA = Path(__file__).resolve().parent / "resultados"
sys.path.insert(0, str(LIVRO))

from base.base_experimentos import EXPERIMENTOS, circuitos, leitura  # noqa: E402

BASE_SEED = 20261109
T95 = {2: 12.706, 9: 2.262, 19: 2.093, 20: 2.093}


def agora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def medidas(qc) -> list[tuple[int, int]]:
    saida = []
    for instr in qc.data:
        if instr.operation.name == "measure":
            q = qc.find_bit(instr.qubits[0]).index
            c = qc.find_bit(instr.clbits[0]).index
            saida.append((q, c))
    return saida


def dist_ideal(qc) -> dict[str, float]:
    """Distribuição ideal nos bits clássicos medidos."""
    mapa = medidas(qc)
    limpo = qc.remove_final_measurements(inplace=False)
    probs = Statevector(limpo).probabilities_dict()
    n, m = qc.num_qubits, qc.num_clbits
    dist: dict[str, float] = {}
    for estado, prob in probs.items():
        bits = ["0"] * m
        for q, c in mapa:
            bits[m - 1 - c] = estado[n - 1 - q]
        chave = "".join(bits)
        dist[chave] = dist.get(chave, 0.0) + float(prob)
    return dist


def normalizar(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total else {}


def tvd(a: dict[str, float], b: dict[str, float]) -> float:
    return 0.5 * sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in set(a) | set(b))


def media_ic(valores: list[float], n_sementes: int) -> tuple[float, float]:
    media = statistics.mean(valores)
    if len(valores) < 2:
        return media, 0.0
    erro = statistics.stdev(valores) / math.sqrt(len(valores))
    return media, T95.get(n_sementes, 1.96) * erro


def rodar_circuito(qc, shots: int, seed: int, backend: AerSimulator):
    qc_t = transpile(qc, backend=backend, optimization_level=1)
    resultado = backend.run(qc_t, shots=shots, seed_simulator=seed).result()
    return {str(k): int(v) for k, v in resultado.get_counts().items()}


def carregar_arquivo(exp_id: str) -> dict | None:
    caminho = DADOS / f"{exp_id}.json"
    if not caminho.exists():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def _lista_counts(dados: dict | None, chave: str) -> list[dict[str, int]] | None:
    if not dados:
        return None
    bloco = dados.get(chave)
    if not bloco:
        return None
    counts = bloco.get("counts") if isinstance(bloco, dict) else None
    if not counts:
        return None
    return [dict(c) for c in counts]


def reproduzir(exp_id: str, shots: int, sementes: int) -> dict:
    exp = EXPERIMENTOS[exp_id]
    circuitos_exp = circuitos(exp_id)
    backend = AerSimulator()
    n_circ = len(circuitos_exp)

    ideais = [dist_ideal(qc) for qc in circuitos_exp]
    por_semente: list[list[dict[str, int]]] = []
    for s in range(sementes):
        rodada = []
        for i, qc in enumerate(circuitos_exp):
            seed = BASE_SEED + s * 100 + i
            rodada.append(rodar_circuito(qc, shots, seed, backend))
        por_semente.append(rodada)

    agregados: list[dict[str, int]] = []
    for i in range(n_circ):
        soma: Counter[str] = Counter()
        for rodada in por_semente:
            soma.update(rodada[i])
        agregados.append(dict(soma))

    dist_media: list[dict[str, float]] = []
    dist_ic: list[dict[str, list[float]]] = []
    for i in range(n_circ):
        dists = [normalizar(rodada[i]) for rodada in por_semente]
        chaves = sorted({k for d in dists for k in d})
        media = {k: statistics.mean(d.get(k, 0.0) for d in dists) for k in chaves}
        ic = {}
        for k in chaves:
            m, h = media_ic([d.get(k, 0.0) for d in dists], sementes)
            ic[k] = [m, h]
        dist_media.append(media)
        dist_ic.append(ic)

    tvd_por_semente = []
    for rodada in por_semente:
        valores = [tvd(normalizar(rodada[i]), ideais[i]) for i in range(n_circ)]
        tvd_por_semente.append(statistics.mean(valores))
    tvd_media, tvd_h = media_ic(tvd_por_semente, sementes)

    arquivo = carregar_arquivo(exp_id)
    sim_arquivo = _lista_counts(arquivo, "simulado")
    real_arquivo = _lista_counts(arquivo, "real")

    def tvd_lista(lista: list[dict[str, int]] | None) -> float | None:
        if not lista or len(lista) != n_circ:
            return None
        return statistics.mean(
            tvd(normalizar(lista[i]), ideais[i]) for i in range(n_circ)
        )

    comparacao = {
        "tvd_arquivo_simulado": tvd_lista(sim_arquivo),
        "tvd_arquivo_real": tvd_lista(real_arquivo),
    }
    if sim_arquivo and len(sim_arquivo) == n_circ:
        comparacao["tvd_reproduzido_vs_arquivo_simulado"] = statistics.mean(
            tvd(dist_media[i], normalizar(sim_arquivo[i])) for i in range(n_circ)
        )

    return {
        "id": exp_id,
        "nome": exp["nome"],
        "descricao": exp["descricao"],
        "protocolo": {
            "sementes": sementes,
            "shots_por_semente": shots,
            "total_shots": shots * sementes,
            "simulador": "AerSimulator",
            "transpilacao": "optimization_level=1",
            "seed_base": BASE_SEED,
        },
        "ideal": {
            "distribuicoes": ideais,
        },
        "reproduzido": {
            "dist_media": dist_media,
            "dist_ic95": dist_ic,
            "counts_agregados": agregados,
            "leitura_agregada": leitura(exp_id, agregados),
            "tvd_media": tvd_media,
            "tvd_ic95": [max(0.0, tvd_media - tvd_h), tvd_media + tvd_h],
        },
        "comparacao": comparacao,
        "limites": (
            "Simulação Aer; não é execução em hardware. A TVD mede diferença "
            "entre distribuições, não fidelidade de estado. O JSON real arquivado "
            "não foi reproduzido em hardware nesta rodada."
        ),
        "timestamp": agora(),
    }


def _celula(texto) -> str:
    return str(texto).replace("|", "&#124;")


def gerar_relatorio(resumo: dict) -> str:
    linhas = [
        "# Relatório de reprodução dos experimentos E01–E18",
        "",
        f"Gerado em {resumo['timestamp']}.",
        "",
        "## Protocolo",
        "",
        f"- Simulador: `{resumo['protocolo']['simulador']}`.",
        f"- Sementes por experimento: **{resumo['protocolo']['sementes']}**.",
        f"- Tiros por semente: **{resumo['protocolo']['shots_por_semente']}**.",
        f"- Total por experimento: **{resumo['protocolo']['total_shots']}** tiros.",
        "- Métrica principal: distância de variação total (TVD) contra a "
        "distribuição ideal; TVD menor é melhor.",
        "",
        "## Resultados",
        "",
        "| Exp. | Nome | Leitura agregada | TVD ideal | IC95 TVD | TVD arquivo simulado | TVD arquivo real |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for exp_id in sorted(resumo["experimentos"]):
        d = resumo["experimentos"][exp_id]
        rep = d["reproduzido"]
        comp = d["comparacao"]
        ic = rep["tvd_ic95"]
        real = comp.get("tvd_arquivo_real")
        real_txt = "—" if real is None else f"{real:.4f}"
        sim = comp.get("tvd_arquivo_simulado")
        sim_txt = "—" if sim is None else f"{sim:.4f}"
        linhas.append(
            f"| {exp_id} | {_celula(d['nome'])} | {_celula(rep['leitura_agregada'])} | "
            f"{rep['tvd_media']:.4f} | [{ic[0]:.4f}, {ic[1]:.4f}] | "
            f"{sim_txt} | {real_txt} |"
        )
    linhas += [
        "",
        "## Leitura",
        "",
        "- A TVD contra o ideal mede o erro de amostragem e a distância do "
        "circuito ao estado preparado; ela não mede fidelidade de estado.",
        "- O arquivo simulado original tem 1024 tiros em uma execução; a "
        "reprodução usa 81.920 tiros, então a TVD tende a ser menor apenas "
        "pelo tamanho da amostra.",
        "- O arquivo real foi coletado em hardware e não foi reproduzido em "
        "hardware nesta rodada; a coluna serve como referência, não como prova.",
        "- Nenhum job foi enviado ao GJQ/Tiangong.",
        "",
        "## Limites",
        "",
        "- Simulação clássica de circuitos pequenos; não há vantagem quântica.",
        "- O protocolo controla seed e shots, mas não corrige erros de calibração "
        "do hardware original.",
        "- A comparação com o JSON real é descritiva; não é replicação "
        "experimental nem teste de hipótese sobre o hardware.",
        "",
    ]
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", type=Path, default=SAIDA)
    args = ap.parse_args()

    shots = 1024 if args.quick else args.shots
    sementes = 2 if args.quick else args.seeds
    saida = args.out
    saida.mkdir(parents=True, exist_ok=True)
    ids = args.only or sorted(EXPERIMENTOS)
    resultados = {}
    for exp_id in ids:
        if exp_id not in EXPERIMENTOS:
            raise SystemExit(f"experimento desconhecido: {exp_id}")
        print(f"reproduzindo {exp_id} …")
        resultado = reproduzir(exp_id, shots, sementes)
        (saida / f"{exp_id}.json").write_text(
            json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        resultados[exp_id] = resultado
        print(f"  {resultado['reproduzido']['leitura_agregada']}")

    resumo = {
        "timestamp": agora(),
        "protocolo": {
            "simulador": "AerSimulator",
            "sementes": sementes,
            "shots_por_semente": shots,
            "total_shots": shots * sementes,
            "seed_base": BASE_SEED,
        },
        "experimentos": resultados,
    }
    (saida / "RESUMO.json").write_text(
        json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    relatorio = (
        Path(__file__).resolve().parent / "RELATORIO.md"
        if saida.resolve() == SAIDA.resolve()
        else saida / "RELATORIO.md"
    )
    relatorio.write_text(gerar_relatorio(resumo), encoding="utf-8")
    print(f"RESUMO: {saida / 'RESUMO.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
