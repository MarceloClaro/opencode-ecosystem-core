"""
Peer Review System — Multi-LLM Blind Peer Review for academic theses.

Simula revisao cega por pares (double-blind) usando:
  - Multiplos perfis de revisores (professores de diferentes faculdades)
  - LLM real via OpenCode CLI para gerar revisoes estruturadas
  - Agregacao com decisao editorial
  - Cache por hash da tese

SPEC-935-R91 — R91 do OpenCode Ecosystem Core.
"""

import hashlib
import json
import logging
import os
import re
import statistics
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Tuple

from synthetic_university.llm_evaluator import LLMEvaluator
from synthetic_university.agents.professor_base import Professor

logger = logging.getLogger(__name__)


@dataclass
class Review:
    """Review individual de um revisor."""
    reviewer_id: str
    reviewer_name: str
    score: int
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    source: str
    detailed_text: str = ""
    reviewer_faculty: str = ""
    reviewer_h_index: int = 0
    timestamp: str = ""


@dataclass
class ReviewReport:
    """Relatorio agregado de revisao."""
    thesis_id: str
    thesis_title: str
    reviews: List[Review]
    aggregate_score: float
    score_std: float
    decision: str
    summary: str
    generated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "thesis_id": self.thesis_id,
            "thesis_title": self.thesis_title,
            "aggregate_score": round(self.aggregate_score, 2),
            "score_std": round(self.score_std, 2),
            "decision": self.decision,
            "summary": self.summary,
            "generated_at": self.generated_at,
            "reviews": [
                {
                    "reviewer_id": r.reviewer_id,
                    "reviewer_name": r.reviewer_name,
                    "reviewer_faculty": r.reviewer_faculty,
                    "score": r.score,
                    "summary": r.summary,
                    "strengths": r.strengths,
                    "weaknesses": r.weaknesses,
                    "suggestions": r.suggestions,
                    "source": r.source,
                }
                for r in self.reviews
            ],
        }

    def to_text(self, lang: str = "en") -> str:
        """Gera relatorio em texto formatado."""
        is_pt = lang == "pt"
        lines = []
        if is_pt:
            lines.append("=" * 60)
            lines.append("RELATORIO DE REVISAO POR PARES")
            lines.append("=" * 60)
            lines.append(f"Tese: {self.thesis_title}")
            lines.append(f"ID: {self.thesis_id}")
            lines.append(f"Score Agregado: {self.aggregate_score:.1f}/10")
            lines.append(f"Desvio Padrao: {self.score_std:.2f}")
            lines.append(f"Decisao: {self.decision}")
            lines.append(f"Data: {self.generated_at}")
            lines.append("")
            lines.append("-" * 60)
            lines.append("REVISOES INDIVIDUAIS")
            lines.append("-" * 60)
            for i, r in enumerate(self.reviews, 1):
                lines.append(f"\nRevisor {i}: {r.reviewer_name} ({r.reviewer_faculty})")
                lines.append(f"  Score: {r.score}/10")
                lines.append(f"  Sumario: {r.summary}")
                lines.append(f"  Pontos Fortes: {', '.join(r.strengths)}")
                lines.append(f"  Pontos Fracos: {', '.join(r.weaknesses)}")
                lines.append(f"  Sugestoes: {', '.join(r.suggestions)}")
        else:
            lines.append("=" * 60)
            lines.append("PEER REVIEW REPORT")
            lines.append("=" * 60)
            lines.append(f"Thesis: {self.thesis_title}")
            lines.append(f"ID: {self.thesis_id}")
            lines.append(f"Aggregate Score: {self.aggregate_score:.1f}/10")
            lines.append(f"Std Deviation: {self.score_std:.2f}")
            lines.append(f"Decision: {self.decision}")
            lines.append(f"Date: {self.generated_at}")
            lines.append("")
            lines.append("-" * 60)
            lines.append("INDIVIDUAL REVIEWS")
            lines.append("-" * 60)
            for i, r in enumerate(self.reviews, 1):
                lines.append(f"\nReviewer {i}: {r.reviewer_name} ({r.reviewer_faculty})")
                lines.append(f"  Score: {r.score}/10")
                lines.append(f"  Summary: {r.summary}")
                lines.append(f"  Strengths: {', '.join(r.strengths)}")
                lines.append(f"  Weaknesses: {', '.join(r.weaknesses)}")
                lines.append(f"  Suggestions: {', '.join(r.suggestions)}")

        return "\n".join(lines)


