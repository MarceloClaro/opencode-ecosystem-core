"""
Illustrations — Subsistema de ilustrações científicas do OpenCode Ecosystem Core.

Motores:
- MermaidEngine: diagramas (fluxograma, sequência, mindmap) renderizados para PNG/SVG.
- GraphifyEngine: grafo de conhecimento do manuscrito (graph.json/html + relatório).
- MiraEngine: cards HTML animados com metáforas visuais (Regra Zero: loop perpétuo).
"""

from .mermaid_engine import MermaidEngine, MermaidFigure
from .graphify_engine import GraphifyEngine, KnowledgeGraph
from .mira_engine import MiraEngine, MiraCard, CATALOG as MIRA_CATALOG
from .mira_deck import (
    MiraDeckPipeline, Briefing, Section, SlideSpec, SlidePlan, Deck,
    ConformityReport,
)

__all__ = [
    "MermaidEngine", "MermaidFigure",
    "GraphifyEngine", "KnowledgeGraph",
    "MiraEngine", "MiraCard", "MIRA_CATALOG",
    "MiraDeckPipeline", "Briefing", "Section", "SlideSpec", "SlidePlan",
    "Deck", "ConformityReport",
]
