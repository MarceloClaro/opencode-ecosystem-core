# -*- coding: utf-8 -*-
"""
Scientific RAG Evolved — R99
=============================
Evolucao do RAG cientifico com:

  1. AdaptiveRetriever — analise de complexidade, estrategias sequential/parallel/recursive
  2. CitationGraph — grafo de citacoes entre documentos
  3. OutlineSynthesizer — sintese guiada por outline com secoes
  4. RAGEvolved — orquestrador integrado

Uso:
    from rag.scientific import ScientificRAG, ScientificDocument
    from rag.evolved import RAGEvolved

    rag = ScientificRAG()
    rag.index([...])
    evolved = RAGEvolved(rag)

    # Auto-detecta complexidade
    result = evolved.answer("What is causal inference?")

    # Forca estruturada
    result = evolved.answer_structured("Compare X and Y")

SPEC-935-R99.
"""

from __future__ import annotations

import json
import logging
import math
import re
import statistics
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# C1 — AdaptiveRetriever
# ============================================================

class AdaptiveRetriever:
    """Analisa complexidade da consulta e seleciona estrategia de retrieval."""

    def analyze_complexity(self, query: str) -> str:
        """Analisa complexidade da consulta.

        Args:
            query: String de consulta.

        Returns:
            'simple', 'moderate', ou 'complex'.
        """
        word_count = len(query.split())
        # Conta conceitos (palavras maiusculas/citadas ou termos tecnicos)
        concepts = len(re.findall(r'\b[A-Z][a-z]+\b', query))
        # Conta conectores que indicam multi-etapa
        connectors = len(re.findall(
            r'\b(compare|contrast|synthesize|analyze|discuss|evaluate|'
            r'implications|regarding|across|between|among|versus|vs)\b',
            query.lower()
        ))
        # Conta referencias a multiplas fontes
        multi_source = len(re.findall(r'\b[A-Z][a-z]+(?:\s+et\s+al\.?)?(?=\s*\()', query))
        multi_source += len(re.findall(r'\([^)]*\d{4}[^)]*\)', query))

        score = (word_count * 0.15) + (concepts * 2.0) + (connectors * 4.0) + (multi_source * 3.0)

        # Complexo: score alto OU multi-etapa com conectores + conceitos
        if score >= 12.0 or (connectors >= 3 and concepts >= 2) or word_count > 25:
            return "complex"
        # Moderado: score medio OU consulta comparativa
        elif score >= 5.0 or connectors >= 1 or word_count > 10:
            return "moderate"
        else:
            return "simple"

    def retrieve_adaptive(
        self,
        query: str,
        rag: Any,
        top_k: int = 5,
    ) -> List[Any]:
        """Seleciona e executa estrategia de retrieval baseada na complexidade.

        Args:
            query: Consulta.
            rag: Instancia de ScientificRAG.
            top_k: Maximo de evidencias.

        Returns:
            Lista de RetrievedEvidence.
        """
        complexity = self.analyze_complexity(query)

        if complexity == "simple":
            return self._retrieve_sequential(query, rag, top_k)
        elif complexity == "complex":
            return self._retrieve_parallel(query, rag, top_k)
        else:  # moderate
            # moderate usa sequential tambem, mas com mais resultados
            return self._retrieve_sequential(query, rag, top_k + 2)

    def _retrieve_sequential(
        self, query: str, rag: Any, top_k: int = 5
    ) -> List[Any]:
        """Retrieval sequencial padrao — 1 chamada ao RAG."""
        return rag.retrieve(query, top_k=top_k)

    def _retrieve_parallel(
        self, query: str, rag: Any, top_k: int = 5
    ) -> List[Any]:
        """Retrieval paralelo — divide query em sub-queries, funde resultados."""
        sub_queries = self._decompose_query(query)

        all_evidence = []
        seen_chunks = set()

        for sub_q in sub_queries:
            evidences = rag.retrieve(sub_q, top_k=max(3, top_k // 2))
            for ev in evidences:
                if ev.chunk_id not in seen_chunks:
                    all_evidence.append(ev)
                    seen_chunks.add(ev.chunk_id)

        # Ordena por final_score descendente
        all_evidence.sort(key=lambda ev: ev.final_score, reverse=True)
        return all_evidence[:top_k]

    def _decompose_query(self, query: str) -> List[str]:
        """Decompoe query complexa em sub-queries focadas."""
        sub_queries = [query]  # sempre inclui a original

        # Extrai entidades nomeadas (maiusculas)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))*', query)
        for e in entities[:3]:
            sub_queries.append(f"research on {e.lower()}")

        # Extrai conceitos entre aspas
        quoted = re.findall(r'"([^"]+)"', query)
        for q in quoted[:2]:
            sub_queries.append(q)

        # Extrai pares comparativos
        compare_match = re.search(
            r'compare\s+(\w+(?:\s+\w+)?)\s+(?:and|vs|versus)\s+(\w+(?:\s+\w+)?)',
            query, re.IGNORECASE
        )
        if compare_match:
            sub_queries.append(compare_match.group(1))
            sub_queries.append(compare_match.group(2))

        # Remove duplicatas mantendo ordem
        seen = set()
        unique = []
        for q in sub_queries:
            qn = q.lower().strip()
            if qn not in seen:
                seen.add(qn)
                unique.append(q)
        return unique


# ============================================================
# C2 — CitationGraph
# ============================================================

class CitationGraph:
    """Grafo direcionado de citacoes entre documentos.

    Attributes:
        _edges: Dict[citing_id, Set[cited_id]]
    """

    def __init__(self):
        self._edges: Dict[str, Set[str]] = {}

    def add_edge(self, citing_id: str, cited_id: str) -> None:
        """Registra que citing_id cita cited_id.

        Args:
            citing_id: ID do documento que cita.
            cited_id: ID do documento citado.
        """
        if citing_id not in self._edges:
            self._edges[citing_id] = set()
        self._edges[citing_id].add(cited_id)

    def add_document_edges(
        self, doc_id: str, references: List[str]
    ) -> None:
        """Registra citacoes de um documento a partir de lista de referencias.

        Args:
            doc_id: ID do documento citante.
            references: Lista de IDs de documentos citados.
        """
        for ref in references:
            self.add_edge(doc_id, ref)

    def get_related(
        self, doc_id: str, max_depth: int = 1
    ) -> Set[str]:
        """Retorna documentos relacionados (citados + citantes) ate max_depth.

        Args:
            doc_id: ID do documento central.
            max_depth: Profundidade maxima de navegacao.

        Returns:
            Set de doc_ids relacionados.
        """
        related: Set[str] = set()
        visited: Set[str] = set()

        def _dfs(current: str, depth: int):
            if depth > max_depth or current in visited:
                return
            visited.add(current)

            # Citados por current
            cited = self._edges.get(current, set())
            for c in cited:
                if c != doc_id and c not in visited:
                    related.add(c)
                    _dfs(c, depth + 1)

            # Citantes de current (quem cita current)
            for citing, refs in self._edges.items():
                if current in refs and citing != doc_id and citing not in visited:
                    related.add(citing)
                    _dfs(citing, depth + 1)

        _dfs(doc_id, 0)
        return related

    def expand_retrieval(
        self,
        evidence_list: List[Any],
        max_depth: int = 1,
    ) -> List[str]:
        """Expande lista de evidencias com doc_ids relacionados no grafo.

        Args:
            evidence_list: Lista de objetos RetrievedEvidence.
            max_depth: Profundidade maxima de expansao.

        Returns:
            Lista de doc_ids expandidos (alem dos originais).
        """
        if not evidence_list:
            return []

        # Doc_ids das evidencias originais
        original_ids = {ev.doc_id for ev in evidence_list if hasattr(ev, 'doc_id')}
        expanded: Set[str] = set()

        for doc_id in original_ids:
            related = self.get_related(doc_id, max_depth=max_depth)
            expanded.update(related - original_ids)

        return list(expanded)

    def get_citation_network(self, doc_id: str) -> Dict[str, Any]:
        """Retorna rede de citacoes de um documento.

        Args:
            doc_id: ID do documento central.

        Returns:
            Dict com cited_by, cites, e network_size.
        """
        cited_by = [
            citer for citer, refs in self._edges.items()
            if doc_id in refs
        ]
        cites = list(self._edges.get(doc_id, set()))

        return {
            "doc_id": doc_id,
            "cited_by": cited_by,
            "cites": cites,
            "network_size": len(cited_by) + len(cites),
        }


# ============================================================
# C3 — OutlineSynthesizer
# ============================================================

@dataclass
class OutlineSection:
    """Uma secao do outline de resposta."""
    section_id: str
    title: str
    focus_query: str
    expected_content: str


class OutlineSynthesizer:
    """Sintese de resposta guiada por outline."""

    # Templates de outline por tema
    OUTLINE_TEMPLATES = {
        "definition": [
            OutlineSection("sec_intro", "Introduction & Context",
                          "What is {topic}? Basic definition and context",
                          "Define the topic, establish background"),
            OutlineSection("sec_core", "Core Concepts & Mechanisms",
                          "How does {topic} work? Key mechanisms and principles",
                          "Explain the fundamental mechanisms"),
            OutlineSection("sec_evidence", "Evidence & Applications",
                          "What evidence supports {topic}? Key findings and applications",
                          "Summarize empirical evidence and real-world applications"),
        ],
        "comparison": [
            OutlineSection("sec_overview", "Overview of Approaches",
                          "Overview of {topic_a} and {topic_b}",
                          "Brief introduction to both approaches"),
            OutlineSection("sec_similarities", "Similarities",
                          "Similarities between {topic_a} and {topic_b}",
                          "Points of convergence between the two"),
            OutlineSection("sec_differences", "Key Differences",
                          "Differences between {topic_a} and {topic_b}",
                          "Points of divergence and unique aspects"),
            OutlineSection("sec_synthesis", "Synthesis & Implications",
                          "Synthesis: integrating {topic_a} and {topic_b}",
                          "Implications of comparing both approaches"),
        ],
        "analysis": [
            OutlineSection("sec_framework", "Theoretical Framework",
                          "Theoretical foundations of {topic}",
                          "Establish the theoretical framework"),
            OutlineSection("sec_methodology", "Methodological Approaches",
                          "Methods used to study {topic}",
                          "Describe methodological approaches"),
            OutlineSection("sec_findings", "Key Findings",
                          "Main findings regarding {topic}",
                          "Summarize empirical findings"),
            OutlineSection("sec_discussion", "Discussion & Implications",
                          "Implications of {topic} for {field}",
                          "Discuss broader implications and future directions"),
        ],
    }

    def plan(self, query: str) -> List[OutlineSection]:
        """Gera outline a partir da consulta.

        Args:
            query: Consulta do usuario.

        Returns:
            Lista de OutlineSection.
        """
        q_lower = query.lower()

        # Detecta tipo de consulta
        is_comparison = any(w in q_lower for w in [
            'compare', 'contrast', 'versus', 'vs', 'difference', 'similarit',
            'rather than', 'compared to'
        ])
        is_analysis = any(w in q_lower for w in [
            'synthesize', 'analyze', 'evaluate', 'implications', 'impact',
            'discuss', 'critically'
        ])

        # Extrai topicos
        if is_comparison:
            return self._build_comparison_outline(query)
        elif is_analysis:
            return self._build_analysis_outline(query)
        else:
            return self._build_definition_outline(query)

    def _build_definition_outline(self, query: str) -> List[OutlineSection]:
        """Constroi outline de definicao."""
        # Extrai topico principal
        topic = self._extract_topic(query)

        sections = []
        for tpl in self.OUTLINE_TEMPLATES["definition"]:
            sections.append(OutlineSection(
                section_id=tpl.section_id,
                title=tpl.title,
                focus_query=tpl.focus_query.format(topic=topic),
                expected_content=tpl.expected_content,
            ))
        return sections

    def _build_comparison_outline(self, query: str) -> List[OutlineSection]:
        """Constroi outline de comparacao."""
        # Tenta extrair pares comparativos
        match = re.search(
            r'(?:compare|between|versus|vs)\s+'
            r'(\w+(?:\s+\w+)?)'
            r'(?:\s+(?:and|vs|versus|with|against)\s+)'
            r'(\w+(?:\s+\w+)?)',
            query, re.IGNORECASE
        )
        topic_a = match.group(1) if match else "first approach"
        topic_b = match.group(2) if match else "second approach"

        sections = []
        for tpl in self.OUTLINE_TEMPLATES["comparison"]:
            sections.append(OutlineSection(
                section_id=tpl.section_id,
                title=tpl.title,
                focus_query=tpl.focus_query.format(
                    topic_a=topic_a, topic_b=topic_b
                ),
                expected_content=tpl.expected_content,
            ))
        return sections

    def _build_analysis_outline(self, query: str) -> List[OutlineSection]:
        """Constroi outline de analise."""
        topic = self._extract_topic(query)
        field = self._extract_field(query)

        sections = []
        for tpl in self.OUTLINE_TEMPLATES["analysis"]:
            sections.append(OutlineSection(
                section_id=tpl.section_id,
                title=tpl.title,
                focus_query=tpl.focus_query.format(
                    topic=topic, field=field
                ),
                expected_content=tpl.expected_content,
            ))
        return sections

    @staticmethod
    def _extract_topic(query: str) -> str:
        """Extrai o topico principal de uma consulta."""
        # Remove palavras de comando
        cleaned = re.sub(
            r'\b(what|is|are|the|of|in|for|how|does|do|explain|describe|'
            r'synthesize|analyze|discuss|compare|contrast|evaluate)\b',
            '', query, flags=re.IGNORECASE
        ).strip()
        # Pega as primeiras 2-3 palavras significativas
        words = [w for w in cleaned.split() if len(w) > 2]
        return ' '.join(words[:3]) if words else query[:50]

    @staticmethod
    def _extract_field(query: str) -> str:
        """Extrai o campo/dominio de uma consulta."""
        field_keywords = [
            r'in\s+(\w+(?:\s+\w+)?)\s*$',
            r'for\s+(\w+(?:\s+\w+)?)\s*$',
            r'regarding\s+(\w+(?:\s+\w+)?)',
            r'within\s+(\w+(?:\s+\w+)?)',
        ]
        for pattern in field_keywords:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        return "this field"

    def retrieve_per_section(
        self,
        outline: List[OutlineSection],
        rag: Any,
        top_k_per_section: int = 2,
    ) -> Dict[str, List[Any]]:
        """Recupera evidencias para cada secao do outline.

        Args:
            outline: Lista de OutlineSection.
            rag: Instancia de ScientificRAG.
            top_k_per_section: Maximo de evidencias por secao.

        Returns:
            Dict com section_id -> lista de RetrievedEvidence.
        """
        section_evidence: Dict[str, List[Any]] = {}
        for section in outline:
            evidences = rag.retrieve(
                section.focus_query, top_k=top_k_per_section
            )
            section_evidence[section.section_id] = evidences
        return section_evidence

    def synthesize(
        self,
        outline: List[OutlineSection],
        section_evidence: Dict[str, List[Any]],
    ) -> Dict[str, Any]:
        """Sintetiza resposta estruturada a partir do outline e evidencias.

        Args:
            outline: Lista de OutlineSection.
            section_evidence: Dict com section_id -> lista de evidencia.

        Returns:
            Dict com sections, cada uma com title, evidence_summary, key_findings.
        """
        sections = []
        for section in outline:
            evidence = section_evidence.get(section.section_id, [])

            if evidence:
                # Sumariza evidencias
                fragments = [
                    f"[{ev.citation}] {ev.text[:150]}"
                    for ev in evidence[:2]
                ]
                evidence_summary = " | ".join(fragments)
                key_findings = [
                    ev.text[:100] for ev in evidence[:3]
                ]
            else:
                evidence_summary = "No evidence retrieved for this section"
                key_findings = []

            sections.append({
                "section_id": section.section_id,
                "title": section.title,
                "evidence_summary": evidence_summary,
                "key_findings": key_findings,
                "evidence_count": len(evidence),
            })

        return {
            "sections": sections,
            "total_sections": len(sections),
            "total_evidence": sum(
                len(evidence) for evidence in section_evidence.values()
            ),
        }


# ============================================================
# C4 — RAGEvolved (orquestrador principal)
# ============================================================

class RAGEvolved:
    """Orquestrador RAG evolvido com retrieval adaptativo, grafo e sintese.

    Args:
        rag: Instancia de ScientificRAG (base).
    """

    def __init__(self, rag: Any):
        self.rag = rag
        self.retriever = AdaptiveRetriever()
        self.graph = CitationGraph()
        self.synthesizer = OutlineSynthesizer()

    def analyze_complexity(self, query: str) -> str:
        """Analisa complexidade de uma consulta.

        Args:
            query: Consulta.

        Returns:
            'simple', 'moderate', ou 'complex'.
        """
        return self.retriever.analyze_complexity(query)

    def retrieve(self, query: str, top_k: int = 5) -> List[Any]:
        """Retrieval adaptativo com expansao de citacoes.

        Args:
            query: Consulta.
            top_k: Maximo de evidencias.

        Returns:
            Lista de RetrievedEvidence.
        """
        evidence = self.retriever.retrieve_adaptive(query, self.rag, top_k=top_k)

        # Expande via grafo de citacoes se populado
        if self.graph._edges:
            expanded_ids = self.graph.expand_retrieval(evidence, max_depth=1)
            if expanded_ids:
                # Busca documentos expandidos
                for doc_id in expanded_ids[:3]:
                    more = self.rag.retrieve(doc_id, top_k=2)
                    existing_ids = {ev.chunk_id for ev in evidence}
                    for ev in more:
                        if ev.chunk_id not in existing_ids:
                            evidence.append(ev)
                            existing_ids.add(ev.chunk_id)

                evidence.sort(key=lambda ev: ev.final_score, reverse=True)
                evidence = evidence[:top_k]

        return evidence

    def answer(self, query: str) -> Dict[str, Any]:
        """Resposta automatica com roteamento por complexidade.

        Args:
            query: Consulta.

        Returns:
            Dict com resultado (answer ou structured).
        """
        complexity = self.analyze_complexity(query)
        logger.debug("R99: complexity=%s for query='%s'", complexity, query[:60])

        if complexity == "complex":
            return self.answer_structured(query)
        else:
            return self.answer_simple(query)

    def answer_simple(self, query: str) -> Dict[str, Any]:
        """Resposta direta para queries simples (usa RAG base).

        Args:
            query: Consulta.

        Returns:
            Dict com answer, evidence, groundedness.
        """
        result = self.rag.answer(query, top_k=3)

        # Adiciona metadados de complexidade
        result["complexity"] = self.analyze_complexity(query)
        result["mode"] = "direct"

        return result

    def answer_structured(self, query: str) -> Dict[str, Any]:
        """Resposta estruturada com outline e secoes.

        Args:
            query: Consulta.

        Returns:
            Dict com outline, sections, query, complexity.
        """
        # 1. Planeja outline
        outline = self.synthesizer.plan(query)

        # 2. Recupera evidencias por secao
        section_evidence = self.synthesizer.retrieve_per_section(
            outline, self.rag, top_k_per_section=2
        )

        # 3. Sintetiza resposta
        synthesized = self.synthesizer.synthesize(outline, section_evidence)

        return {
            "query": query,
            "complexity": "complex",
            "mode": "structured",
            "outline": [
                {"section_id": s.section_id, "title": s.title}
                for s in outline
            ],
            "sections": synthesized["sections"],
            "total_evidence": synthesized["total_evidence"],
            "total_sections": synthesized["total_sections"],
        }
