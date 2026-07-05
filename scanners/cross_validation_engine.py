#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CrossValidationEngine v1.0 — Validação Cruzada Evolutiva (Módulo 3)

Identifica dependências ocultas entre capacidades e modela efeitos cascata.

Regras de inferência:
  R1 (Prerequisite): Se A requer B e B está ausente → A é inviável
  R2 (Cascade): Se A habilita B,C,D e A está ausente → B,C,D em risco
  R3 (Co-occurrence): A e B aparecem juntos em >80% dos sistemas → alta afinidade
  R4 (Bottleneck): Se A é prerequisite de >3 capacidades → bottleneck crítico
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CapabilityNode:
    """Nó no grafo de dependências entre capacidades."""
    name: str
    domain: str
    category: str
    provides: list[str] = field(default_factory=list)   # capacidades que habilita
    requires: list[str] = field(default_factory=list)    # capacidades das quais depende
    influence_score: float = 0.0
    cascade_impact: float = 0.0
    composition: Any | None = None  # SPEC-033: CapabilityUnit opcional


@dataclass
class DependencyEdge:
    """Aresta direcionada no grafo de dependências."""
    source: str          # "raciocinio.probabilistico"
    target: str          # "metodos.quantitativo_experimental"
    weight: float        # força da dependência (0-1)
    relation: str        # "requires" | "enables" | "co_occurs"


# ═══════════════════════════════════════════════════════════════════════════
# REGRAS DE DEPENDÊNCIA ENTRE CAPACIDADES
# ═══════════════════════════════════════════════════════════════════════════

