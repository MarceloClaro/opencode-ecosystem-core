"""MiroFish Combinatorial Discovery Engine — SPEC-935.

Motor combinatorial que testa 10.000+ combinações de conceitos entre faculdades,
usando pesos de similaridade conceitual, coerência interdisciplinar,
e métricas de viabilidade para descobrir novas correlações.
"""

from __future__ import annotations
import random
import math
import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set, Callable
from itertools import combinations, product
from collections import Counter

logger = logging.getLogger(__name__)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class CombinationResult:
    """Resultado de uma combinação de conceitos testada."""
    combination_id: str
    concepts: Tuple[str, ...]
    faculties: Tuple[str, ...]
    viability_score: float          # 0..1 — quão viável é a combinação
    novelty_score: float            # 0..1 — quão nova/original
    coherence_score: float          # 0..1 — coerência interna
    impact_score: float             # 0..1 — impacto potencial
    composite_score: float          # média ponderada dos scores
    discovered_pattern: str         # padrão identificado na combinação
    timestamp: float = field(default_factory=time.time)
    debated: bool = False           # se passou pelo MiroFish debate
    
    def __repr__(self) -> str:
        return (f"<Combination {self.combination_id}: "
                f"{' × '.join(self.concepts[:3])}… "
                f"viab={self.viability_score:.2f} "
                f"composite={self.composite_score:.2f}>")


