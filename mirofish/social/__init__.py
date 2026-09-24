"""
MiroFish Social Simulation — pacote MIT (SPEC-976).

Integração por composição com o MiroFish-Offline (AGPL-3.0): nenhum código do
projeto original é copiado; contratos de dados e motor determinístico são
reimplementados em stdlib própria. O serviço externo real é acionado pelo
driver em integrations/mirofish_offline.py (fail-closed, opcional).
"""
from .contracts import (
    AgentActivityConfig,
    EventConfig,
    OasisAgentProfile,
    PlatformConfig,
    SimulationParameters,
    TimeSimulationConfig,
)
from .engine import SocialSimulationEngine, SocialSimulationEngine as SocialRunner
from .profiles import SimulationProfileGenerator
from .report import SocialReportGenerator, _summarize
from .editorial_profiles import (
    EDITORIAL_PROFILES,
    EditorialProfile,
    JOURNAL_ALIASES,
    JOURNAL_KEYS,
    get_profile,
    merge_weights,
    profile_summary,
)
from .banca import (
    BancaMember,
    BancaProfileGenerator,
    banca_verdict,
    banca_weighted_score,
    recommendation_from_score,
    summarize_banca,
    text_signals,
    adjust_bias_by_signal,
    CRITERIA,
    CRITERION_WEIGHTS,
    POSITIONS,
)

__all__ = [
    "AgentActivityConfig",
    "BancaMember",
    "BancaProfileGenerator",
    "CRITERIA",
    "CRITERION_WEIGHTS",
    "EDITORIAL_PROFILES",
    "EditorialProfile",
    "EventConfig",
    "JOURNAL_ALIASES",
    "JOURNAL_KEYS",
    "OasisAgentProfile",
    "PlatformConfig",
    "POSITIONS",
    "SimulationParameters",
    "SimulationProfileGenerator",
    "SocialReportGenerator",
    "SocialSimulationEngine",
    "SocialRunner",
    "TimeSimulationConfig",
    "adjust_bias_by_signal",
    "banca_verdict",
    "banca_weighted_score",
    "get_profile",
    "merge_weights",
    "profile_summary",
    "recommendation_from_score",
    "summarize_banca",
    "text_signals",
    "_summarize",
]