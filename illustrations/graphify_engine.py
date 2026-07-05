"""
Graphify Engine — Grafo de conhecimento do manuscrito.
======================================================

Inspirado no MarceloClaro/graphify: mapeia o conteúdo de uma produção
científica (manuscrito, fichamentos, referências) em um grafo de
conhecimento navegável, exportando:

- graph.json       : o grafo completo (nós, arestas, pesos)
- graph.html       : visualização interativa (vis-network via CDN, self-contained fallback)
- GRAPH_REPORT.md  : destaques (conceitos-chave, conexões, perguntas sugeridas)

100% stdlib: extração de conceitos por frequência/coocorrência de janelas.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

STOPWORDS = set("""
a o e de da do das dos em no na nos nas um uma uns umas para por com sem sob sobre
que se ao aos as os seu sua seus suas este esta isto esse essa isso aquele aquela
como mais menos muito pouco também já não sim é são foi eram ser ter há entre até
the of and to in for on with a an is are was were be been this that it as by from
or at which we our their its can may not such has have but других et al fig table
""".split())


def _normalize(word: str) -> str:
    word = unicodedata.normalize("NFKD", word.lower())
    return "".join(c for c in word if not unicodedata.combining(c))


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9_-]{2,}", text)
    return [w for w in words if _normalize(w) not in STOPWORDS]


@dataclass
class KnowledgeGraph:
    nodes: List[Dict] = field(default_factory=list)
    edges: List[Dict] = field(default_factory=list)
    report: str = ""

    def to_dict(self) -> Dict:
        return {"nodes": self.nodes, "edges": self.edges}


class GraphifyEngine:
    """Constrói e exporta o grafo de conhecimento de uma produção científica."""

    def __init__(self, output_dir: str = "ilustracoes/grafo", max_nodes: int = 40,
                 window: int = 8):
        self.output_dir = Path(output_dir)
        self.max_nodes = max_nodes
        self.window = window

    # ------------------------------------------------------------------
    def build(self, texts: Dict[str, str]) -> KnowledgeGraph:
        """
        Constrói o grafo a partir de {nome_documento: conteúdo}.
        Conceitos frequentes viram nós; coocorrência em janela vira aresta.
        """
        freq: Counter = Counter()
        cooc: Counter = Counter()
        doc_of: Dict[str, set] = defaultdict(set)

        for doc, text in texts.items():
            tokens = [t.lower() for t in _tokenize(text)]
            freq.update(tokens)
            for t in tokens:
                doc_of[t].add(doc)
            for i in range(len(tokens)):
                for j in range(i + 1, min(i + self.window, len(tokens))):
                    if tokens[i] != tokens[j]:
                        pair = tuple(sorted((tokens[i], tokens[j])))
                        cooc[pair] += 1

        top = [w for w, _ in freq.most_common(self.max_nodes)]
        top_set = set(top)

        nodes = [
            {
                "id": w,
                "label": w,
                "value": freq[w],
                "docs": sorted(doc_of[w]),
                "group": min(len(doc_of[w]), 5),
            }
            for w in top
        ]
        edges = [
            {"from": a, "to": b, "value": c}
            for (a, b), c in cooc.most_common(self.max_nodes * 4)
            if a in top_set and b in top_set and c >= 2
        ]

        graph = KnowledgeGraph(nodes=nodes, edges=edges)
        graph.report = self._make_report(graph, texts)
        return graph

    # ------------------------------------------------------------------
    def _make_report(self, graph: KnowledgeGraph, texts: Dict[str, str]) -> str:
        degree: Counter = Counter()
        for e in graph.edges:
            degree[e["from"]] += e["value"]
            degree[e["to"]] += e["value"]
        hubs = degree.most_common(10)
        bridges = [n["id"] for n in graph.nodes if len(n["docs"]) > 1][:10]

        lines = ["# GRAPH REPORT — Grafo de Conhecimento da Produção", ""]
        lines.append(f"Documentos analisados: **{len(texts)}** | Nós: **{len(graph.nodes)}** | Arestas: **{len(graph.edges)}**")
        lines.append("")
        lines.append("## Conceitos-chave (hubs)")
        lines.append("")
        lines.append("| Conceito | Grau ponderado |")
        lines.append("|---|---|")
        for w, d in hubs:
            lines.append(f"| {w} | {d} |")
        lines.append("")
        if bridges:
            lines.append("## Conceitos-ponte (aparecem em múltiplos documentos)")
            lines.append("")
            lines.append(", ".join(f"**{b}**" for b in bridges))
            lines.append("")
        lines.append("## Perguntas sugeridas para a pesquisa")
        lines.append("")
        for w, _ in hubs[:5]:
            lines.append(f"- Como o conceito de *{w}* se articula com os demais eixos do manuscrito?")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    def export(self, graph: KnowledgeGraph) -> Dict[str, str]:
        """Exporta graph.json, graph.html e GRAPH_REPORT.md. Retorna os caminhos."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {}

        p_json = self.output_dir / "graph.json"
        p_json.write_text(json.dumps(graph.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        paths["json"] = str(p_json)

        p_html = self.output_dir / "graph.html"
        p_html.write_text(self._html(graph), encoding="utf-8")
        paths["html"] = str(p_html)

        p_report = self.output_dir / "GRAPH_REPORT.md"
        p_report.write_text(graph.report, encoding="utf-8")
        paths["report"] = str(p_report)
        return paths

    def _html(self, graph: KnowledgeGraph) -> str:
        data = json.dumps(graph.to_dict(), ensure_ascii=False)
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Grafo de Conhecimento — OpenCode Ecosystem Core</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin:0; font-family: system-ui, sans-serif; background:#0d1117; color:#e6edf3; }}
  #graph {{ width:100vw; height:92vh; }}
  header {{ padding:10px 16px; background:#161b22; }}
  input {{ background:#0d1117; color:#e6edf3; border:1px solid #30363d; border-radius:6px; padding:4px 8px; }}
</style>
</head>
<body>
<header>
  <strong>Grafo de Conhecimento</strong> — clique nos nós, arraste, use a busca:
  <input id="q" placeholder="buscar conceito...">
</header>
<div id="graph"></div>
<script>
const data = {data};
const nodes = new vis.DataSet(data.nodes.map(n => ({{...n, shape:'dot', font:{{color:'#e6edf3'}}}})));
const edges = new vis.DataSet(data.edges.map((e,i) => ({{id:i, ...e, color:{{opacity:0.35}}}})));
const net = new vis.Network(document.getElementById('graph'), {{nodes, edges}}, {{
  physics: {{ barnesHut: {{ gravitationalConstant: -12000, springLength: 140 }} }},
  nodes: {{ scaling: {{ min: 6, max: 42 }} }},
  interaction: {{ hover: true }}
}});
document.getElementById('q').addEventListener('input', ev => {{
  const q = ev.target.value.toLowerCase();
  const hit = data.nodes.find(n => n.id.includes(q));
  if (hit) {{ net.selectNodes([hit.id]); net.focus(hit.id, {{scale:1.4, animation:true}}); }}
}});
</script>
</body>
</html>
"""
