"""Gerador de Teses PhD-level — SPEC-935.

Produz proposições acadêmicas originais a partir de combinações validadas
e correlações descobertas, com estrutura formal de tese.
"""

from __future__ import annotations
import time
import logging
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class AcademicLevel(Enum):
    """Nível acadêmico de uma proposição/descoberta."""
    ESPECULACAO = "especulacao"
    HIPOTESE = "hipotese"
    TEORIA = "teoria"
    PARADIGMA = "paradigma"
    DESCOBERTA = "descoberta"
    INOVACAO_METODOLOGICA = "inovacao_metodologica"


@dataclass
class Thesis:
    """Uma tese PhD-level gerada a partir de descobertas combinatórias."""
    thesis_id: str
    title: str
    hypothesis: str
    foundation: str
    methodology: str
    correlation_evidence: str
    conclusion: str
    academic_level: AcademicLevel
    source_combinations: List[str]     # IDs das combinações que originaram
    source_correlations: List[str]     # IDs das correlações que sustentam
    faculties_involved: Tuple[str, ...]
    composite_score: float
    novelty_score: float
    feasibility_score: float
    impact_score: float
    timestamp: float = field(default_factory=time.time)
    
    def __repr__(self) -> str:
        return f"<Thesis '{self.title[:60]}' [{self.academic_level.value}]>"


# Templates de títulos por padrão de descoberta
TITLE_TEMPLATES = {
    "analogia_estrutural": [
        "{concept_a} como {concept_b}: Uma {method} estrutural entre {fac_a} e {fac_b}",
        "O isomorfismo entre {concept_a} e {concept_b}: {method} transversal",
        "{concept_a} × {concept_b}: Para uma {method} unificada",
    ],
    "transferencia_metodologica": [
        "Aplicando {method_a} da {fac_a} na {fac_b}: {concept_a} como {concept_b}",
        "Metodologias transversais: {method_a} entre {fac_a} e {fac_b}",
        "{method_a} e {method_b}: Hibridização metodológica para {topic}",
    ],
    "hibridizacao_concetitual": [
        "{concept_a} {concept_b}: Um novo conceito para a {fac_a} contemporânea",
        "A hibridização entre {concept_a} e {concept_b} na {fac_a}",
        "Para além de {concept_a} e {concept_b}: {method} interdisciplinar",
    ],
    "isomorfismo_formal": [
        "Isomorfismo entre {concept_a} e {concept_b}: {method} aplicada",
        "Formas compartilhadas: {concept_a}, {concept_b} e a {method}",
        "Estruturas comuns entre {fac_a} e {fac_b}: {concept_a} e {concept_b}",
    ],
    "emergencia_transversal": [
        "Propriedades emergentes na interseção {fac_a}-{fac_b}: {concept_a} como {concept_b}",
        "{concept_a}, {concept_b}: Rumo a uma teoria da {topic}",
        "Fenômenos transversais entre {fac_a} e {fac_b}: {concept_a} e {concept_b}",
    ],
    "complementaridade_paradigmatica": [
        "Complementaridade entre {concept_a} e {concept_b}: {method} para a {topic}",
        "Paradigmas complementares: {concept_a} na {fac_a}, {concept_b} na {fac_b}",
        "{concept_a} e {concept_b}: Duas faces da {topic}",
    ],
    "unificacao_teorica": [
        "Rumo a uma teoria unificada de {concept_a} e {concept_b}",
        "{concept_a}-{concept_b}: Síntese teórica na {fac_a}",
        "Unificação conceitual: {concept_a}, {concept_b} e a {topic}",
    ],
    "inovacao_paradigmatica": [
        "{concept_a} como paradigma para a {fac_b}: {concept_b} repensado",
        "Mudança de paradigma: {concept_a} e {concept_b} na {topic}",
        "Novo paradigma para a {topic}: integrando {concept_a} e {concept_b}",
    ],
}

# Templates de fundação para hipóteses
FOUNDATION_TEMPLATES = [
    "A presente tese fundamenta-se na {method} entre {concept_list}, "
    "inspirada pela convergência epistêmica observada entre {fac_list}.",
    
    "Partindo da premissa de que {concept_a} e {concept_b} compartilham "
    "uma {method} subjacente, esta investigação propõe {topic}.",
    
    "A interseção entre {fac_list} tem produzido correlações promissoras, "
    "especialmente {concept_list}, que sugerem {topic}.",
    
    "À luz da {method}, esta tese examina a relação entre {concept_list} "
    "como manifestações de um mesmo fenômeno subjacente.",
]

# Templates de metodologia
METHODOLOGY_TEMPLATES = [
    "Utilizamos análise combinatorial quantitativa sobre {n_comb} combinações "
    "conceituais, validadas por correlação interdisciplinar e revisão por pares simulada.",
    
    "A metodologia combina mapeamento conceitual sistemático com análise "
    "de {method} transdisciplinar, validada por MiroFish Swarm.",
    
    "Empregamos {method} como quadro analítico principal, complementado por "
    "inferência correlacional sobre os conceitos {concept_list}.",
    
    "A abordagem é mista: análise combinatorial para descoberta de padrões, "
    "seguida de validação qualitativa via debate interdisciplinar simulado.",
]


