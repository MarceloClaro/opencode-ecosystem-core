"""Correlator Interdisciplinar — SPEC-935.

Detecta correlações entre conceitos de diferentes faculdades,
calculando força, significância e tipo da correlação.
"""

from __future__ import annotations
import math
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Tipo de correlação interdisciplinar descoberta."""
    CAUSAL = "causal"
    CORRELACIONAL = "correlacional"
    ANALOGICA = "analogica"
    ANTAGONICA = "antagonica"
    EMERGENTE = "emergente"
    COMPLEMENTAR = "complementar"
    HIERARQUICA = "hierarquica"
    ISOMORFICA = "isomorfica"
    DIALETICA = "dialetica"
    TRADUTIVA = "tradutiva"
    METODOLOGICA = "metodologica"
    PARADIGMATICA = "paradigmatica"


@dataclass
class Correlation:
    """Uma correlação descoberta entre conceitos."""
    correlation_id: str
    concepts: Tuple[str, ...]
    faculties: Tuple[str, ...]
    correlation_type: CorrelationType
    strength: float                    # 0..1
    significance: float                # 0..1
    empirical_support: float           # 0..1
    composite_correlation: float       # média ponderada
    description: str
    timestamp: float = field(default_factory=time.time)
    
    def __repr__(self) -> str:
        return (f"<Correlation {self.correlation_type.value}: "
                f"{' × '.join(self.concepts[:3])}… "
                f"strength={self.strength:.2f}>")


class InterdisciplinaryCorrelator:
    """Detecta e quantifica correlações entre conceitos interdisciplinares.
    
    Usa co-ocorrência semântica, similaridade estrutural e
    análise de padrões para classificar correlações.
    """
    
    # Pesos para o score composto
    W_STRENGTH = 0.35
    W_SIGNIFICANCE = 0.35
    W_EMPIRICAL = 0.30
    
    # Pares de faculdades com alta propensão a correlações
    HIGH_AFFINITY_PAIRS = {
        ("quantum", "programming"),
        ("quantum", "exact_sciences"),
        ("statistics_ds", "exact_sciences"),
        ("statistics_ds", "social_sciences"),
        ("human_sciences", "social_sciences"),
        ("human_sciences", "literary_linguistic"),
        ("historical", "human_sciences"),
        ("historical", "literary_linguistic"),
        ("engineering", "exact_sciences"),
        ("engineering", "programming"),
        ("interdisciplinary", "*"),  # coringa: interdisciplinar com todas
    }
    
    def __init__(self, faculty_map: Dict[str, 'Faculdade']):
        self.faculty_map = faculty_map
        self._correlations: List[Correlation] = []
        self._correlation_ids: Set[str] = set()
        
        # Cache de afiliação de conceitos por faculdade
        self._concept_to_faculties: Dict[str, Set[str]] = {}
        self._build_concept_index()
    
    def _build_concept_index(self):
        """Constrói índice conceito → faculdades."""
        for fid, fac in self.faculty_map.items():
            for c in fac.conceitos:
                key = c.lower()
                if key not in self._concept_to_faculties:
                    self._concept_to_faculties[key] = set()
                self._concept_to_faculties[key].add(fid)
    
    def _get_faculties_for_concept(self, concept: str) -> Set[str]:
        """Retorna faculdades que contêm um conceito."""
        key = concept.lower()
        return self._concept_to_faculties.get(key, set())
    
    def _compute_strength(self, concepts: List[str]) -> float:
        """Força da correlação baseada em co-ocorrência semântica."""
        if len(concepts) < 2:
            return 0.5
        
        # Força via sobreposição lexical
        total_overlap = 0.0
        pairs = 0
        for i, a in enumerate(concepts):
            for b in concepts[i+1:]:
                tokens_a = set(a.lower().split())
                tokens_b = set(b.lower().split())
                if tokens_a and tokens_b:
                    jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
                    total_overlap += jaccard
                    pairs += 1
        
        lexical_strength = total_overlap / max(1, pairs)
        
        # Força via co-afiliação (mesma faculdade = mais forte)
        same_fac = 0
        diff_fac = 0
        for i, a in enumerate(concepts):
            facs_a = self._get_faculties_for_concept(a)
            for b in concepts[i+1:]:
                facs_b = self._get_faculties_for_concept(b)
                if facs_a & facs_b:
                    same_fac += 1
                else:
                    diff_fac += 1
        
        affiliation_ratio = same_fac / max(1, same_fac + diff_fac)
        
        # Força composta
        return min(1.0, lexical_strength * 0.4 + affiliation_ratio * 0.6)
    
    def _compute_significance(self, concepts: List[str]) -> float:
        """Significância: quão central/importante é a correlação."""
        # Conceitos que aparecem em múltiplas faculdades são mais significativos
        fac_counts = []
        for c in concepts:
            facs = self._get_faculties_for_concept(c)
            fac_counts.append(len(facs))
        
        avg_fac_count = sum(fac_counts) / max(1, len(fac_counts))
        
        # Significância máxima quando conceito está em 2-3 faculdades
        # (muito genérico = baixa significância, muito específico = baixa)
        if avg_fac_count <= 1:
            significance = 0.3  # específico demais
        elif avg_fac_count <= 3:
            significance = 0.9  # ponto ideal
        elif avg_fac_count <= 5:
            significance = 0.7
        else:
            significance = 0.4  # muito genérico
        
        return significance
    
    def _compute_empirical_support(self, concepts: List[str]) -> float:
        """Suporte empírico da correlação."""
        # Proxy: conceitos com subdisciplinas são mais "estabelecidos"
        support = 0.5  # baseline
        
        for c in concepts:
            # Verifica se o conceito existe em alguma subdisciplina
            for fid, fac in self.faculty_map.items():
                for sub in fac.subdisciplinas:
                    if c.lower() in sub.lower():
                        support += 0.1
                        break
        
        return min(1.0, support)
    
    def _determine_type(self, concepts: List[str]) -> CorrelationType:
        """Determina o tipo de correlação baseado nas propriedades."""
        strength = self._compute_strength(concepts)
        fac_sets = [self._get_faculties_for_concept(c) for c in concepts]
        
        # Todas compartilham faculdade? → correlação complementar
        share_all = all(
            fac_sets[0] & fs for fs in fac_sets[1:]
        ) if len(fac_sets) >= 2 else False
        
        if share_all and strength > 0.6:
            return CorrelationType.COMPLEMENTAR
        
        # Todas de faculdades diferentes? → pode ser emergente ou analógica
        all_different = all(
            not (fac_sets[i] & fac_sets[j])
            for i in range(len(fac_sets))
            for j in range(i+1, len(fac_sets))
        )
        
        if all_different:
            # Verificar se há similaridade formal (tokens compartilhados)
            tokens_all = [set(c.lower().split()) for c in concepts]
            max_shared = max(
                len(t1 & t2) for t1 in tokens_all for t2 in tokens_all if t1 != t2
            ) if len(tokens_all) >= 2 else 0
            
            if max_shared >= 2:
                return CorrelationType.ISOMORFICA
            elif strength > 0.5:
                return CorrelationType.ANALOGICA
            else:
                return CorrelationType.EMERGENTE
        
        # Pares antagônicos (mesma faculdade mas direções opostas)
        if strength < 0.2 and share_all:
            return CorrelationType.ANTAGONICA
        
        # Padrão metodológico
        if any("método" in c.lower() or "metodologia" in c.lower() for c in concepts):
            return CorrelationType.METODOLOGICA
        
        # Dialética (opostos que se complementam)
        opposites = {
            ("ordem", "caos"), ("estrutura", "agência"), ("sujeito", "objeto"),
            ("razão", "emoção"), ("natureza", "cultura"), ("indivíduo", "sociedade"),
            ("determinismo", "liberdade"), ("local", "global"),
        }
        concept_lower = set(c.lower() for c in concepts)
        for pair in opposites:
            if pair[0] in concept_lower and pair[1] in concept_lower:
                return CorrelationType.DIALETICA
        
        # Fallback: correlação simples
        return CorrelationType.CORRELACIONAL
    
    def _generate_id(self, concepts: Tuple[str, ...]) -> str:
        """Gera ID único para correlação."""
        import hashlib
        key = "corr|" + "|".join(sorted(concepts))
        return hashlib.md5(key.encode()).hexdigest()[:12]
    
    def _generate_description(self, corr: Correlation) -> str:
        """Gera descrição textual da correlação."""
        type_desc = {
            CorrelationType.CAUSAL: "relação causal",
            CorrelationType.CORRELACIONAL: "correlação",
            CorrelationType.ANALOGICA: "analogia estrutural",
            CorrelationType.ANTAGONICA: "tensão dialética",
            CorrelationType.EMERGENTE: "emergência transversal",
            CorrelationType.COMPLEMENTAR: "complementaridade",
            CorrelationType.HIERARQUICA: "hierarquia conceitual",
            CorrelationType.ISOMORFICA: "isomorfismo formal",
            CorrelationType.DIALETICA: "relação dialética",
            CorrelationType.TRADUTIVA: "tradução interdisciplinar",
            CorrelationType.METODOLOGICA: "transferência metodológica",
            CorrelationType.PARADIGMATICA: "tensão paradigmática",
        }
        
        concepts_str = " × ".join(list(corr.concepts)[:3])
        if len(corr.concepts) > 3:
            concepts_str += f" +{len(corr.concepts) - 3}"
        
        return (f"Descoberta {type_desc.get(corr.correlation_type, 'correlação')} "
                f"entre '{concepts_str}' "
                f"(força={corr.strength:.2f}, "
                f"significância={corr.significance:.2f})")
    
    def discover_correlation(
        self, concepts: Tuple[str, ...]
    ) -> Optional[Correlation]:
        """Descobre e registra correlação entre conceitos."""
        if len(concepts) < 2:
            return None
        
        cid = self._generate_id(concepts)
        if cid in self._correlation_ids:
            for c in self._correlations:
                if c.correlation_id == cid:
                    return c
        
        # Determinar faculdades
        faculties = set()
        for c in concepts:
            faculties |= self._get_faculties_for_concept(c)
        
        if not faculties:
            return None
        
        strength = self._compute_strength(list(concepts))
        significance = self._compute_significance(list(concepts))
        empirical = self._compute_empirical_support(list(concepts))
        corr_type = self._determine_type(list(concepts))
        
        correlation = Correlation(
            correlation_id=cid,
            concepts=concepts,
            faculties=tuple(sorted(faculties)),
            correlation_type=corr_type,
            strength=round(strength, 4),
            significance=round(significance, 4),
            empirical_support=round(empirical, 4),
            composite_correlation=round(
                self.W_STRENGTH * strength +
                self.W_SIGNIFICANCE * significance +
                self.W_EMPIRICAL * empirical, 4
            ),
            description=self._generate_description(
                Correlation(cid, concepts, tuple(sorted(faculties)),
                           corr_type, strength, significance, empirical, 0.0, "")
            ),
        )
        
        self._correlations.append(correlation)
        self._correlation_ids.add(cid)
        
        return correlation
    
    def discover_from_combination(
        self, combination_result: 'CombinationResult'
    ) -> Optional[Correlation]:
        """Descobre correlação a partir de um resultado de combinação."""
        return self.discover_correlation(combination_result.concepts)
    
    def batch_discover(
        self, combination_results: List['CombinationResult'],
        threshold: float = 0.3,
    ) -> List[Correlation]:
        """Descobre correlações de um lote de combinações, filtrando por threshold."""
        correlations = []
        for cr in combination_results:
            if cr.composite_score >= threshold:
                corr = self.discover_from_combination(cr)
                if corr:
                    correlations.append(corr)
        return correlations
    
    def get_top_correlations(
        self, n: int = 20, min_composite: float = 0.4
    ) -> List[Correlation]:
        """Retorna as N melhores correlações."""
        eligible = [c for c in self._correlations 
                    if c.composite_correlation >= min_composite]
        eligible.sort(key=lambda c: c.composite_correlation, reverse=True)
        return eligible[:n]
    
    def get_correlations_by_type(
        self, corr_type: CorrelationType
    ) -> List[Correlation]:
        """Filtra correlações por tipo."""
        return [c for c in self._correlations if c.correlation_type == corr_type]
    
    def get_correlations_by_faculty(self, faculty_id: str) -> List[Correlation]:
        """Filtra correlações envolvendo uma faculdade."""
        return [c for c in self._correlations if faculty_id in c.faculties]
    
    def get_cross_faculty_matrix(self) -> Dict[Tuple[str, str], int]:
        """Matriz de adjacência entre faculdades baseada em correlações."""
        matrix: Dict[Tuple[str, str], int] = defaultdict(int)
        for corr in self._correlations:
            if len(corr.faculties) >= 2:
                for i in range(len(corr.faculties)):
                    for j in range(i+1, len(corr.faculties)):
                        pair = tuple(sorted([corr.faculties[i], corr.faculties[j]]))
                        matrix[pair] += 1
        return dict(matrix)
    
    def get_statistics(self) -> Dict:
        """Estatísticas do correlator."""
        type_counter = defaultdict(int)
        for c in self._correlations:
            type_counter[c.correlation_type.value] += 1
        
        return {
            "total_correlations": len(self._correlations),
            "correlations_by_type": dict(type_counter),
            "avg_strength": (sum(c.strength for c in self._correlations) 
                            / max(1, len(self._correlations))),
            "avg_significance": (sum(c.significance for c in self._correlations) 
                                / max(1, len(self._correlations))),
            "avg_composite": (sum(c.composite_correlation for c in self._correlations) 
                             / max(1, len(self._correlations))),
            "top_correlation_score": (max(c.composite_correlation for c in self._correlations) 
                                     if self._correlations else 0.0),
        }