class ConceptEmbeddingSpace:
    """Espaço conceitual para medir similaridade entre conceitos.
    
    R75: Embedding semântico neural via Ollama (nomic-embed-text, 768-dim).
    R76: Faculty-aware similarity + refined pattern detection.
    
    Interface 100% compatível com a implementação original.
    """
    
    CACHE_PATH = "/tmp/semantic_embedder.pkl"
    
    # Fator de bônus por proximidade entre faculdades
    FACULTY_PROXIMITY_BONUS = 0.08
    
    def __init__(self, faculty_map: Optional[Dict] = None):
        from synthetic_university.semantic_embedder import SemanticEmbedder, create_semantic_embedder
        
        # Embedder semântico neural
        self._semantic = SemanticEmbedder(dimension=768)
        
        # Mapa conceito → faculdade
        self._concept_to_faculty: Dict[str, str] = {}
        self._faculty_map: Optional[Dict] = faculty_map
        
        # Matriz de proximidade entre faculdades
        self._faculty_proximity: Dict[Tuple[str, str], float] = {}
        self._faculty_list: List[str] = []
        
        # Tentar carregar cache primeiro
        if self._semantic.load(self.CACHE_PATH):
            self._corpus_built = True
            logger.info(f"ConceptEmbeddingSpace: embeddings carregados de cache")
        else:
            self._corpus_built = False
        
        # Fallback lexical
        self._lexical_cache: Dict[str, Set[str]] = {}
        
        # Se faculty_map foi fornecido
        if faculty_map is not None:
            # Constrói índice conceito → faculdade
            for fid, fac in faculty_map.items():
                for c in getattr(fac, 'conceitos', []):
                    self._concept_to_faculty[c.lower().strip()] = fid
            self._faculty_list = list(faculty_map.keys())
            
            # Constrói corpus se necessário
            if not self._corpus_built:
                self.build_corpus(faculty_map)
            
            # Computa matriz de proximidade entre faculdades
            if self._corpus_built:
                self._compute_faculty_proximity(faculty_map)
    
    def _compute_faculty_proximity(self, faculty_map: Dict) -> None:
        """Computa similaridade semântica média entre faculdades.
        
        Para cada par de faculdades, calcula a média das similaridades
        entre todos os seus conceitos. Isso gera uma matriz 11×11
        que captura relações epistemológicas reais entre domínios.
        """
        logger.info("Computando matriz de proximidade entre faculdades...")
        
        fac_ids = list(faculty_map.keys())
        n_facs = len(fac_ids)
        
        # Cache de embeddings médios por faculdade
        fac_centroids: Dict[str, List[np.ndarray]] = {}
        for fid in fac_ids:
            fac = faculty_map[fid]
            conceitos = getattr(fac, 'conceitos', [])
            vecs = []
            for c in conceitos[:50]:  # amostra de 50 para velocidade
                vec = self._semantic.embed(c)
                if np.linalg.norm(vec) > 1e-8:
                    vecs.append(vec)
            if vecs:
                fac_centroids[fid] = vecs
        
        # Similaridade média entre faculdades
        for i in range(n_facs):
            for j in range(i, n_facs):
                fi, fj = fac_ids[i], fac_ids[j]
                if fi == fj:
                    self._faculty_proximity[(fi, fj)] = 1.0
                    continue
                
                vecs_i = fac_centroids.get(fi, [])
                vecs_j = fac_centroids.get(fj, [])
                
                if not vecs_i or not vecs_j:
                    self._faculty_proximity[(fi, fj)] = 0.0
                    self._faculty_proximity[(fj, fi)] = 0.0
                    continue
                
                # Amostragem: no máximo 30×30 = 900 comparações
                import random
                sample_i = random.Random(42).sample(
                    vecs_i, min(30, len(vecs_i))
                )
                sample_j = random.Random(42).sample(
                    vecs_j, min(30, len(vecs_j))
                )
                
                similarities = []
                for vi in sample_i:
                    for vj in sample_j:
                        dot = float(np.dot(vi, vj))
                        similarities.append(max(0.0, dot))
                
                prox = sum(similarities) / len(similarities) if similarities else 0.0
                self._faculty_proximity[(fi, fj)] = prox
                self._faculty_proximity[(fj, fi)] = prox
        
        logger.info(
            f"Matriz de proximidade: {n_facs} faculdades computadas"
        )
    
    def _faculty_bonus(self, concept_a: str, concept_b: str) -> float:
        """Bônus de similaridade baseado na proximidade entre faculdades.
        
        Se dois conceitos pertencem à mesma faculdade ou a faculdades
        próximas, recebem um pequeno bônus semântico.
        """
        if not self._faculty_proximity:
            return 0.0
        
        fa = self._concept_to_faculty.get(concept_a.lower().strip())
        fb = self._concept_to_faculty.get(concept_b.lower().strip())
        
        if fa is None or fb is None:
            return 0.0
        
        prox = self._faculty_proximity.get((fa, fb), 0.0)
        return prox * self.FACULTY_PROXIMITY_BONUS
    
    def build_corpus(self, faculty_map: Dict) -> None:
        """Constrói o corpus a partir das faculdades."""
        from synthetic_university.semantic_embedder import create_semantic_embedder
        
        texts: List[str] = []
        for fid, fac in faculty_map.items():
            desc = getattr(fac, 'descricao', getattr(fac, 'description', ''))
            if desc:
                texts.append(desc)
            conceitos = getattr(fac, 'conceitos', [])
            texts.extend(conceitos)
        
        if texts:
            embedder = create_semantic_embedder(texts, cache_path=self.CACHE_PATH)
            self._semantic = embedder
            self._corpus_built = True
            logger.info(
                f"ConceptEmbeddingSpace: corpus construído com "
                f"{len(texts)} textos de {len(faculty_map)} faculdades"
            )
        else:
            self._corpus_built = False
            logger.warning("ConceptEmbeddingSpace: corpus vazio")
    
    def _tokenize(self, text: str) -> Set[str]:
        if text not in self._lexical_cache:
            tokens = set()
            for word in text.lower().split():
                word = word.strip(".,;:!?()[]{}""''«»-–")
                if len(word) >= 3 and word not in {
                    "que", "para", "com", "dos", "das", "uma", "mais",
                    "como", "por", "mas", "seu", "sua", "pelo", "pela",
                    "entre", "onde", "sobre", "após", "até", "sem",
                }:
                    tokens.add(word)
            self._lexical_cache[text] = tokens
        return self._lexical_cache[text]
    
    def similarity(self, concept_a: str, concept_b: str) -> float:
        """Similaridade semântica entre dois conceitos.
        
        Combina:
        1. Embedding neural (Ollama nomic-embed-text, 768-dim)
        2. Bônus de proximidade entre faculdades
        3. Fallback lexical (Jaccard)
        """
        if concept_a == concept_b:
            return 1.0
        
        sim = 0.0
        
        # Embedding neural
        if self._corpus_built:
            sim = self._semantic.similarity(concept_a, concept_b)
        
        # Bônus faculty-aware
        if sim > 0.0:
            bonus = self._faculty_bonus(concept_a, concept_b)
            sim = min(1.0, sim + bonus)
        
        # Fallback lexical se neural não capturou
        if sim <= 0.0:
            tokens_a = self._tokenize(concept_a)
            tokens_b = self._tokenize(concept_b)
            
            if tokens_a and tokens_b:
                intersection = tokens_a & tokens_b
                union = tokens_a | tokens_b
                if union:
                    sim = len(intersection) / len(union)
        
        return max(0.0, min(1.0, sim))
    
    def coherence(self, concepts: List[str]) -> float:
        """Coerência média entre todos os pares de conceitos."""
        if len(concepts) <= 1:
            return 1.0
        scores = [self.similarity(a, b) for a, b in combinations(concepts, 2)]
        return sum(scores) / len(scores) if scores else 0.5
    
    def diversity(self, concepts: List[str]) -> float:
        """Diversidade como 1 - similaridade média."""
        return 1.0 - self.coherence(concepts)
    
    def get_faculty_proximity_report(self) -> Dict:
        """Relatório da matriz de proximidade entre faculdades."""
        if not self._faculty_proximity:
            return {"error": "faculty proximity not computed"}
        
        report = {}
        for (fa, fb), prox in sorted(self._faculty_proximity.items()):
            if fa < fb:  # cada par uma vez
                report[f"{fa} ↔ {fb}"] = round(prox, 4)
        return report


