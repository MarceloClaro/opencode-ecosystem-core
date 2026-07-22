# -*- coding: utf-8 -*-
"""
Deep Research Agent — R102
===========================
Agente de pesquisa profunda com orquestracao hierarquica:

  - OrchestratorAgent: planejamento, roteamento, suficiencia, sintese
  - BFRS Agent: exploracao larga (Breadth-First ReSearch)
  - DFRS Agent: investigacao profunda (Depth-First ReSearch)
  - ExecutionSandbox: execucao Python programatica isolada

Inspirado no DeepEvidence (Wang et al., Nature Machine Intelligence 2026),
com integracoes do DualGraph, A2RAG, e Super Research.

SPEC-935-R102.
"""

from __future__ import annotations

import json
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from agentic_science_v2.evidence_graph import (
    EvidenceGraph,
    Entity,
    Relation,
    Evidence,
)

logger = logging.getLogger(__name__)


# ============================================================
# Dataclasses
# ============================================================

@dataclass
class ResearchPlan:
    """Plano de pesquisa decomposto."""
    id: str = field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:8]}")
    question: str = ""
    sub_questions: List[Dict[str, Any]] = field(default_factory=list)
    strategy: str = "hybrid"  # breadth_first, depth_first, hybrid
    max_depth: int = 3
    max_breadth: int = 5
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "sub_questions": self.sub_questions,
            "strategy": self.strategy,
            "max_depth": self.max_depth,
            "max_breadth": self.max_breadth,
        }


@dataclass
class ResearchReport:
    """Relatorio final de pesquisa."""
    id: str = field(default_factory=lambda: f"rep-{uuid.uuid4().hex[:8]}")
    question: str = ""
    summary: str = ""
    sections: List[Dict[str, str]] = field(default_factory=list)
    citations: List[Dict[str, str]] = field(default_factory=list)
    evidence_graph_summary: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "summary": self.summary[:500],
            "sections": self.sections,
            "citations_count": len(self.citations),
            "evidence_graph": self.evidence_graph_summary,
            "confidence": self.confidence,
            "duration": round(self.duration_seconds, 2),
        }


# ============================================================
# KnowledgeBaseRegistry (simulated sources)
# ============================================================

class KnowledgeBaseRegistry:
    """Registro de bases de conhecimento simulado.

    Em producao, conecta a PubMed, OpenTargets, ClinicalTrials, etc.
    """

    def __init__(self):
        self.sources: List[Dict[str, Any]] = [
            {"id": "pubmed", "name": "PubMed", "type": "literature"},
            {"id": "opentargets", "name": "OpenTargets", "type": "genetics"},
            {"id": "clinical_trials", "name": "ClinicalTrials.gov", "type": "trials"},
            {"id": "drugbank", "name": "DrugBank", "type": "pharmacology"},
            {"id": "pathway", "name": "Pathway KG", "type": "pathways"},
        ]

    def list_sources(self) -> List[Dict[str, Any]]:
        return self.sources

    def query(self, source_id: str, query: str) -> List[Dict[str, Any]]:
        """Query simulada a uma base."""
        # Resultados simulados para teste
        results = []
        if "cancer" in query.lower() or "BRAF" in query:
            results = [
                {"entity": "BRAF", "type": "gene",
                 "description": "B-Raf proto-oncogene"},
                {"entity": "Vemurafenib", "type": "drug",
                 "description": "BRAF inhibitor for melanoma"},
                {"entity": "Melanoma", "type": "disease",
                 "description": "Skin cancer"},
            ]
        elif "diabetes" in query.lower():
            results = [
                {"entity": "INS", "type": "gene",
                 "description": "Insulin gene"},
                {"entity": "Metformin", "type": "drug",
                 "description": "First-line diabetes treatment"},
                {"entity": "Type 2 Diabetes", "type": "disease",
                 "description": "Metabolic disorder"},
            ]
        elif "alzheimer" in query.lower():
            results = [
                {"entity": "APP", "type": "gene",
                 "description": "Amyloid precursor protein"},
                {"entity": "Donepezil", "type": "drug",
                 "description": "Cholinesterase inhibitor"},
            ]
        else:
            # Resultados genericos
            results = [
                {"entity": query.split()[0] if query.split() else "Entity",
                 "type": "concept",
                 "description": f"Concept related to: {query}"},
            ]

        # Filtrar por source para simular diferencas
        if source_id == "clinical_trials":
            results = [
                r for r in results
                if r["type"] in ("drug", "disease")
            ]
        elif source_id == "pathway":
            results = []

        return results


