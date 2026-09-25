# -*- coding: utf-8 -*-
"""Hermes Bridge — contratos opcionais de interoperabilidade (SPEC-935-R505).

Fronteira com o runtime Hermes (Nous Research, autoria externa preservada)
como contratos opcionais. Inerte sem transporte; nunca transfere autoridade
epistemológica ao runtime. Integra com o EvidenceGuard (R504).
"""
from hermes_bridge.contracts import (
    CONTRACTS, MemoryEvent, SkillProposal, TrajectoryEvent, ExecutionResult,
    validate_contract,
)
from hermes_bridge.memory_firewall import MemoryFirewall, MemoryFirewallError
from hermes_bridge.skill_governance import SkillGovernance
from hermes_bridge.trajectory import extract_trajectory_signals
from hermes_bridge.evidence_adapter import EvidenceAdapter
from hermes_bridge.bridge import HermesBridge

__all__ = [
    "CONTRACTS", "MemoryEvent", "SkillProposal", "TrajectoryEvent",
    "ExecutionResult", "validate_contract", "MemoryFirewall",
    "MemoryFirewallError", "SkillGovernance", "extract_trajectory_signals",
    "EvidenceAdapter", "HermesBridge",
]