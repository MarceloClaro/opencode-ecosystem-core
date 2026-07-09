# -*- coding: utf-8 -*-
"""
Academic Novelty V2 — OpenNovelty-style Pipeline (R98)
========================================================
Pipeline granular de analise de novidade academica com:

  1. ContributionPointExtractor — extrai claims especificas da tese
  2. PointwiseLiteratureRetriever — busca literatura por ponto
  3. PointwiseNoveltyScorer — score por ponto com evidencia
  4. HierarchicalTaxonomyBuilder — arvore hierarquica de literatura
  5. EvidencedNoveltyReport — relatorio enriquecido

Uso:
    from synthetic_university.novelty_v2 import NoveltyAnalyzerV2

    analyzer = NoveltyAnalyzerV2(lang="en")
    report = analyzer.analyze(thesis_dict)
    print(report.to_dict())

SPEC-935-R98.
"""

from __future__ import annotations

import json
import logging
import os
import statistics
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Dataclasses
# ============================================================

@dataclass
class ContributionPoint:
    """Um ponto especifico de contribuicao extraido da tese."""
    point_id: str
    type: str  # hypothesis_claim, methodological_claim, framework_claim, application_claim
    claim: str
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.5


@dataclass
class PointWithLiterature:
    """ContributionPoint com literatura relacionada."""
    point: ContributionPoint
    related_works: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PointNovelty:
    """Score de novidade para um ponto especifico."""
    point_id: str
    point_type: str
    novelty_score: float
    evidence: str
    overlapping_works: List[str] = field(default_factory=list)
    gap_identified: str = ""