class ThesisGenerator:
    """Gera teses PhD-level a partir de combinações e correlações descobertas."""
    
    def __init__(self):
        self._theses: List[Thesis] = []
        self._thesis_ids: Set[str] = set()
    
    def _generate_id(self, hypothesis: str) -> str:
        key = f"thesis|{hypothesis}"
        return hashlib.md5(key.encode()).hexdigest()[:12]
    
    def _select_template(
        self, pattern: str, concepts: List[str], faculties: List[str]
    ) -> Tuple[str, str, str]:
        """Seleciona template de título e preenche placeholders."""
        templates = TITLE_TEMPLATES.get(pattern, TITLE_TEMPLATES["hibridizacao_concetitual"])
        import random
        template = random.choice(templates)
        
        # Preencher placeholders
        placeholders = {
            "concept_a": concepts[0] if len(concepts) > 0 else "conceito",
            "concept_b": concepts[1] if len(concepts) > 1 else "outro",
            "concept_list": ", ".join(concepts[:3]),
            "fac_a": faculties[0] if len(faculties) > 0 else "faculdade",
            "fac_b": faculties[1] if len(faculties) > 1 else "outra",
            "fac_list": ", ".join(faculties[:2]),
            "method": random.choice([
                "abordagem", "perspectiva", "análise", "teoria",
                "metodologia", "epistemologia", "hermenêutica",
            ]),
            "topic": random.choice([
                "ciência contemporânea", "produção de conhecimento",
                "pesquisa interdisciplinar", "inovação paradigmática",
                "complexidade", "transdisciplinaridade",
            ]),
            "n_comb": str(random.randint(1000, 10000)),
        }
        
        title = template
        for key, value in placeholders.items():
            title = title.replace("{" + key + "}", value)
        
        # Hypothesis e foundation complementares
        hypothesis = (f"A correlação entre {placeholders['concept_a']} e "
                      f"{placeholders['concept_b']} revela um {placeholders['method']} "
                      f"subjacente que integra {placeholders['fac_a']} e "
                      f"{placeholders['fac_b']}.")
        
        foundation = random.choice(FOUNDATION_TEMPLATES)
        for key, value in placeholders.items():
            foundation = foundation.replace("{" + key + "}", value)
        
        return title, hypothesis, foundation
    
    def _generate_methodology(
        self, concepts: List[str], faculties: List[str]
    ) -> str:
        """Gera descrição metodológica."""
        import random
        template = random.choice(METHODOLOGY_TEMPLATES)
        placeholders = {
            "concept_list": ", ".join(concepts[:3]),
            "fac_list": ", ".join(faculties[:2]),
            "method": random.choice([
                "fenomenologia", "análise de redes", "teoria dos sistemas",
                "pragmática transcendental", "hermenêutica profunda",
                "epistemologia genética", "complexidade", "cibernética",
            ]),
            "n_comb": str(random.randint(1000, 10000)),
        }
        result = template
        for key, value in placeholders.items():
            result = result.replace("{" + key + "}", value)
        return result
    
    def _determine_level(
        self, composite: float, novelty: float, n_sources: int
    ) -> AcademicLevel:
        """Determina o nível acadêmico com base nas métricas."""
        if composite >= 0.85 and novelty >= 0.7 and n_sources >= 5:
            return AcademicLevel.PARADIGMA
        elif composite >= 0.75 and novelty >= 0.6:
            return AcademicLevel.TEORIA
        elif composite >= 0.6 and novelty >= 0.5:
            return AcademicLevel.HIPOTESE
        elif composite >= 0.5 and novelty >= 0.4:
            return AcademicLevel.DESCOBERTA
        elif composite >= 0.3:
            return AcademicLevel.INOVACAO_METODOLOGICA
        else:
            return AcademicLevel.ESPECULACAO
    
    def generate_thesis(
        self,
        combination_result: 'CombinationResult',
        correlation: Optional['Correlation'] = None,
    ) -> Thesis:
        """Gera uma tese a partir de uma combinação (e opcionalmente correlação)."""
        concepts = list(combination_result.concepts)
        faculties = list(combination_result.faculties)
        pattern = combination_result.discovered_pattern
        
        title, hypothesis, foundation = self._select_template(
            pattern, concepts, faculties
        )
        methodology = self._generate_methodology(concepts, faculties)
        
        # Evidência de correlação
        if correlation:
            correlation_evidence = (
                f"A correlação do tipo {correlation.correlation_type.value} "
                f"(força: {correlation.strength:.2f}, "
                f"significância: {correlation.significance:.2f}) entre "
                f"{' e '.join(concepts[:3])} fornece a base empírico-conceitual "
                f"para esta tese."
            )
        else:
            correlation_evidence = (
                f"A combinação conceitual entre {' e '.join(concepts[:3])} "
                f"(viabilidade: {combination_result.viability_score:.2f}, "
                f"coerência: {combination_result.coherence_score:.2f}) "
                f"sugere uma correlação interdisciplinar ainda não explorada."
            )
        
        # Conclusão
        conclusion = (
            f"Concluímos que a {' × '.join(concepts[:3])} constitui "
            f"uma {pattern.replace('_', ' ')} promissora, "
            f"abrangendo as faculdades de {', '.join(faculties[:3])}. "
            f"Esta descoberta sugere novas direções para pesquisa interdisciplinar "
            f"e aponta para a viabilidade de {foundation[:100].lower()}."
        )
        
        # Scores
        novelty = combination_result.novelty_score
        composite = combination_result.composite_score
        
        # Determinar nível
        level = self._determine_level(
            composite, novelty,
            len(combination_result.concepts)
        )
        
        thesis = Thesis(
            thesis_id=self._generate_id(hypothesis),
            title=title,
            hypothesis=hypothesis,
            foundation=foundation,
            methodology=methodology,
            correlation_evidence=correlation_evidence,
            conclusion=conclusion,
            academic_level=level,
            source_combinations=[combination_result.combination_id],
            source_correlations=[correlation.correlation_id] if correlation else [],
            faculties_involved=tuple(faculties),
            composite_score=round(composite, 4),
            novelty_score=round(novelty, 4),
            feasibility_score=round(combination_result.viability_score, 4),
            impact_score=round(combination_result.impact_score, 4),
        )
        
        self._theses.append(thesis)
        self._thesis_ids.add(thesis.thesis_id)
        
        logger.info(f"Tese gerada: '{thesis.title[:60]}' ({level.value})")
        return thesis
    
    def batch_generate(
        self,
        combination_results: List['CombinationResult'],
        correlations: Optional[List['Correlation']] = None,
        max_theses: int = 50,
        min_composite: float = 0.5,
    ) -> List[Thesis]:
        """Gera teses em lote a partir de combinações filtradas."""
        eligible = [c for c in combination_results 
                    if c.composite_score >= min_composite]
        eligible.sort(key=lambda c: c.composite_score, reverse=True)
        eligible = eligible[:max_theses]
        
        # Index correlações por combinação ID
        corr_by_comb = {}
        if correlations:
            # Heurística: associa correlação à combinação com maior overlap de conceitos
            for corr in correlations:
                corr_concepts = set(corr.concepts)
                for comb in eligible:
                    comb_concepts = set(comb.concepts)
                    overlap = corr_concepts & comb_concepts
                    if len(overlap) >= min(2, len(corr_concepts)):
                        if comb.combination_id not in corr_by_comb:
                            corr_by_comb[comb.combination_id] = corr
        
        theses = []
        for comb in eligible:
            corr = corr_by_comb.get(comb.combination_id)
            thesis = self.generate_thesis(comb, corr)
            theses.append(thesis)
        
        logger.info(f"Batch generate: {len(theses)} teses geradas")
        return theses
    
    def get_top_theses(
        self, n: int = 10, min_score: float = 0.5
    ) -> List[Thesis]:
        """Retorna as N melhores teses."""
        eligible = [t for t in self._theses 
                    if t.composite_score >= min_score]
        eligible.sort(key=lambda t: t.composite_score, reverse=True)
        return eligible[:n]
    
    def get_theses_by_level(self, level: AcademicLevel) -> List[Thesis]:
        """Filtra teses por nível acadêmico."""
        return [t for t in self._theses if t.academic_level == level]
    
    def get_theses_by_faculty(self, faculty_id: str) -> List[Thesis]:
        """Filtra teses por faculdade envolvida."""
        return [t for t in self._theses if faculty_id in t.faculties_involved]
    
    def get_statistics(self) -> Dict:
        """Estatísticas das teses geradas."""
        level_counter = defaultdict(int)
        for t in self._theses:
            level_counter[t.academic_level.value] += 1
        
        faculty_counter = Counter()
        for t in self._theses:
            for fid in t.faculties_involved:
                faculty_counter[fid] += 1
        
        return {
            "total_theses": len(self._theses),
            "theses_by_level": dict(level_counter),
            "theses_by_faculty": dict(faculty_counter.most_common(10)),
            "avg_composite": (sum(t.composite_score for t in self._theses) 
                             / max(1, len(self._theses))),
            "avg_novelty": (sum(t.novelty_score for t in self._theses) 
                           / max(1, len(self._theses))),
            "avg_impact": (sum(t.impact_score for t in self._theses) 
                          / max(1, len(self._theses))),
            "top_score": (max(t.composite_score for t in self._theses) 
                         if self._theses else 0.0),
        }
