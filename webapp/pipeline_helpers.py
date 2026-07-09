# -*- coding: utf-8 -*-
"""
Helpers do Pipeline Academico Agentivo (R101-R105) para a interface web.

Oferece funcoes puras de ponte entre a UI Streamlit e os modulos
agentic_science_v2, evolution, rag, etc.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Garante a raiz do repositorio no path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# =========================================================================
# R101 - EvoSci
# =========================================================================

def run_evosci(seed_domain: str, max_rounds: int = 3, verbose: bool = False) -> Dict[str, Any]:
    """Executa um ciclo EvoSci (R101) completo."""
    from agentic_science_v2.orchestrator import AgenticScienceV2
    engine = AgenticScienceV2(verbose=verbose)
    result = engine.run(seed_domain=seed_domain, max_rounds=max_rounds)
    return {
        "cycle_id": result.get("cycle_id", "N/A"),
        "best_solution": result.get("best_solution", {}),
        "evolutionary_trajectory": result.get("evolutionary_trajectory", []),
        "convergence_analysis": result.get("convergence_analysis", {}),
        "rounds_executed": len(result.get("evolutionary_trajectory", [])),
        "status": "completed",
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
    """Executa pesquisa profunda (R102)."""
    from agentic_science_v2.deep_research import OrchestratorAgent
    orchestrator = OrchestratorAgent(max_depth=max_depth, verbose=verbose)
    report = orchestrator.run(question=question, max_rounds=max_rounds)
    return {
        "question": question,
        "answer": report.get("answer", ""),
        "evidence_count": len(report.get("evidence_subgraph", {}).get("evidences", [])),
        "entity_count": len(report.get("evidence_subgraph", {}).get("entities", [])),
        "sufficiency_gate": report.get("sufficiency_gate", {}),
        "knowledge_sources": report.get("knowledge_sources", []),
        "research_plan": report.get("research_plan", {}),
    }

def query_evidence_graph(entity: str, graph_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Consulta o grafo de evidencias por entidade."""
    from agentic_science_v2.evidence_graph import EvidenceGraph
    g = EvidenceGraph()
    if graph_data:
        g.load(graph_data)
    results = g.subgraph_query([entity]) if entity else {"entities": [], "relations": [], "evidences": []}
    return {
        "query": entity,
        "entities_found": len(results.get("entities", [])),
        "relations_found": len(results.get("relations", [])),
        "evidences_found": len(results.get("evidences", [])),
        "subgraph": results,
    }

# =========================================================================
# R103 - Peer Review
# =========================================================================

def run_peer_review(title: str, abstract: str, sections: Dict[str, str],
                    citations: Optional[List[str]] = None,
                    verbose: bool = False) -> Dict[str, Any]:
    """Executa revisao por pares agentiva (R103)."""
    from agentic_science_v2.review_agent import OrchestratorReviewer
    reviewer = OrchestratorReviewer(verbose=verbose)
    review = reviewer.run(title=title, abstract=abstract,
                          sections=sections, citations=citations or [])
    return {
        "meta_review": review.get("meta_review", ""),
        "scores": review.get("scores", {}),
        "repair_plan": review.get("repair_plan", []),
        "verification_agenda": review.get("verification_agenda", []),
        "critic_reports": review.get("critic_reports", []),
        "gate_result": review.get("gate_result", {}),
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
                            review_package: Optional[Dict] = None,
                            verbose: bool = False) -> Dict[str, Any]:
    """Executa revisao de manuscrito (R104d)."""
    from agentic_science_v2.revision_agent import OrchestratorRevision
    revision = OrchestratorRevision(verbose=verbose)
    # Se nao tiver review package, cria um sintetico basico
    if not review_package:
        review_package = {
            "meta_review": "Revisao textual basica.",
            "scores": {"Clareza": 7.0, "Metodologia": 6.5},
            "repair_plan": [
                {"severity": "minor", "claim": "Melhorar clareza na introducao",
                 "evidence": "Texto confuso", "section": "introduction"}
            ]
        }
    # Cria um manuscrito dict se for string
    if isinstance(manuscript_text, str):
        manuscript = {"full_text": manuscript_text}
    else:
        manuscript = manuscript_text
    result = revision.run(review_package=review_package, manuscript=manuscript)
    return {
        "revised_manuscript": result.get("revised_manuscript", ""),
        "rebuttal_letter": result.get("rebuttal_letter", ""),
        "diff_stats": result.get("diff_stats", {}),
        "changes_applied": len(result.get("diff_stats", {}).get("changes", [])),
    }

