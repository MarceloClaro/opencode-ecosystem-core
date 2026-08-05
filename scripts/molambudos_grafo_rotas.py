#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o mapa de grafo das rotas de Molambudos a partir dos fragmentos reais.

Os três PNGs em `misc/` eram estáticos, de 30/07/2026, e nenhum script os
produzia — ficaram defasados de todas as mudanças posteriores (expansão CONT,
conversão das linhas de navegação para `\\rota{}` no R389, deduplicação de
DOC-24/25/27 no R398). Um mapa que não acompanha o texto engana o leitor
exatamente onde ele mais precisa de precisão: na navegação.

Este script lê as chamadas `\\rota{}` dos fragmentos e desenha o grafo, de modo
que regenerá-lo seja um comando e não um trabalho manual.

    python3 -m scripts.molambudos_grafo_rotas            # gera o PNG
    python3 -m scripts.molambudos_grafo_rotas --stats    # só as métricas

Cores por família de fragmento, iguais às do livro (misc/options.sty):
MEM (memórias), DOC (documentos), LUC (investigação), CONT (contaminação).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
FRAGMENTOS = BOOK / "fragmentos"
SAIDA = BOOK / "misc" / "grafo_narrativo.png"

ROTA_RE = re.compile(r"\\rota\{([A-Z]{3,4}-(?:\d+|[A-Za-z][A-Za-z-]*))\}")

CORES = {
    "MEM": "#8C6A3F",   # sépia queimado — memórias
    "DOC": "#4A5A6A",   # azul-ardósia — documentos
    "LUC": "#6B4A6B",   # roxo acinzentado — investigação
    "CONT": "#8B2E2E",  # sangue — contaminação
    "EPI": "#1A1410",   # fundo escuro — o Epílogo, sorvedouro do grafo
}
FAMILIA = {
    "MEM": "Memórias", "DOC": "Documentos", "LUC": "Investigação",
    "CONT": "Contaminação", "EPI": "Epílogo (convergência)",
}

# O Epílogo não tem arquivo de fragmento — é capítulo inline em main*.tex,
# ancorado por \fragdef{EPI-01}. É nó legítimo do grafo e seu sorvedouro:
# toda rota leva até ele e dele não sai nenhuma.
EPILOGO = "EPI-01"


def familia(fid: str) -> str:
    return fid.split("-", 1)[0]


def ler_rotas() -> tuple[list[str], list[tuple[str, str]]]:
    """(fragmentos, arestas) lidos do corpus PT."""
    nos: list[str] = []
    arestas: list[tuple[str, str]] = []
    for path in sorted(FRAGMENTOS.rglob("*.tex")):
        origem = path.stem
        nos.append(origem)
        texto = path.read_text(encoding="utf-8")
        # Só a linha de navegação no fim do fragmento conta como rota de leitura;
        # `\rota{}` no corpo (raro) também é um salto oferecido ao leitor.
        for destino in ROTA_RE.findall(texto):
            arestas.append((origem, destino))
    nos.append(EPILOGO)
    return nos, arestas


def estatisticas(nos: list[str], arestas: list[tuple[str, str]]) -> dict:
    import networkx as nx

    g = nx.DiGraph()
    g.add_nodes_from(nos)
    g.add_edges_from(arestas)
    entrada = Counter(d for _, d in arestas)
    saida = Counter(o for o, _ in arestas)
    orfaos = sorted(n for n in nos if entrada.get(n, 0) == 0)
    # O Epílogo é sorvedouro por projeto: não emite rotas, e isso não é beco.
    becos = sorted(n for n in nos if saida.get(n, 0) == 0 and n != EPILOGO)
    quebradas = sorted({d for _, d in arestas if d not in set(nos)})

    reverso = g.reverse()
    alcancam = nx.descendants(reverso, EPILOGO) if EPILOGO in g else set()
    sem_saida_para_o_fim = sorted(set(nos) - alcancam - {EPILOGO})

    ciclos = [c for c in nx.strongly_connected_components(g) if len(c) > 1]
    aprisionantes = [
        sorted(c) for c in ciclos
        if not any(d not in c for n in c for d in g.successors(n))
    ]

    return {
        "fragmentos": len(nos) - 1,          # EPI-01 é capítulo, não fragmento
        "rotas": len(arestas),
        "destinos_distintos": len(set(d for _, d in arestas)),
        "sem_entrada": orfaos,
        "sem_saida": becos,
        "destinos_inexistentes": quebradas,
        "nao_alcancam_o_epilogo": sem_saida_para_o_fim,
        "ciclos": len(ciclos),
        "maior_ciclo": max((len(c) for c in ciclos), default=0),
        "ciclos_que_aprisionam": aprisionantes,
        "mais_referenciados": entrada.most_common(8),
        "componentes_fracos": nx.number_weakly_connected_components(g),
    }


