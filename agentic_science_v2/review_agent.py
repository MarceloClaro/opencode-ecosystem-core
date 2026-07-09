# -*- coding: utf-8 -*-
"""
Agentic Peer Review — R103
==========================
Sistema agentivo de revisao por pares com auditagem baseada em grafo.

Componentes:
  - RubricEngine: 8 meta-dimensoes + instanciacao por paper
  - ReviewLedger: claim–evidence–risk ledger + verification agenda
  - AuditGraph: grafo de auditoria integrado R102 EvidenceGraph
  - MultiCriticReviewer: 4 revisores especialistas paralelos
  - OrchestratorReviewer: pipeline drafting → grounding → synthesis

Inspirado em REVIEWGROUNDER (ACL 2026), DeepReviewer 2.0 (arXiv 2026),
ProReviewer (arXiv 2026), ScholarPeer (arXiv 2026), ReViewGraph (2025).

SPEC-935-R103.
"""

from __future__ import annotations

import json
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# RubricEngine (REVIEWGROUNDER-inspired)
# ============================================================

META_RUBRICS = {
    "core_contribution_accuracy": {
        "name": "Core Contribution Accuracy",
        "polarity": "positive",
        "description": "Precisao sobre contribuicoes, claims principais e novidade",
        "checklist": [
            "Identifica corretamente a contribuicao principal",
            "Nao distorce ou superestima claims",
            "Contextualiza novidade em relacao ao estado-da-arte",
        ],
    },
    "results_interpretation": {
        "name": "Results Interpretation",
        "polarity": "positive",
        "description": "Interpretacao correta dos resultados e metricas",
        "checklist": [
            "Analisa metricas relatadas corretamente",
            "Identifica limitacoes nos resultados",
            "Verifica consistencia interna dos achados",
        ],
    },
    "comparative_analysis": {
        "name": "Comparative Analysis",
        "polarity": "positive",
        "description": "Analise comparativa com baseline e literatura relacionada",
        "checklist": [
            "Compara com baselines apropriados",
            "Identifica omitted state-of-the-art",
            "Contextualiza avancos relativos",
        ],
    },
    "evidence_based_critique": {
        "name": "Evidence-Based Critique",
        "polarity": "positive",
        "description": "Critica fundamentada em evidencia concreta do texto",
        "checklist": [
            "Cada critica referencia evidencia especifica",
            "Evita comentarios genericos ou superficiais",
            "Fundamenta objecoes em dados ou argumentos",
        ],
    },
    "critique_clarity": {
        "name": "Critique Clarity",
        "polarity": "positive",
        "description": "Clareza e precisao da critica",
        "checklist": [
            "Linguagem clara e especifica",
            "Estrutura logica facil de seguir",
            "Termos tecnicos usados corretamente",
        ],
    },
    "completeness_coverage": {
        "name": "Completeness Coverage",
        "polarity": "positive",
        "description": "Cobertura completa dos aspectos do paper",
        "checklist": [
            "Cobre metodologia, resultados e conclusoes",
            "Nao omite secoes ou aspectos importantes",
            "Avalia contribuicao geral",
        ],
    },
    "constructive_tone": {
        "name": "Constructive Tone",
        "polarity": "positive",
        "description": "Tom construtivo e sugestoes acionaveis",
        "checklist": [
            "Sugestoes sao acionaveis e especificas",
            "Tom respeitoso e profissional",
            "Foco em melhoria do trabalho",
        ],
    },
    "false_or_contradictory_claims": {
        "name": "False or Contradictory Claims",
        "polarity": "pitfall",
        "description": "Ausencia de alegacoes falsas ou contraditorias",
        "checklist": [
            "Nao contem afirmacoes factualmente incorretas",
            "Nao contradiz secoes anteriores da propria revisao",
            "Nao faz alegacoes sem suporte",
        ],
    },
}


@dataclass
class PaperSpecificRubric:
    """Rubrica instanciada para um paper especifico."""
    dimension: str = ""
    criteria: List[str] = field(default_factory=list)
    score: float = 0.0
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "criteria": self.criteria,
            "score": self.score,
            "rationale": self.rationale[:200],
        }


