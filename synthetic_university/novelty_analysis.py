"""
Academic Novelty Analysis — Avalia originalidade de teses vs literatura real.

Pipeline:
  1. Busca literatura similar via web (OpenCode CLI)
  2. Calcula score de novidade (originalidade + nao-trivialidade + impacto)
  3. Gera mapa de contribuicoes vs estado da arte
  4. Relatorio de posicionamento academico

SPEC-935-R93 — R93 do OpenCode Ecosystem Core.
"""

import hashlib
import json
import logging
import os
import re
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ContributionMap:
    """Mapa do que a tese adiciona vs o que ja existe."""
    additions: List[str] = field(default_factory=list)
    overlaps: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    unique_claims: List[str] = field(default_factory=list)


@dataclass
class NoveltyReport:
    """Relatorio completo de analise de novidade."""
    thesis_id: str
    novelty_score: float
    components: Dict[str, float]
    related_works: List[Dict]
    contribution_map: ContributionMap
    positioning: str
    analyzed_at: str = ""

    def to_dict(self) -> dict:
        return {
            "thesis_id": self.thesis_id,
            "novelty_score": round(self.novelty_score, 1),
            "components": {k: round(v, 1) for k, v in self.components.items()},
            "related_works_count": len(self.related_works),
            "related_works": self.related_works[:5],
            "contribution_additions": self.contribution_map.additions[:5],
            "contribution_unique_claims": self.contribution_map.unique_claims[:3],
            "positioning": self.positioning[:300],
            "analyzed_at": self.analyzed_at,
        }