class CombinatorialDiscoveryEngine:
    """Motor de descoberta combinatorial usando MiroFish.
    
    Gera, testa e pontua combinações de conceitos entre faculdades
    para descobrir correlações interdisciplinares viáveis.
    """
    
    # Pesos para o score composto (R76: mais peso para coerência semântica)
    WEIGHT_VIABILITY = 0.25
    WEIGHT_NOVELTY = 0.20
    WEIGHT_COHERENCE = 0.30    # aumentado — embedding neural dá coerência real
    WEIGHT_IMPACT = 0.25
    
    # Padrões de descoberta
    DISCOVERY_PATTERNS = [
        "analogia_estrutural",
        "transferencia_metodologica",
        "hibridizacao_concetitual",
        "isomorfismo_formal",
        "emergencia_transversal",
        "complementaridade_paradigmatica",
        "unificacao_teorica",
        "traducao_interdisciplinar",
        "meta_padrao",
        "inovacao_paradigmatica",
    ]
    
    def __init__(self, faculty_map: Dict[str, 'Faculdade']):
        self.faculty_map = faculty_map
        self.embedding = ConceptEmbeddingSpace(faculty_map=faculty_map)
        
        # Cache de combinações já testadas
        self._history: List[CombinationResult] = []
        self._history_set: Set[str] = set()
        
        # Contadores
        self.total_combinations_tested = 0
        self.total_combinations_generated = 0
        
        # Estatísticas por faculdade
        self.faculty_stats: Dict[str, Dict] = {}
        
        logger.info(f"CombinatorialDiscoveryEngine inicializado com "
                     f"{len(faculty_map)} faculdades")
    
    def _concepts_from_faculties(self, faculty_ids: List[str]) -> List[str]:
        """Coleta todos os conceitos das faculdades especificadas."""
        concepts = []
        for fid in faculty_ids:
            fac = self.faculty_map.get(fid)
            if fac:
                concepts.extend(fac.conceitos)
        return concepts
    
    def _compute_viability(self, concepts: List[str]) -> float:
        """Calcula viabilidade baseada em pares epistemológicos.
        
        Calibrado para embedding neural (R76):
        - Diversidade neural: 0.30-0.60 (mesmo domínio), 0.40-0.80 (cross-domínio)
        - Viabilidade ótima: diversidade moderada (0.45-0.65) → descoberta fértil
        """
        if len(concepts) < 2:
            return 0.5
        
        diversity = self.embedding.diversity(concepts)
        
        # Função sino com pico em diversidade 0.55
        # Isso maximiza combinações que são nem muito óbvias nem muito absurdas
        if diversity < 0.30:
            # Muito similar → baixa novidade → viabilidade baixa
            viability = 0.2 + diversity * 0.5
        elif diversity < 0.55:
            # Crescente até o pico
            viability = 0.5 + (diversity - 0.30) / 0.25 * 0.35
        elif diversity < 0.75:
            # Decrescente do pico
            viability = 0.85 - (diversity - 0.55) / 0.20 * 0.35
        else:
            # Muito diferente → baixa compatibilidade
            viability = max(0.15, 0.50 - (diversity - 0.75) * 1.5)
        
        return max(0.0, min(1.0, viability))
    
    def _compute_novelty(self, concepts: List[str]) -> float:
        """Novelty: quão inédita é a combinação."""
        # Se já testamos combinações similares, reduz novelty
        concept_set = frozenset(concepts)
        
        # Verificar similaridade com combinações existentes
        max_sim = 0.0
        for existing in self._history:
            existing_set = frozenset(existing.concepts)
            if concept_set == existing_set:
                return 0.0
            
            # Jaccard entre sets
            intersection = concept_set & existing_set
            union = concept_set | existing_set
            if union:
                sim = len(intersection) / len(union)
                max_sim = max(max_sim, sim)
        
        # Quanto mais similar ao já testado, menor novelty
        base_novelty = 1.0 - max_sim
        
        # Bônus para combinações que cruzam muitas faculdades
        faculties_in_concepts = set()
        for c in concepts:
            for fid, fac in self.faculty_map.items():
                if c in fac.conceitos:
                    faculties_in_concepts.add(fid)
        
        cross_bonus = min(0.3, len(faculties_in_concepts) * 0.05)
        
        return min(1.0, base_novelty + cross_bonus)
    
    def _compute_impact(self, concepts: List[str]) -> float:
        """Impacto potencial baseado na abrangência dos conceitos."""
        # Conceitos mais gerais/abrangentes podem ter maior impacto
        # Usamos comprimento como proxy: conceitos curtos são mais gerais
        impact_scores = []
        for c in concepts:
            # Palavras muito curtas tendem a ser muito genéricas
            # Palavras muito longas tendem a ser muito específicas
            length = len(c)
            if length <= 5:
                impact_scores.append(0.7)  # conceito geral
            elif length <= 12:
                impact_scores.append(0.5)  # médio
            elif length <= 20:
                impact_scores.append(0.3)  # específico
            else:
                impact_scores.append(0.1)  # muito específico
        
        # Impacto também vem da diversidade da combinação
        diversity = self.embedding.diversity(concepts)
        diversity_bonus = diversity * 0.3
        
        base = sum(impact_scores) / len(impact_scores) if impact_scores else 0.5
        return min(1.0, base + diversity_bonus)
    
    def _compute_composite(self, result: CombinationResult) -> float:
        """Score composto ponderado."""
        return (
            self.WEIGHT_VIABILITY * result.viability_score +
            self.WEIGHT_NOVELTY * result.novelty_score +
            self.WEIGHT_COHERENCE * result.coherence_score +
            self.WEIGHT_IMPACT * result.impact_score
        )
    
    def _assign_pattern(self, concepts: List[str]) -> str:
        """Atribui um padrão de descoberta com base nas propriedades.
        
        Thresholds calibrados para embedding neural (R76):
        - Coerência neural: 0.45-0.60 (mesmo domínio), 0.30-0.50 (cross-domínio)
        - Diversidade = 1 - coerência
        """
        coherence = self.embedding.coherence(concepts)
        diversity = self.embedding.diversity(concepts)
        
        # Padrões determinísticos baseados em coerência × diversidade
        if diversity < 0.30:
            # Conceitos muito similares → unificação teórica
            return "unificacao_teorica"
        elif coherence > 0.55 and diversity < 0.45:
            # Alta coerência, baixa diversidade → analogia estrutural
            return "analogia_estrutural"
        elif 0.35 <= coherence <= 0.55 and diversity >= 0.40:
            # Coerência moderada → hibridização ou isomorfismo
            if diversity > 0.55:
                return "hibridizacao_concetitual"
            else:
                if HAS_NUMPY and np.random.random() > 0.5:
                    return "isomorfismo_formal"
                return "complementaridade_paradigmatica"
        elif coherence < 0.30 and diversity > 0.60:
            # Baixa coerência, alta diversidade → emergência transversal
            return "emergencia_transversal"
        elif 0.30 <= coherence < 0.45:
            # Coerência baixa-moderada → tradução ou meta-padrão
            if HAS_NUMPY and np.random.random() > 0.5:
                return "traducao_interdisciplinar"
            return "meta_padrao"
        else:
            return random.choice([
                "transferencia_metodologica",
                "inovacao_paradigmatica",
                "complementaridade_paradigmatica",
            ])
    
    def _combination_id(self, concepts: Tuple[str, ...]) -> str:
        """Gera ID único para a combinação."""
        import hashlib
        key = "|".join(sorted(concepts))
        return hashlib.md5(key.encode()).hexdigest()[:12]
    
    def test_combination(self, concepts: Tuple[str, ...]) -> CombinationResult:
        """Testa uma combinação específica e retorna resultado."""
        cid = self._combination_id(concepts)
        
        # Evitar re-testes
        if cid in self._history_set:
            for existing in self._history:
                if existing.combination_id == cid:
                    return existing
        
        # Determinar faculdades envolvidas
        faculties = set()
        for c in concepts:
            for fid, fac in self.faculty_map.items():
                if c in fac.conceitos:
                    faculties.add(fid)
        
        result = CombinationResult(
            combination_id=cid,
            concepts=concepts,
            faculties=tuple(sorted(faculties)),
            viability_score=self._compute_viability(list(concepts)),
            novelty_score=self._compute_novelty(list(concepts)),
            coherence_score=self.embedding.coherence(list(concepts)),
            impact_score=self._compute_impact(list(concepts)),
            composite_score=0.0,  # será calculado abaixo
            discovered_pattern=self._assign_pattern(list(concepts)),
        )
        result.composite_score = self._compute_composite(result)
        
        self._history.append(result)
        self._history_set.add(cid)
        self.total_combinations_tested += 1
        
        return result
    
    def generate_pair_combinations(
        self, 
        faculties_a: List[str], 
        faculties_b: List[str],
        max_combinations: int = 1000,
    ) -> List[CombinationResult]:
        """Gera combinações de pares entre dois grupos de faculdades."""
        concepts_a = self._concepts_from_faculties(faculties_a)
        concepts_b = self._concepts_from_faculties(faculties_b)
        
        results = []
        # Limit to max_combinations
        total_pairs = min(len(concepts_a) * len(concepts_b), max_combinations)
        
        if total_pairs <= 0:
            return results
        
        # Amostra aleatória para manter dentro do limite
        sample_pairs = min(max_combinations, len(concepts_a) * len(concepts_b))
        count = 0
        attempts = 0
        max_attempts = sample_pairs * 3  # evitar loop infinito
        
        while count < sample_pairs and attempts < max_attempts:
            attempts += 1
            a = random.choice(concepts_a)
            b = random.choice(concepts_b)
            if a != b:
                result = self.test_combination((a, b))
                if result.combination_id not in {r.combination_id for r in results}:
                    results.append(result)
                    count += 1
        
        self.total_combinations_generated += len(results)
        results.sort(key=lambda r: r.composite_score, reverse=True)
        return results
    
    def generate_triple_combinations(
        self,
        faculty_ids: List[str],
        max_combinations: int = 2000,
    ) -> List[CombinationResult]:
        """Gera combinações triplas entre conceitos de três faculdades."""
        concepts_by_fac = {}
        for fid in faculty_ids:
            fac = self.faculty_map.get(fid)
            if fac:
                concepts_by_fac[fid] = fac.conceitos
        
        results = []
        all_concept_sets = list(concepts_by_fac.values())
        if len(all_concept_sets) < 2:
            return results
        
        count = 0
        attempts = 0
        max_attempts = max_combinations * 5
        
        while count < max_combinations and attempts < max_attempts:
            attempts += 1
            chosen = []
            for cset in all_concept_sets:
                chosen.append(random.choice(cset))
            # Remove duplicates within combination
            chosen = list(dict.fromkeys(chosen))
            if len(chosen) >= 2:
                result = self.test_combination(tuple(chosen))
                if result.combination_id not in {r.combination_id for r in results}:
                    results.append(result)
                    count += 1
        
        self.total_combinations_generated += len(results)
        results.sort(key=lambda r: r.composite_score, reverse=True)
        return results
    
    def generate_quadruple_combinations(
        self,
        faculty_ids: List[str],
        max_combinations: int = 3000,
    ) -> List[CombinationResult]:
        """Gera combinações quádruplas entre conceitos de até 4 faculdades."""
        concepts_by_fac = {}
        for fid in faculty_ids:
            fac = self.faculty_map.get(fid)
            if fac:
                concepts_by_fac[fid] = fac.conceitos
        
        results = []
        all_concept_sets = list(concepts_by_fac.values())
        if len(all_concept_sets) < 2:
            return results
        
        count = 0
        attempts = 0
        max_attempts = max_combinations * 8
        
        while count < max_combinations and attempts < max_attempts:
            attempts += 1
            chosen = []
            # Escolhe de 2 a 4 faculdades aleatórias
            n_facs = random.randint(2, min(4, len(all_concept_sets)))
            selected_sets = random.sample(all_concept_sets, n_facs)
            for cset in selected_sets:
                chosen.append(random.choice(cset))
            chosen = list(dict.fromkeys(chosen))
            if len(chosen) >= 2:
                result = self.test_combination(tuple(chosen))
                if result.combination_id not in {r.combination_id for r in results}:
                    results.append(result)
                    count += 1
        
        self.total_combinations_generated += len(results)
        results.sort(key=lambda r: r.composite_score, reverse=True)
        return results
    
    def full_discovery_run(
        self,
        target_combinations: int = 10000,
        faculty_ids: Optional[List[str]] = None,
    ) -> List[CombinationResult]:
        """Execução completa de descoberta: gera N combinações-alvo.
        
        Distribui entre pares, triplas e quádruplas para maximizar diversidade.
        """
        fac_ids = faculty_ids or list(self.faculty_map.keys())
        
        logger.info(f"Iniciando full_discovery_run: target={target_combinations}")
        
        # Estratégia: ~40% pares, ~35% triplas, ~25% quádruplas
        n_pairs = int(target_combinations * 0.40)
        n_triples = int(target_combinations * 0.35)
        n_quads = target_combinations - n_pairs - n_triples
        
        # Para pares, usar pares de faculdades diferentes
        all_fac_pairs = list(combinations(fac_ids, 2))
        all_results = []
        
        # Distribuir pares entre combinações de faculdades
        if all_fac_pairs:
            per_pair = max(10, n_pairs // len(all_fac_pairs))
            for fac_a, fac_b in all_fac_pairs:
                pairs = self.generate_pair_combinations(
                    [fac_a], [fac_b], max_combinations=per_pair
                )
                all_results.extend(pairs)
        
        # Triplas entre 3 faculdades
        if len(fac_ids) >= 3:
            all_fac_triples = list(combinations(fac_ids, 3))
            per_triple = max(5, n_triples // len(all_fac_triples))
            for triple in all_fac_triples[:20]:  # limitar para não explodir
                triples = self.generate_triple_combinations(
                    list(triple), max_combinations=per_triple
                )
                all_results.extend(triples)
        
        # Quádruplas mistas
        quads = self.generate_quadruple_combinations(
            fac_ids, max_combinations=n_quads
        )
        all_results.extend(quads)
        
        logger.info(
            f"Full discovery run concluído: "
            f"{len(all_results)} combinações únicas geradas "
            f"(total testado: {self.total_combinations_tested})"
        )
        
        return all_results
    
    def get_top_combinations(
        self, n: int = 20, min_composite: float = 0.5
    ) -> List[CombinationResult]:
        """Retorna as N melhores combinações com score mínimo."""
        eligible = [r for r in self._history if r.composite_score >= min_composite]
        eligible.sort(key=lambda r: r.composite_score, reverse=True)
        return eligible[:n]
    
    def get_combinations_by_pattern(self, pattern: str) -> List[CombinationResult]:
        """Retorna combinações que correspondem a um padrão."""
        return [r for r in self._history if r.discovered_pattern == pattern]
    
    def get_combinations_by_faculty(self, faculty_id: str) -> List[CombinationResult]:
        """Retorna combinações envolvendo uma faculdade específica."""
        return [r for r in self._history if faculty_id in r.faculties]
    
    def get_statistics(self) -> Dict:
        """Estatísticas do motor combinatorial."""
        # Top patterns
        pattern_counter = Counter(r.discovered_pattern for r in self._history)
        
        # Scores médios
        avg_viability = (sum(r.viability_score for r in self._history) 
                         / max(1, len(self._history)))
        avg_novelty = (sum(r.novelty_score for r in self._history) 
                       / max(1, len(self._history)))
        avg_coherence = (sum(r.coherence_score for r in self._history) 
                         / max(1, len(self._history)))
        avg_impact = (sum(r.impact_score for r in self._history) 
                      / max(1, len(self._history)))
        
        # Faculdades mais envolvidas
        fac_counter = Counter()
        for r in self._history:
            for fid in r.faculties:
                fac_counter[fid] += 1
        
        return {
            "total_tested": self.total_combinations_tested,
            "total_generated": self.total_combinations_generated,
            "unique_combinations": len(self._history),
            "avg_composite": (sum(r.composite_score for r in self._history) 
                              / max(1, len(self._history))),
            "avg_viability": avg_viability,
            "avg_novelty": avg_novelty,
            "avg_coherence": avg_coherence,
            "avg_impact": avg_impact,
            "top_patterns": pattern_counter.most_common(5),
            "top_faculties": fac_counter.most_common(10),
            "top_combination_score": (max(r.composite_score for r in self._history) 
                                      if self._history else 0.0),
        }
    
    def export_combinations(self, limit: int = 100) -> List[Dict]:
        """Exporta as melhores combinações para serialização."""
        top = self.get_top_combinations(limit, min_composite=0.0)
        return [
            {
                "id": r.combination_id,
                "concepts": list(r.concepts),
                "faculties": list(r.faculties),
                "viability": round(r.viability_score, 3),
                "novelty": round(r.novelty_score, 3),
                "coherence": round(r.coherence_score, 3),
                "impact": round(r.impact_score, 3),
                "composite": round(r.composite_score, 3),
                "pattern": r.discovered_pattern,
                "timestamp": r.timestamp,
            }
            for r in top
        ]