class RubricEngine:
    """Engine de rubricas multi-dimensionais.

    REVIEWGROUNDER-inspired: 8 meta-dimensoes + instanciacao por paper.
    """

    def __init__(self, strictness: float = 0.5):
        self.strictness = strictness
        self.meta_rubrics = META_RUBRICS

    def list_dimensions(self) -> List[str]:
        """Lista dimensoes disponiveis."""
        return list(self.meta_rubrics.keys())

    def get_meta_rubric(self, dimension: str) -> Optional[Dict[str, Any]]:
        """Recupera meta-rubrica por dimensao."""
        return self.meta_rubrics.get(dimension)

    def instantiate_for_paper(
        self,
        paper_title: str = "",
        paper_abstract: str = "",
        paper_sections: Optional[List[str]] = None,
    ) -> List[PaperSpecificRubric]:
        """Instancia rubricas para um paper especifico.

        Em producao, usaria LLM para adaptar criterios ao contexto.
        Aqui: adaptacao heuristica baseada em palavras-chave.
        """
        rubrics = []
        text = (paper_title + " " + paper_abstract + " " +
                " ".join(paper_sections or [])).lower()
        keywords = set(text.split())

        for dim, meta in self.meta_rubrics.items():
            # Adaptar checklist ao contexto do paper
            criteria = []
            for item in meta["checklist"]:
                if any(kw in item.lower() for kw in keywords):
                    criteria.append(f"{item} (contextualizado)")
                else:
                    criteria.append(item)

            rubrics.append(PaperSpecificRubric(
                dimension=dim,
                criteria=criteria,
            ))

        return rubrics

    def score_review(
        self,
        review_sections: Dict[str, str],
        paper_rubrics: List[PaperSpecificRubric],
    ) -> List[PaperSpecificRubric]:
        """Avalia uma revisao contra as rubricas."""
        scored = []
        for rubric in paper_rubrics:
            dim = rubric.dimension
            section_text = review_sections.get(dim, "")

            # Heuristica de scoring baseada em comprimento e palavras-chave
            text_len = len(section_text.split())
            has_evidence = any(
                w in section_text.lower()
                for w in ["figure", "table", "section", "equation",
                          "result", "experiment", "show", "demonstrate"]
            )
            has_actionable = any(
                w in section_text.lower()
                for w in ["suggest", "recommend", "could", "should",
                          "improve", "clarify", "consider"]
            )

            base = 0.3
            if text_len > 20:
                base += 0.2
            if has_evidence:
                base += 0.25
            if has_actionable:
                base += 0.25

            # Aplicar strictness
            score = min(1.0, base * (1.0 + 0.2 * (1.0 - self.strictness)))

            # Pitfall: inverter para dimensoes negativas
            if meta := self.meta_rubrics.get(dim):
                if meta.get("polarity") == "pitfall":
                    score = 1.0 - score

            rubric.score = round(score, 2)
            rubric.rationale = (
                f"Length: {text_len} words, evidence: {has_evidence}, "
                f"actionable: {has_actionable}"
            )
            scored.append(rubric)

        return scored

    def aggregate_score(
        self,
        scored_rubrics: List[PaperSpecificRubric],
    ) -> Dict[str, Any]:
        """Agrega scores em metricas compostas."""
        if not scored_rubrics:
            return {"overall": 0.0, "dimension_scores": {}}

        dim_scores = {r.dimension: r.score for r in scored_rubrics}
        overall = round(
            sum(dim_scores.values()) / max(1, len(dim_scores)),
            2,
        )
        return {
            "overall": overall,
            "dimension_scores": dim_scores,
        }


# ============================================================
# ReviewLedger (DeepReviewer 2.0-inspired)
# ============================================================

