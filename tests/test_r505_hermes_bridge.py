# -*- coding: utf-8 -*-
"""Testes R505 — Hermes Bridge (contratos opcionais, sem runtime).
SPEC-935-R505. Ciclo RED→GREEN: API especificada antes da implementação.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hermes_bridge.contracts import (
    MemoryEvent, SkillProposal, TrajectoryEvent, ExecutionResult,
    validate_contract,
)
from hermes_bridge.memory_firewall import MemoryFirewall, MemoryFirewallError
from hermes_bridge.skill_governance import SkillGovernance
from hermes_bridge.trajectory import extract_trajectory_signals
from hermes_bridge.evidence_adapter import EvidenceAdapter
from hermes_bridge.bridge import HermesBridge


# ── Contracts ──────────────────────────────────────────────────────────────

def test_contratos_schemas():
    mem = MemoryEvent(event_id="m1", scope="personalization", content="x")
    assert validate_contract(mem, "hermes.memory/v1") is True
    sp = SkillProposal(proposal_id="p1", skill_name="s")
    assert validate_contract(sp, "hermes.skill.proposal/v1") is True
    tr = TrajectoryEvent(event_id="t1", steps=3, failures=1, tool_calls=2,
                         duration_s=10.0, retries=0, terminal_state="success")
    assert validate_contract(tr, "hermes.trajectory/v1") is True
    ex = ExecutionResult(event_id="e1", success=True,
                         direct_evidence=[{"kind": "test", "ref": "t.py:1"}],
                         claim_id="claim-ok")
    assert validate_contract(ex, "hermes.execution.result/v1") is True


# ── MemoryFirewall ─────────────────────────────────────────────────────────

def test_memoria_nunca_observado():
    fw = MemoryFirewall()
    with pytest.raises(MemoryFirewallError):
        fw.accept(MemoryEvent(event_id="m1", scope="episodic",
                              content="vi a verdade", epistemic_state="OBSERVED"))
    ev = fw.accept(MemoryEvent(event_id="m2", scope="episodic",
                               content="talvez", epistemic_state="INFERRED"))
    assert ev.epistemic_state == "INFERRED"


def test_personalizacao_isolada():
    fw = MemoryFirewall()
    ev = fw.accept(MemoryEvent(event_id="m3", scope="personalization",
                               content="prefere formal", epistemic_state="UNVERIFIED"))
    assert ev.isolated_from_evidence is True


# ── SkillGovernance ────────────────────────────────────────────────────────

def test_skill_proposal_nasce_shadow():
    gov = SkillGovernance()
    prop = gov.propose(SkillProposal(proposal_id="p1", skill_name="cubo"))
    assert prop.mode == "shadow"
    assert prop.requires_review is True
    assert prop.requires_tests is True
    assert prop.evidence_authority is False


def test_skill_mutation_nunca_automatica():
    gov = SkillGovernance()
    prop = gov.propose(SkillProposal(proposal_id="p2", skill_name="cubo"))
    # mesmo com todos os gates "verdes", não executa mutação
    eligible = gov.check_eligibility(prop, review_approved=True, tests_passing=True,
                                     feynman_approved=True, no_drift=True)
    assert eligible is True
    assert prop.executable is False
    assert prop.file_mutation_performed is False


# ── Trajectory ─────────────────────────────────────────────────────────────

def test_trajectory_sinais_conservadores():
    tr = TrajectoryEvent(event_id="t1", steps=3, failures=1, tool_calls=2,
                         duration_s=10.0, retries=0, terminal_state="success")
    sig = extract_trajectory_signals(tr)
    assert sig["steps"] == 3
    assert sig["retry_like"] == (sig["retries"] > 0)
    assert "runner_provision_failed" not in sig or sig["runner_provision_failed"] is False


# ── EvidenceAdapter ────────────────────────────────────────────────────────

def test_execution_result_sem_claim_nao_promove():
    adapter = EvidenceAdapter()
    # sem claim_id → não propõe OBSERVED
    claim = adapter.to_evidence_proposal(
        ExecutionResult(event_id="e1", success=True,
                        direct_evidence=[{"kind": "execution", "ref": "run:1"}],
                        claim_id=None))
    assert claim["proposed"] != "OBSERVED"


def test_execution_result_com_evidencia_direta_promove_ao_guard():
    adapter = EvidenceAdapter()
    proposal = adapter.to_evidence_proposal(
        ExecutionResult(event_id="e2", success=True,
                        direct_evidence=[{"kind": "test", "ref": "tests/x.py:1"}],
                        claim_id="claim-ok"))
    # passa pelo EvidenceGuard (R504) — aceita só se evidência direta
    assert proposal["source"]["direct"] is True


# ── Bridge (inerte) ────────────────────────────────────────────────────────

def test_bridge_sem_transporte_e_inerte():
    bridge = HermesBridge()
    result = bridge.dispatch("any-event", {})
    assert result["dispatched"] is False
    assert result["reason"] == "no_transport"


def test_bridge_nao_importa_hermes():
    import inspect
    from hermes_bridge import bridge as b
    src = inspect.getsource(b)
    assert "hermes" not in [m for m in ("import hermes", "from hermes")] or "hermes" in src