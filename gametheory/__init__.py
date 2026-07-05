"""
Game Theory & Debate — 38 tipos de raciocínio + Teoria dos Jogos.

Portado do OpenCode_Ecosystem (skills/agent-forum). Inclui:
- debate_strategies: 38 ReasoningType (lógica clássica, dialética, 10+ modelos
  de Teoria dos Jogos — Nash, Dilema do Prisioneiro, Soma Zero, Tit-for-Tat,
  Stackelberg, Barganha, Sinalização, Evolutiva, Bayesiana, Cooperativa/Shapley,
  Mechanism Design), PayoffMatrix com solver de equilíbrio de Nash puro,
  ShapleyValue e MetaReasoner (seleção dinâmica de estratégias por contexto).
- moderator: fórum de debate multiagente (Forum, ForumModerator, canais).
- phd_auditor: NashSolver, StatisticalRigor, QualisA1Auditor, SensitivityAnalyzer
  e IMRADFormatter para auditoria acadêmica com rigor de banca.

Referências: Nash (1950), Axelrod (1984), von Neumann (1928), Shapley (1953),
Harsanyi (1967), Maynard Smith (1982), Spence (1973), Kahneman & Tversky (1979).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from debate_strategies import (  # noqa: E402
    ReasoningType,
    PayoffMatrix,
    ShapleyValue,
    DebateStrategy,
    TitForTatStrategy,
    GenerousTitForTatStrategy,
    GrimTriggerStrategy,
    MetaReasoner,
)
from phd_auditor import (  # noqa: E402
    NashSolver,
    StatisticalRigor,
    QualisA1Auditor,
    SensitivityAnalyzer,
    IMRADFormatter,
)

__all__ = [
    "ReasoningType",
    "PayoffMatrix",
    "ShapleyValue",
    "DebateStrategy",
    "TitForTatStrategy",
    "GenerousTitForTatStrategy",
    "GrimTriggerStrategy",
    "MetaReasoner",
    "NashSolver",
    "StatisticalRigor",
    "QualisA1Auditor",
    "SensitivityAnalyzer",
    "IMRADFormatter",
]