@dataclass
class ClaimEntry:
    """Entrada do ledger: claim extraido do manuscrito."""
    id: str = field(default_factory=lambda: f"cl-{uuid.uuid4().hex[:8]}")
    text: str = ""
    section: str = ""
    page: int = 0
    risk: str = "medium"  # low, medium, high
    evidence_anchors: List[str] = field(default_factory=list)
    verified: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text[:150],
            "section": self.section,
            "risk": self.risk,
            "verified": self.verified,
        }


class ReviewLedger:
    """Ledger claim–evidence–risk.

    DeepReviewer 2.0-inspired: extrai claims, anota risco,
    e mantem agenda de verificacao.
    """

    def __init__(self):
        self.claims: Dict[str, ClaimEntry] = {}
        self.verification_agenda: List[Dict[str, Any]] = []

    def extract_claim(
        self,
        text: str,
        section: str = "unknown",
        page: int = 0,
    ) -> ClaimEntry:
        """Extrai claim do manuscrito."""
        # Heuristica de risco baseada em palavras-chave (case-insensitive)
        risk = "medium"
        high_risk_words = ["state-of-the-art", "sota", "first", "novel",
                           "significant", "breakthrough"]
        low_risk_words = ["preliminary", "suggest", "may", "could",
                          "potential", "initial"]

        text_lower = text.lower()
        if any(w in text_lower for w in high_risk_words):
            risk = "high"
        elif any(w in text_lower for w in low_risk_words):
            risk = "low"

        claim = ClaimEntry(
            text=text,
            section=section,
            page=page,
            risk=risk,
        )
        self.claims[claim.id] = claim

        # Adicionar a agenda de verificacao se alto risco
        if risk == "high":
            self.verification_agenda.append({
                "claim_id": claim.id,
                "action": f"Verify: {text[:100]}",
                "priority": "high",
                "status": "pending",
            })

        return claim

    def add_evidence_anchor(self, claim_id: str, anchor: str) -> None:
        """Adiciona ancora de evidencia a um claim."""
        if claim_id in self.claims:
            self.claims[claim_id].evidence_anchors.append(anchor)

    def verify_claim(self, claim_id: str, notes: str = "") -> None:
        """Marca claim como verificado."""
        if claim_id in self.claims:
            self.claims[claim_id].verified = True
            self.claims[claim_id].notes = notes
            # Atualizar agenda
            for item in self.verification_agenda:
                if item["claim_id"] == claim_id:
                    item["status"] = "verified"

    def get_pending_verifications(self) -> List[Dict[str, Any]]:
        """Retorna itens pendentes na agenda."""
        return [
            item for item in self.verification_agenda
            if item["status"] == "pending"
        ]

    def get_high_risk_claims(self) -> List[ClaimEntry]:
        """Retorna claims de alto risco."""
        return [
            c for c in self.claims.values() if c.risk == "high"
        ]

    def summary(self) -> Dict[str, Any]:
        """Sumario do ledger."""
        return {
            "total_claims": len(self.claims),
            "high_risk": len(self.get_high_risk_claims()),
            "verified": sum(1 for c in self.claims.values() if c.verified),
            "pending_verifications": len(self.get_pending_verifications()),
        }


# ============================================================
# AuditGraph (integrado com R102 EvidenceGraph)
# ============================================================