# ============================================================
# BFRS Agent (Breadth-First ReSearch)
# ============================================================

class BFRSAgent:
    """Exploracao larga: descobre conexoes vizinhas em multiplas bases."""

    def __init__(
        self,
        graph: EvidenceGraph,
        kb_registry: KnowledgeBaseRegistry,
        max_breadth: int = 5,
    ):
        self.graph = graph
        self.kb = kb_registry
        self.max_breadth = max_breadth
        self.call_count = 0

    def explore(
        self,
        seed_entities: List[str],
        max_sources: int = 3,
    ) -> Dict[str, Any]:
        """Explora vizinhanca de entidades semente em multiplas fontes."""
        self.call_count += 1
        discoveries = {"entities": 0, "relations": 0, "sources_used": []}

        for seed_name in seed_entities[:self.max_breadth]:
            # Buscar entidade no grafo primeiro
            entity = self.graph.find_entity_by_name(seed_name)
            if not entity:
                entity = self.graph.add_entity(
                    name=seed_name,
                    entity_type="concept",
                    source="bfrs",
                )

            # Explorar em cada base
            for source in self.kb.list_sources()[:max_sources]:
                results = self.kb.query(source["id"], seed_name)
                for res in results:
                    # Adicionar entidade descoberta
                    target = self.graph.find_entity_by_name(res["entity"])
                    if not target:
                        target = self.graph.add_entity(
                            name=res["entity"],
                            entity_type=res.get("type", "concept"),
                            description=res.get("description", ""),
                            source=f"bfrs:{source['id']}",
                            source_type=source["type"],
                        )
                        discoveries["entities"] += 1

                    # Adicionar relacao
                    rel = self.graph.add_relation(
                        source_id=entity.id,
                        target_id=target.id,
                        relation_type="ASSOCIATED_WITH",
                        evidence_text=f"Discovered via {source['id']} "
                                      f"query on '{seed_name}'",
                        source=f"bfrs:{source['id']}",
                    )
                    if rel:
                        discoveries["relations"] += 1

                discoveries["sources_used"].append(source["id"])

        discoveries["sources_used"] = list(set(discoveries["sources_used"]))
        return discoveries

    def reset(self) -> None:
        self.call_count = 0


# ============================================================
# DFRS Agent (Depth-First ReSearch)
# ============================================================

