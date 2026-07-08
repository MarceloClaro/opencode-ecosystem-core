"""Validação Empírica — SPEC-935 R79.

Painel de professores-especialistas avaliando as teses geradas pela
Universidade Sintética Transversal.

Cada professor avalia as teses do seu domínio, produzindo:
- Score de relevância (especialidade + interesse)
- Endosso (forte/moderado/fraco)
- Feedback qualitativo
- Viability ajustada pela perspectiva do especialista
"""

from __future__ import annotations
import json
import time
import math
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter

from synthetic_university.agents.professors import create_all_professors
from synthetic_university.agents.professor_base import Professor
from synthetic_university.thesis_generator import Thesis
from synthetic_university.semantic_embedder import SemanticEmbedder, create_semantic_embedder

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENDORSEMENT_WEIGHTS = {
    "strong": 1.0,
    "moderate": 0.6,
    "weak": 0.2,
}

EVALUATION_CRITERIA = [
    "relevance",          # relevância para a área do professor
    "originality",        # originalidade percebida
    "feasibility",        # exequibilidade da pesquisa
    "impact",             # impacto potencial
    "clarity",            # clareza da proposta
]

# ---------------------------------------------------------------------------
# EmpiricalValidator
# ---------------------------------------------------------------------------

class EmpiricalValidator:
    """Painel de validação empírica com professores-especialistas.
    
    Arquitetura:
    1. Pool de professores (38+ especialistas de 11 faculdades)
    2. Roteamento: cada tese é avaliada pelos professores mais relevantes
    3. Scoring multi-critério com ponderação por especialidade
    4. Relatório consolidado com rankings e insights
    """

    def __init__(self, embedder: Optional[SemanticEmbedder] = None):
        self.professors = create_all_professors()
        self.embedder = embedder
        
        # Índice de professores por faculdade
        self._profs_by_faculty: Dict[str, List[Professor]] = defaultdict(list)
        for p in self.professors:
            self._profs_by_faculty[p.faculty_id].append(p)
        
        logger.info(
            f"EmpiricalValidator: {len(self.professors)} professores "
            f"de {len(self._profs_by_faculty)} faculdades"
        )
    
    # ------------------------------------------------------------------
    # Avaliação de tese individual
    # ------------------------------------------------------------------

    def evaluate_thesis(self, thesis: Thesis) -> Dict:
        """Avalia uma tese com todos os professores relevantes.
        
        Returns:
            Dict com avaliação consolidada da tese
        """
        # Identificar professores relevantes (mesma faculdade ou interesse similar)
        relevant_profs = self._find_relevant_professors(thesis)
        
        if not relevant_profs:
            return {
                "thesis_id": thesis.thesis_id,
                "title": thesis.title,
                "error": "Nenhum professor relevante encontrado",
                "n_evaluators": 0,
            }
        
        # Cada professor avalia
        evaluations = []
        for prof in relevant_profs:
            eval_result = self._professor_evaluate_thesis(prof, thesis)
            evaluations.append(eval_result)
        
        # Consolidar
        consolidated = self._consolidate_evaluations(thesis, evaluations)
        return consolidated
    
    def _find_relevant_professors(self, thesis: Thesis) -> List[Professor]:
        """Encontra professores relevantes para avaliar a tese.
        
        Critérios:
        1. Professores das faculdades envolvidas na tese
        2. Professores cujas especialidades têm overlap semântico com a tese
        """
        relevant = []
        seen = set()
        
        # 1. Por faculdade
        for fid in thesis.faculties_involved:
            for prof in self._profs_by_faculty.get(fid, []):
                if prof.professor_id not in seen:
                    relevant.append(prof)
                    seen.add(prof.professor_id)
        
        # 2. Por similaridade semântica de interesses
        if self.embedder:
            thesis_text = thesis.title + " " + thesis.hypothesis
            for prof in self.professors:
                if prof.professor_id in seen:
                    continue
                # Verificar similaridade entre interesses do professor e a tese
                for interest in prof.research_interests:
                    sim = self.embedder.similarity(interest, thesis_text[:200])
                    if sim > 0.50:  # threshold de relevância
                        relevant.append(prof)
                        seen.add(prof.professor_id)
                        break
        
        # Limitar a no máximo 5 avaliadores por tese
        if len(relevant) > 5:
            # Ordenar por índice H (mais experientes primeiro)
            relevant.sort(key=lambda p: p.h_index, reverse=True)
            relevant = relevant[:5]
        
        return relevant
    
    def _professor_evaluate_thesis(self, prof: Professor, thesis: Thesis) -> Dict:
        """Um professor avalia uma tese."""
        # Extrair conceitos da tese
        thesis_concepts = []
        for src_id in thesis.source_combinations[:5]:
            thesis_concepts.append(src_id)
        thesis_concepts.extend([
            c for c in [thesis.title, thesis.hypothesis] if c
        ])
        
        # Overlap léxico entre especialidades do prof e conceitos da tese
        specialty_overlap = 0
        interest_overlap = 0
        
        thesis_lower = (thesis.title + " " + thesis.hypothesis).lower()
        
        for s in prof.specialties:
            if s.lower() in thesis_lower:
                specialty_overlap += 1
        
        for i in prof.research_interests:
            if i.lower() in thesis_lower:
                interest_overlap += 1
        
        # Usar embedding para overlap semântico se disponível
        semantic_relevance = 0.0
        if self.embedder:
            semantic_scores = []
            for interest in prof.research_interests:
                sim = self.embedder.similarity(interest, thesis_lower[:300])
                semantic_scores.append(sim)
            semantic_relevance = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0.0
        
        # Scores
        n_concepts = max(1, len(thesis_concepts))
        specialty_score = min(1.0, specialty_overlap / max(1, len(prof.specialties)))
        interest_score = min(1.0, interest_overlap / max(1, len(prof.research_interests)))
        
        # Score composto de relevância
        relevance = max(
            specialty_score * 0.4 + interest_score * 0.3 + semantic_relevance * 0.3,
            semantic_relevance * 0.6  # mínimo baseado em embedding
        )
        
        # Determinar endosso
        if relevance >= 0.5:
            endorsement = "strong"
        elif relevance >= 0.25:
            endorsement = "moderate"
        else:
            endorsement = "weak"
        
        # Viability ajustada
        adjusted_viability = min(1.0, thesis.feasibility_score * (0.5 + 0.5 * relevance))
        
        # Feedback qualitativo
        feedback = self._generate_feedback(prof, thesis, relevance, endorsement)
        
        return {
            "professor_id": prof.professor_id,
            "professor_nome": prof.nome,
            "professor_title": prof.title,
            "faculty_id": prof.faculty_id,
            "h_index": prof.h_index,
            "specialty_score": round(specialty_score, 4),
            "interest_score": round(interest_score, 4),
            "semantic_relevance": round(semantic_relevance, 4),
            "composite_relevance": round(relevance, 4),
            "endorsement": endorsement,
            "adjusted_viability": round(adjusted_viability, 4),
            "feedback": feedback,
        }
    
    def _generate_feedback(self, prof: Professor, thesis: Thesis, 
                           relevance: float, endorsement: str) -> str:
        """Gera feedback textual do professor sobre a tese."""
        templates_pro = [
            f"Prof. {prof.nome} endossa a investigacao da correlacao entre "
            f"os conceitos apresentados, que se alinha com sua pesquisa em "
            f"{prof.specialties[0] if prof.specialties else 'sua area'}.",
            
            f"Para o Prof. {prof.nome}, a tese apresenta uma contribuicao "
            f"original ao conectar dominios que raramente sao articulados, "
            f"especialmente relevante para {prof.research_interests[0] if prof.research_interests else 'pesquisas interdisciplinares'}.",
            
            f"{prof.nome} reconhece o merito da abordagem e sugere "
            f"expandir a investigacao incorporando metodos de "
            f"{prof.specialties[0] if prof.specialties else 'sua area'}.",
        ]
        
        templates_moderate = [
            f"Prof. {prof.nome} ve potencial na proposta, mas recomenda "
            f"maior aprofundamento teorico em {prof.specialties[0] if prof.specialties else 'sua area'}.",
            
            f"{prof.nome} considera a correlacao interessante, porem "
            f"nota que a conexao entre os conceitos poderia ser mais "
            f"diretamente articulada com {prof.research_interests[0] if prof.research_interests else 'a literatura existente'}.",
        ]
        
        templates_weak = [
            f"Prof. {prof.nome} tem reservas quanto a viabilidade "
            f"da correlacao proposta, que se distancia de sua expertise "
            f"em {prof.specialties[0] if prof.specialties else 'sua area'}.",
            
            f"{prof.nome} sugere revisitar a hipotese a luz de "
            f"metodologias consolidadas em {prof.specialties[0] if prof.specialties else 'sua area'} "
            f"para maior robustez teorica.",
        ]
        
        if endorsement == "strong":
            import random
            return random.choice(templates_pro)
        elif endorsement == "moderate":
            return templates_moderate[0]
        else:
            return templates_weak[0]
    
    # ------------------------------------------------------------------
    # Consolidação
    # ------------------------------------------------------------------

    def _consolidate_evaluations(self, thesis: Thesis, 
                                  evaluations: List[Dict]) -> Dict:
        """Consolida múltiplas avaliações em um parecer único."""
        n = len(evaluations)
        if n == 0:
            return {"thesis_id": thesis.thesis_id, "error": "sem avaliacoes"}
        
        avg_relevance = sum(e["composite_relevance"] for e in evaluations) / n
        avg_viability = sum(e["adjusted_viability"] for e in evaluations) / n
        
        # Endosso majoritário
        endorsement_counts = Counter(e["endorsement"] for e in evaluations)
        majority_endorsement = endorsement_counts.most_common(1)[0][0]
        
        # Score composto da tese (avaliação empírica)
        endorsement_weight = ENDORSEMENT_WEIGHTS.get(majority_endorsement, 0.5)
        empirical_score = (
            avg_relevance * 0.4 +
            avg_viability * 0.3 +
            endorsement_weight * 0.3
        )
        
        return {
            "thesis_id": thesis.thesis_id,
            "title": thesis.title,
            "n_evaluators": n,
            "avg_relevance": round(avg_relevance, 4),
            "avg_adjusted_viability": round(avg_viability, 4),
            "majority_endorsement": majority_endorsement,
            "endorsement_distribution": dict(endorsement_counts),
            "empirical_score": round(empirical_score, 4),
            "composite_score_original": round(thesis.composite_score, 4),
            "evaluations": evaluations,
        }
    
    # ------------------------------------------------------------------
    # Validação em lote
    # ------------------------------------------------------------------

    def validate_theses(self, theses: List[Thesis]) -> Dict:
        """Valida um lote de teses com painel de especialistas."""
        logger.info(f"Validando {len(theses)} teses com painel empirico...")
        
        results = []
        total_start = time.time()
        
        for i, thesis in enumerate(theses):
            t_start = time.time()
            result = self.evaluate_thesis(thesis)
            t_elapsed = time.time() - t_start
            results.append(result)
            
            # Log progresso
            emp_score = result.get("empirical_score", 0)
            endorsement = result.get("majority_endorsement", "N/A")
            logger.info(
                f"  [{i+1}/{len(theses)}] {thesis.title[:50]}... "
                f"score={emp_score:.3f} end={endorsement} ({t_elapsed:.1f}s)"
            )
        
        total_time = time.time() - total_start
        
        # Estatísticas agregadas
        valid_results = [r for r in results if "error" not in r]
        
        agg_scores = {
            "avg_empirical_score": (
                sum(r["empirical_score"] for r in valid_results) / len(valid_results)
                if valid_results else 0
            ),
            "avg_relevance": (
                sum(r["avg_relevance"] for r in valid_results) / len(valid_results)
                if valid_results else 0
            ),
            "avg_viability": (
                sum(r["avg_adjusted_viability"] for r in valid_results) / len(valid_results)
                if valid_results else 0
            ),
        }
        
        # Distribuição de endosso
        endorsement_dist = Counter()
        for r in valid_results:
            endorsement_dist[r["majority_endorsement"]] += 1
        
        # Top teses por score empírico
        valid_results.sort(key=lambda r: r["empirical_score"], reverse=True)
        
        return {
            "pipeline": "R79 Empirical Validation",
            "n_theses": len(theses),
            "n_valid": len(valid_results),
            "n_evaluators_total": sum(r.get("n_evaluators", 0) for r in valid_results),
            "total_time_seconds": round(total_time, 2),
            "aggregate_scores": agg_scores,
            "endorsement_distribution": dict(endorsement_dist),
            "theses_ranked": [
                {
                    "rank": i + 1,
                    "thesis_id": r["thesis_id"],
                    "title": r["title"],
                    "empirical_score": r["empirical_score"],
                    "original_composite": r.get("composite_score_original", 0),
                    "majority_endorsement": r["majority_endorsement"],
                    "n_evaluators": r["n_evaluators"],
                    "top_evaluator": max(
                        r["evaluations"],
                        key=lambda e: e["composite_relevance"]
                    )["professor_nome"] if r.get("evaluations") else "N/A",
                }
                for i, r in enumerate(valid_results[:20])
            ],
            "all_results": results,
        }
    
    # ------------------------------------------------------------------
    # Relatório
    # ------------------------------------------------------------------

    def generate_report(self, validation_result: Dict) -> str:
        """Gera relatório textual da validação empírica."""
        agg = validation_result.get("aggregate_scores", {})
        end_dist = validation_result.get("endorsement_distribution", {})
        
        lines = []
        lines.append("=" * 65)
        lines.append("  RELATORIO DE VALIDACAO EMPIRICA — R79")
        lines.append(f"  {validation_result['n_theses']} teses avaliadas por "
                     f"{validation_result['n_evaluators_total']} avaliacoes de professores")
        lines.append("=" * 65)
        
        lines.append(f"\nSCORES AGREGADOS:")
        lines.append(f"  Score empírico médio: {agg.get('avg_empirical_score', 0):.4f}")
        lines.append(f"  Relevância média:     {agg.get('avg_relevance', 0):.4f}")
        lines.append(f"  Viability ajustada:   {agg.get('avg_viability', 0):.4f}")
        
        lines.append(f"\nDISTRIBUIÇÃO DE ENDOSSO:")
        total = sum(end_dist.values())
        for level in ["strong", "moderate", "weak"]:
            count = end_dist.get(level, 0)
            pct = count / total * 100 if total > 0 else 0
            bar = "█" * max(1, int(pct / 5))
            lines.append(f"  {level:10s} {bar} {count}/{total} ({pct:.0f}%)")
        
        lines.append(f"\nTOP TESES VALIDADAS (por score empírico):")
        lines.append(f"  {'Rank':>5s} {'Score':>6s} {'Endosso':>10s} {'Titulo':60s}")
        lines.append(f"  {'-'*5} {'-'*6} {'-'*10} {'-'*60}")
        for t in validation_result.get("theses_ranked", [])[:10]:
            lines.append(
                f"  {t['rank']:5d} {t['empirical_score']:.4f} "
                f"{t['majority_endorsement']:>10s} "
                f"{t['title'][:60]}"
            )
        
        lines.append(f"\nTEMPO TOTAL: {validation_result['total_time_seconds']:.1f}s")
        lines.append("=" * 65)
        
        return "\n".join(lines)