class AuditGraph:
    """Grafo de auditoria para revisao.

    Integrado com R102 EvidenceGraph.
    Nos: claims, evidence_anchors, critiques, retrieved_papers
    Arestas: supported-by, contradicted-by, localized-to, overlaps-with
    """

    def __init__(self, evidence_graph: Optional[Any] = None):
        self.evidence_graph = evidence_graph
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self._node_counter = 0

    def add_node(
        self,
        node_type: str,
        label: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Adiciona no ao grafo de auditoria."""
        nid = f"an-{uuid.uuid4().hex[:8]}"
        self.nodes[nid] = {
            "id": nid,
            "type": node_type,
            "label": label,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        return nid

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 1.0,
    ) -> Dict[str, Any]:
        """Adiciona aresta de auditoria."""
        edge = {
            "id": f"ae-{uuid.uuid4().hex[:8]}",
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "weight": weight,
        }
        self.edges.append(edge)
        return edge

    def get_edges_for_node(self, node_id: str) -> List[Dict[str, Any]]:
        """Recupera arestas conectadas a um no."""
        return [
            e for e in self.edges
            if e["source"] == node_id or e["target"] == node_id
        ]

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Recupera no por ID."""
        return self.nodes.get(node_id)

    def find_path(
        self,
        source_type: str,
        target_type: str,
        max_hops: int = 3,
    ) -> List[Dict[str, Any]]:
        """Encontra caminho entre tipos de no."""
        source_nodes = [
            nid for nid, n in self.nodes.items()
            if n["type"] == source_type
        ]
        target_nodes = set(
            nid for nid, n in self.nodes.items()
            if n["type"] == target_type
        )

        for sid in source_nodes:
            visited = {sid}
            queue = [(sid, [])]
            while queue:
                current, path = queue.pop(0)
                if current in target_nodes:
                    return path
                if len(path) >= max_hops:
                    continue
                for edge in self.get_edges_for_node(current):
                    neighbor = (
                        edge["target"] if edge["source"] == current
                        else edge["source"]
                    )
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [edge]))
        return []

    def traceability_score(self) -> float:
        """Calcula score de rastreabilidade.

        Cada critique deve ter ao menos uma ancora de evidencia.
        """
        critique_nodes = [
            n for n in self.nodes.values()
            if n["type"] == "critique"
        ]
        if not critique_nodes:
            return 0.0

        anchored = 0
        for node in critique_nodes:
            edges = self.get_edges_for_node(node["id"])
            has_anchor = any(
                e["type"] in ("localized-to", "supported-by")
                for e in edges
            )
            if has_anchor:
                anchored += 1

        return round(anchored / len(critique_nodes), 2)

    def coverage_score(self) -> float:
        """Calcula score de cobertura.

        Quantas secoes do paper tem ao menos uma critique.
        """
        sections = set()
        for node in self.nodes.values():
            if node["type"] == "critique":
                sec = node.get("metadata", {}).get("section", "")
                if sec:
                    sections.add(sec)

        if not sections:
            return 0.0
        return min(1.0, len(sections) / 4.0)  # 4+ secoes = cobertura total

    def summary(self) -> Dict[str, Any]:
        """Sumario do grafo de auditoria."""
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "traceability": self.traceability_score(),
            "coverage": self.coverage_score(),
            "node_types": self._count_types(),
        }

    def _count_types(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for node in self.nodes.values():
            t = node["type"]
            counts[t] = counts.get(t, 0) + 1
        return counts


# ============================================================
# MultiCriticReviewer
# ============================================================

@dataclass
class Critique:
    """Critica de um revisor especialista."""
    id: str = field(default_factory=lambda: f"cr-{uuid.uuid4().hex[:8]}")
    reviewer_type: str = ""
    section: str = ""
    text: str = ""
    evidence_anchors: List[str] = field(default_factory=list)
    severity: str = "minor"  # minor, major, critical
    actionable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "reviewer": self.reviewer_type,
            "section": self.section,
            "severity": self.severity,
            "actionable": self.actionable,
            "text_preview": self.text[:200],
        }


class BaseCritic:
    """Revisor especialista base."""

    def __init__(self, critic_type: str):
        self.critic_type = critic_type
        self.critiques: List[Critique] = []

    def review(self, paper: Dict[str, Any]) -> List[Critique]:
        """Revisa paper e retorna criticas."""
        raise NotImplementedError

    def summary(self) -> Dict[str, Any]:
        return {
            "type": self.critic_type,
            "critiques": len(self.critiques),
        }


