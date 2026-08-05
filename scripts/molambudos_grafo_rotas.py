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
MISC = BOOK / "misc"
SAIDA = MISC / "grafo_narrativo.png"
SAIDA_ENREDO = MISC / "grafo_enredo.png"
SAIDA_LINEAR = MISC / "grafo_leitura_linear.png"

ROTA_RE = re.compile(r"\\rota\{([A-Z]{3,4}-(?:\d+|[A-Za-z][A-Za-z-]*))\}")
# Ordem linear canônica e divisão em partes vêm do próprio main.tex — não de
# uma lista mantida à mão, que foi como as legendas dos mapas 2 e 3 acabaram
# afirmando "78 fragmentos" muito depois de o corpus ter passado de 78.
PARTE_RE = re.compile(
    r"\\partopener\{[^}]*\}\{([^}]*)\}\{[^}]*\}|\\fragdef\{([A-Za-z0-9-]+)\}"
)

# Os três atos do Mapa 2 agrupam as cinco partes da leitura linear.
ATOS = (
    ("ATO 1 — O Trauma", ("Sertão",), "#8C6A3F"),
    ("ATO 2 — Institucionalização", ("Colônia", "Diário de Oliveira e Laudos"), "#4A5A6A"),
    ("ATO 3 — O Ciclo", ("Investigação Lúcia", "Contaminação"), "#8B2E2E"),
)
COR_PARTE = {
    "Sertão": "#8C6A3F",
    "Colônia": "#6E5A47",
    "Diário de Oliveira e Laudos": "#4A5A6A",
    "Investigação Lúcia": "#6B4A6B",
    "Contaminação": "#8B2E2E",
}


def ler_partes() -> list[tuple[str, list[str]]]:
    """[(nome da parte, [fragmentos na ordem])] extraído de main.tex."""
    texto = (BOOK / "main.tex").read_text(encoding="utf-8")
    partes: list[tuple[str, list[str]]] = []
    atual: tuple[str, list[str]] | None = None
    for m in PARTE_RE.finditer(texto):
        if m.group(1):
            atual = (m.group(1), [])
            partes.append(atual)
        elif atual is not None:
            atual[1].append(m.group(2))
    return partes

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


def _fig_sepia(largura: float, altura: float):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(largura, altura))
    fig.patch.set_facecolor("#F2E8CF")
    ax.set_facecolor("#F2E8CF")
    ax.axis("off")
    return fig, ax


def desenhar_enredo(arestas: list[tuple[str, str]], saida: Path) -> dict:
    """Mapa 2 — arquitetura em três atos: a estrutura causal, não as conexões.

    Cada ato ocupa uma faixa; as rotas internas ficam esmaecidas e as que
    **atravessam atos** ganham destaque, porque são elas que mostram como o
    trauma alimenta a institucionalização e esta alimenta o ciclo.
    """
    import matplotlib.patches as mpatches

    partes = dict(ler_partes())
    ato_de: dict[str, int] = {}
    membros: list[list[str]] = [[], [], []]
    for indice, (_, nomes, _) in enumerate(ATOS):
        for nome in nomes:
            for frag in partes.get(nome, []):
                ato_de[frag] = indice
                membros[indice].append(frag)

    fig, ax = _fig_sepia(24, 12)
    pos: dict[str, tuple[float, float]] = {}
    LARG = 30.0
    COLUNAS = 13
    PASSO = 0.95

    # Cada faixa tem altura proporcional ao seu conteúdo: o Ato 1 tem 9
    # fragmentos e o Ato 2 tem 41; caixas de mesma altura deixariam o primeiro
    # quase vazio e sugeririam um equilíbrio que a obra não tem.
    linhas_por_ato = [max(1, -(-len(f) // COLUNAS)) for f in membros]
    topo = 0.0
    limites: list[tuple[float, float]] = []
    for indice in range(len(ATOS) - 1, -1, -1):     # desenha de baixo para cima
        altura = linhas_por_ato[indice] * PASSO + 1.15
        limites.insert(0, (topo, altura))
        topo += altura + 0.55

    for indice, frags in enumerate(membros):
        y0, altura = limites[indice]
        for k, frag in enumerate(frags):
            linha, coluna = divmod(k, COLUNAS)
            pos[frag] = (1.5 + coluna * (LARG / COLUNAS),
                         y0 + altura - 0.75 - linha * PASSO)
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.3, y0), LARG + 1.6, altura,
            boxstyle="round,pad=0.12", linewidth=1.4,
            edgecolor=ATOS[indice][2], facecolor=ATOS[indice][2] + "18",
        ))
        ax.text(0.55, y0 + altura + 0.12, ATOS[indice][0], fontsize=17,
                family="serif", weight="bold", color=ATOS[indice][2], va="bottom")
        ax.text(LARG + 1.4, y0 + altura + 0.12, f"{len(frags)} fragmentos",
                fontsize=12, family="serif", style="italic", color="#5A4632",
                ha="right", va="bottom")

    entre_atos = 0
    for origem, destino in arestas:
        if origem not in pos or destino not in pos:
            continue
        xo, yo = pos[origem]
        xd, yd = pos[destino]
        cruza = ato_de.get(origem) != ato_de.get(destino)
        if cruza:
            entre_atos += 1
        ax.annotate(
            "", xy=(xd, yd), xytext=(xo, yo),
            arrowprops=dict(
                arrowstyle="-|>", color="#8B2E2E" if cruza else "#5A4632",
                alpha=0.55 if cruza else 0.13,
                linewidth=1.0 if cruza else 0.5,
                connectionstyle="arc3,rad=0.14", shrinkA=4, shrinkB=4,
            ),
        )
    for frag, (x, y) in pos.items():
        ax.plot(x, y, "o", markersize=9, color=ATOS[ato_de[frag]][2],
                markeredgecolor="#2E241A", markeredgewidth=0.6, zorder=3)
        ax.text(x, y - 0.3, frag, fontsize=5.6, ha="center", va="top",
                family="serif", color="#1A1410", zorder=4)

    ax.set_xlim(-0.4, LARG + 2.4)
    ax.set_ylim(-0.6, topo + 0.4)
    ax.set_title(
        "Molambudos — Mapa 2 · Arquitetura em Três Atos\n"
        f"{sum(len(m) for m in membros)} entradas · "
        f"{entre_atos} rotas atravessam atos (em vermelho): é por elas que o ciclo se propaga",
        fontsize=19, color="#2E241A", family="serif", pad=20,
    )
    fig.tight_layout()
    fig.savefig(saida, dpi=200, facecolor=fig.get_facecolor())
    import matplotlib.pyplot as plt
    plt.close(fig)
    return {"atos": [len(m) for m in membros], "rotas_entre_atos": entre_atos}


