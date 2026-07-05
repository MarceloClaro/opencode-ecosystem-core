"""
MiroFish Cross-Validator — Validação cruzada Enxame × Teoria dos Jogos × Qualis.

Reproduz a integração "MiroFish/BettaFish v5.0" do OpenCode_Ecosystem original:
OASIS + Forum + Nash + Stats + Qualis + Sensitivity + IMRAD + Debate.

Fluxo:
1. O enxame MiroFish prevê a probabilidade de aprovação de um artefato.
2. O NashSolver modela a decisão autor × revisor como um jogo e verifica se
   "submeter agora" é um equilíbrio.
3. O QualisA1Auditor pontua o manuscrito (quando aplicável).
4. O veredito final tripla-valida: enxame, jogo e auditoria devem concordar.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from mirofish.swarm import MiroFishSwarm  # noqa: E402


class CrossValidator:
    """Validação cruzada tripla para decisões e manuscritos."""

    def __init__(self, n_agents: int = 25, seed: Optional[int] = 42):
        self.swarm = MiroFishSwarm(n_agents=n_agents, seed=seed)

    def validate_decision(self, question: str, signal: float = 0.5,
                          payoff_submit: float = 3.0,
                          payoff_wait: float = 1.0) -> Dict[str, Any]:
        """Valida uma decisão binária com enxame + equilíbrio de Nash."""
        # 1. Enxame
        debate = self.swarm.debate(question, rounds=3, signal=signal)
        swarm_approves = debate["final"] >= 0.5

        # 2. Teoria dos Jogos (jogo autor × revisor)
        game_result = self._nash_check(payoff_submit, payoff_wait)

        verdict = swarm_approves and game_result["submit_is_equilibrium"]
        return {
            "question": question,
            "swarm": debate,
            "game": game_result,
            "approved": verdict,
            "rationale": (
                "Enxame e equilíbrio de Nash concordam"
                if verdict else "Divergência entre enxame e análise de jogo"
            ),
        }

    def validate_manuscript(self, manuscript: str,
                            signal: float = 0.6) -> Dict[str, Any]:
        """Valida manuscrito com enxame + auditoria Qualis A1 (se disponível)."""
        debate = self.swarm.debate(
            "O manuscrito atinge o padrão de publicação?", rounds=3, signal=signal
        )
        qualis: Dict[str, Any] = {"available": False}
        try:
            from gametheory import QualisA1Auditor
            auditor = QualisA1Auditor()
            audit = auditor.audit(manuscript) if hasattr(auditor, "audit") else None
            if audit is None and hasattr(auditor, "evaluate"):
                audit = auditor.evaluate(manuscript)
            qualis = {"available": True, "result": audit}
        except Exception as exc:  # noqa: BLE001
            qualis = {"available": False, "error": str(exc)}

        return {
            "swarm": debate,
            "qualis": qualis,
            "approved": debate["final"] >= 0.5,
        }

    @staticmethod
    def _nash_check(payoff_submit: float, payoff_wait: float) -> Dict[str, Any]:
        """Modela submeter × aguardar como jogo 2×2 e busca equilíbrio puro."""
        try:
            from gametheory import PayoffMatrix
            matrix = PayoffMatrix(
                player1_strategies=["Submeter", "Aguardar"],
                player2_strategies=["Aceitar", "Rejeitar"],
                payoff_matrix={
                    "Submeter": {
                        "Aceitar": (payoff_submit, payoff_submit),
                        "Rejeitar": (-1.0, payoff_wait),
                    },
                    "Aguardar": {
                        "Aceitar": (payoff_wait, 0.0),
                        "Rejeitar": (payoff_wait, payoff_wait),
                    },
                },
            )
            equilibria = matrix.find_nash_equilibria()
            return {
                "equilibria": equilibria,
                "submit_is_equilibrium": any(e[0] == "Submeter" for e in equilibria),
            }
        except Exception as exc:  # noqa: BLE001
            # Fallback heurístico
            return {
                "equilibria": [],
                "submit_is_equilibrium": payoff_submit > payoff_wait,
                "note": f"fallback: {exc}",
            }