class MethodologyCritic(BaseCritic):
    """Avalia solidez metodologica."""

    def __init__(self):
        super().__init__("methodology")

    def review(self, paper: Dict[str, Any]) -> List[Critique]:
        self.critiques = []
        sections = paper.get("sections", [])
        for sec in sections:
            sec_lower = sec.lower()
            if any(w in sec_lower for w in ["method", "approach", "implementation"]):
                critique = Critique(
                    reviewer_type=self.critic_type,
                    section=sec,
                    text=(f"Methodology review of '{sec}': "
                          f"Assess reproducibility, clarity of description, "
                          f"and appropriateness of methodology."),
                    severity="major",
                    actionable=True,
                )
                self.critiques.append(critique)
            if any(w in sec_lower for w in ["baseline", "comparison", "ablation"]):
                critique = Critique(
                    reviewer_type=self.critic_type,
                    section=sec,
                    text=(f"Baseline comparison review: verify that all "
                          f"relevant state-of-the-art methods are compared."),
                    severity="major",
                    actionable=True,
                )
                self.critiques.append(critique)
        if not self.critiques:
            self.critiques.append(Critique(
                reviewer_type=self.critic_type,
                section="methodology",
                text="Methodology section requires more detail on experimental setup.",
                severity="minor",
                actionable=True,
            ))
        return self.critiques


class ResultsCritic(BaseCritic):
    """Avalia validade experimental."""

    def __init__(self):
        super().__init__("results")

    def review(self, paper: Dict[str, Any]) -> List[Critique]:
        self.critiques = []
        sections = paper.get("sections", [])
        for sec in sections:
            sec_lower = sec.lower()
            if any(w in sec_lower for w in ["result", "experiment", "evaluation"]):
                critique = Critique(
                    reviewer_type=self.critic_type,
                    section=sec,
                    text=(f"Results review of '{sec}': verify metric reporting, "
                          f"statistical significance, and comparison fairness."),
                    severity="major",
                    actionable=True,
                )
                self.critiques.append(critique)
            if any(w in sec_lower for w in ["metric", "accuracy", "performance"]):
                critique = Critique(
                    reviewer_type=self.critic_type,
                    section=sec,
                    text="Verify that all reported metrics include variance/error bars.",
                    severity="minor",
                    actionable=True,
                )
                self.critiques.append(critique)
        if not self.critiques:
            self.critiques.append(Critique(
                reviewer_type=self.critic_type,
                section="results",
                text="Results section lacks quantitative evaluation.",
                severity="critical",
                actionable=True,
            ))
        return self.critiques


class LiteratureCritic(BaseCritic):
    """Avalia contextualizacao na literatura."""

    def __init__(self):
        super().__init__("literature")

    def review(self, paper: Dict[str, Any]) -> List[Critique]:
        self.critiques = []
        # Verificar se ha secao de related work
        has_related = any(
            "related" in s.lower() or "prior" in s.lower()
            for s in paper.get("sections", [])
        )
        if not has_related:
            self.critiques.append(Critique(
                reviewer_type=self.critic_type,
                section="related_work",
                text="Paper lacks a dedicated related work section.",
                severity="major",
                actionable=True,
            ))

        # Verificar citacoes
        citations = paper.get("citations", [])
        if len(citations) < 5:
            self.critiques.append(Critique(
                reviewer_type=self.critic_type,
                section="references",
                text=(f"Only {len(citations)} references found. "
                      f"Literature coverage may be insufficient."),
                severity="minor",
                actionable=True,
            ))

        if not self.critiques:
            self.critiques.append(Critique(
                reviewer_type=self.critic_type,
                section="literature",
                text="Adequate literature coverage.",
                severity="minor",
                actionable=False,
            ))
        return self.critiques


class EthicsCritic(BaseCritic):
    """Avalia conformidade etica."""

    def __init__(self):
        super().__init__("ethics")

    def review(self, paper: Dict[str, Any]) -> List[Critique]:
        self.critiques = []
        text = json.dumps(paper).lower()

        checks = [
            ("bias", "Discuss potential bias in data or methodology"),
            ("reproducibility", "Ensure reproducibility details are provided"),
            ("data_privacy", "Address data privacy and ethical considerations"),
            ("limitation", "Acknowledge limitations of the approach"),
        ]

        for keyword, suggestion in checks:
            if keyword not in text:
                self.critiques.append(Critique(
                    reviewer_type=self.critic_type,
                    section="ethics",
                    text=(f"Missing discussion: {suggestion}. "
                          f"Consider adding a section on {keyword}."),
                    severity="minor" if keyword != "bias" else "major",
                    actionable=True,
                ))

        if not self.critiques:
            self.critiques.append(Critique(
                reviewer_type=self.critic_type,
                section="ethics",
                text="Ethical considerations adequately addressed.",
                severity="minor",
                actionable=False,
            ))
        return self.critiques