@dataclass
class TaxonomyNode:
    """No da arvore de taxonomia."""
    name: str
    relevance: float = 0.5
    works: List[Dict[str, Any]] = field(default_factory=list)
    children: List["TaxonomyNode"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "relevance": round(self.relevance, 2),
            "works_count": len(self.works),
            "works": self.works[:3],
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class TaxonomyTree:
    """Arvore hierarquica de trabalhos relacionados."""
    root: str
    children: List[TaxonomyNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class EvidencedNoveltyReport:
    """Relatorio enriquecido de novidade academica."""
    thesis_id: str
    thesis_title: str
    global_novelty_score: float
    per_point_scores: Dict[str, PointNovelty]
    taxonomy_tree: TaxonomyTree
    top_related_works: List[Dict[str, Any]]
    discrepancy_analysis: str
    positioning_statement: str
    methodology_novelty: float = 0.0
    framework_novelty: float = 0.0
    application_novelty: float = 0.0
    analyzed_at: str = ""

    def to_dict(self) -> dict:
        return {
            "thesis_id": self.thesis_id,
            "thesis_title": self.thesis_title,
            "global_novelty_score": round(self.global_novelty_score, 1),
            "per_point_scores": {
                pid: {
                    "point_id": ns.point_id,
                    "point_type": ns.point_type,
                    "novelty_score": round(ns.novelty_score, 1),
                    "evidence": ns.evidence[:200],
                    "overlapping_works": ns.overlapping_works[:5],
                    "gap_identified": ns.gap_identified[:200],
                }
                for pid, ns in self.per_point_scores.items()
                if pid != "_global"
            },
            "top_related_works": [
                {k: v for k, v in w.items() if k != "contribution"}
                for w in self.top_related_works[:5]
            ],
            "taxonomy_tree": self.taxonomy_tree.to_dict(),
            "discrepancy_analysis": self.discrepancy_analysis[:500],
            "positioning_statement": self.positioning_statement[:500],
            "sub_scores": {
                "methodology_novelty": round(self.methodology_novelty, 1),
                "framework_novelty": round(self.framework_novelty, 1),
                "application_novelty": round(self.application_novelty, 1),
            },
            "analyzed_at": self.analyzed_at,
        }


# ============================================================
# C1 — ContributionPointExtractor
# ============================================================

class ContributionPointExtractor:
    """Extrai pontos de contribuicao de uma tese."""

    def extract(self, thesis: dict) -> List[ContributionPoint]:
        """Extrai pontos de contribuicao do texto da tese.

        Args:
            thesis: Dict com thesis_id, title, hypothesis, abstract,
                    methodology, concepts.

        Returns:
            Lista de ContributionPoint.
        """
        points = []
        has_hypothesis = bool(thesis.get("hypothesis"))
        has_methodology = bool(thesis.get("methodology"))
        has_abstract = bool(thesis.get("abstract"))

        # Se tese tem hipotese + metodologia, extrai pontos específicos
        if has_hypothesis or has_abstract:
            points.append(self._extract_hypothesis_claim(thesis))

        if has_methodology:
            points.append(self._extract_methodological_claim(thesis))

        if has_abstract:
            points.append(self._extract_framework_claim(thesis))
            points.append(self._extract_application_claim(thesis))

        # Fallback: 1 ponto por conceito
        if not points:
            concepts = thesis.get("concepts", ["unknown"])
            for i, c in enumerate(concepts[:3]):
                points.append(ContributionPoint(
                    point_id=f"cp_fallback_{i}",
                    type="hypothesis_claim",
                    claim=f"Investigation of {c} as a novel contribution",
                    keywords=[c],
                    confidence=0.3,
                ))

        return points

    def _extract_hypothesis_claim(self, thesis: dict) -> ContributionPoint:
        """Extrai claim da hipotese central."""
        hypothesis = thesis.get("hypothesis", "") or thesis.get("abstract", "")
        title = thesis.get("title", "")
        concepts = thesis.get("concepts", [])

        claim_text = hypothesis[:200] if len(hypothesis) > 20 else title

        return ContributionPoint(
            point_id=f"cp_hypothesis_{uuid.uuid4().hex[:6]}",
            type="hypothesis_claim",
            claim=claim_text,
            keywords=concepts[:4] if concepts else [title[:30]],
            confidence=0.8 if thesis.get("hypothesis") else 0.4,
        )

    def _extract_methodological_claim(self, thesis: dict) -> ContributionPoint:
        """Extrai claim metodologica."""
        methodology = thesis.get("methodology", "")
        concepts = thesis.get("concepts", [])

        claim_text = (
            methodology[:200] if len(methodology) > 20
            else f"Novel methodology combining {'/'.join(concepts[:3])}"
        )

        return ContributionPoint(
            point_id=f"cp_method_{uuid.uuid4().hex[:6]}",
            type="methodological_claim",
            claim=claim_text,
            keywords=(concepts[:3] if concepts else ["methodology"]),
            confidence=0.7,
        )

    def _extract_framework_claim(self, thesis: dict) -> ContributionPoint:
        """Extrai claim de framework/paradigma."""
        abstract = thesis.get("abstract", "")
        title = thesis.get("title", "")
        concepts = thesis.get("concepts", [])

        # Busca por termos de framework no abstract
        framework_keywords = ["framework", "paradigm", "theory", "model", "approach"]
        sentences = abstract.split(".")
        framework_sentences = [
            s.strip() for s in sentences
            if any(kw in s.lower() for kw in framework_keywords)
        ]

        if framework_sentences:
            claim_text = framework_sentences[0][:200]
        else:
            claim_text = f"Novel {concepts[0] if concepts else 'theoretical'} framework for {title[:60] if title else 'the research question'}"

        return ContributionPoint(
            point_id=f"cp_framework_{uuid.uuid4().hex[:6]}",
            type="framework_claim",
            claim=claim_text,
            keywords=concepts[:3] if concepts else ["framework"],
            confidence=0.6 if framework_sentences else 0.4,
        )

    def _extract_application_claim(self, thesis: dict) -> ContributionPoint:
        """Extrai claim de aplicacao/impacto."""
        abstract = thesis.get("abstract", "")
        title = thesis.get("title", "")
        concepts = thesis.get("concepts", [])

        app_keywords = ["application", "impact", "implication", "practical",
                       "implementation", "deployment", "validate", "simulation"]
        sentences = abstract.split(".")
        app_sentences = [
            s.strip() for s in sentences
            if any(kw in s.lower() for kw in app_keywords)
        ]

        if app_sentences:
            claim_text = app_sentences[0][:200]
        else:
            claim_text = f"Potential applications of {title[:60] if title else 'this research'} in real-world scenarios"

        return ContributionPoint(
            point_id=f"cp_application_{uuid.uuid4().hex[:6]}",
            type="application_claim",
            claim=claim_text,
            keywords=concepts[:3] if concepts else ["application"],
            confidence=0.5 if app_sentences else 0.3,
        )


# ============================================================
# C2 — PointwiseLiteratureRetriever
# ============================================================

class PointwiseLiteratureRetriever:
    """Busca literatura relacionada para cada contribution point."""

    # Banco de fallback de trabalhos simulados por area tematica
    FALLBACK_WORKS_BY_AREA = {
        "quantum": [
            {"title": "Quantum Computing Ethics: A Preliminary Analysis",
             "year": 2024, "relevance": 0.75,
             "contribution": "First systematic survey of ethical issues in quantum computing",
             "gap": "Lacks formal framework for moral decision-making in quantum systems",
             "source": "fallback"},
            {"title": "Ethical AI: From Classical to Quantum Paradigms",
             "year": 2023, "relevance": 0.60,
             "contribution": "Compares classical AI ethics with emerging quantum ethics",
             "gap": "Does not formalize quantum-specific moral states",
             "source": "fallback"},
        ],
        "ethics": [
            {"title": "Moral Responsibility in Autonomous Systems",
             "year": 2023, "relevance": 0.70,
             "contribution": "Framework for moral accountability in AI decision-making",
             "gap": "Does not address quantum superposition of moral states",
             "source": "fallback"},
        ],
        "AI": [
            {"title": "Explainable AI: A Review of Moral Dimensions",
             "year": 2024, "relevance": 0.55,
             "contribution": "Survey of ethical frameworks for explainable AI",
             "gap": "Limited to classical computing paradigms",
             "source": "fallback"},
        ],
        "default": [
            {"title": "_TEMPLATE_Advances_in_{topic}:_A_Systematic_Review",
             "year": 2024, "relevance": 0.50,
             "contribution": "_TEMPLATE_Comprehensive_survey_of_{topic}_research",
             "gap": "Identifies need for novel theoretical frameworks",
             "source": "fallback"},
            {"title": "_TEMPLATE_Methodological_Innovations_in_{topic}_Studies",
             "year": 2023, "relevance": 0.45,
             "contribution": "_TEMPLATE_Novel_methodological_approaches_for_{topic}",
             "gap": "Empirical validation across domains needed",
             "source": "fallback"},
        ],
    }

    def retrieve(
        self,
        points: List[ContributionPoint],
        thesis: dict,
    ) -> List[PointWithLiterature]:
        """Busca literatura para cada contribution point.

        Args:
            points: Lista de ContributionPoint.
            thesis: Dict da tese (usado para contexto adicional).

        Returns:
            Lista de PointWithLiterature.
        """
        results = []
        for point in points:
            works = self._search_for_point(point, top_k=3)
            results.append(PointWithLiterature(
                point=point,
                related_works=works,
            ))
        return results

    def _search_for_point(
        self, point: ContributionPoint, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Busca literatura especifica para um contribution point."""
        return self._fallback_literature(point, top_k)

    @staticmethod
    def _expand_template(work: dict, topic: str) -> dict:
        """Expande templates _TEMPLATE_ em um dict de work."""
        expanded = {}
        for k, v in work.items():
            if isinstance(v, str) and v.startswith("_TEMPLATE_"):
                # Remove prefix, restaura espacos, formata com topic
                template = v.replace("_TEMPLATE_", "").replace("_", " ")
                expanded[k] = template.format(topic=topic)
            else:
                expanded[k] = v
        return expanded

    def _fallback_literature(
        self, point: ContributionPoint, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Gera literatura fallback baseada nas keywords do ponto."""
        works = []
        seen_titles = set()
        keywords = [kw.lower() for kw in point.keywords]

        for kw in keywords:
            if len(works) >= top_k:
                break
            pool = list(self.FALLBACK_WORKS_BY_AREA.get(kw, []))
            if point.type == "methodological_claim":
                pool += [
                    {"title": f"Methodological Framework for {kw.title()} Research",
                     "year": 2024, "relevance": 0.65,
                     "contribution": f"Systematic methodology for {kw} studies",
                     "gap": "Needs integration with interdisciplinary approaches",
                     "source": "fallback"},
                ]
            for w in pool:
                title = w.get("title", "")
                if title not in seen_titles and len(works) < top_k:
                    works.append(w)
                    seen_titles.add(title)

        # Se ainda nao temos trabalhos suficientes, usa default com template
        if len(works) < top_k:
            topic = point.keywords[0] if point.keywords else "this field"
            for w in self.FALLBACK_WORKS_BY_AREA["default"]:
                expanded = self._expand_template(w, topic)
                title = expanded.get("title", "")
                if title not in seen_titles and len(works) < top_k:
                    works.append(expanded)
                    seen_titles.add(title)

        return works[:top_k]


# ============================================================
# C3 — PointwiseNoveltyScorer
# ============================================================

class PointwiseNoveltyScorer:
    """Calcula novidade ponto-a-ponto com evidencia."""

    WEIGHTS = {
        "hypothesis_claim": 0.25,
        "methodological_claim": 0.30,
        "framework_claim": 0.25,
        "application_claim": 0.20,
    }

    def score(
        self, points_with_lit: List[PointWithLiterature]
    ) -> Dict[str, PointNovelty]:
        """Calcula scores por ponto e score global.

        Args:
            points_with_lit: Lista de PointWithLiterature.

        Returns:
            Dict com point_id -> PointNovelty, e '_global' -> float.
        """
        point_scores: Dict[str, PointNovelty] = {}

        for pwl in points_with_lit:
            pnl = self._score_single_point(pwl.point, pwl.related_works)
            point_scores[pwl.point.point_id] = pnl

        # Score global ponderado
        global_score = self._compute_global_score(point_scores, points_with_lit)
        global_pn = PointNovelty(
            point_id="_global",
            point_type="global",
            novelty_score=global_score,
            evidence=f"Global novelty score computed from {len(point_scores)} contribution points",
        )
        point_scores["_global"] = global_pn

        return point_scores

    def _score_single_point(
        self, point: ContributionPoint, related: List[Dict[str, Any]]
    ) -> PointNovelty:
        """Calcula score de novidade para um ponto especifico."""
        if not related:
            return PointNovelty(
                point_id=point.point_id,
                point_type=point.type,
                novelty_score=85.0,
                evidence=f"No related works found for '{point.claim[:60]}' — likely novel",
                gap_identified="No prior work identified in this specific direction",
            )

        # Novidade baseada na relevancia media dos trabalhos relacionados
        max_relevance = max(w.get("relevance", 0) for w in related)
        # Quanto maior a relevancia, menor a novidade
        base_novelty = 100.0 - (max_relevance * 70.0)

        # Bonus para confidence alta (extracao mais precisa)
        confidence_bonus = point.confidence * 5.0

        # Penalidade se ha muitas overlaps
        overlap_penalty = 0
        overlapping = []

        for w in related:
            if w.get("relevance", 0) > 0.6:
                overlap_penalty += 5
                overlapping.append(w.get("title", "Unknown"))

        novelty = max(10.0, min(100.0, base_novelty + confidence_bonus - overlap_penalty))

        # Evidencia textual
        if overlapping:
            evidence = (
                f"Point '{point.claim[:80]}...' partially overlaps with "
                f"{len(overlapping)} work(s). Max relevance: {max_relevance:.2f}. "
                f"Novelty score adjusted for existing literature."
            )
        else:
            evidence = (
                f"Point '{point.claim[:80]}...' shows limited overlap with "
                f"existing literature (max relevance: {max_relevance:.2f}). "
                f"Indicates potential novelty."
            )

        # Lacuna identificada
        gaps = [w.get("gap", "") for w in related if w.get("gap")]
        gap_text = gaps[0] if gaps else "No specific gap identified in related works"

        return PointNovelty(
            point_id=point.point_id,
            point_type=point.type,
            novelty_score=round(novelty, 1),
            evidence=evidence,
            overlapping_works=overlapping[:5],
            gap_identified=gap_text,
        )

    def _compute_global_score(
        self,
        point_scores: Dict[str, PointNovelty],
        points_with_lit: List[PointWithLiterature],
    ) -> float:
        """Computa score global ponderado."""
        if not points_with_lit:
            return 50.0

        total_weight = 0.0
        weighted_sum = 0.0

        for pwl in points_with_lit:
            point_type = pwl.point.type
            weight = self.WEIGHTS.get(point_type, 0.20)
            pnl = point_scores.get(pwl.point.point_id)
            if pnl:
                weighted_sum += pnl.novelty_score * weight
                total_weight += weight

        if total_weight == 0:
            return 50.0

        return round(weighted_sum / total_weight, 1)


# ============================================================
# C4 — HierarchicalTaxonomyBuilder
# ============================================================

class HierarchicalTaxonomyBuilder:
    """Constroi taxonomia hierarquica de trabalhos relacionados."""

    AREA_NAMES = {
        "hypothesis_claim": "Central Hypothesis & Research Questions",
        "methodological_claim": "Methodological Approaches",
        "framework_claim": "Theoretical Frameworks & Paradigms",
        "application_claim": "Applications & Impact Studies",
    }

    def build(
        self, points_with_lit: List[PointWithLiterature]
    ) -> TaxonomyTree:
        """Constroi arvore de taxonomia a partir dos pontos.

        Args:
            points_with_lit: Lista de PointWithLiterature.

        Returns:
            TaxonomyTree.
        """
        if not points_with_lit:
            return TaxonomyTree(root="No related literature")

        # Agrupa works por tipo de ponto
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for pwl in points_with_lit:
            area = self.AREA_NAMES.get(pwl.point.type, "Other")
            if area not in groups:
                groups[area] = []
            groups[area].extend(pwl.related_works)

        # Remove duplicatas mantendo ordem
        for area in groups:
            seen = set()
            unique = []
            for w in groups[area]:
                title = w.get("title", "")
                if title not in seen:
                    seen.add(title)
                    unique.append(w)
            groups[area] = unique

        # Constroi nos
        children = []
        for area_name, works in groups.items():
            if not works:
                continue
            avg_relevance = statistics.mean(
                [w.get("relevance", 0) for w in works]
            ) if works else 0
            children.append(TaxonomyNode(
                name=area_name,
                relevance=round(avg_relevance, 2),
                works=works,
                children=[],
            ))

        # Ordena por relevance
        children.sort(key=lambda n: n.relevance, reverse=True)

        return TaxonomyTree(
            root="Related Literature Taxonomy",
            children=children,
        )


# ============================================================
# C5 — NoveltyAnalyzerV2 (orquestrador principal)
# ============================================================

class NoveltyAnalyzerV2:
    """Analisador de novidade academica V2 — pipeline OpenNovelty-style.

    Args:
        lang: Idioma ('en' ou 'pt').
        memory: EvolutionaryMemorySubstrate opcional (R97).
    """

    def __init__(
        self,
        lang: str = "en",
        memory: Optional[Any] = None,  # EvolutionaryMemorySubstrate
    ):
        self.lang = lang
        self.memory = memory
        self.extractor = ContributionPointExtractor()
        self.retriever = PointwiseLiteratureRetriever()
        self.scorer = PointwiseNoveltyScorer()
        self.taxonomy = HierarchicalTaxonomyBuilder()

    def analyze(self, thesis: dict) -> EvidencedNoveltyReport:
        """Analisa novidade academica de uma tese (pipeline completo).

        Args:
            thesis: Dict com thesis_id, title, hypothesis, abstract,
                    methodology, concepts, composite_score.

        Returns:
            EvidencedNoveltyReport completo.
        """
        thesis_id = thesis.get("thesis_id", "unknown")
        thesis_title = thesis.get("title", "")

        # 1. Extrair contribution points
        points = self.extractor.extract(thesis)
        logger.debug("R98: Extracted %d contribution points", len(points))

        # 2. Buscar literatura por ponto
        points_with_lit = self.retriever.retrieve(points, thesis)
        logger.debug("R98: Retrieved literature for %d points", len(points_with_lit))

        # 3. Calcular scores por ponto
        scores = self.scorer.score(points_with_lit)
        global_score = scores["_global"].novelty_score if "_global" in scores else 50.0
        logger.debug("R98: Global novelty score: %.1f", global_score)

        # 4. Construir taxonomia
        tree = self.taxonomy.build(points_with_lit)

        # 5. Coletar top related works
        all_works = []
        seen_titles = set()
        for pwl in points_with_lit:
            for w in pwl.related_works:
                title = w.get("title", "")
                if title not in seen_titles:
                    all_works.append(w)
                    seen_titles.add(title)
        all_works.sort(key=lambda w: w.get("relevance", 0), reverse=True)
        top_related = all_works[:5]

        # 6. Gerar analise de discrepancia
        discrepancy = self._generate_discrepancy(scores, points_with_lit)

        # 7. Gerar positioning statement
        positioning = self._generate_positioning(
            thesis_title, scores, top_related, points
        )

        # 8. Extrair sub-scores
        method_novelty = self._get_sub_score(scores, "methodological_claim")
        framework_novelty = self._get_sub_score(scores, "framework_claim")
        application_novelty = self._get_sub_score(scores, "application_claim")

        report = EvidencedNoveltyReport(
            thesis_id=thesis_id,
            thesis_title=thesis_title,
            global_novelty_score=global_score,
            per_point_scores=scores,
            taxonomy_tree=tree,
            top_related_works=top_related,
            discrepancy_analysis=discrepancy,
            positioning_statement=positioning,
            methodology_novelty=method_novelty,
            framework_novelty=framework_novelty,
            application_novelty=application_novelty,
            analyzed_at=datetime.now().isoformat(),
        )

        # 9. Registrar na memoria R97 se disponivel
        self._record_in_memory(thesis_id, thesis_title, global_score, points)

        return report

    # --------------------------------------------------------
    # Metodos auxiliares
    # --------------------------------------------------------

    def _generate_discrepancy(
        self,
        scores: Dict[str, PointNovelty],
        points_with_lit: List[PointWithLiterature],
    ) -> str:
        """Gera analise de discrepancias entre claims e literatura."""
        parts = []
        is_pt = self.lang == "pt"

        # Verifica pontos com baixa novidade (alta sobreposicao)
        low_novelty = [
            (pid, ns) for pid, ns in scores.items()
            if pid != "_global" and ns.novelty_score < 50
        ]

        if low_novelty:
            for pid, ns in low_novelty:
                if is_pt:
                    parts.append(
                        f"O ponto '{ns.point_type}' apresenta baixa novidade "
                        f"({ns.novelty_score:.0f}/100). "
                        f"Sobreposicao com {len(ns.overlapping_works)} trabalho(s) existente(s). "
                        f"Lacuna identificada: {ns.gap_identified[:100]}."
                    )
                else:
                    parts.append(
                        f"Point '{ns.point_type}' shows low novelty "
                        f"({ns.novelty_score:.0f}/100). "
                        f"Overlaps with {len(ns.overlapping_works)} existing work(s). "
                        f"Gap identified: {ns.gap_identified[:100]}."
                    )
        else:
            if is_pt:
                parts.append(
                    "Nenhuma discrepancia significativa identificada entre "
                    "as claims da tese e a literatura existente. "
                    "Todos os pontos apresentam potencial de novidade."
                )
            else:
                parts.append(
                    "No significant discrepancies identified between "
                    "the thesis claims and existing literature. "
                    "All points show novelty potential."
                )

        # Verifica pontos com alta novidade (pouca literatura)
        high_novelty = [
            (pid, ns) for pid, ns in scores.items()
            if pid != "_global" and ns.novelty_score >= 80
        ]
        if high_novelty:
            for pid, ns in high_novelty[:2]:
                if is_pt:
                    parts.append(
                        f"O ponto '{ns.point_type}' tem alta novidade "
                        f"({ns.novelty_score:.0f}/100) — "
                        f"pouca literatura previa identificada."
                    )
                else:
                    parts.append(
                        f"Point '{ns.point_type}' has high novelty "
                        f"({ns.novelty_score:.0f}/100) — "
                        f"limited prior literature identified."
                    )

        return "\n".join(parts)

    def _generate_positioning(
        self,
        title: str,
        scores: Dict[str, PointNovelty],
        top_related: List[Dict[str, Any]],
        points: List[ContributionPoint],
    ) -> str:
        """Gera statement de posicionamento academico."""
        is_pt = self.lang == "pt"
        global_score = scores["_global"].novelty_score if "_global" in scores else 50

        if is_pt:
            if global_score >= 70:
                return (
                    f"A tese '{title}' posiciona-se em territorio de alta novidade "
                    f"(score global {global_score:.0f}/100), com contribuicoes "
                    f"originais em {len(points)} dimensoes. "
                    f"Dialoga com {len(top_related)} trabalho(s) relacionado(s) "
                    f"mas avanca significativamente o estado da arte."
                )
            elif global_score >= 40:
                return (
                    f"A tese '{title}' oferece contribuicoes moderadamente originais "
                    f"(score global {global_score:.0f}/100) em {len(points)} areas. "
                    f"Expande o estado da arte com nova perspectiva sobre "
                    f"{len(top_related)} trabalho(s) existente(s)."
                )
            else:
                return (
                    f"A tese '{title}' situa-se em territorio com literatura "
                    f"estabelecida (score global {global_score:.0f}/100). "
                    f"Sua contribuicao principal e a aplicacao de "
                    f"metodologias existentes em novo contexto."
                )
        else:
            if global_score >= 70:
                return (
                    f"The thesis '{title}' positions itself in high-novelty territory "
                    f"(global score {global_score:.0f}/100), with original contributions "
                    f"across {len(points)} dimensions. "
                    f"It engages with {len(top_related)} related work(s) "
                    f"but significantly advances the state of the art."
                )
            elif global_score >= 40:
                return (
                    f"The thesis '{title}' offers moderately original contributions "
                    f"(global score {global_score:.0f}/100) across {len(points)} areas. "
                    f"It extends the state of the art with a fresh perspective on "
                    f"{len(top_related)} existing work(s)."
                )
            else:
                return (
                    f"The thesis '{title}' is situated in well-established territory "
                    f"(global score {global_score:.0f}/100). "
                    f"Its main contribution is the application of "
                    f"existing methodologies in a new context."
                )

    @staticmethod
    def _get_sub_score(
        scores: Dict[str, PointNovelty],
        point_type: str,
    ) -> float:
        """Extrai sub-score para um tipo especifico de ponto."""
        for pid, ns in scores.items():
            if ns.point_type == point_type:
                return ns.novelty_score
        return 0.0

    def _record_in_memory(
        self,
        thesis_id: str,
        thesis_title: str,
        global_score: float,
        points: List[ContributionPoint],
    ) -> None:
        """Registra resultados na memoria R97, se disponivel."""
        if self.memory is None:
            return

        try:
            # Registra score de novidade no stagnation detector
            if hasattr(self.memory, 'stagnation'):
                cycle = hash(thesis_id) % 100  # cycle aproximado
                self.memory.stagnation.record_novelty_score(cycle, global_score)

            # Registra contribution points no ideation memory
            if hasattr(self.memory, 'ideation'):
                outcome = "success" if global_score >= 60 else "failure"
                self.memory.ideation.record_idea(
                    direction=thesis_title,
                    outcome=outcome,
                    score=global_score,
                    metadata={
                        "thesis_id": thesis_id,
                        "n_points": len(points),
                        "source": "novelty_v2",
                    },
                )

            # Registra estrategia de analise
            if hasattr(self.memory, 'experimentation'):
                self.memory.experimentation.record_strategy(
                    strategy_id=f"novelty_v2_analysis_{thesis_id[:8]}",
                    context=["novelty", "analysis", "opennovelty"],
                    effectiveness=global_score,
                    metadata={"n_points": len(points)},
                )
        except Exception as e:
            logger.warning("R98: Failed to record in memory (non-fatal): %s", e)
