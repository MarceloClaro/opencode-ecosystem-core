#!/usr/bin/env python3
"""
GameTheoryLocal — Cálculo de Teoria dos Jogos Local (sem LLM)
===============================================================
Substituto de debate_strategies.py (146 chamadas de reasoning via LLM)
para cálculo de equilíbrios de Nash, Stackelberg, Shapley e
análise de estratégias multi-agente.

Usa nashpy + implementações locais determinísticas.

Uso:
    from skills.tooling.game_theory_local import GameTheoryLocal
    gt = GameTheoryLocal()
    nash = gt.nash_equilibrium(payoff_matrix_a, payoff_matrix_b)
    shapley = gt.shapley_value(coalition_values, player_count)
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import math

import numpy as np

try:
    import nashpy as nash

    HAS_NASHPY = True
except ImportError:
    HAS_NASHPY = False


class GameTheoryLocal:
    """
    Motor de teoria dos jogos determinístico.
    Substitui chamadas LLM para análise de estratégias multi-agente.

    Capacidades:
    - Equilíbrio de Nash (2 jogadores, soma zero e não-zero)
    - Equilíbrio de Stackelberg (líder-seguidor)
    - Valor de Shapley (contribuição de cada agente)
    - Pareto-optimalidade
    - Matriz de payoff entre agentes
    """

    def __init__(self):
        self.stats = {
            "nash_calls": 0,
            "stackelberg_calls": 0,
            "shapley_calls": 0,
            "pareto_calls": 0,
            "avg_ms": 0.0,
        }

    def _update_stats(self, key: str, elapsed_ms: float):
        self.stats[key] += 1
        total_calls = sum(
            self.stats[k] for k in ["nash_calls", "stackelberg_calls",
                                     "shapley_calls", "pareto_calls"]
        )
        self.stats["avg_ms"] = (
            (self.stats["avg_ms"] * (total_calls - 1) + elapsed_ms) / total_calls
        )

    # ─── Equilíbrio de Nash ──────────────────────────────────

    def nash_equilibrium(
        self,
        payoff_matrix_a: List[List[float]],
        payoff_matrix_b: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        """
        Calcula equilíbrio(s) de Nash para jogos de 2 jogadores.

        Args:
            payoff_matrix_a: payoff do jogador A (linhas = ações A, cols = ações B)
            payoff_matrix_b: payoff do jogador B.
                             Se None, assume jogo de soma zero (-payoff_matrix_a)

        Returns:
            Dict com equilíbrios, estratégias mistas, suporte
        """
        start = time.time()
        A = np.array(payoff_matrix_a, dtype=float)

        if payoff_matrix_b is None:
            # Soma zero
            B = -A
        else:
            B = np.array(payoff_matrix_b, dtype=float)

        result: Dict[str, Any] = {
            "type": "nash",
            "num_actions_a": A.shape[0],
            "num_actions_b": A.shape[1],
            "equilibria": [],
            "has_nash": False,
        }

        if HAS_NASHPY:
            try:
                game = nash.Game(A, B)
                equilibria = list(game.support_enumeration())

                # nashpy retorna gerador, precisamos iterar
                eq_list = []
                for eq in equilibria:
                    eq_dict = {
                        "strategy_a": [round(float(x), 4) for x in eq[0]],
                        "strategy_b": [round(float(x), 4) for x in eq[1]],
                    }
                    # Calcular payoff esperado
                    payoff_a = float(np.sum(A * np.outer(eq[0], eq[1])))
                    payoff_b = float(np.sum(B * np.outer(eq[0], eq[1])))
                    eq_dict["expected_payoff_a"] = round(payoff_a, 4)
                    eq_dict["expected_payoff_b"] = round(payoff_b, 4)
                    eq_list.append(eq_dict)

                result["equilibria"] = eq_list
                result["has_nash"] = len(eq_list) > 0
                result["num_equilibria"] = len(eq_list)

                # Melhor resposta
                if len(eq_list) > 0:
                    best = max(
                        eq_list,
                        key=lambda e: e["expected_payoff_a"] + e["expected_payoff_b"],
                    )
                    result["recommended"] = best

            except Exception as exc:
                result["error"] = str(exc)
        else:
            # Fallback: melhor resposta pura
            result["note"] = "nashpy não instalado — usando busca de estratégia pura"
            row_max = A.max(axis=1)
            col_max = B.max(axis=0)
            for i in range(A.shape[0]):
                for j in range(A.shape[1]):
                    if A[i, j] == row_max[i] and B[i, j] == col_max[j]:
                        result["equilibria"].append({
                            "pure_strategy": (i, j),
                            "payoff_a": float(A[i, j]),
                            "payoff_b": float(B[i, j]),
                        })
            result["has_nash"] = len(result["equilibria"]) > 0

        elapsed = (time.time() - start) * 1000
        self._update_stats("nash_calls", elapsed)
        result["elapsed_ms"] = round(elapsed, 2)
        return result

    # ─── Stackelberg ─────────────────────────────────────────

    def stackelberg_equilibrium(
        self,
        cost_leader: List[float],
        reaction_follower: List[float],
    ) -> Dict[str, Any]:
        """
        Equilíbrio de Stackelberg líder-seguidor.

        Args:
            cost_leader: custos do líder para cada ação
            reaction_follower: melhor resposta do seguidor para cada ação do líder

        Returns:
            Dict com estratégia ótima do líder e reação do seguidor
        """
        start = time.time()
        result: Dict[str, Any] = {"type": "stackelberg"}

        try:
            # Líder escolhe ação que minimiza seu custo,
            # antecipando a reação do seguidor
            leader_costs = np.array(cost_leader)
            follower_reaction = np.array(reaction_follower)

            # Payoff do líder = -custo (assumindo minimização de custo)
            leader_payoffs = -leader_costs + follower_reaction

            best_action = int(np.argmax(leader_payoffs))
            result["leader_optimal_action"] = best_action
            result["leader_payoff"] = float(leader_payoffs[best_action])
            result["follower_reaction"] = float(follower_reaction[best_action])
            result["leader_cost"] = float(leader_costs[best_action])

        except Exception as exc:
            result["error"] = str(exc)

        elapsed = (time.time() - start) * 1000
        self._update_stats("stackelberg_calls", elapsed)
        result["elapsed_ms"] = round(elapsed, 2)
        return result

    # ─── Shapley Value ───────────────────────────────────────

    def shapley_value(
        self,
        coalition_values: Dict[str, float],
        players: List[str],
    ) -> Dict[str, Any]:
        """
        Calcula o valor de Shapley para cada jogador.

        Args:
            coalition_values: dict mapeando frozenset de jogadores → valor da coalizão
            players: lista de nomes dos jogadores

        Returns:
            Dict com valor de Shapley de cada jogador
        """
        start = time.time()
        result: Dict[str, Any] = {"type": "shapley", "players": players}

        try:
            n = len(players)
            shapley = {p: 0.0 for p in players}

            # Para cada jogador i
            for i, player_i in enumerate(players):
                # Para cada subconjunto S que não contém i
                for r in range(n):
                    for subset_idx in range(1 << n):
                        if (subset_idx >> i) & 1:
                            continue  # S não pode conter i

                        S = frozenset(
                            players[j] for j in range(n)
                            if (subset_idx >> j) & 1
                        )
                        S_plus_i = frozenset(list(S) + [player_i])

                        val_S = coalition_values.get(S, 0.0)
                        val_S_plus_i = coalition_values.get(S_plus_i, 0.0)

                        # Fator de ponderação: |S|! * (n-|S|-1)! / n!
                        s = len(S)
                        weight = (math.factorial(s) *
                                  math.factorial(n - s - 1) /
                                  math.factorial(n))

                        shapley[player_i] += weight * (val_S_plus_i - val_S)

            result["shapley_values"] = {
                p: round(v, 4) for p, v in sorted(
                    shapley.items(), key=lambda x: -x[1]
                )
            }
            result["total_value"] = round(sum(shapley.values()), 4)

        except Exception as exc:
            result["error"] = str(exc)

        elapsed = (time.time() - start) * 1000
        self._update_stats("shapley_calls", elapsed)
        result["elapsed_ms"] = round(elapsed, 2)
        return result

    # ─── Pareto ──────────────────────────────────────────────

    def pareto_frontier(
        self,
        payoffs: List[Tuple[float, float]],
    ) -> Dict[str, Any]:
        """
        Encontra a fronteira de Pareto (trade-offs multi-agente).

        Args:
            payoffs: lista de (payoff_agente1, payoff_agente2)

        Returns:
            Dict com pontos Pareto-ótimos e análise
        """
        start = time.time()
        result: Dict[str, Any] = {"type": "pareto", "num_points": len(payoffs)}

        try:
            pareto_points = []
            for i, (a1_i, a2_i) in enumerate(payoffs):
                dominated = False
                for j, (a1_j, a2_j) in enumerate(payoffs):
                    if i == j:
                        continue
                    # j domina i se j é >= i em todos e > i em pelo menos um
                    if a1_j >= a1_i and a2_j >= a2_i and (
                        a1_j > a1_i or a2_j > a2_i
                    ):
                        dominated = True
                        break
                if not dominated:
                    pareto_points.append({
                        "point": i,
                        "payoffs": [float(a1_i), float(a2_i)],
                    })

            result["pareto_frontier"] = pareto_points
            result["pareto_count"] = len(pareto_points)
            result["pareto_ratio"] = round(
                len(pareto_points) / len(payoffs), 3
            ) if payoffs else 0

        except Exception as exc:
            result["error"] = str(exc)

        elapsed = (time.time() - start) * 1000
        self._update_stats("pareto_calls", elapsed)
        result["elapsed_ms"] = round(elapsed, 2)
        return result


# Singleton
_default_gt: Optional[GameTheoryLocal] = None


def get_gametheory() -> GameTheoryLocal:
    global _default_gt
    if _default_gt is None:
        _default_gt = GameTheoryLocal()
    return _default_gt


# ─── Teste ───────────────────────────────────────────────────

if __name__ == "__main__":
    gt = GameTheoryLocal()

    # Teste 1: Nash Equilibrium (Dilema do Prisioneiro)
    print("=== Nash: Dilema do Prisioneiro ===")
    A = [[-1, -3], [0, -2]]  # Cooperar/Defeccionar
    B = [[-1, 0], [-3, -2]]
    nash_result = gt.nash_equilibrium(A, B)
    print(f"  Equilíbrios: {nash_result['num_equilibria']}")
    for eq in nash_result.get("equilibria", []):
        print(f"    A: {eq['strategy_a']} | B: {eq['strategy_b']}")
        print(f"    Payoff: A={eq['expected_payoff_a']}, B={eq['expected_payoff_b']}")

    # Teste 2: Shapley Value
    print("\n=== Shapley: Contribuição de Agentes ===")
    players = ["scanner", "orchestrator", "writer"]
    coalitions = {
        frozenset(): 0.0,
        frozenset(["scanner"]): 10.0,
        frozenset(["orchestrator"]): 20.0,
        frozenset(["writer"]): 15.0,
        frozenset(["scanner", "orchestrator"]): 40.0,
        frozenset(["scanner", "writer"]): 35.0,
        frozenset(["orchestrator", "writer"]): 50.0,
        frozenset(["scanner", "orchestrator", "writer"]): 100.0,
    }
    shapley_result = gt.shapley_value(coalitions, players)
    for p, v in shapley_result["shapley_values"].items():
        print(f"  {p}: {v}")

    # Teste 3: Pareto
    print("\n=== Pareto: Trade-offs ===")
    payoffs = [(3, 1), (2, 2), (1, 3), (0, 0), (2.5, 1.5)]
    pareto = gt.pareto_frontier(payoffs)
    print(f"  Fronteira: {pareto['pareto_count']} de {pareto['num_points']} pontos")

    # Teste 4: Stackelberg
    print("\n=== Stackelberg: Líder-Seguidor ===")
    stackelberg = gt.stackelberg_equilibrium(
        cost_leader=[5, 3, 8],
        reaction_follower=[1, 0.5, 2],
    )
    print(f"  Líder ação ótima: {stackelberg['leader_optimal_action']}")
    print(f"  Payoff líder: {stackelberg['leader_payoff']}")

    print(f"\nStats: {gt.stats}")
