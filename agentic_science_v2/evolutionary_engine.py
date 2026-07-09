# -*- coding: utf-8 -*-
"""
Evolutionary Engine — R101
===========================
Operacoes darwinianas sobre clusters de entidades no grafo de conhecimento:

  - Selection: Filtra clusters com base em feedback do reviewer
  - Crossover: Recombina entidades de clusters de alta fitness
  - Mutation: Injeta entidades novas ou de baixa frequencia
  - Inheritance: Propaga entidades de alta fitness

Inspirado no bio-inspired evolutionary loop do EvoSci (Xiong et al., ACL 2026).

SPEC-935-R101.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Tipos de operacao evolutiva
EVO_OPERATIONS = ["selection", "crossover", "mutation", "inheritance"]


@dataclass
class EvolutionRound:
    """Registro de uma rodada de evolucao."""
    round_number: int = 0
    operations: List[Dict[str, Any]] = field(default_factory=list)
    population_size_before: int = 0
    population_size_after: int = 0
    avg_fitness_before: float = 0.0
    avg_fitness_after: float = 0.0
    diversity_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round": self.round_number,
            "operations": self.operations,
            "population_before": self.population_size_before,
            "population_after": self.population_size_after,
            "fitness_before": self.avg_fitness_before,
            "fitness_after": self.avg_fitness_after,
            "diversity": self.diversity_score,
        }


# ============================================================
# EvoEngine
# ============================================================

class EvoEngine:
    """Motor de evolucao bio-inspirado para descoberta cientifica.

    Atua sobre a camada de entidades (conceitos/dominios), mantendo
    a camada de disciplina estatica como backbone estrutural.
    """

    def __init__(
        self,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        selection_pressure: float = 0.8,
        diversity_target: float = 0.3,
    ):
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.selection_pressure = selection_pressure
        self.diversity_target = diversity_target
        self.history: List[EvolutionRound] = []

    def select(
        self,
        entities: List[Dict[str, Any]],
        fitness_scores: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Seleciona entidades com base em fitness (torneio).

        Args:
            entities: Lista de entidades (dicts com "id" key).
            fitness_scores: Dict {entity_id: score}.

        Returns:
            Lista de entidades selecionadas.
        """
        if not entities:
            return []

        # Torneio: cada entidade compete contra um oponente aleatorio
        selected = []
        for entity in entities:
            eid = entity.get("id", "")
            if eid not in fitness_scores:
                continue

            opponent = random.choice(entities)
            oid = opponent.get("id", "")
            opponent_score = fitness_scores.get(oid, 0.0)

            # Vence se score > opponent * selection_pressure
            if fitness_scores[eid] >= opponent_score * self.selection_pressure:
                selected.append(entity)

        # Garantir pelo menos 1 entidade
        if not selected and entities:
            selected = [entities[0]]

        return selected

    def crossover(
        self,
        parent_a: Dict[str, Any],
        parent_b: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Recombina duas entidades para gerar descendentes.

        Opera sobre as chaves 'concepts' e 'traits' dos parents.
        """
        # Inicializar descendentes
        child_a = dict(parent_a)
        child_b = dict(parent_b)

        # Crossover de conceitos (se existirem)
        concepts_a = list(parent_a.get("concepts", []))
        concepts_b = list(parent_b.get("concepts", []))

        if concepts_a and concepts_b and random.random() < self.crossover_rate:
            midpoint = len(concepts_a) // 2
            child_a["concepts"] = list(
                set(concepts_a[:midpoint] + concepts_b[midpoint:])
            )
            child_b["concepts"] = list(
                set(concepts_b[:midpoint] + concepts_a[midpoint:])
            )

        # Crossover de traits (se existirem)
        traits_a = dict(parent_a.get("traits", {}))
        traits_b = dict(parent_b.get("traits", {}))
        child_a["traits"] = {**traits_a, **traits_b}
        child_b["traits"] = {**traits_b, **traits_a}

        # Marcar como descendentes
        child_a["evolution"] = "crossover"
        child_b["evolution"] = "crossover"

        return child_a, child_b

    def mutate(
        self,
        entity: Dict[str, Any],
        novelty_pool: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Aplica mutacao a entidade.

        Args:
            entity: Entidade a mutar.
            novelty_pool: Pool de novos conceitos para injecao.

        Returns:
            Entidade mutada.
        """
        mutated = dict(entity)

        if random.random() < self.mutation_rate:
            concepts = list(mutated.get("concepts", []))

            if novelty_pool and random.random() < 0.5:
                # Injetar novo conceito do pool
                new_concept = random.choice(novelty_pool)
                if new_concept not in concepts:
                    concepts.append(new_concept)
            elif concepts:
                # Substituir um conceito existente por variacao
                idx = random.randrange(len(concepts))
                concepts[idx] = concepts[idx] + "_mutated"

            mutated["concepts"] = concepts
            mutated["evolution"] = "mutation"

        return mutated

    def inherit(
        self,
        entities: List[Dict[str, Any]],
        fitness_scores: Dict[str, float],
        top_k: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """Propaga entidades de alta fitness para proxima geracao.

        Args:
            entities: Populacao atual.
            fitness_scores: Dict {entity_id: score}.
            top_k: Fracao do topo a preservar (0.0 a 1.0).

        Returns:
            Entidades com alta fitness preservadas.
        """
        if not entities:
            return []

        # Ordenar por fitness
        scored = []
        for entity in entities:
            eid = entity.get("id", "")
            score = fitness_scores.get(eid, 0.0)
            scored.append((score, entity))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Preservar top_k%
        n_preserve = max(1, int(len(scored) * top_k))
        inherited = [entity for _, entity in scored[:n_preserve]]

        # Marcar
        for ent in inherited:
            ent["evolution"] = "inheritance"

        return inherited

    def compute_diversity(
        self,
        entities: List[Dict[str, Any]],
    ) -> float:
        """Computa diversidade da populacao baseada em conceitos."""
        if len(entities) < 2:
            return 1.0

        all_concepts = []
        for entity in entities:
            concepts = set(entity.get("concepts", []))
            if concepts:
                all_concepts.append(concepts)

        if len(all_concepts) < 2:
            return 0.0

        # Jaccard medio entre pares
        total_sim = 0.0
        pairs = 0
        for i in range(len(all_concepts)):
            for j in range(i + 1, len(all_concepts)):
                inter = all_concepts[i] & all_concepts[j]
                union = all_concepts[i] | all_concepts[j]
                if union:
                    total_sim += len(inter) / len(union)
                    pairs += 1

        avg_sim = total_sim / max(1, pairs)
        return 1.0 - avg_sim  # diversidade = 1 - similaridade media

    def step(
        self,
        entities: List[Dict[str, Any]],
        fitness_scores: Dict[str, float],
        novelty_pool: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], EvolutionRound]:
        """Executa um passo completo de evolucao.

        Ciclo: Selection -> Crossover -> Mutation -> Inheritance.

        Args:
            entities: Populacao atual de entidades.
            fitness_scores: Dict {entity_id: score}.
            novelty_pool: Pool de novos conceitos para mutacao.

        Returns:
            (nova_populacao, EvolutionRound)
        """
        round_num = len(self.history) + 1
        round_record = EvolutionRound(
            round_number=round_num,
            population_size_before=len(entities),
            avg_fitness_before=(
                statistics.mean(fitness_scores.values())
                if fitness_scores else 0.0
            ),
            diversity_score=self.compute_diversity(entities),
        )

        operations = []
        new_population = []

        # 1. Selection
        selected = self.select(entities, fitness_scores)
        operations.append({
            "op": "selection",
            "input": len(entities),
            "output": len(selected),
        })

        # 2. Crossover (aplicado aos selecionados)
        crossed = []
        for i in range(0, len(selected) - 1, 2):
            if random.random() < self.crossover_rate:
                ca, cb = self.crossover(selected[i], selected[i + 1])
                crossed.extend([ca, cb])
            else:
                crossed.extend([selected[i], selected[i + 1]])

        if len(selected) % 2 == 1:
            crossed.append(selected[-1])

        operations.append({
            "op": "crossover",
            "input": len(selected),
            "output": len(crossed),
        })

        # 3. Mutation
        mutated = [self.mutate(e, novelty_pool) for e in crossed]
        operations.append({
            "op": "mutation",
            "input": len(crossed),
            "output": len(mutated),
        })

        # 4. Inheritance (preservar top entidades)
        inherited = self.inherit(entities, fitness_scores)

        # Combinar: descendentes mutados + elite herdada
        new_population = mutated + inherited

        # Remover duplicatas por id
        seen_ids = set()
        deduped = []
        for entity in new_population:
            eid = entity.get("id", "")
            if eid not in seen_ids:
                seen_ids.add(eid)
                deduped.append(entity)

        operations.append({
            "op": "inheritance",
            "input": len(entities),
            "output": len(inherited),
        })

        round_record.operations = operations
        round_record.population_size_after = len(deduped)
        round_record.avg_fitness_after = (
            statistics.mean(fitness_scores.values())
            if fitness_scores else 0.0
        )

        self.history.append(round_record)

        return deduped, round_record

    def is_stagnant(
        self,
        window: int = 3,
        threshold: float = 0.02,
    ) -> bool:
        """Detecta estagnacao na evolucao.

        Args:
            window: Numero de rodadas para analisar.
            threshold: Variacao maxima para considerar estagnado.

        Returns:
            True se estagnado.
        """
        if len(self.history) < window:
            return False

        recent = self.history[-window:]
        fitnesses = [r.avg_fitness_after for r in recent]
        if len(fitnesses) < 2:
            return False

        return max(fitnesses) - min(fitnesses) < threshold

    def summary(self) -> Dict[str, Any]:
        """Sumario do estado do motor evolutivo."""
        return {
            "total_rounds": len(self.history),
            "current_diversity": (
                self.history[-1].diversity_score if self.history else 0.0
            ),
            "current_fitness": (
                self.history[-1].avg_fitness_after if self.history else 0.0
            ),
            "is_stagnant": self.is_stagnant(),
            "config": {
                "mutation_rate": self.mutation_rate,
                "crossover_rate": self.crossover_rate,
                "selection_pressure": self.selection_pressure,
                "diversity_target": self.diversity_target,
            },
        }


# Import interno para evitar circular
import statistics  # noqa: E402
