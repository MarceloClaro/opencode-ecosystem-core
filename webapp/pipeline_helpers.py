# -*- coding: utf-8 -*-
"""
Helpers do Pipeline Academico Agentivo (R101-R105) para a interface web.

Este módulo adapta os contratos internos reais de ``agentic_science_v2``
para um payload estável e amigável à UI Streamlit.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Garante a raiz do repositório no path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _iter_payload_items(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        return [item for item in payload.values() if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _extract_best_idea(history: List[Dict[str, Any]], seed_domain: str) -> Dict[str, Any]:
    ideas: List[Dict[str, Any]] = []
    for cycle in history:
        ideas.extend(cycle.get("ideas", []))

    if not ideas:
        return {
            "title": seed_domain,
            "content": seed_domain,
            "methodology": "",
            "score": 0.0,
        }

    best = max(
        ideas,
        key=lambda item: (item.get("scores", {}) or {}).get("overall", 0.0),
    )
    return {
        "id": best.get("id", "N/A"),
        "title": best.get("title", seed_domain),
        "content": best.get("hypothesis") or best.get("title") or seed_domain,
        "methodology": best.get("methodology", ""),
        "score": round((best.get("scores", {}) or {}).get("overall", 0.0), 2),
        "rationale": best.get("rationale", ""),
    }


def _build_sufficiency_gate(stats: Dict[str, Any]) -> Dict[str, Any]:
    entities = int(stats.get("entities", 0) or 0)
    relations = int(stats.get("relations", 0) or 0)
    score = entities + relations
    threshold = 6
    gaps = []

    if entities < 3:
        gaps.append(f"Need more entities (have {entities})")
    if relations < 3:
        gaps.append(f"Need more relations (have {relations})")

    return {
        "status": "PASS" if not gaps else "NEEDS_MORE_EVIDENCE",
        "score": score,
        "threshold": threshold,
        "gaps": gaps,
    }


def _coerce_review_sections(sections: Any) -> List[str]:
    if isinstance(sections, dict):
        return [str(name) for name in sections.keys()]
    if isinstance(sections, list):
        return [str(name) for name in sections]
    return []


def _coerce_review_package(review_package: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if review_package and review_package.get("reviews"):
        return review_package

    normalized_reviews = []
    for index, item in enumerate((review_package or {}).get("repair_plan", []), start=1):
        priority = (item.get("priority") or item.get("severity") or "medium").lower()
        risk = "high" if "critical" in priority or "major" in priority or priority == "high" else (
            "low" if "minor" in priority or priority == "low" else "medium"
        )
        normalized_reviews.append({
            "critic": item.get("reviewer", "Reviewer"),
            "claims": [{
                "id": f"claim-{index}",
                "text": item.get("action") or item.get("claim") or "Review comment",
                "risk": risk,
                "section": item.get("area") or item.get("section") or "introduction",
                "evidence": item.get("evidence", ""),
            }],
        })

    if not normalized_reviews:
        normalized_reviews = [{
            "critic": "SyntheticReviewer",
            "claims": [{
                "id": "claim-1",
                "text": "Clarify the manuscript structure and improve methodological detail.",
                "risk": "low",
                "section": "introduction",
                "evidence": "Synthetic fallback review package",
            }],
        }]

    return {"reviews": normalized_reviews}


def _build_graph_from_export(graph_data: Optional[Dict[str, Any]]):
    from agentic_science_v2.evidence_graph import EvidenceGraph

    graph = EvidenceGraph()
    if not graph_data:
        return graph

    id_map: Dict[str, str] = {}
    for item in _iter_payload_items(graph_data.get("entities", {})):
        entity = graph.add_entity(
            name=item.get("name") or item.get("label") or item.get("title") or item.get("id") or "Entity",
            entity_type=item.get("type") or item.get("entity_type") or item.get("group") or "concept",
            description=item.get("description", ""),
            aliases=item.get("aliases", []),
        )
        if item.get("id"):
            id_map[item["id"]] = entity.id

    for item in _iter_payload_items(graph_data.get("relations", {})):
        source_id = id_map.get(item.get("source") or item.get("source_id") or item.get("from"))
        target_id = id_map.get(item.get("target") or item.get("target_id") or item.get("to"))
        if source_id and target_id:
            graph.add_relation(
                source_id=source_id,
                target_id=target_id,
                relation_type=item.get("type") or item.get("relation_type") or item.get("label") or "ASSOCIATED_WITH",
                weight=item.get("weight", item.get("width", 1.0)) or 1.0,
            )

    return graph


# =========================================================================
# R101 - EvoSci
# =========================================================================

def run_evosci(seed_domain: str, max_rounds: int = 3, verbose: bool = False) -> Dict[str, Any]:
    """Executa um ciclo EvoSci (R101) completo e normaliza para a UI."""
    from agentic_science_v2.orchestrator import run_agentic_science_v2

    raw = run_agentic_science_v2(seed_domain=seed_domain, max_rounds=max_rounds)
    history = raw.get("history", [])
    best_solution = _extract_best_idea(history, seed_domain)

    trajectory = []
    for cycle in history:
        trajectory.append({
            "round": cycle.get("round", 0),
            "cluster": (cycle.get("cluster") or {}).get("title", "N/A"),
            "idea_count": len(cycle.get("ideas", [])),
            "fitness": (cycle.get("fitness") or {}).get("overall", 0.0),
            "duration": cycle.get("duration", 0.0),
        })

    if verbose:
        trajectory.append({"note": "verbose mode requested"})

    return {
        "cycle_id": history[-1].get("id", "N/A") if history else "N/A",
        "best_solution": best_solution,
        "evolutionary_trajectory": trajectory,
        "convergence_analysis": raw.get("summary", {}).get("evolution", {}),
        "rounds_executed": len(history),
        "status": "completed",
        "raw_summary": raw.get("summary", {}),
    }


def explain_evosci_components() -> Dict[str, str]:
    """Retorna descricao dos componentes do EvoSci para exibicao na UI."""
    return {
        "MentorAgent": "Constroi o espaco do problema e divide em subproblemas estrategicos.",
        "PrimeResearcherAgent": "Gera solucoes candidatas para cada subproblema com decomposicao hierarquica.",
        "ReviewerAgent": "Avalia cada solucao em multiplas dimensoes (novidade, viabilidade, impacto).",
        "EvolutionManagerAgent": "Mantem memorias persistentes de ideacao e experimentacao entre ciclos.",
        "EvoEngine": "Ciclo evolutivo: Selection -> Crossover -> Mutation -> Inheritance com deteccao de estagnacao.",
    }


# =========================================================================
# R102 - Deep Research
# =========================================================================

def run_deep_research(question: str, max_depth: int = 3, max_rounds: int = 5,
                      verbose: bool = False) -> Dict[str, Any]:
    """Executa pesquisa profunda (R102) e adapta o contrato para a UI."""
    from agentic_science_v2.deep_research import run_deep_research as run_deep_research_core

    raw = run_deep_research_core(
        question=question,
        max_rounds=max_rounds,
        max_depth=max_depth,
    )
    reports = raw.get("reports", [])
    latest = reports[-1] if reports else {}
    graph_data = raw.get("evidence_graph", {})
    stats = graph_data.get("stats") or raw.get("summary", {}).get("graph", {}) or {}

    sections = latest.get("sections", [])
    synthesized_answer = latest.get("summary", "")
    if not synthesized_answer and sections:
        synthesized_answer = "\n\n".join(
            section.get("content", "")
            for section in sections
            if isinstance(section, dict)
        )

    knowledge_sources = []
    for citation in latest.get("citations", []):
        if isinstance(citation, dict):
            knowledge_sources.append(
                citation.get("entity") or citation.get("source") or citation.get("type") or "citation"
            )

    if verbose:
        knowledge_sources.append("verbose")

    return {
        "question": question,
        "answer": synthesized_answer,
        "evidence_count": int(stats.get("evidence_pieces", 0) or 0),
        "entity_count": int(stats.get("entities", 0) or 0),
        "sufficiency_gate": _build_sufficiency_gate(stats),
        "knowledge_sources": knowledge_sources,
        "research_plan": (raw.get("plans") or [{}])[-1],
        "graph_data": graph_data,
        "raw_summary": raw.get("summary", {}),
    }


def query_evidence_graph(entity: str, graph_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Consulta o grafo de evidencias por nome de entidade."""
    graph = _build_graph_from_export(graph_data)
    entity_node = graph.find_entity_by_name(entity) if entity else None

    if not entity_node:
        return {
            "query": entity,
            "entities_found": 0,
            "relations_found": 0,
            "evidences_found": 0,
            "subgraph": {"entities": [], "relations": [], "total_entities": 0, "total_relations": 0},
        }

    subgraph = graph.subgraph_query([entity_node.id])
    evidences_found = sum(item.get("evidence_count", 0) for item in subgraph.get("entities", []))
    evidences_found += sum(item.get("evidence_count", 0) for item in subgraph.get("relations", []))

    return {
        "query": entity,
        "entities_found": subgraph.get("total_entities", 0),
        "relations_found": subgraph.get("total_relations", 0),
        "evidences_found": evidences_found,
        "subgraph": subgraph,
    }


