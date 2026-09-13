# -*- coding: utf-8 -*-
"""
Reversa Universal — engenharia reversa transversal (SPEC-935-R437/R471)
"""

from reversa_universal.engine import ReversaUniversalEngine, reversa_engine
from reversa_universal.bridge import ReversaBridge, reversa_bridge
from reversa_universal.skill_dispatch import (
    ReversaSkillDispatcher,
    SkillDispatchDecision,
    plan_skill_handoff,
)

__all__ = [
    "ReversaUniversalEngine",
    "reversa_engine",
    "ReversaBridge",
    "reversa_bridge",
    "ReversaSkillDispatcher",
    "SkillDispatchDecision",
    "plan_skill_handoff",
]