# =========================================================================
# R105 - Paper Composer
# =========================================================================

def compose_paper(title: str, sections_content: Dict[str, str],
                  venue: str = "abnt",
                  citations: Optional[List[Dict]] = None,
                  verbose: bool = False) -> Dict[str, Any]:
    """Compoe paper academico completo (R105)."""
    from agentic_science_v2.paper_composer import OrchestratorComposer
    composer = OrchestratorComposer(verbose=verbose)
    paper = composer.run(title=title, sections_content=sections_content,
                         venue=venue, citations=citations or [])
    return {
        "full_text": paper.get("full_text", ""),
        "citations_formatted": paper.get("citations_formatted", []),
        "consistency_report": paper.get("consistency_report", {}),
        "structure": paper.get("structure", {}),
        "venue": venue,
    }

# =========================================================================
# Pipeline Completo R101 -> R105
# =========================================================================

def run_full_academic_pipeline(seed_domain: str, max_rounds: int = 3,
                               venue: str = "abnt",
                               verbose: bool = False) -> Dict[str, Any]:
    """Executa o pipeline completo: EvoSci -> DeepRes -> Review -> Revision -> Composer."""
    import time
    timeline = {}
    t0 = time.time()

    # R101
    t1 = time.time()
    evosci = run_evosci(seed_domain, max_rounds, verbose)
    timeline["R101_evosci"] = round(time.time() - t1, 1)

    # R102 - usa a melhor solucao do EvoSci como pergunta
    best = evosci.get("best_solution", {})
    question = best.get("content", seed_domain)
    t2 = time.time()
    deep = run_deep_research(question, max_depth=3, max_rounds=5, verbose=verbose)
    timeline["R102_deep"] = round(time.time() - t2, 1)

    # R103
    t3 = time.time()
    review = run_peer_review(
        title=seed_domain,
        abstract=deep.get("answer", "")[:500],
        sections={"introduction": f"Context: {seed_domain}",
                  "methods": "Deep Research methodology",
                  "results": deep.get("answer", "")},
        verbose=verbose,
    )
    timeline["R103_review"] = round(time.time() - t3, 1)

    # R104d
    t4 = time.time()
    revision = run_manuscript_revision(
        manuscript_text=deep.get("answer", "Manuscrito gerado automaticamente."),
        review_package=review,
        verbose=verbose,
    )
    timeline["R104d_revision"] = round(time.time() - t4, 1)

    # R105
    t5 = time.time()
    paper = compose_paper(
        title=seed_domain,
        sections_content={
            "abstract": deep.get("answer", "")[:300],
            "introduction": f"Este artigo aborda {seed_domain}.",
            "methods": "Utilizou-se o pipeline agentico EvoSci + Deep Research.",
            "results": deep.get("answer", ""),
            "discussion": "Os resultados indicam direcoes promissoras para pesquisa futura.",
            "conclusion": f"{seed_domain} representa uma area importante para investigacao.",
        },
        venue=venue,
        verbose=verbose,
    )
    timeline["R105_composer"] = round(time.time() - t5, 1)
    timeline["total"] = round(time.time() - t0, 1)

    return {
        "pipeline_result": "completed",
        "seed_domain": seed_domain,
        "venue": venue,
        "timeline": timeline,
        "evosci": evosci,
        "deep_research": deep,
        "peer_review": review,
        "manuscript_revision": revision,
        "paper": paper,
    }


__all__ = [
    "run_evosci", "explain_evosci_components",
    "run_deep_research", "query_evidence_graph",
    "run_peer_review", "get_rubric_descriptions",
    "run_manuscript_revision",
    "compose_paper",
    "run_full_academic_pipeline",
]
