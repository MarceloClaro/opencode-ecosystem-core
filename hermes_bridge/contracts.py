# -*- coding: utf-8 -*-
"""Hermes Bridge — contratos v1 (SPEC-935-R505).

Schemas de fronteira com o runtime Hermes (Nous Research, autoria externa
preservada). Contratos são OPTIONAIS; a bridge permanece inerte sem
transporte configurado e não transfere autoridade epistemológica.
Contratos (v1):
  hermes.memory/v1, hermes.skill.proposal/v1,
  hermes.trajectory/v1, hermes.execution.result/v1
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

CONTRACTS = {
    "hermes.memory/v1": "MemoryEvent",
    "hermes.skill.proposal/v1": "SkillProposal",
    "hermes.trajectory/v1": "TrajectoryEvent",
    "hermes.execution.result/v1": "ExecutionResult",
}


@dataclass
class MemoryEvent:
    event_id: str
    scope: str  # episodic | personalization | procedural
    content: str
    epistemic_state: str = "UNVERIFIED"
    confidence: Optional[float] = None


@dataclass
class SkillProposal:
    proposal_id: str
    skill_name: str
    mode: str = "shadow"
    requires_review: bool = True
    requires_tests: bool = True
    evidence_authority: bool = False
    executable: bool = False
    file_mutation_performed: bool = False


@dataclass
class TrajectoryEvent:
    event_id: str
    steps: int
    failures: int
    tool_calls: int
    duration_s: float
    retries: int = 0
    terminal_state: str = "success"


@dataclass
class ExecutionResult:
    event_id: str
    success: bool
    direct_evidence: List[Dict[str, Any]] = field(default_factory=list)
    claim_id: Optional[str] = None
    logs: List[str] = field(default_factory=list)


def validate_contract(obj: Any, schema: str) -> bool:
    """Valida se o objeto corresponde ao contrato declarado."""
    expected = CONTRACTS.get(schema)
    if expected is None:
        return False
    return isinstance(obj, globals().get(expected, type(None)))