# (source_domain.category, target_domain.category, weight, relation)
DEPENDENCY_RULES: list[tuple[str, str, float, str]] = [
    # ─── Prerequisites (requires) ────────────────────────────────────────
    ("metodos.Quantitativo experimental", "raciocinio.Probabilístico", 0.8, "requires"),
    ("metodos.Quantitativo experimental", "raciocinio.Dedutivo", 0.7, "requires"),
    ("metodos.Quantitativo correlacional", "raciocinio.Probabilístico", 0.6, "requires"),
    ("metodos.Meta-análise", "raciocinio.Probabilístico", 0.9, "requires"),
    ("metodos.Meta-análise", "dados.Metadados (revisões)", 0.8, "requires"),
    ("metodos.Revisão sistemática", "dados.Metadados (revisões)", 0.7, "requires"),
    ("dados.Dados longitudinais", "temporalidade.Longitudinal (longo prazo)", 0.9, "requires"),
    ("dados.Dados epidemiológicos", "populacao.Contexto clínico", 0.7, "requires"),
    ("dados.Dados comparativos (cross-cultural)", "populacao.Cross-cultural", 0.8, "requires"),
    ("raciocinio.Contrafactual", "raciocinio.Probabilístico", 0.5, "requires"),
    ("raciocinio.Probabilístico", "raciocinio.Dedutivo", 0.5, "requires"),
    
    # ─── Enablers (habilita) ────────────────────────────────────────────
    ("raciocinio.Probabilístico", "metodos.Meta-análise", 0.9, "enables"),
    ("raciocinio.Probabilístico", "raciocinio.Bayesiano", 0.8, "enables"),
    ("raciocinio.Probabilístico", "raciocinio.Contrafactual", 0.6, "enables"),
    ("raciocinio.Sistêmico", "niveis_analise.Sistêmico/político", 0.7, "enables"),
    ("raciocinio.Sistêmico", "dominios.Neurociências", 0.5, "enables"),
    ("temporalidade.Longitudinal (longo prazo)", "dados.Dados longitudinais", 0.9, "enables"),
    ("temporalidade.Longitudinal (longo prazo)", "raciocinio.Probabilístico", 0.6, "enables"),
    ("paradigmas.Complexo/Sistêmico", "raciocinio.Sistêmico", 0.8, "enables"),
    ("paradigmas.Complexo/Sistêmico", "dominios.Sociologia", 0.5, "enables"),
    ("paradigmas.Pragmatista", "metodos.Misto sequencial", 0.7, "enables"),
    ("paradigmas.Pragmatista", "metodos.Misto convergente", 0.7, "enables"),
    ("teoria_jogos.Equilíbrio de Nash", "raciocinio.Probabilístico", 0.6, "enables"),
    ("teoria_jogos.Equilíbrio de Nash", "raciocinio.Contrafactual", 0.5, "enables"),
    ("teoria_jogos.Cooperativo", "niveis_analise.Sistêmico/político", 0.5, "enables"),
    
    # ─── Co-occurrence (alta afinidade) ─────────────────────────────────
    ("paradigmas.Fenomenológico", "metodos.Qualitativo fenomenológico", 0.95, "co_occurs"),
    ("paradigmas.Fenomenológico", "dados.Dados qualitativos (entrevistas)", 0.90, "co_occurs"),
    ("paradigmas.Positivista", "metodos.Quantitativo experimental", 0.90, "co_occurs"),
    ("paradigmas.Positivista", "raciocinio.Dedutivo", 0.80, "co_occurs"),
    ("paradigmas.Construtivista", "metodos.Qualitativo grounded theory", 0.85, "co_occurs"),
    ("raciocinio.Indutivo", "metodos.Qualitativo grounded theory", 0.80, "co_occurs"),
    ("raciocinio.Abdutivo", "paradigmas.Pragmatista", 0.75, "co_occurs"),
    ("teoria_jogos.Bayesiano", "raciocinio.Probabilístico", 0.85, "co_occurs"),
    ("teoria_jogos.Evolutivo", "paradigmas.Complexo/Sistêmico", 0.75, "co_occurs"),
    ("dominios.Neurociências", "dados.Dados neurobiológicos", 0.90, "co_occurs"),
    ("dominios.Antropologia", "metodos.Qualitativo fenomenológico", 0.80, "co_occurs"),
    ("dominios.Economia comportamental", "teoria_jogos.Bayesiano", 0.75, "co_occurs"),
    
    # ─── v2.0 Expansion: Prerequisites (12 novas) ────────────────────────
    ("paradigmas.Crítico/Transformador", "raciocinio.Dialético", 0.85, "requires"),
    ("paradigmas.Crítico/Transformador", "niveis_analise.Sistêmico/político", 0.75, "requires"),
    ("dados.Dados neurobiológicos", "dominios.Neurociências", 0.9, "requires"),
    ("metodos.Pesquisa-ação", "paradigmas.Pragmatista", 0.8, "requires"),
    ("metodos.Pesquisa-ação", "niveis_analise.Comunitário", 0.7, "requires"),
    ("raciocinio.Teleológico", "temporalidade.Prospectivo/preditivo", 0.7, "requires"),
    ("teoria_jogos.Stackelberg", "teoria_jogos.Equilíbrio de Nash", 0.8, "requires"),
    ("teoria_jogos.Sinalização", "teoria_jogos.Bayesiano", 0.85, "requires"),
    ("teoria_jogos.Barganha", "teoria_jogos.Cooperativo", 0.75, "requires"),
    ("dominios.Psicofarmacologia", "dominios.Neurociências", 0.8, "requires"),
    ("dominios.Inteligência Artificial / Tecnologia", "raciocinio.Probabilístico", 0.7, "requires"),
    ("populacao.Cross-cultural", "dominios.Antropologia", 0.65, "requires"),
    
    # ─── v2.0 Expansion: Enablers (10 novas) ─────────────────────────────
    ("raciocinio.Dialético", "paradigmas.Crítico/Transformador", 0.85, "enables"),
    ("raciocinio.Dialético", "niveis_analise.Sistêmico/político", 0.7, "enables"),
    ("dados.Dados qualitativos (entrevistas)", "metodos.Qualitativo grounded theory", 0.8, "enables"),
    ("dados.Dados qualitativos (entrevistas)", "paradigmas.Fenomenológico", 0.75, "enables"),
    ("dominios.Inteligência Artificial / Tecnologia", "dados.Dados comparativos (cross-cultural)", 0.6, "enables"),
    ("dominios.Inteligência Artificial / Tecnologia", "raciocinio.Probabilístico", 0.7, "enables"),
    ("temporalidade.Histórico/retrospectivo", "dados.Dados epidemiológicos", 0.65, "enables"),
    ("raciocinio.Metacognitivo", "paradigmas.Construtivista", 0.7, "enables"),
    ("raciocinio.Metacognitivo", "raciocinio.Abdutivo", 0.6, "enables"),
    ("populacao.Contexto comunitário", "niveis_analise.Comunitário", 0.8, "enables"),
    
    # ─── v2.0 Expansion: Co-occurrence (6 novas) ─────────────────────────
    ("paradigmas.Pós-estruturalista", "dominios.Sociologia", 0.8, "co_occurs"),
    ("metodos.Misto sequencial", "paradigmas.Pragmatista", 0.85, "co_occurs"),
    ("raciocinio.Abdutivo", "metodos.Qualitativo fenomenológico", 0.7, "co_occurs"),
    ("temporalidade.Desenvolvimental (ciclo de vida)", "populacao.Infância", 0.75, "co_occurs"),
    ("teoria_jogos.Dilema do Prisioneiro", "raciocinio.Contrafactual", 0.7, "co_occurs"),
    ("dados.Dados observacionais", "metodos.Estudo de caso", 0.8, "co_occurs"),
    
    # ─── v2.0: teorias dimension edges ─────────────────────────────────
    ("teorias.Cognitivo-comportamental", "metodos.Quantitativo experimental", 0.7, "co_occurs"),
    ("teorias.Neurobiológico", "dados.Dados neurobiológicos", 0.9, "enables"),
    ("teorias.Sistêmico", "paradigmas.Complexo/Sistêmico", 0.75, "co_occurs"),
    ("teorias.Evolucionista", "teoria_jogos.Evolutivo", 0.85, "co_occurs"),
    ("teorias.Integrativo/transdiagnóstico", "dominios.Neurociências", 0.6, "enables"),
    ("teorias.Integrativo/transdiagnóstico", "dominios.Sociologia", 0.55, "enables"),
    ("teorias.Social-crítico", "paradigmas.Crítico/Transformador", 0.8, "co_occurs"),
    ("teorias.Fenomenológico-existencial", "paradigmas.Fenomenológico", 0.9, "co_occurs"),
]


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class CrossValidationEngine:
    """Motor de validação cruzada entre capacidades do ecossistema.

    Constrói um grafo de dependências a partir de regras pré-definidas
    e do scan noológico, identificando bottlenecks, efeitos cascata
    e afinidades estruturais.
    """

    def __init__(self):
        self.nodes: dict[str, CapabilityNode] = {}
        self.edges: list[DependencyEdge] = []
        self._node_key = lambda d, c: f"{d}.{c}"

    # ─── GRAPH CONSTRUCTION ──────────────────────────────────────────────

    def build_graph(self, noological_scan: dict[str, Any]) -> dict[str, CapabilityNode]:
        """Constrói grafo de dependências a partir do scan noológico.

        Cria nós para todas as 92 categorias e arestas a partir
        das DEPENDENCY_RULES.
        """
        self.nodes = {}
        self.edges = []

        dims = noological_scan.get("dimensions", {})
        for dim_key, dim_data in dims.items():
            all_cats = dim_data.get("covered", []) + dim_data.get("absent", [])
            for cat in all_cats:
                node_key = self._node_key(dim_key, cat)
                self.nodes[node_key] = CapabilityNode(
                    name=cat,
                    domain=dim_key,
                    category=cat,
                )

        # Aplicar regras de dependência
        for src_key, tgt_key, weight, relation in DEPENDENCY_RULES:
            if src_key in self.nodes and tgt_key in self.nodes:
                self.edges.append(DependencyEdge(
                    source=src_key, target=tgt_key,
                    weight=weight, relation=relation,
                ))
                src_node = self.nodes[src_key]
                tgt_node = self.nodes[tgt_key]
                if relation == "requires":
                    src_node.requires.append(tgt_key)
                elif relation == "enables":
                    src_node.provides.append(tgt_key)
                # co_occurs não altera provides/requires

        return self.nodes

    # ─── BOTTLENECK DETECTION ────────────────────────────────────────────

    def find_bottlenecks(self, min_dependents: int = 3) -> list[CapabilityNode]:
        """Identifica bottlenecks: nós que habilitam (provides/requires) muitas outras capacidades.

        Um nó é bottleneck se:
        - Habilita (provides) >= min_dependents outros nós, OU
        - É prerequisite (outros requires apontam para ele) >= min_dependents
        """
        # Contar quantos nós cada nó habilita (provides)
        provides_count: dict[str, int] = {}
        # Contar quantos nós dependem de cada nó (reverse requires)
        depended_by_count: dict[str, int] = {}

        for node_key, node in self.nodes.items():
            provides_count[node_key] = len(node.provides)
            depended_by_count[node_key] = 0

        for edge in self.edges:
            if edge.relation == "requires":
                depended_by_count[edge.target] = depended_by_count.get(edge.target, 0) + 1

        bottlenecks = []
        for node_key, node in self.nodes.items():
            total_influence = provides_count.get(node_key, 0) + depended_by_count.get(node_key, 0)
            if total_influence >= min_dependents:
                node.influence_score = min(1.0, total_influence / 10.0)
                bottlenecks.append(node)

        # Ordenar por influence_score decrescente
        bottlenecks.sort(key=lambda n: n.influence_score, reverse=True)
        return bottlenecks

    # ─── CASCADE IMPACT ──────────────────────────────────────────────────

    def cascade_impact(self, noological_scan: dict[str, Any]) -> dict[str, float]:
        """Calcula impacto em cascata: se categoria X está ausente, quantas outras são afetadas.

        Retorna dict: {node_key: cascade_score} onde cascade_score é o número
        de capacidades que dependem direta ou indiretamente desta, ponderado
        pelos pesos das arestas.
        """
        dims = noological_scan.get("dimensions", {})
        cascade: dict[str, float] = {}

        for node_key, node in self.nodes.items():
            # Verificar se esta categoria está ausente no scan
            dim_data = dims.get(node.domain, {})
            absent_cats = dim_data.get("absent", [])
            if node.category not in absent_cats:
                continue  # só calcular impacto para categorias ausentes

            # Impacto direto: soma dos pesos das arestas "enables"
            direct = sum(
                e.weight for e in self.edges
                if e.source == node_key and e.relation == "enables"
            )
            # Impacto reverso: quantos nós "require" este
            reverse = sum(
                e.weight for e in self.edges
                if e.target == node_key and e.relation == "requires"
            )
            cascade[node_key] = round(direct + reverse, 2)

        return cascade

    # ─── CO-OCCURRENCE ───────────────────────────────────────────────────

    def co_occurrence_matrix(self) -> dict[tuple[str, str], float]:
        """Calcula matriz de co-ocorrência entre pares de categorias.

        Retorna: {(cat_a, cat_b): affinity_score}
        """
        matrix: dict[tuple[str, str], float] = {}
        for edge in self.edges:
            if edge.relation == "co_occurs":
                items = sorted([edge.source, edge.target])
                key: tuple[str, str] = (items[0], items[1])
                matrix[key] = max(matrix.get(key, 0), edge.weight)
        return matrix

    # ─── DETECT CYCLES ───────────────────────────────────────────────────

    def detect_cycles(self) -> list[list[str]]:
        """Detecta ciclos no grafo de dependências (A→B→A).

        Retorna lista de ciclos encontrados.
        """
        cycles = []
        for edge_a in self.edges:
            if edge_a.relation not in ("requires", "enables"):
                continue
            for edge_b in self.edges:
                if edge_b.relation not in ("requires", "enables"):
                    continue
                if edge_a.source == edge_b.target and edge_a.target == edge_b.source:
                    cycle = [edge_a.source, edge_a.target]
                    if cycle not in cycles and list(reversed(cycle)) not in cycles:
                        cycles.append(cycle)
        return cycles

    # ─── SELF-DISCOVERY (v2.0) ──────────────────────────────────────────

    def learn_from_scan(self, noological_scan: dict[str, Any]) -> list[DependencyEdge]:
        """v2.0: Auto-descoberta de co-ocorrencias implicitas no scan.

        Se duas categorias estao AMBAS presentes (covered), sugere
        afinidade implicita como regra de co-ocorrencia (weight=0.6).
        """
        discovered: list[DependencyEdge] = []
        dims = noological_scan.get("dimensions", {})
        existing_pairs = {(e.source, e.target) for e in self.edges}
        existing_pairs.update({(e.target, e.source) for e in self.edges})
        
        items = []
        for dk, dd in dims.items():
            for cat in dd.get("covered", []):
                items.append((dk, cat))
        
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                dk1, cat1 = items[i]
                dk2, cat2 = items[j]
                key1 = f"{dk1}.{cat1}"
                key2 = f"{dk2}.{cat2}"
                if (key1, key2) not in existing_pairs and (key2, key1) not in existing_pairs:
                    discovered.append(DependencyEdge(
                        source=key1, target=key2,
                        weight=0.6, relation="co_occurs"
                    ))
        return discovered