# =========================================================================
# R103 - Peer Review
# =========================================================================

def run_peer_review(title: str, abstract: str, sections: Dict[str, str],
                    citations: Optional[List[str]] = None,
                    verbose: bool = False) -> Dict[str, Any]:
    """Executa revisao por pares agentiva (R103) e normaliza para a UI."""
    from agentic_science_v2.review_agent import run_peer_review as run_peer_review_core

    raw = run_peer_review_core(
        paper_title=title,
        paper_abstract=abstract,
        paper_sections=_coerce_review_sections(sections),
        citations=citations or [],
    )

    repair_plan = raw.get("repair_plan", [])
    verification_agenda = [
        item.get("action", "")
        for item in repair_plan
        if item.get("action")
    ]

    meta_review = (
        f"Score geral: {raw.get('overall_score', 0)} | "
        f"Rastreabilidade: {raw.get('traceability', 0)} | "
        f"Cobertura: {raw.get('coverage', 0)} | "
        f"Gate: {'APROVADO' if raw.get('export_gate_passed') else 'REPROVADO'}"
    )
    if verbose:
        meta_review += " | verbose"

    return {
        "meta_review": meta_review,
        "scores": raw.get("dimension_scores", {}),
        "repair_plan": repair_plan,
        "verification_agenda": verification_agenda,
        "critic_reports": raw.get("critiques_count", 0),
        "gate_result": {
            "overall_score": raw.get("overall_score", 0),
            "traceability": raw.get("traceability", 0),
            "coverage": raw.get("coverage", 0),
            "export_gate_passed": raw.get("export_gate_passed", False),
        },
        "paper_title": raw.get("paper_title", title),
        "overall_score": raw.get("overall_score", 0),
    }