class ReviewAggregator:
    """Agrega multiplas revisoes em um relatorio unificado."""

    @staticmethod
    def aggregate(thesis: dict, reviews: List[Review]) -> ReviewReport:
        """Combina revisoes em relatorio com score agregado e decisao."""
        scores = [r.score for r in reviews]
        agg_score = statistics.mean(scores) if scores else 0.0
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0.0
        decision = ReviewAggregator._decide(agg_score, score_std)

        # Sumario consolidado
        all_strengths = []
        all_weaknesses = []
        for r in reviews:
            all_strengths.extend(r.strengths)
            all_weaknesses.extend(r.weaknesses)

        summary_parts = []
        if all_strengths:
            summary_parts.append(f"Strengths: {'; '.join(all_strengths[:3])}")
        if all_weaknesses:
            summary_parts.append(f"Concerns: {'; '.join(all_weaknesses[:3])}")

        return ReviewReport(
            thesis_id=thesis.get("thesis_id", "unknown"),
            thesis_title=thesis.get("title", "Untitled"),
            reviews=reviews,
            aggregate_score=agg_score,
            score_std=score_std,
            decision=decision,
            summary=" | ".join(summary_parts),
            generated_at=datetime.now().isoformat(),
        )

    @staticmethod
    def _decide(avg_score: float, std: float) -> str:
        """Decisao editorial baseada em score medio e consistencia."""
        if avg_score >= 8.0:
            return "Accept"
        elif avg_score >= 6.5:
            return "Minor Revision"
        elif avg_score >= 4.5:
            return "Major Revision"
        else:
            return "Reject"