class DFRSAgent:
    """Investigacao profunda: cadeias multi-hop com tracagem de referencias."""

    def __init__(
        self,
        graph: EvidenceGraph,
        kb_registry: KnowledgeBaseRegistry,
        max_depth: int = 3,
    ):
        self.graph = graph
        self.kb = kb_registry
        self.max_depth = max_depth
        self.call_count = 0
        self._visited_paths: set = set()

    def investigate(
        self,
        start_entity_name: str,
        relation_chain: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Investigacao profunda seguindo cadeias de relacoes."""
        self.call_count += 1
        findings = {"depth_reached": 0, "entities_found": 0,
                     "paths_traced": 0, "evidence_collected": 0}

        start = self.graph.find_entity_by_name(start_entity_name)
        if not start:
            start = self.graph.add_entity(
                name=start_entity_name,
                entity_type="concept",
                source="dfrs",
            )

        # BFS com profundidade limitada
        frontier: List[Tuple[str, int, List[str]]] = [
            (start.id, 0, [start.name])
        ]
        visited_entities: set = {start.id}
        chain = relation_chain or ["ASSOCIATED_WITH"]

        while frontier:
            current_id, depth, path = frontier.pop(0)
            findings["depth_reached"] = max(findings["depth_reached"], depth)

            if depth >= self.max_depth:
                continue

            # Buscar novas conexoes na KB
            current_entity = self.graph.get_entity(current_id)
            if not current_entity:
                continue

            kb_results = self.kb.query("pubmed", current_entity.name)
            for res in kb_results:
                target = self.graph.find_entity_by_name(res["entity"])
                if not target:
                    target = self.graph.add_entity(
                        name=res["entity"],
                        entity_type=res.get("type", "concept"),
                        description=res.get("description", ""),
                        source=f"dfrs:pubmed",
                        source_type="literature",
                    )
                    findings["entities_found"] += 1

                # Adicionar relacao com tipo da chain
                rel_type = chain[depth % len(chain)]
                rel = self.graph.add_relation(
                    source_id=current_id,
                    target_id=target.id,
                    relation_type=rel_type,
                    evidence_text=f"Deep dive from {current_entity.name} "
                                  f"to {res['entity']} via {rel_type}",
                    source=f"dfrs:{current_entity.name}",
                )
                if rel:
                    findings["paths_traced"] += 1
                    # Coletar evidencia textual (simulada)
                    self._add_deep_evidence(current_entity, target)
                    findings["evidence_collected"] += 1

                # Expandir fronteira
                if target.id not in visited_entities:
                    visited_entities.add(target.id)
                    new_path = path + [target.name]
                    path_key = "->".join(new_path)
                    if path_key not in self._visited_paths:
                        self._visited_paths.add(path_key)
                        frontier.append(
                            (target.id, depth + 1, new_path)
                        )

        return findings

    def _add_deep_evidence(
        self,
        source: Entity,
        target: Entity,
    ) -> None:
        """Adiciona evidencia textual simulada."""
        evidence_text = (
            f"Evidence linking {source.name} ({source.entity_type}) "
            f"to {target.name} ({target.entity_type}). "
            f"Based on literature review and pathway analysis."
        )
        ev = self.graph._add_evidence(
            text=evidence_text,
            source=f"dfrs:{source.name}->{target.name}",
            source_type="literature",
            agent="dfrs",
        )
        # Vincular evidencia a ambas entidades
        if ev.id not in source.evidence:
            source.evidence.append(ev.id)
        if ev.id not in target.evidence:
            target.evidence.append(ev.id)

    def reset(self) -> None:
        self.call_count = 0
        self._visited_paths.clear()


# ============================================================
# ExecutionSandbox
# ============================================================

class ExecutionSandbox:
    """Sandbox Python para execucao programatica de pesquisa.

    Simula execucao de codigo para query a APIs, analise downstream,
    e verificacao cruzada.
    """

    def __init__(self):
        self.execution_log: List[Dict[str, Any]] = []
        self.cache: Dict[str, Any] = {}

    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executa codigo Python no sandbox (simulado)."""
        exec_id = f"exec-{uuid.uuid4().hex[:8]}"
        start = time.time()

        # Simular execucao
        result = {
            "success": True,
            "output": f"Executed: {code[:100]}...",
            "tables": [],
            "plots": [],
        }

        duration = time.time() - start
        entry = {
            "id": exec_id,
            "code": code[:200],
            "result": result,
            "duration": round(duration, 3),
            "timestamp": start,
        }
        self.execution_log.append(entry)
        return result

    def query_api(
        self,
        api_name: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Query simulada a API externa."""
        cache_key = f"{api_name}:{json.dumps(params, sort_keys=True)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        result = {
            "api": api_name,
            "params": params,
            "results": [
                {"id": f"result_{i}", "value": random.random()}
                for i in range(3)
            ],
            "status": "success",
        }
        self.cache[cache_key] = result
        self.execution_log.append({
            "id": f"api-{uuid.uuid4().hex[:8]}",
            "type": "api_query",
            "api": api_name,
            "params": params,
            "timestamp": time.time(),
        })
        return result

    def cross_validate(
        self,
        statements: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Verificacao cruzada de afirmacoes."""
        validated = []
        for stmt in statements:
            # Simular validacao
            validated.append({
                "statement": stmt.get("text", ""),
                "confidence": random.uniform(0.5, 0.95),
                "supporting_sources": stmt.get("sources", []),
                "verified": random.random() > 0.2,
            })
        return validated

    def summary(self) -> Dict[str, Any]:
        return {
            "total_executions": len(self.execution_log),
            "cache_size": len(self.cache),
        }


# ============================================================
# OrchestratorAgent
# ============================================================

class OrchestratorAgent:
    """Orquestrador hierarquico da pesquisa profunda.

    Planeja, roteia, avalia suficiencia e sintetiza.
    """

    def __init__(
        self,
        graph: Optional[EvidenceGraph] = None,
        kb_registry: Optional[KnowledgeBaseRegistry] = None,
        max_rounds: int = 3,
        max_actions: int = 15,
    ):
        self.graph = graph or EvidenceGraph()
        self.kb = kb_registry or KnowledgeBaseRegistry()
        self.max_rounds = max_rounds
        self.max_actions = max_actions

        # Sub-agentes
        self.bfrs = BFRSAgent(self.graph, self.kb)
        self.dfrs = DFRSAgent(self.graph, self.kb)
        self.sandbox = ExecutionSandbox()

        # Estado
        self.plans: List[ResearchPlan] = []
        self.reports: List[ResearchReport] = []
        self.action_count = 0
        self.round_count = 0

    def research(
        self,
        question: str,
        strategy: str = "hybrid",
        max_depth: int = 3,
        max_breadth: int = 5,
    ) -> ResearchReport:
        """Executa pesquisa completa sobre uma pergunta."""
        start = time.time()
        self.round_count += 1

        # 1. Planejamento
        plan = self._create_plan(question, strategy, max_depth, max_breadth)
        self.plans.append(plan)

        # 2. Executar sub-perguntas
        all_findings = []
        for sub_q in plan.sub_questions:
            if self.action_count >= self.max_actions:
                break

            findings = self._execute_sub_question(sub_q)
            all_findings.append(findings)

        # 3. Verificacao de suficiencia
        sufficient, gaps = self._check_sufficiency(question)
        if not sufficient and self.round_count < self.max_rounds:
            # Segunda rodada focada nas lacunas
            for gap in gaps[:2]:
                self._execute_sub_question({
                    "question": gap,
                    "strategy": "depth_first",
                    "seed": "",
                })

        # 4. Sintese do relatorio
        report = self._synthesize_report(question, start)
        self.reports.append(report)

        return report

    def _create_plan(
        self,
        question: str,
        strategy: str,
        max_depth: int,
        max_breadth: int,
    ) -> ResearchPlan:
        """Decompoe pergunta em sub-perguntas."""
        # Simular decomposicao baseada em palavras-chave
        words = question.lower().split()
        sub_questions = []

        if "mechanism" in words or "pathway" in words:
            sub_questions.append({
                "question": f"What are the molecular mechanisms of {question}?",
                "strategy": "depth_first",
                "seed": words[0] if words else question,
            })
        if "treatment" in words or "drug" in words or "therapy" in words:
            sub_questions.append({
                "question": f"What treatments exist for {question}?",
                "strategy": "breadth_first",
                "seed": words[0] if words else question,
            })
        if "gene" in words or "genetic" in words or "biomarker" in words:
            sub_questions.append({
                "question": f"What genes are associated with {question}?",
                "strategy": "hybrid",
                "seed": words[0] if words else question,
            })

        # Sempre adicionar pergunta geral
        sub_questions.append({
            "question": f"Overview of {question}",
            "strategy": "breadth_first",
            "seed": words[0] if words else question,
        })

        return ResearchPlan(
            question=question,
            sub_questions=sub_questions,
            strategy=strategy,
            max_depth=max_depth,
            max_breadth=max_breadth,
        )

    def _execute_sub_question(
        self,
        sub_q: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Executa uma sub-pergunta com a estrategia apropriada."""
        self.action_count += 1
        strategy = sub_q.get("strategy", "hybrid")
        seed = sub_q.get("seed", "")

        findings = {"strategy": strategy, "seed": seed,
                     "bfrs_findings": {}, "dfrs_findings": {}}

        if strategy in ("breadth_first", "hybrid"):
            findings["bfrs_findings"] = self.bfrs.explore(
                seed_entities=[seed] if seed else ["Cancer", "Diabetes"],
                max_sources=3,
            )

        if strategy in ("depth_first", "hybrid"):
            findings["dfrs_findings"] = self.dfrs.investigate(
                start_entity_name=seed if seed else "BRAF",
                relation_chain=["ASSOCIATED_WITH", "TREATS", "CAUSES"],
            )

        return findings

    def _check_sufficiency(
        self,
        question: str,
    ) -> Tuple[bool, List[str]]:
        """Avalia se evidencia acumulada e suficiente."""
        stats = self.graph.stats()

        # Heuristica: suficiente se > 3 entidades e > 3 relacoes
        sufficient = (
            stats["entities"] >= 3 and stats["relations"] >= 3
        )

        gaps = []
        if stats["entities"] < 3:
            gaps.append(f"Need more entities (have {stats['entities']})")
        if stats["relations"] < 3:
            gaps.append(f"Need more relations (have {stats['relations']})")

        return sufficient, gaps

    def _synthesize_report(
        self,
        question: str,
        start_time: float,
    ) -> ResearchReport:
        """Sintetiza relatorio final a partir do grafo de evidencia."""
        stats = self.graph.stats()
        entities = self.graph.get_entities_by_type("gene")[:3]
        drugs = self.graph.get_entities_by_type("drug")[:3]

        # Construir secoes
        sections = [
            {
                "title": "Summary",
                "content": (
                    f"Deep research on '{question}' completed. "
                    f"Explored {stats['entities']} entities and "
                    f"{stats['relations']} relations across "
                    f"{stats['evidence_pieces']} evidence pieces."
                ),
            },
            {
                "title": "Key Entities",
                "content": (
                    f"Genes: {', '.join(e.name for e in entities)}. "
                    f"Drugs: {', '.join(d.name for d in drugs)}."
                ) if entities or drugs else "No specific entities identified.",
            },
            {
                "title": "Evidence Graph",
                "content": (
                    f"Entity types: {stats['entity_types']}. "
                    f"Relation types: {stats['relation_types']}."
                ),
            },
        ]

        # Citacoes
        citations = []
        for eid, entity in list(self.graph.entities.items())[:5]:
            citations.append({
                "entity": entity.name,
                "type": entity.entity_type,
                "evidence_count": len(entity.evidence),
            })

        confidence = min(1.0, (
            0.3 * min(1.0, stats["entities"] / 10) +
            0.3 * min(1.0, stats["relations"] / 10) +
            0.2 * min(1.0, stats["evidence_pieces"] / 5) +
            0.2 * min(1.0, self.bfrs.call_count / 3)
        ))

        return ResearchReport(
            question=question,
            summary=f"Deep research findings on {question}",
            sections=sections,
            citations=citations,
            evidence_graph_summary=stats,
            confidence=round(confidence, 2),
            duration_seconds=time.time() - start_time,
        )

    def summary(self) -> Dict[str, Any]:
        """Sumario do orquestrador."""
        return {
            "rounds": self.round_count,
            "actions": self.action_count,
            "plans": len(self.plans),
            "reports": len(self.reports),
            "graph": self.graph.stats(),
            "bfrs_calls": self.bfrs.call_count,
            "dfrs_calls": self.dfrs.call_count,
            "sandbox": self.sandbox.summary(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Exporta estado completo."""
        return {
            "summary": self.summary(),
            "plans": [p.to_dict() for p in self.plans],
            "reports": [r.to_dict() for r in self.reports],
            "evidence_graph": self.graph.to_dict(),
        }


# ============================================================
# Helper function
# ============================================================

def run_deep_research(
    question: str,
    max_rounds: int = 2,
    max_depth: int = 3,
) -> Dict[str, Any]:
    """Executa pesquisa profunda completa."""
    orchestrator = OrchestratorAgent(
        max_rounds=max_rounds,
        max_actions=10,
    )
    report = orchestrator.research(
        question=question,
        strategy="hybrid",
        max_depth=max_depth,
    )
    return orchestrator.to_dict()
