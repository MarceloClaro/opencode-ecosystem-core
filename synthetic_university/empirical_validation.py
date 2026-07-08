"""Validação Empírica Calibrada — SPEC-935 R82.
 
 Painel expandido de 100+ professores com thresholds de endosso recalibrados.
 
 Principais melhorias (R82):
 1. Painel expandido para 100+ professores (pool sintético)
 2. Endosso considera convergência entre avaliadores
 3. Ponderação por confiança (baseada em h-index)
 4. Thresholds calibrados para permitir endosso "strong"
 5. Score empírico com penalidade por baixa convergência
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
# Constants (R82 — Calibrados)
# ---------------------------------------------------------------------------

ENDORSEMENT_WEIGHTS = {
    "strong": 1.0,
    "moderate": 0.6,
    "weak": 0.2,
}

# R82: Novos thresholds com convergência
STRONG_THRESHOLD_RELEVANCE = 0.40     # relevância mínima para strong
STRONG_CONVERGENCE_RATE = 0.60         # ≥60% dos avaliadores concordam
STRONG_CONFIDENCE_THRESHOLD = 0.50     # confiança mínima

MODERATE_THRESHOLD_RELEVANCE = 0.20    # relevância mínima para moderate
MODERATE_CONVERGENCE_RATE = 0.40       # ≥40% dos avaliadores concordam

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
        """Encontra professores relevantes para avaliar a tese (R82 — expandido).
        
        Critérios:
        1. Professores das faculdades envolvidas na tese (pool prioritário)
        2. Professores com overlap semântico via embedding
        3. Amostra balanceada para evitar super-representação de uma faculdade
        
        Retorna até 5 avaliadores (R82: garante diversidade de faculdades).
        """
        relevant = []
        seen = set()
        
        # 1. Por faculdade envolvida na tese (pool prioritário)
        faculty_pool = defaultdict(list)
        for fid in thesis.faculties_involved:
            for prof in self._profs_by_faculty.get(fid, []):
                if prof.professor_id not in seen:
                    faculty_pool[fid].append(prof)
                    seen.add(prof.professor_id)
        
        # Selecionar até 2 professores de cada faculdade envolvida
        for fid, profs in faculty_pool.items():
            profs.sort(key=lambda p: p.h_index, reverse=True)
            for prof in profs[:2]:
                relevant.append(prof)
        
        # 2. Se ainda faltam avaliadores, buscar por similaridade semântica
        if len(relevant) < 3 and self.embedder:
            thesis_text = thesis.title + " " + thesis.hypothesis
            candidates = []
            for prof in self.professors:
                if prof.professor_id in seen:
                    continue
                max_sim = max(
                    (self.embedder.similarity(interest, thesis_text[:200]) 
                     for interest in prof.research_interests),
                    default=0.0
                )
                if max_sim > 0.50:
                    candidates.append((prof, max_sim))
            
            # Ordenar por similaridade e adicionar
            candidates.sort(key=lambda x: x[1], reverse=True)
            for prof, _ in candidates[:3]:
                if len(relevant) >= 5:
                    break
                relevant.append(prof)
                seen.add(prof.professor_id)
        
        # 3. Limitar a no máximo 5, garantindo diversidade
        if len(relevant) > 5:
            # Manter diversidade de faculdades
            relevant.sort(key=lambda p: (
                # Priorizar faculdades sub-representadas
                sum(1 for r in relevant if r.faculty_id == p.faculty_id),
                -p.h_index  # depois por senioridade
            ))
            relevant = relevant[:5]
        
        return relevant
    
    def _professor_evaluate_thesis(self, prof: Professor, thesis: Thesis) -> Dict:
        """Um professor avalia uma tese (R82 — com confidence score)."""
        # Extrair conceitos da tese
        thesis_concepts = []
        for src_id in thesis.source_combinations[:5]:
            thesis_concepts.append(src_id)
        thesis_concepts.extend([
            c for c in [thesis.title, thesis.hypothesis] if c
        ])
        
        thesis_lower = (thesis.title + " " + thesis.hypothesis).lower()
        
        # Overlap léxico
        specialty_overlap = 0
        interest_overlap = 0
        
        for s in prof.specialties:
            if s.lower() in thesis_lower:
                specialty_overlap += 1
        
        for i in prof.research_interests:
            if i.lower() in thesis_lower:
                interest_overlap += 1
        
        # Embedding semântico
        semantic_relevance = 0.0
        if self.embedder:
            semantic_scores = []
            for interest in prof.research_interests:
                sim = self.embedder.similarity(interest, thesis_lower[:300])
                semantic_scores.append(sim)
            semantic_relevance = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0.0
        
        scores = {
            "specialty": min(1.0, specialty_overlap / max(1, len(prof.specialties))),
            "interest": min(1.0, interest_overlap / max(1, len(prof.research_interests))),
            "semantic": semantic_relevance,
        }
        
        # Score composto de relevância
        relevance = max(
            scores["specialty"] * 0.4 + scores["interest"] * 0.3 + scores["semantic"] * 0.3,
            scores["semantic"] * 0.6
        )
        
        # R82: Confidence score baseado em h-index
        # h-index normalizado para [0, 1] com sqrt para suavizar
        h_norm = min(1.0, math.sqrt(prof.h_index / 50.0))
        confidence = 0.4 + 0.6 * h_norm  # mínimo 0.4 para professores juniors
        
        # Determinar endosso (R82: sem threshold fixo — será consolidado)
        if relevance >= 0.45:
            endorsement = "strong"
        elif relevance >= 0.20:
            endorsement = "moderate"
        else:
            endorsement = "weak"
        
        # Viability ajustada
        adjusted_viability = min(1.0, thesis.feasibility_score * (0.5 + 0.5 * relevance))
        
        # Feedback
        feedback = self._generate_feedback(prof, thesis, relevance, endorsement)
        
        return {
            "professor_id": prof.professor_id,
            "professor_nome": prof.nome,
            "professor_title": prof.title,
            "faculty_id": prof.faculty_id,
            "h_index": prof.h_index,
            "confidence": round(confidence, 4),
            "specialty_score": round(scores["specialty"], 4),
            "interest_score": round(scores["interest"], 4),
            "semantic_relevance": round(scores["semantic"], 4),
            "composite_relevance": round(relevance, 4),
            "endorsement": endorsement,
            "adjusted_viability": round(adjusted_viability, 4),
            "feedback": feedback,
        }
    
    def _generate_feedback(self, prof: Professor, thesis: Thesis, 
                           relevance: float, endorsement: str) -> str:
        """Gera feedback textual do professor sobre a tese.
        
        R83: Usa LLM local (Ollama) quando disponível para gerar feedback
        contextualizado e rico. Fallback para templates quando LLM não responde.
        """
        # Tentar LLM
        llm_feedback = self._try_llm_feedback(prof, thesis, endorsement)
        if llm_feedback:
            return llm_feedback
        
        # Fallback para templates
        return self._template_feedback(prof, thesis, relevance, endorsement)
    
    def _try_llm_feedback(self, prof: Professor, thesis: Thesis, 
                           endorsement: str) -> Optional[str]:
        """Tenta gerar feedback via Ollama. Retorna None se indisponível."""
        try:
            import urllib.request
            import json
            
            # Construir prompt contextualizado
            prompt = (
                f"Voce e o Professor {prof.nome}, {prof.title} da faculdade de "
                f"{prof.faculty_id}. Suas especialidades sao: "
                f"{', '.join(prof.specialties[:3])}. "
                f"Seus interesses de pesquisa incluem: "
                f"{', '.join(prof.research_interests[:3])}. "
                f"\n\n"
                f"Voce esta avaliando a seguinte tese:\n"
                f"Titulo: {thesis.title}\n"
                f"Hipótese: {thesis.hypothesis[:200]}\n"
                f"Dominios envolvidos: {', '.join(thesis.faculties_involved)}\n"
                f"\n"
                f"Seu endosso e: {endorsement.upper()}\n"
                f"\n"
                f"Escreva UM PARAGRAFO de feedback academico (2-4 frases) "
                f"justificando sua avaliacao. Seja especifico: mencione conceitos "
                f"da tese e relacione com sua propria pesquisa. "
                f"Escreva em portugues academico, em primeira pessoa."
                f"Nao use cumprimentos nem saudacoes."
            )
            
            payload = json.dumps({
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 200,
                    "num_predict": 200,
                }
            }).encode()
            
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            # Timeout curto para nao travar a validacao
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode())
                text = result.get("response", "").strip()
                
                if text and len(text) > 20:
                    # Limpar: remover possivel prefixo do prompt
                    if ":" in text[:30]:
                        text = text.split(":", 1)[1].strip()
                    return text[:500]  # limitar tamanho
        
        except Exception:
            pass  # Fallback silencioso
        
        return None
    
    def _template_feedback(self, prof: Professor, thesis: Thesis, 
                           relevance: float, endorsement: str) -> str:
        """Fallback: feedback baseado em templates quando LLM não disponível."""
        templates_pro = [
            f"Prof. {prof.nome} endossa a investigacao da correlacao entre "
            f"os conceitos apresentados, que se alinha com sua pesquisa em "
            f"{prof.specialties[0] if prof.specialties else 'sua area'}.",
            
            f"Para o Prof. {prof.nome}, a tese apresenta uma contribuicao "
            f"original ao conectar dominios que raramente sao articulados, "
            f"especialmente relevante para {prof.research_interests[0] if prof.research_interests else 'pesquisas interdisciplinares'}.",
        ]
        
        templates_moderate = [
            f"Prof. {prof.nome} ve potencial na proposta, mas recomenda "
            f"maior aprofundamento teorico em {prof.specialties[0] if prof.specialties else 'sua area'}.",
        ]
        
        templates_weak = [
            f"Prof. {prof.nome} tem reservas quanto a viabilidade "
            f"da correlacao proposta, que se distancia de sua expertise "
            f"em {prof.specialties[0] if prof.specialties else 'sua area'}.",
        ]
        
        import random
        if endorsement == "strong":
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
        """Consolida múltiplas avaliações em um parecer único (R82).
        
        R82: Nova lógica de endosso com:
        - Convergência entre avaliadores
        - Ponderação por confiança (h-index)
        - Thresholds calibrados para permitir "strong"
        """
        n = len(evaluations)
        if n == 0:
            return {"thesis_id": thesis.thesis_id, "error": "sem avaliacoes"}
        
        # Médias
        avg_relevance = sum(e["composite_relevance"] for e in evaluations) / n
        avg_viability = sum(e["adjusted_viability"] for e in evaluations) / n
        
        # R82: Score ponderado por confiança
        total_confidence = sum(e["confidence"] for e in evaluations)
        weighted_relevance = sum(
            e["composite_relevance"] * e["confidence"] for e in evaluations
        ) / total_confidence if total_confidence > 0 else avg_relevance
        
        # Convergência: fração que deu pelo menos "moderate"
        moderate_or_better = sum(
            1 for e in evaluations 
            if e["endorsement"] in ("strong", "moderate")
        )
        convergence_rate = moderate_or_better / n
        
        # Endosso majoritário (voto simples como fallback)
        endorsement_counts = Counter(e["endorsement"] for e in evaluations)
        majority_endorsement = endorsement_counts.most_common(1)[0][0]
        
        # R82: Calibrar endosso com base em convergência + relevância
        calibrated_endorsement = self._calibrate_endorsement(
            weighted_relevance, convergence_rate, evaluations
        )
        
        # R82: Score empírico com penalidade por baixa convergência
        endorsement_weight = ENDORSEMENT_WEIGHTS.get(calibrated_endorsement, 0.5)
        convergence_bonus = 0.5 + 0.5 * convergence_rate  # [0.5, 1.0]
        empirical_score = (
            weighted_relevance * 0.4 +
            avg_viability * 0.3 +
            endorsement_weight * 0.3
        ) * convergence_bonus
        
        return {
            "thesis_id": thesis.thesis_id,
            "title": thesis.title,
            "n_evaluators": n,
            "avg_relevance": round(avg_relevance, 4),
            "weighted_relevance": round(weighted_relevance, 4),
            "avg_adjusted_viability": round(avg_viability, 4),
            "convergence_rate": round(convergence_rate, 4),
            "majority_endorsement": majority_endorsement,
            "calibrated_endorsement": calibrated_endorsement,
            "endorsement_distribution": dict(endorsement_counts),
            "empirical_score": round(empirical_score, 4),
            "composite_score_original": round(thesis.composite_score, 4),
            "evaluations": evaluations,
        }
    
    def _calibrate_endorsement(
        self, 
        weighted_relevance: float, 
        convergence_rate: float,
        evaluations: List[Dict]
    ) -> str:
        """R82: Determina endosso calibrado com convergência e confiança.
        
        Critérios:
        - Strong:  relevância ≥ 0.40 E convergência ≥ 60% E confiança média ≥ 0.50
        - Moderate: relevância ≥ 0.20 E convergência ≥ 40%
        - Weak:     caso contrário
        """
        avg_confidence = sum(e["confidence"] for e in evaluations) / len(evaluations)
        
        if (weighted_relevance >= STRONG_THRESHOLD_RELEVANCE 
            and convergence_rate >= STRONG_CONVERGENCE_RATE
            and avg_confidence >= STRONG_CONFIDENCE_THRESHOLD):
            return "strong"
        
        if (weighted_relevance >= MODERATE_THRESHOLD_RELEVANCE 
            and convergence_rate >= MODERATE_CONVERGENCE_RATE):
            return "moderate"
        
        return "weak"
    
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
            "avg_weighted_relevance": (
                sum(r["weighted_relevance"] for r in valid_results) / len(valid_results)
                if valid_results else 0
            ),
            "avg_viability": (
                sum(r["avg_adjusted_viability"] for r in valid_results) / len(valid_results)
                if valid_results else 0
            ),
            "avg_convergence_rate": (
                sum(r["convergence_rate"] for r in valid_results) / len(valid_results)
                if valid_results else 0
            ),
        }
        
        # Distribuição de endosso (majoritário e calibrado)
        endorsement_dist = Counter()
        calibrated_dist = Counter()
        for r in valid_results:
            endorsement_dist[r["majority_endorsement"]] += 1
            calibrated_dist[r["calibrated_endorsement"]] += 1
        
        # Top teses por score empírico
        valid_results.sort(key=lambda r: r["empirical_score"], reverse=True)
        
        return {
            "pipeline": "R82 Calibrated Empirical Validation",
            "n_theses": len(theses),
            "n_valid": len(valid_results),
            "n_evaluators_total": sum(r.get("n_evaluators", 0) for r in valid_results),
            "total_time_seconds": round(total_time, 2),
            "aggregate_scores": agg_scores,
            "endorsement_distribution": dict(endorsement_dist),
            "calibrated_endorsement_distribution": dict(calibrated_dist),
            "n_professors_in_pool": len(self.professors),
            "theses_ranked": [
                {
                    "rank": i + 1,
                    "thesis_id": r["thesis_id"],
                    "title": r["title"],
                    "empirical_score": r["empirical_score"],
                    "original_composite": r.get("composite_score_original", 0),
                    "majority_endorsement": r["majority_endorsement"],
                    "calibrated_endorsement": r["calibrated_endorsement"],
                    "convergence_rate": r["convergence_rate"],
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
        """Gera relatório textual da validação empírica (R82)."""
        agg = validation_result.get("aggregate_scores", {})
        end_dist = validation_result.get("endorsement_distribution", {})
        cal_dist = validation_result.get("calibrated_endorsement_distribution", {})
        
        lines = []
        lines.append("=" * 72)
        lines.append("  RELATORIO DE VALIDACAO EMPIRICA CALIBRADA — R82")
        n_profs = validation_result.get('n_professors_in_pool', 0)
        lines.append(f"  {validation_result['n_theses']} teses avaliadas por "
                     f"{validation_result['n_evaluators_total']} avaliacoes "
                     f"(pool de {n_profs} professores)")
        lines.append("=" * 72)
        
        lines.append(f"\nSCORES AGREGADOS:")
        lines.append(f"  Score empírico médio:     {agg.get('avg_empirical_score', 0):.4f}")
        lines.append(f"  Relevância média:         {agg.get('avg_relevance', 0):.4f}")
        lines.append(f"  Relevância ponderada:     {agg.get('avg_weighted_relevance', 0):.4f}")
        lines.append(f"  Viability ajustada:       {agg.get('avg_viability', 0):.4f}")
        lines.append(f"  Taxa de convergência:     {agg.get('avg_convergence_rate', 0):.4f}")
        
        lines.append(f"\nDISTRIBUIÇÃO DE ENDOSSO (majoritário):")
        total = max(sum(end_dist.values()), 1)
        for level in ["strong", "moderate", "weak"]:
            count = end_dist.get(level, 0)
            pct = count / total * 100
            bar = "█" * max(1, int(pct / 5))
            lines.append(f"  {level:10s} {bar} {count}/{total} ({pct:.0f}%)")
        
        lines.append(f"\nDISTRIBUIÇÃO DE ENDOSSO (calibrado R82):")
        total_c = max(sum(cal_dist.values()), 1)
        for level in ["strong", "moderate", "weak"]:
            count = cal_dist.get(level, 0)
            pct = count / total_c * 100
            bar = "█" * max(1, int(pct / 5))
            lines.append(f"  {level:10s} {bar} {count}/{total_c} ({pct:.0f}%)")
        
        lines.append(f"\nTOP TESES VALIDADAS (por score empírico):")
        lines.append(f"  {'Rank':>5s} {'Score':>6s} {'Conv':>6s} {'Endosso':>10s} {'Titulo':60s}")
        lines.append(f"  {'-'*5} {'-'*6} {'-'*6} {'-'*10} {'-'*60}")
        for t in validation_result.get("theses_ranked", [])[:10]:
            conv = t.get('convergence_rate', 0)
            end = t.get('calibrated_endorsement', t.get('majority_endorsement', 'N/A'))
            lines.append(
                f"  {t['rank']:5d} {t['empirical_score']:.4f} "
                f"{conv:.2f} "
                f"{end:>10s} "
                f"{t['title'][:55]}"
            )
        
        lines.append(f"\nTEMPO TOTAL: {validation_result['total_time_seconds']:.1f}s")
        lines.append("=" * 72)
        
        return "\n".join(lines)