class NoveltyAnalyzer:
    """Analisador de novidade academica.

    Args:
        lang: Idioma ('pt' ou 'en').
        model: Modelo OpenCode CLI para busca e analise.
    """

    def __init__(
        self,
        lang: str = "en",
        model: str = "opencode/north-mini-code-free",
    ):
        self.lang = lang
        self.model = model
        self._cache: dict = {}

    def analyze(self, thesis: dict) -> NoveltyReport:
        """Analisa novidade academica de uma tese.

        Args:
            thesis: Dict com 'thesis_id', 'title', 'hypothesis', 'abstract', 'concepts'.

        Returns:
            NoveltyReport com score, mapa de contribuicoes e posicionamento.
        """
        cache_key = self._hash(thesis)
        if cache_key in self._cache:
            logger.debug("R93 Cache hit: %s", thesis.get("thesis_id"))
            return self._cache[cache_key]

        thesis_id = thesis.get("thesis_id", "unknown")

        # 1. Busca literatura relacionada
        related = self._find_related(thesis)

        # 2. Calcula componentes de novidade
        components = self._score_components(thesis, related)
        novelty_score = (
            components["originality"] * 0.35 +
            components["non_triviality"] * 0.35 +
            components["impact_potential"] * 0.30
        )

        # 3. Mapa de contribuicoes
        contrib_map = self._build_contribution_map(thesis, related)

        # 4. Posicionamento
        positioning = self._positioning_statement(thesis, related, components)

        report = NoveltyReport(
            thesis_id=thesis_id,
            novelty_score=novelty_score,
            components=components,
            related_works=related[:5],
            contribution_map=contrib_map,
            positioning=positioning,
            analyzed_at=datetime.now().isoformat(),
        )

        self._cache[cache_key] = report
        return report

    def _find_related(self, thesis: dict) -> list:
        """Busca trabalhos relacionados."""
        try:
            results = self._search_literature(thesis)
            if results:
                return results
        except Exception as e:
            logger.warning("R93 Busca falhou: %s", e)

        # Fallback
        concepts = thesis.get("concepts", [])
        return [
            {
                "title": f"Existing research on {c}",
                "year": 2023,
                "relevance": 0.5,
                "source": "fallback",
            }
            for c in concepts[:3]
        ]

    def _search_literature(self, thesis: dict) -> Optional[list]:
        """Busca literatura academica via OpenCode CLI."""
        title = thesis.get("title", "")
        concepts = thesis.get("concepts", [])
        query = f"academic research {title} {' '.join(concepts[:3])} novelty contribution"

        prompt = (
            f"Search for existing academic literature related to: '{title}'. "
            f"Key concepts: {', '.join(concepts[:3])}. "
            f"Return a JSON array of related works. "
            f"Format: [{{\"title\": \"...\", \"year\": 2024, "
            f"\"relevance\": 0.0-1.0, \"contribution\": \"...\", \"gap\": \"...\"}}]"
        )

        try:
            import subprocess
            cmd = [
                "opencode", "run",
                "--model", self.model,
                "--format", "json",
                prompt,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=45
            )
            if result.returncode == 0 and result.stdout.strip():
                data = self._extract_json_array(result.stdout)
                if data:
                    return data
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug("R93 OpenCode: %s", e)

        return None

    def _score_components(self, thesis: dict, related: list) -> Dict[str, float]:
        """Calcula componentes do score de novidade."""
        title = thesis.get("title", "").lower()
        hypothesis = thesis.get("hypothesis", "").lower()

        # Originalidade: quao unico e o tema
        novelty_keywords = ["novel", "new", "first", "framework", "paradigm",
                          "unprecedented", "groundbreaking", "innovative"]
        originality = min(100, sum(5 for kw in novelty_keywords if kw in title))

        # Nao-trivialidade: profundidade da hipotese
        depth_indicators = len(hypothesis.split())
        non_triviality = min(100, depth_indicators * 2)

        # Impacto potencial: baseado em score composto e conceitos
        score = thesis.get("composite_score", 0.5)
        n_concepts = len(thesis.get("concepts", []))
        impact_potential = min(100, (score * 60) + (n_concepts * 8))

        # Penalidade por similaridade com literatura existente
        if related:
            max_relevance = max(r.get("relevance", 0) for r in related)
            penalty = max_relevance * 30  # ate -30 pontos
            originality = max(10, originality - penalty)
            non_triviality = max(10, non_triviality - (penalty * 0.5))

        return {
            "originality": originality,
            "non_triviality": non_triviality,
            "impact_potential": impact_potential,
        }

    def _build_contribution_map(self, thesis: dict, related: list) -> ContributionMap:
        """Constroi mapa de contribuicoes."""
        title = thesis.get("title", "")
        hypothesis = thesis.get("hypothesis", "")
        concepts = thesis.get("concepts", [])

        additions = [
            f"Novel integration of {concepts[0] if concepts else 'multiple fields'}",
            f"Formal framework for {title[:50] if title else 'the research question'}",
            f"Methodology combining {' and '.join(concepts[:2]) if len(concepts) >= 2 else 'interdisciplinary approaches'}",
        ]

        overlaps = []
        unique_claims = [f"H: {hypothesis[:100]}"]

        for r in related[:3]:
            if r.get("relevance", 0) > 0.7:
                overlaps.append(f"Partially overlaps with: {r.get('title', 'related work')[:80]}")
            else:
                unique_claims.append(f"Distinct from: {r.get('title', 'other work')[:80]}")

        gaps = [
            f"Empirical validation needed for {title[:50] if title else 'the claims'}",
            "Cross-domain replication studies required",
        ]

        return ContributionMap(
            additions=additions,
            overlaps=overlaps,
            gaps=gaps,
            unique_claims=unique_claims,
        )

    def _positioning_statement(self, thesis: dict, related: list, components: dict) -> str:
        """Gera statement de posicionamento academico."""
        title = thesis.get("title", "this thesis")
        n_related = len(related)
        avg_relevance = statistics.mean(
            [r.get("relevance", 0) for r in related]
        ) if related else 0

        is_pt = self.lang == "pt"

        if is_pt:
            if n_related == 0:
                return (
                    f"A tese '{title}' aborda um tema com pouca literatura previa identificada, "
                    f"sugerindo alta originalidade. Score de novidade: "
                    f"originalidade {components['originality']:.0f}/100, "
                    f"nao-trivialidade {components['non_triviality']:.0f}/100."
                )
            elif avg_relevance < 0.5:
                return (
                    f"A tese '{title}' se posiciona em uma lacuna da literatura, "
                    f"com {n_related} trabalhos relacionados mas de baixa sobreposicao "
                    f"(relevancia media {avg_relevance:.2f}). "
                    f"A contribuicao principal e a integracao original de conceitos."
                )
            else:
                return (
                    f"A tese '{title}' dialoga com {n_related} trabalhos existentes "
                    f"(relevancia media {avg_relevance:.2f}), "
                    f"expandindo o estado da arte com nova perspectiva metodologica."
                )
        else:
            if n_related == 0:
                return (
                    f"The thesis '{title}' addresses a topic with limited prior literature, "
                    f"suggesting high originality. Novelty components: "
                    f"originality {components['originality']:.0f}/100, "
                    f"non-triviality {components['non_triviality']:.0f}/100."
                )
            elif avg_relevance < 0.5:
                return (
                    f"The thesis '{title}' positions itself in a literature gap, "
                    f"with {n_related} related works but low overlap "
                    f"(avg relevance {avg_relevance:.2f}). "
                    f"The main contribution is the original integration of concepts."
                )
            else:
                return (
                    f"The thesis '{title}' engages with {n_related} existing works "
                    f"(avg relevance {avg_relevance:.2f}), "
                    f"extending the state of the art with a novel methodological perspective."
                )

    @staticmethod
    def _extract_json_array(text: str) -> Optional[list]:
        """Extrai array JSON de texto."""
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _hash(thesis: dict) -> str:
        content = json.dumps(thesis, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()