def get_rubric_descriptions() -> List[Dict[str, Any]]:
    """Retorna as 8 dimensoes da rubrica com descricoes."""
    return [
        {"dimension": "Originalidade", "description": "O trabalho apresenta contribuicao nova?",
         "weight": 0.15, "polarity": "positiva"},
        {"dimension": "Metodologia", "description": "Os metodos sao adequados e bem descritos?",
         "weight": 0.20, "polarity": "positiva"},
        {"dimension": "Resultados", "description": "Os resultados sao convincentes e bem analisados?",
         "weight": 0.15, "polarity": "positiva"},
        {"dimension": "Reprodutibilidade", "description": "O experimento pode ser reproduzido?",
         "weight": 0.10, "polarity": "positiva"},
        {"dimension": "Clareza", "description": "A escrita e clara e bem estruturada?",
         "weight": 0.10, "polarity": "positiva"},
        {"dimension": "Etica", "description": "Ha preocupacoes eticas significativas?",
         "weight": 0.10, "polarity": "negativa"},
        {"dimension": "Literature Review", "description": "A revisao da literatura e adequada?",
         "weight": 0.10, "polarity": "positiva"},
        {"dimension": "Impacto", "description": "Qual o impacto potencial do trabalho?",
         "weight": 0.10, "polarity": "positiva"},
    ]


# =========================================================================
# R104d - Manuscript Revision
# =========================================================================