class PeerReviewSystem:
    """Sistema de revisao cega por pares com multiplos LLMs.

    Args:
        lang: Idioma ('pt' ou 'en').
        model: Modelo OpenCode CLI para geracao de revisoes.
        output_dir: Diretorio para salvar relatorios.
    """

    def __init__(
        self,
        lang: str = "en",
        model: str = "opencode/north-mini-code-free",
        output_dir: str = "academic/peer_reviews",
    ):
        self.lang = lang
        self.evaluator = LLMEvaluator(lang=lang)
        self.model = model
        self.output_dir = output_dir
        self.aggregator = ReviewAggregator()
        self._cache: dict = {}
        os.makedirs(output_dir, exist_ok=True)

    def review(self, thesis: dict, reviewers: list) -> ReviewReport:
        """Executa ciclo completo de revisao para uma tese.

        Args:
            thesis: Dict com dados da tese.
            reviewers: Lista de dicts com perfil de cada revisor.

        Returns:
            ReviewReport com revisoes, score agregado e decisao.
        """
        thesis_hash = self._thesis_hash(thesis)

        # Cache hit?
        if thesis_hash in self._cache:
            logger.debug("R91 Cache hit: %s", thesis.get("thesis_id"))
            return self._cache[thesis_hash]

        # Anonimiza e prepara
        blind_thesis = self._anonymize(thesis)

        # Gera revisoes
        reviews = []
        for reviewer in reviewers:
            review = self._review_by(blind_thesis, reviewer, thesis.get("abstract", ""))
            reviews.append(review)

        # Agrega
        report = self.aggregator.aggregate(thesis, reviews)
        self._cache[thesis_hash] = report

        logger.info(
            "R91 Revisao concluida para '%s': score %.1f, decisao: %s",
            thesis.get("title", "")[:40],
            report.aggregate_score,
            report.decision,
        )

        return report

    def _review_by(self, thesis: dict, reviewer: dict, abstract: str) -> Review:
        """Gera uma revisao individual por um revisor."""
        reviewer_id = reviewer.get("id", "unknown")
        reviewer_name = reviewer.get("name", "Anonymous")
        faculty = reviewer.get("faculty", "general")
        specialties = reviewer.get("specialties", [])
        h_index = reviewer.get("h_index", 20)

        # Cria professor para o LLMEvaluator
        prof = Professor(
            professor_id=reviewer_id,
            nome=reviewer_name,
            title="PhD",
            faculty_id=faculty,
            specialties=specialties,
            research_interests=specialties,
            h_index=h_index,
        )

        # Prompt de revisao estruturada
        prompt = self._review_prompt(prof, thesis)

        # Gera feedback via LLM
        feedback_text, source, elapsed = self.evaluator.generate(prof, thesis, "moderate")

        # Estrutura o feedback em campos
        score = self._parse_score(feedback_text) or 7
        summary, strengths, weaknesses, suggestions = self._parse_review_text(
            feedback_text, score
        )

        # Fallback se nao conseguiu estruturar
        if not strengths:
            strengths = ["Novel approach to the research question"]
        if not weaknesses:
            weaknesses = ["Further empirical validation needed"]
        if not suggestions:
            suggestions = ["Expand the experimental methodology"]

        return Review(
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            reviewer_faculty=faculty,
            reviewer_h_index=h_index,
            score=score,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            source=source,
            detailed_text=feedback_text,
            timestamp=datetime.now().isoformat(),
        )

    def _review_prompt(self, professor: Professor, thesis: dict) -> str:
        """Prompt para revisao estruturada."""
        is_pt = self.lang == "pt"
        if is_pt:
            return (
                f"**REVISAO CEGA POR PARES**\n\n"
                f"Voce e o revisor {professor.nome}, especialista em "
                f"{', '.join(professor.specialties[:2])} "
                f"(indice h={professor.h_index}).\n\n"
                f"Tese (anonimizada):\n"
                f"Titulo: {thesis.get('title', 'Sem titulo')}\n"
                f"Hipotese: {thesis.get('hypothesis', 'N/A')}\n"
                f"Resumo: {thesis.get('abstract', thesis.get('hypothesis', 'N/A'))}\n\n"
                f"Formato obrigatorio:\n"
                f"Score: X/10\n"
                f"Summary: ...\n"
                f"Strengths: ...\n"
                f"Weaknesses: ...\n"
                f"Suggestions: ..."
            )
        else:
            return (
                f"**BLIND PEER REVIEW**\n\n"
                f"You are reviewer {professor.nome}, expert in "
                f"{', '.join(professor.specialties[:2])} "
                f"(h-index={professor.h_index}).\n\n"
                f"Thesis (anonymized):\n"
                f"Title: {thesis.get('title', 'No title')}\n"
                f"Hypothesis: {thesis.get('hypothesis', 'N/A')}\n"
                f"Abstract: {thesis.get('abstract', thesis.get('hypothesis', 'N/A'))}\n\n"
                f"Required format:\n"
                f"Score: X/10\n"
                f"Summary: ...\n"
                f"Strengths: ...\n"
                f"Weaknesses: ...\n"
                f"Suggestions: ..."
            )

    @staticmethod
    def _anonymize(thesis: dict) -> dict:
        """Remove identificadores do autor para revisao cega."""
        anon = dict(thesis)
        # Remove possiveis campos de autoria
        for key in ["author", "authors", "author_id", "institution", "email"]:
            anon.pop(key, None)
        return anon

    @staticmethod
    def _parse_score(text: str) -> Optional[int]:
        """Extrai score numerico de texto de review e arredonda."""
        # Pattern: "Score: 8/10", "Score: 8.5/10", "Score 7", "8/10"
        patterns = [
            r"(?:score|Score|SCORE)\s*:?\s*(\d+(?:\.\d+)?)(?:/10)?",
            r"(\d+(?:\.\d+)?)\s*/10",
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                val = float(match.group(1))
                return max(1, min(10, int(val + 0.5)))
        return None

    @staticmethod
    def _extract_field(text: str, field: str, max_len: int = 200, fallback: str = "") -> str:
        """Extrai campo especifico do texto."""
        patterns = [
            rf"(?:{field}|{field.capitalize()})\s*:?\s*(.+?)(?:\n(?:Score|Strengths|Weaknesses|Suggestions|$)|\Z)",
        ]
        for pat in patterns:
            match = re.search(pat, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                return content[:max_len]
        return fallback or f"Review for {field}."

    @staticmethod
    def _extract_list(text: str, field: str, *keywords: str) -> List[str]:
        """Extrai lista de itens de um campo."""
        # Tenta achar secao especifica
        pat = rf"(?:{field}|{field.capitalize()})\s*:?\s*(.+?)(?:\n\w+\s*:|$)"
        match = re.search(pat, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Split por bullets, numeros ou newlines
            items = re.split(r'[•\-*\d+\.]+', content)
            items = [i.strip().rstrip('.') for i in items if i.strip() and len(i.strip()) > 5]
            return items[:5]

        # Fallback: procura por palavras-chave no texto
        found = []
        for kw in keywords:
            kw_matches = re.findall(
                rf"[^.]*{kw}[^.]*\.", text, re.IGNORECASE
            )
            for m in kw_matches[:3]:
                found.append(m.strip())
        return found[:5]

    @staticmethod
    def _parse_review_text(text: str, score: int) -> Tuple[str, List[str], List[str], List[str]]:
        """Extrai summary, strengths, weaknesses, suggestions de texto livre de review.

        Funciona tanto com formato rotulado quanto com texto livre.
        """
        # Remove a linha do score
        body = re.sub(r'(?:score|Score|SCORE)\s*:?\s*\d+(?:\.\d+)?(?:/10)?\.?\s*', '', text, count=1).strip()

        summary = body[:300] if body else f"Reviewed as {score}/10."

        # Procura por secoes rotuladas
        sections = {
            'strengths': [],
            'weaknesses': [],
            'suggestions': [],
        }

        # Tenta encontrar secoes com rotulos
        for key in sections:
            # Pattern: "Strengths: item1, item2" ou "Weaknesses: ..."
            pat = rf"(?:{key.capitalize()}|{key.capitalize()[:-1]})\s*:?\s*(.+?)(?:\n(?:{'|'.join(k.capitalize() for k in sections)}|$)|\Z)"
            match = re.search(pat, body, re.DOTALL)
            if match:
                content = match.group(1).strip()
                items = re.split(r'[•\-*\d+\.]+', content)
                items = [i.strip().rstrip('.,') for i in items if i.strip() and len(i.strip()) > 8]
                sections[key] = items[:5]

        # Se nao encontrou secoes rotuladas, busca por palavras-chave no texto
        if not sections['strengths']:
            strength_kws = ['insightful', 'innovative', 'novel', 'strong', 'excellent',
                          'compelling', 'rigorous', 'significant', 'promising', 'original']
            sections['strengths'] = PeerReviewSystem._keyword_extract(body, strength_kws)

        if not sections['weaknesses']:
            weakness_kws = ['weak', 'lack', 'insufficient', 'concern', 'limitation',
                          'problem', 'issue', 'unclear', 'vague', 'missing', 'questionable']
            sections['weaknesses'] = PeerReviewSystem._keyword_extract(body, weakness_kws)

        if not sections['suggestions']:
            suggestion_kws = ['suggest', 'recommend', 'should', 'could', 'consider',
                            'improve', 'expand', 'need', 'further', 'additional']
            sections['suggestions'] = PeerReviewSystem._keyword_extract(body, suggestion_kws)

        # Fallback
        strengths = sections['strengths'] or ["Novel approach to the research question"]
        weaknesses = sections['weaknesses'] or ["Further empirical validation needed"]
        suggestions = sections['suggestions'] or ["Expand the experimental methodology"]

        return summary, strengths, weaknesses, suggestions

    @staticmethod
    def _keyword_extract(text: str, keywords: list, max_items: int = 3) -> List[str]:
        """Extrai frases contendo palavras-chave do texto."""
        found = []
        for kw in keywords:
            pattern = rf"[^.]*{kw}[^.]*\."
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                m = m.strip()
                if m and len(m) > 10 and m not in found:
                    found.append(m)
                    if len(found) >= max_items:
                        return found
        return found

    @staticmethod
    def _thesis_hash(thesis: dict) -> str:
        """Hash do conteudo da tese para cache."""
        content = json.dumps(thesis, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()