def desenhar(nos: list[str], arestas: list[tuple[str, str]], saida: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import networkx as nx

    g = nx.DiGraph()
    g.add_nodes_from(nos)
    g.add_edges_from((o, d) for o, d in arestas if d in set(nos))

    pos = nx.nx_agraph.graphviz_layout(g, prog="sfdp") if _tem_pygraphviz() else \
        nx.spring_layout(g, k=0.55, iterations=260, seed=17)

    entrada = Counter(d for _, d in g.edges())
    tamanhos = [220 + 130 * entrada.get(n, 0) for n in g.nodes()]
    cores = [CORES.get(familia(n), "#555555") for n in g.nodes()]

    fig, ax = plt.subplots(figsize=(22, 16))
    fig.patch.set_facecolor("#F2E8CF")     # sépia do miolo
    ax.set_facecolor("#F2E8CF")

    nx.draw_networkx_edges(
        g, pos, ax=ax, edge_color="#5A4632", width=0.7, alpha=0.42,
        arrows=True, arrowsize=8, arrowstyle="-|>",
        connectionstyle="arc3,rad=0.08", node_size=tamanhos,
    )
    nx.draw_networkx_nodes(
        g, pos, ax=ax, node_size=tamanhos, node_color=cores,
        edgecolors="#2E241A", linewidths=0.8, alpha=0.95,
    )
    nx.draw_networkx_labels(
        g, pos, ax=ax, font_size=7.2, font_color="#1A1410",
        font_family="serif", font_weight="bold",
    )

    ax.legend(
        handles=[mpatches.Patch(color=c, label=FAMILIA[f]) for f, c in CORES.items()],
        loc="lower left", frameon=True, facecolor="#EDE0C0", edgecolor="#5A4632",
        fontsize=13, title="Famílias de fragmento", title_fontsize=14,
    )
    ax.set_title(
        f"Molambudos — Grafo de Leitura: {len(g.nodes())} fragmentos, "
        f"{len(g.edges())} rotas\n"
        "O tamanho do nó cresce com o número de rotas que chegam até ele",
        fontsize=19, color="#2E241A", family="serif", pad=22,
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(saida, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)


def _tem_pygraphviz() -> bool:
    try:
        import pygraphviz  # noqa: F401
        return True
    except ImportError:
        return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stats", action="store_true", help="só imprime métricas")
    p.add_argument("--json", action="store_true")
    p.add_argument("--saida", type=Path, default=SAIDA)
    args = p.parse_args(argv)

    nos, arestas = ler_rotas()
    st = estatisticas(nos, arestas)

    if args.json:
        print(json.dumps(st, ensure_ascii=False, indent=2))
    else:
        print(f"fragmentos: {st['fragmentos']} | rotas: {st['rotas']} | "
              f"destinos distintos: {st['destinos_distintos']}")
        print(f"componentes fracamente conexos: {st['componentes_fracos']}")
        print(f"ciclos: {st['ciclos']} (maior: {st['maior_ciclo']}) | "
              f"que aprisionam o leitor: {len(st['ciclos_que_aprisionam'])}")
        alcancam = st["fragmentos"] - len(st["nao_alcancam_o_epilogo"])
        print(f"alcançam o Epílogo: {alcancam}/{st['fragmentos']}")
        if st["destinos_inexistentes"]:
            print(f"  ROTAS QUEBRADAS: {st['destinos_inexistentes']}")
        if st["nao_alcancam_o_epilogo"]:
            print(f"  NÃO ALCANÇAM O EPÍLOGO: {st['nao_alcancam_o_epilogo']}")
        if st["ciclos_que_aprisionam"]:
            print(f"  CICLOS SEM SAÍDA: {st['ciclos_que_aprisionam']}")
        if st["sem_entrada"]:
            print(f"  sem rota de entrada: {st['sem_entrada']}")
        if st["sem_saida"]:
            print(f"  sem rota de saída: {st['sem_saida']}")
        print(f"  mais referenciados: {st['mais_referenciados']}")

    if not args.stats:
        desenhar(nos, arestas, args.saida)
        print(f"grafo gravado: {args.saida.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