def run_manuscript_revision(manuscript_text: str,
                            review_package: Optional[Dict[str, Any]] = None,
                            verbose: bool = False) -> Dict[str, Any]:
    """Executa revisao de manuscrito (R104d) com adaptação de contrato."""
    from agentic_science_v2.revision_agent import create_revision

    manuscript = manuscript_text if isinstance(manuscript_text, str) else manuscript_text.get("full_text", "")
    coerced_review_package = _coerce_review_package(review_package)
    raw = create_revision(coerced_review_package, manuscript)

    revisions = raw.get("revisions", [])
    revised_manuscript = manuscript
    for revision in reversed(revisions):
        proposal = revision.get("proposal") or {}
        if proposal.get("revised_text"):
            revised_manuscript = proposal["revised_text"]
            break

    changes_applied = sum(1 for revision in revisions if revision.get("status") == "applied")
    if verbose and raw.get("diff"):
        revised_manuscript = revised_manuscript or raw.get("diff")

    return {
        "revised_manuscript": revised_manuscript,
        "rebuttal_letter": raw.get("rebuttal_letter", ""),
        "diff_stats": {
            "changes": revisions,
            "integrity": raw.get("integrity", {}),
            "diff_length": len(raw.get("diff", "")),
        },
        "changes_applied": changes_applied,
        "diff": raw.get("diff", ""),
    }


# =========================================================================
# R105 - Paper Composer
# =========================================================================

def compose_paper(title: str, sections_content: Dict[str, str],
                  venue: str = "abnt",
                  citations: Optional[List[Any]] = None,
                  verbose: bool = False) -> Dict[str, Any]:
    """Compoe paper academico preservando o texto manual da UI."""
    from agentic_science_v2.paper_composer import (
        CitationFormatter,
        CrossConsistencyVerifier,
        StructurePlanner,
    )

    planner = StructurePlanner()
    formatter = CitationFormatter()
    verifier = CrossConsistencyVerifier()
    outline = planner.plan(title, venue)

    normalized_sections = {
        "abstract": sections_content.get("abstract", ""),
        "introduction": sections_content.get("introduction", ""),
        "methods": sections_content.get("methods", ""),
        "results": sections_content.get("results", ""),
        "discussion": sections_content.get("discussion", ""),
        "conclusion": sections_content.get("conclusion", ""),
    }

    formatted_refs = []
    for citation in citations or []:
        if isinstance(citation, dict):
            formatted_refs.append(formatter.format(citation, style=outline["citation_style"]))
        else:
            formatted_refs.append(str(citation))

    normalized_sections["references"] = "\n".join(formatted_refs)
    consistency_report = verifier.full_report(normalized_sections, discoveries=[], evidence_graph={})

    heading_map = {
        "abstract": "Abstract",
        "introduction": "Introduction",
        "methods": "Methods",
        "results": "Results",
        "discussion": "Discussion",
        "conclusion": "Conclusion",
        "references": "References",
    }
    manuscript_parts = [f"# {title}", ""]
    for section_type in ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]:
        manuscript_parts.extend([
            f"## {heading_map[section_type]}",
            normalized_sections.get(section_type, ""),
            "",
        ])
    manuscript_parts.extend([
        "## References",
        normalized_sections.get("references", "") or "References will be added later.",
    ])
    manuscript = "\n".join(manuscript_parts)

    if verbose and not formatted_refs:
        formatted_refs.append("verbose")

    return {
        "full_text": manuscript,
        "citations_formatted": formatted_refs,
        "consistency_report": consistency_report,
        "structure": outline,
        "venue": outline["venue"],
    }


# =========================================================================
# Pipeline Completo R101 -> R105 (fundido no orquestrador marceloclaro)
# =========================================================================
#
# As funcoes abaixo adaptam os estagios BRUTOS retornados por
# ``MarceloClaroOrchestrator.scientific_discovery_pipeline`` (SPEC-935-R108)
# para as mesmas chaves de UI que ``run_evosci``/``run_deep_research``/
# ``run_peer_review``/``run_manuscript_revision`` ja produzem quando usadas
# isoladamente (paineis individuais do dashboard). Sao deliberadamente
# separadas dessas funcoes-irma (nao as reaproveitam) para nao alterar o
# comportamento, ja testado, dos paineis individuais.