class MultiCriticReviewer:
    """Gerencia 4 revisores especialistas em paralelo."""

    def __init__(self):
        self.critics = {
            "methodology": MethodologyCritic(),
            "results": ResultsCritic(),
            "literature": LiteratureCritic(),
            "ethics": EthicsCritic(),
        }

    def review_paper(self, paper: Dict[str, Any]) -> Dict[str, List[Critique]]:
        """Executa todos os revisores em paralelo."""
        results = {}
        for name, critic in self.critics.items():
            results[name] = critic.review(paper)
        return results

    def get_all_critiques(self) -> List[Critique]:
        """Retorna todas as criticas de todos os revisores."""
        all_c = []
        for critic in self.critics.values():
            all_c.extend(critic.critiques)
        return all_c

    def summary(self) -> Dict[str, Any]:
        return {
            name: c.summary()
            for name, c in self.critics.items()
        }


# ============================================================
# OrchestratorReviewer
# ============================================================

@dataclass
class ReviewPackage:
    """Pacote completo de revisao (DeepReviewer 2.0-style)."""
    id: str = field(default_factory=lambda: f"rp-{uuid.uuid4().hex[:8]}")
    paper_title: str = ""
    overall_score: float = 0.0
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    critiques: List[Dict[str, Any]] = field(default_factory=list)
    ledger_summary: Dict[str, Any] = field(default_factory=dict)
    audit_summary: Dict[str, Any] = field(default_factory=dict)
    traceability: float = 0.0
    coverage: float = 0.0
    export_gate_passed: bool = False
    repair_plan: List[Dict[str, str]] = field(default_factory=list)
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "paper_title": self.paper_title,
            "overall_score": self.overall_score,
            "dimension_scores": self.dimension_scores,
            "critiques_count": len(self.critiques),
            "ledger": self.ledger_summary,
            "audit": self.audit_summary,
            "traceability": self.traceability,
            "coverage": self.coverage,
            "export_gate_passed": self.export_gate_passed,
            "repair_plan": self.repair_plan[:3],
        }