def desenhar_linear(saida: Path) -> dict:
    """Mapa 3 — percurso linear em serpentina, colorido por parte."""
    import matplotlib.patches as mpatches

    partes = ler_partes()
    seq = [(f, nome) for nome, frags in partes for f in frags]
    colunas = 9
    fig, ax = _fig_sepia(22, 13)
    ax.set_aspect("equal")

    pos: dict[str, tuple[float, float]] = {}
    for k, (frag, _) in enumerate(seq):
        linha, coluna = divmod(k, colunas)
        if linha % 2:                      # serpentina: linhas ímpares invertem
            coluna = colunas - 1 - coluna
        pos[frag] = (coluna * 2.4, -linha * 1.35)

    for k in range(len(seq) - 1):
        a, b = seq[k][0], seq[k + 1][0]
        muda_parte = seq[k][1] != seq[k + 1][1]
        ax.annotate(
            "", xy=pos[b], xytext=pos[a],
            arrowprops=dict(
                arrowstyle="-|>",
                color="#8B2E2E" if muda_parte else "#5A4632",
                linewidth=1.8 if muda_parte else 0.9,
                alpha=0.9 if muda_parte else 0.45,
                connectionstyle="arc3,rad=0.0" if not muda_parte else "arc3,rad=0.25",
                shrinkA=15, shrinkB=15,
            ),
        )
    for frag, nome in seq:
        x, y = pos[frag]
        cor = "#1A1410" if frag == "EPI-01" else COR_PARTE.get(nome, "#555555")
        ax.plot(x, y, "o", markersize=27, color=cor,
                markeredgecolor="#2E241A", markeredgewidth=0.9, zorder=3)
        ax.text(x, y, frag.replace("LUC-", "LUC\n").replace("CONT-", "CONT\n")
                .replace("MEM-", "MEM\n").replace("DOC-", "DOC\n")
                .replace("EPI-", "EPI\n"),
                fontsize=5.4, ha="center", va="center", linespacing=0.85,
                family="serif", color="#F2E8CF", weight="bold", zorder=4)

    ax.legend(
        handles=[mpatches.Patch(color=c, label=f"{n} ({len(dict(partes)[n])})")
                 for n, c in COR_PARTE.items() if n in dict(partes)],
        loc="lower center", ncol=5, frameon=True, facecolor="#EDE0C0",
        edgecolor="#5A4632", fontsize=12, title="Partes, na ordem de leitura",
        title_fontsize=13, bbox_to_anchor=(0.5, -0.06),
    )
    ax.set_title(
        "Molambudos — Mapa 3 · Percurso Linear\n"
        f"{len(seq) - 1} fragmentos + Epílogo, do Sertão (1914) ao fim do ciclo · "
        "as setas vermelhas marcam a passagem de uma parte para a seguinte",
        fontsize=19, color="#2E241A", family="serif", pad=20,
    )
    fig.tight_layout()
    fig.savefig(saida, dpi=200, facecolor=fig.get_facecolor())
    import matplotlib.pyplot as plt
    plt.close(fig)
    return {"partes": {n: len(f) for n, f in partes}, "total": len(seq)}


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
    p.add_argument("--mapa", choices=("rotas", "enredo", "linear", "todos"),
                   default="todos", help="qual mapa gerar (padrão: todos)")
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

    if args.stats:
        return 0

    if args.mapa in ("rotas", "todos"):
        desenhar(nos, arestas, args.saida)
        print(f"Mapa 1 (rotas)   -> {args.saida.relative_to(ROOT)}")
    if args.mapa in ("enredo", "todos"):
        info = desenhar_enredo(arestas, SAIDA_ENREDO)
        print(f"Mapa 2 (enredo)  -> {SAIDA_ENREDO.relative_to(ROOT)}  "
              f"atos={info['atos']} rotas entre atos={info['rotas_entre_atos']}")
    if args.mapa in ("linear", "todos"):
        info = desenhar_linear(SAIDA_LINEAR)
        print(f"Mapa 3 (linear)  -> {SAIDA_LINEAR.relative_to(ROOT)}  "
              f"total={info['total']}")
        for nome, qtd in info["partes"].items():
            print(f"     {nome}: {qtd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