def _adapt_evosci_raw(raw: Dict[str, Any], seed_domain: str) -> Dict[str, Any]:
    history = raw.get("history", [])
    best_solution = _extract_best_idea(history, seed_domain)
    trajectory = [{
        "round": cycle.get("round", 0),
        "cluster": (cycle.get("cluster") or {}).get("title", "N/A"),
        "idea_count": len(cycle.get("ideas", [])),
        "fitness": (cycle.get("fitness") or {}).get("overall", 0.0),
        "duration": cycle.get("duration", 0.0),
    } for cycle in history]
    return {
        "cycle_id": history[-1].get("id", "N/A") if history else "N/A",
        "best_solution": best_solution,
        "evolutionary_trajectory": trajectory,
        "convergence_analysis": raw.get("summary", {}).get("evolution", {}),
        "rounds_executed": len(history),
        "status": "completed",
        "raw_summary": raw.get("summary", {}),
    }


def _adapt_deep_research_raw(raw: Dict[str, Any], question: str) -> Dict[str, Any]:
    reports = raw.get("reports", [])
    latest = reports[-1] if reports else {}
    graph_data = raw.get("evidence_graph", {})
    stats = graph_data.get("stats") or raw.get("summary", {}).get("graph", {}) or {}
    sections = latest.get("sections", [])
    synthesized_answer = latest.get("summary", "")
    if not synthesized_answer and sections:
        synthesized_answer = "\n\n".join(
            section.get("content", "") for section in sections if isinstance(section, dict)
        )
    knowledge_sources = []
    for citation in latest.get("citations", []):
        if isinstance(citation, dict):
            knowledge_sources.append(
                citation.get("entity") or citation.get("source") or citation.get("type") or "citation"
            )
    return {
        "question": question,
        "answer": synthesized_answer,
        "evidence_count": int(stats.get("evidence_pieces", 0) or 0),
        "entity_count": int(stats.get("entities", 0) or 0),
        "sufficiency_gate": _build_sufficiency_gate(stats),
        "knowledge_sources": knowledge_sources,
        "research_plan": (raw.get("plans") or [{}])[-1],
        "graph_data": graph_data,
        "raw_summary": raw.get("summary", {}),
    }


def _adapt_peer_review_raw(raw: Dict[str, Any], title: str) -> Dict[str, Any]:
    repair_plan = raw.get("repair_plan", [])
    verification_agenda = [item.get("action", "") for item in repair_plan if item.get("action")]
    meta_review = (
        f"Score geral: {raw.get('overall_score', 0)} | "
        f"Rastreabilidade: {raw.get('traceability', 0)} | "
        f"Cobertura: {raw.get('coverage', 0)} | "
        f"Gate: {'APROVADO' if raw.get('export_gate_passed') else 'REPROVADO'}"
    )
    return {
        "meta_review": meta_review,
        "scores": raw.get("dimension_scores", {}),
        "repair_plan": repair_plan,
        "verification_agenda": verification_agenda,
        "critic_reports": raw.get("critiques_count", 0),
        "gate_result": {
            "overall_score": raw.get("overall_score", 0),
            "traceability": raw.get("traceability", 0),
            "coverage": raw.get("coverage", 0),
            "export_gate_passed": raw.get("export_gate_passed", False),
        },
        "paper_title": raw.get("paper_title", title),
        "overall_score": raw.get("overall_score", 0),
    }


def _adapt_revision_raw(raw: Dict[str, Any], manuscript: str) -> Dict[str, Any]:
    revisions = raw.get("revisions", [])
    revised_manuscript = manuscript
    for revision in reversed(revisions):
        proposal = revision.get("proposal") or {}
        if proposal.get("revised_text"):
            revised_manuscript = proposal["revised_text"]
            break
    changes_applied = sum(1 for revision in revisions if revision.get("status") == "applied")
    return {
        "revised_manuscript": revised_manuscript,
        "rebuttal_letter": raw.get("rebuttal_letter", ""),
        "diff_stats": {
            "changes": revisions,
            "integrity": raw.get("integrity", {}),
            "diff_length": len(raw.get("diff", "")),
        },
        "changes_applied": changes_applied,
        "diff": raw.get("diff", ""),
    }


