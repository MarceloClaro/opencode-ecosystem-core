"""
Mermaid Engine — Geração de diagramas científicos a partir de texto.
====================================================================

Gera diagramas Mermaid (fluxograma, sequência, mindmap, arquitetura)
a partir de outlines/manuscritos, e renderiza para PNG/SVG quando um
renderizador está disponível (mmdc / manus-render-diagram), com
fallback gracioso para o arquivo `.mmd` puro (renderizável no GitHub).

Uso:
    engine = MermaidEngine(output_dir="ilustracoes")
    fig = engine.flowchart("Pipeline", [("Busca", "Download"), ("Download", "Fichamento")])
    engine.render(fig)  # PNG se houver renderizador
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

RENDERERS = ["manus-render-diagram", "mmdc"]


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")[:60] or "diagrama"


def _sanitize_label(label: str) -> str:
    """Remove caracteres que quebram o parser Mermaid em labels."""
    return label.replace("(", "").replace(")", "").replace('"', "'").replace("[", "").replace("]", "").strip()


@dataclass
class MermaidFigure:
    """Uma figura Mermaid pronta para renderização e inclusão em documentos."""
    title: str
    code: str
    kind: str = "flowchart"
    caption: str = ""
    mmd_path: Optional[str] = None
    image_path: Optional[str] = None

    @property
    def slug(self) -> str:
        return _slugify(self.title)

    def latex_figure(self, label: Optional[str] = None) -> str:
        """Bloco LaTeX pronto para inserir na seção .tex."""
        label = label or f"fig:{self.slug}"
        img = self.image_path or f"{self.slug}.png"
        caption = self.caption or self.title
        return (
            "\\begin{figure}[htbp]\n"
            "  \\centering\n"
            f"  \\includegraphics[width=0.9\\textwidth]{{{img}}}\n"
            f"  \\caption{{{caption}}}\n"
            f"  \\label{{{label}}}\n"
            "\\end{figure}\n"
        )

    def markdown_block(self) -> str:
        """Bloco Markdown com o código Mermaid (renderiza nativamente no GitHub)."""
        return f"```mermaid\n{self.code}\n```\n"


class MermaidEngine:
    """Gera e renderiza diagramas Mermaid para produções científicas."""

    def __init__(self, output_dir: str = "ilustracoes"):
        self.output_dir = Path(output_dir)
        self.figures: List[MermaidFigure] = []

    # ------------------------------------------------------------------
    # Geradores de diagramas
    # ------------------------------------------------------------------
    def flowchart(self, title: str, edges: Sequence[Tuple[str, str]],
                  caption: str = "", direction: str = "TD") -> MermaidFigure:
        """Fluxograma a partir de pares (origem, destino)."""
        ids: Dict[str, str] = {}
        lines = [f"graph {direction}"]
        for src, dst in edges:
            for node in (src, dst):
                if node not in ids:
                    ids[node] = f"N{len(ids)}"
                    lines.append(f"    {ids[node]}[{_sanitize_label(node)}]")
            lines.append(f"    {ids[src]} --> {ids[dst]}")
        fig = MermaidFigure(title=title, code="\n".join(lines), kind="flowchart", caption=caption)
        self.figures.append(fig)
        return fig

    def sequence(self, title: str, interactions: Sequence[Tuple[str, str, str]],
                 caption: str = "") -> MermaidFigure:
        """Diagrama de sequência a partir de triplas (ator_a, ator_b, mensagem)."""
        lines = ["sequenceDiagram"]
        for a, b, msg in interactions:
            lines.append(f"    {_sanitize_label(a).replace(' ', '_')}->>{_sanitize_label(b).replace(' ', '_')}: {_sanitize_label(msg)}")
        fig = MermaidFigure(title=title, code="\n".join(lines), kind="sequence", caption=caption)
        self.figures.append(fig)
        return fig

    def mindmap(self, title: str, root: str, branches: Dict[str, List[str]],
                caption: str = "") -> MermaidFigure:
        """Mapa mental: raiz -> ramos -> folhas."""
        lines = ["mindmap", f"  root(({_sanitize_label(root)}))"]
        for branch, leaves in branches.items():
            lines.append(f"    {_sanitize_label(branch)}")
            for leaf in leaves:
                lines.append(f"      {_sanitize_label(leaf)}")
        fig = MermaidFigure(title=title, code="\n".join(lines), kind="mindmap", caption=caption)
        self.figures.append(fig)
        return fig

    def from_outline(self, title: str, outline: Sequence[str], caption: str = "") -> MermaidFigure:
        """Converte um outline (lista de seções) em fluxograma sequencial."""
        edges = [(outline[i], outline[i + 1]) for i in range(len(outline) - 1)]
        return self.flowchart(title, edges, caption=caption or f"Estrutura lógica: {title}")

    # ------------------------------------------------------------------
    # Renderização
    # ------------------------------------------------------------------
    def _find_renderer(self) -> Optional[str]:
        for r in RENDERERS:
            if shutil.which(r):
                return r
        return None

    def render(self, fig: MermaidFigure, fmt: str = "png") -> MermaidFigure:
        """Salva o .mmd e tenta renderizar para imagem; sempre preserva o .mmd."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mmd = self.output_dir / f"{fig.slug}.mmd"
        mmd.write_text(fig.code + "\n", encoding="utf-8")
        fig.mmd_path = str(mmd)

        renderer = self._find_renderer()
        if renderer:
            out = self.output_dir / f"{fig.slug}.{fmt}"
            try:
                if renderer == "manus-render-diagram":
                    cmd = [renderer, str(mmd), str(out)]
                else:  # mmdc
                    cmd = [renderer, "-i", str(mmd), "-o", str(out)]
                res = subprocess.run(cmd, capture_output=True, timeout=120)
                if res.returncode == 0 and out.exists():
                    fig.image_path = str(out)
            except Exception:
                pass
        return fig

    def render_all(self, fmt: str = "png") -> List[MermaidFigure]:
        return [self.render(f, fmt) for f in self.figures]