class OrchestratorReviewer:
    """Orquestrador do pipeline de revisao.

    Pipeline: Drafting → Ledger Construction → Grounding →
              Audit → Export Gate → Synthesis
    """

    def __init__(
        self,
        evidence_graph: Optional[Any] = None,
        min_traceability: float = 0.5,
        min_coverage: float = 0.3,
    ):
        self.rubric_engine = RubricEngine()
        self.ledger = ReviewLedger()
        self.audit_graph = AuditGraph(evidence_graph)
        self.multi_critic = MultiCriticReviewer()
        self.min_traceability = min_traceability
        self.min_coverage = min_coverage

    def review(self, paper: Dict[str, Any]) -> ReviewPackage:
        """Executa pipeline completo de revisao."""
        start = time.time()
        title = paper.get("title", "Untitled")

        # 1. Drafting: rubricas para o paper
        paper_rubrics = self.rubric_engine.instantiate_for_paper(
            paper_title=title,
            paper_abstract=paper.get("abstract", ""),
            paper_sections=paper.get("sections", []),
        )

        # 2. Ledger Construction
        claim_node_map = {}  # claim_entry_id -> audit_graph_node_id
        for i, sec in enumerate(paper.get("sections", [])):
            claim = self.ledger.extract_claim(
                text=f"Main contribution in section '{sec}'",
                section=sec,
                page=(i // 3) + 1,
            )
            # No de claim no audit graph
            claim_node = self.audit_graph.add_node(
                "claim", f"Claim: {claim.text[:60]}",
                {"section": sec, "risk": claim.risk},
            )
            claim_node_map[claim.id] = claim_node

        # 3. Grounding: MultiCriticReviewer
        critiques = self.multi_critic.review_paper(paper)
        all_critiques = self.multi_critic.get_all_critiques()

        # Adicionar criticas ao audit graph
        for c in all_critiques:
            c_node = self.audit_graph.add_node(
                "critique", f"[{c.reviewer_type}] {c.text[:60]}",
                {"section": c.section, "severity": c.severity},
            )
            # Conectar a claims relacionados via node IDs
            for claim_entry_id, claim_node_id in claim_node_map.items():
                claim_entry = self.ledger.claims.get(claim_entry_id)
                if claim_entry and claim_entry.section == c.section:
                    self.audit_graph.add_edge(
                        c_node, claim_node_id, "localized-to",
                    )

        # 4. Audit: verificar rastreabilidade
        traceability = self.audit_graph.traceability_score()
        coverage = self.audit_graph.coverage_score()

        # 5. Scoring com rubricas
        review_sections = {}
        for c in all_critiques:
            dim = c.reviewer_type
            if dim not in review_sections:
                review_sections[dim] = ""
            review_sections[dim] += c.text + "\n"

        # Mapear tipos de revisor para dimensoes de rubrica
        dim_map = {
            "methodology": "core_contribution_accuracy",
            "results": "results_interpretation",
            "literature": "comparative_analysis",
            "ethics": "evidence_based_critique",
        }
        rubric_review = {}
        for critic_type, rubric_dim in dim_map.items():
            rubric_review[rubric_dim] = review_sections.get(critic_type, "")

        scored = self.rubric_engine.score_review(rubric_review, paper_rubrics)
        agg = self.rubric_engine.aggregate_score(scored)

        # 6. Export Gate
        export_gate_passed = (
            traceability >= self.min_traceability
            and coverage >= self.min_coverage
        )

        # 7. Repair Plan
        repair_plan = self._generate_repair_plan(all_critiques)

        # 8. Package
        package = ReviewPackage(
            paper_title=title,
            overall_score=agg["overall"],
            dimension_scores=agg.get("dimension_scores", {}),
            critiques=[c.to_dict() for c in all_critiques],
            ledger_summary=self.ledger.summary(),
            audit_summary=self.audit_graph.summary(),
            traceability=traceability,
            coverage=coverage,
            export_gate_passed=export_gate_passed,
            repair_plan=repair_plan,
            duration_seconds=time.time() - start,
        )

        return package

    def _generate_repair_plan(
        self,
        critiques: List[Critique],
    ) -> List[Dict[str, str]]:
        """Gera plano de reparos priorizado."""
        plan = []
        # Priorizar criticas por severidade
        severity_order = {"critical": 0, "major": 1, "minor": 2}
        sorted_c = sorted(
            critiques,
            key=lambda c: severity_order.get(c.severity, 99),
        )

        for c in sorted_c[:5]:  # Top 5
            plan.append({
                "priority": c.severity.upper(),
                "area": c.section,
                "action": c.text[:200],
                "reviewer": c.reviewer_type,
            })

        return plan

    def summary(self) -> Dict[str, Any]:
        return {
            "rubric_dimensions": self.rubric_engine.list_dimensions(),
            "ledger": self.ledger.summary(),
            "audit": self.audit_graph.summary(),
            "critics": self.multi_critic.summary(),
            "config": {
                "min_traceability": self.min_traceability,
                "min_coverage": self.min_coverage,
            },
        }


# ============================================================
# Helper function
# ============================================================

def run_peer_review(
    paper_title: str = "Untitled",
    paper_abstract: str = "",
    paper_sections: Optional[List[str]] = None,
    citations: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Executa revisao por pares completa."""
    paper = {
        "title": paper_title,
        "abstract": paper_abstract,
        "sections": paper_sections or [
            "Introduction", "Methodology", "Experiments",
            "Results", "Discussion", "Conclusion",
        ],
        "citations": citations or ["ref1", "ref2", "ref3"],
    }

    orchestrator = OrchestratorReviewer()
    package = orchestrator.review(paper)
    return package.to_dict()