def _adapt_composer_raw(raw: Dict[str, Any], venue: str) -> Dict[str, Any]:
    """Adapta a saida do R105 REAL (SectionWriter auto-compondo a partir de
    discoveries/evidence_graph/review) para a mesma forma que a UI espera
    do ``compose_paper`` manual. ``consistency_report`` e achatado para
    apenas campos escalares porque a UI renderiza cada chave com
    ``st.metric`` (que nao aceita dict como valor)."""
    consistency = raw.get("consistency_report", {}) or {}
    flat_consistency = {
        k: v for k, v in consistency.items()
        if isinstance(v, (int, float, str, bool))
    }
    return {
        "full_text": raw.get("manuscript", ""),
        "citations_formatted": [],
        "consistency_report": flat_consistency,
        "structure": raw.get("outline", {}),
        "venue": venue,
    }


def run_full_academic_pipeline(seed_domain: str, max_rounds: int = 3,
                               venue: str = "abnt",
                               verbose: bool = False) -> Dict[str, Any]:
    """Executa o pipeline completo (EvoSci -> DeepRes -> Review -> Revision ->
    Composer) atraves do orquestrador ``marceloclaro`` (SPEC-935-R108).

    Ao contrario da versao anterior (que encadeava os 5 estagios
    manualmente nesta camada de UI), a orquestracao real — incluindo o
    gate de exportacao do R103, a calibracao de confianca e a avaliacao
    metacognitiva SPEC-920 — agora vive em
    ``MarceloClaroOrchestrator.scientific_discovery_pipeline``. Esta
    funcao apenas adapta o resultado para o payload que a UI ja consome.
    """
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    result = orch.scientific_discovery_pipeline(
        seed_domain=seed_domain, max_rounds=max_rounds, venue=venue,
        strict_gates=True,
    )

    stages = result.get("stages", {})
    r101_raw = stages.get("r101", {})
    r102_raw = stages.get("r102", {})
    r103_raw = stages.get("r103", {})

    evosci = _adapt_evosci_raw(r101_raw, seed_domain) if r101_raw else {}
    question = evosci.get("best_solution", {}).get("content", seed_domain)
    deep = _adapt_deep_research_raw(r102_raw, question) if r102_raw else {}
    review = _adapt_peer_review_raw(r103_raw, seed_domain) if r103_raw else {}

    timeline = {
        "R101_evosci": result.get("timeline", {}).get("r101", 0.0),
        "R102_deep": result.get("timeline", {}).get("r102", 0.0),
        "R103_review": result.get("timeline", {}).get("r103", 0.0),
        "R104d_revision": result.get("timeline", {}).get("r104d", 0.0),
        "R105_composer": result.get("timeline", {}).get("r105", 0.0),
        "total": result.get("timeline", {}).get("total", 0.0),
    }

    if result["status"] == "blocked":
        return {
            "pipeline_result": "blocked",
            "block_reason": result.get("reason", ""),
            "seed_domain": seed_domain,
            "venue": venue,
            "timeline": timeline,
            "evosci": evosci,
            "deep_research": deep,
            "peer_review": review,
            "manuscript_revision": {},
            "paper": {},
            "metacognitive_report": result.get("metacognitive_report", {}),
        }

    r104d_raw = stages.get("r104d", {})
    r105_raw = stages.get("r105", {})
    manuscript_seed = deep.get("answer", "Manuscrito gerado automaticamente.")
    revision = _adapt_revision_raw(r104d_raw, manuscript_seed) if r104d_raw else {}
    paper = _adapt_composer_raw(r105_raw, venue) if r105_raw else {}

    return {
        "pipeline_result": "completed" if result["status"] == "completed" else result["status"],
        "seed_domain": seed_domain,
        "venue": venue,
        "timeline": timeline,
        "evosci": evosci,
        "deep_research": deep,
        "peer_review": review,
        "manuscript_revision": revision,
        "paper": paper,
        "metacognitive_report": result.get("metacognitive_report", {}),
    }


__all__ = [
    "run_evosci", "explain_evosci_components",
    "run_deep_research", "query_evidence_graph",
    "run_peer_review", "get_rubric_descriptions",
    "run_manuscript_revision",
    "compose_paper",
    "run_full_academic_pipeline",
]
