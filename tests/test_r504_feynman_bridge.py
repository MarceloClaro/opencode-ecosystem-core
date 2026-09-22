# -*- coding: utf-8 -*-
"""Testes R504 — ReversaFeynman Bridge (Evidence & Calibration Layer).
SPEC-935-R504. Ciclo RED→GREEN: testes criados antes da API existir.
"""
import json
import math
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reversa_feynman.evidence_guard import (
    EvidenceGuard, EPISTEMIC_STATES, OBSERVED, INFERRED, UNVERIFIED, BLOCKED,
)
from reversa_feynman.feynman_gates import FeynmanGates, TeachbackResult
from reversa_feynman.offline_eval import (
    OfflinePolicyEvaluator, DecisionRecord, DriftDetector, PromotionReadiness,
)
from reversa_feynman.ledger import AuditLedger
from reversa_feynman.router_calibration import CalibratedRoutingAdvisor


# ── EvidenceGuard ──────────────────────────────────────────────────────────

def test_guard_rejeita_policy_ou_memoria_como_observado():
    guard = EvidenceGuard()
    with pytest.raises(ValueError):
        guard.apply_evidence_proposal(
            {"id": "claim-1", "epistemic_state": INFERRED},
            {"proposed": OBSERVED,
             "source": {"kind": "learned-policy", "direct": False, "ref": "policy:acme"}},
        )
    with pytest.raises(ValueError):
        guard.apply_evidence_proposal(
            {"id": "claim-2", "epistemic_state": UNVERIFIED},
            {"proposed": OBSERVED,
             "source": {"kind": "memory", "direct": False, "ref": "hermes:memory:abc"}},
        )
    # confiança de skill também não pode
    with pytest.raises(ValueError):
        guard.apply_evidence_proposal(
            {"id": "claim-3", "epistemic_state": INFERRED},
            {"proposed": OBSERVED,
             "source": {"kind": "skill-confidence", "direct": False, "ref": "skill:x"}},
        )


def test_guard_aceita_evidencia_direta_rastreavel():
    guard = EvidenceGuard()
    claim = guard.apply_evidence_proposal(
        {"id": "claim-ok", "epistemic_state": INFERRED},
        {"proposed": OBSERVED,
         "source": {"kind": "test", "direct": True, "ref": "tests/test_r504_feynman_bridge.py:1"}},
    )
    assert claim["epistemic_state"] == OBSERVED
    assert claim["source"]["ref"].startswith("tests/")


def test_guard_estados_validos():
    assert EPISTEMIC_STATES == {OBSERVED, INFERRED, UNVERIFIED, BLOCKED}


# ── FeynmanGates ───────────────────────────────────────────────────────────

def test_feynman_score_zero_sem_evidencia():
    gates = FeynmanGates()
    res = gates.score(claim={"name": "x", "evidence": []})
    assert 0 <= res["feg_01_06_score"] <= 12
    assert res["feg_01_06_score"] == 0


def test_feynman_score_nao_zero_com_evidencia_e_mecanismo():
    gates = FeynmanGates()
    claim = {
        "name": "solucionador deterministico",
        "mechanism": "enumera 2^k e testa a inequacao; corta no primeiro contraexemplo",
        "evidence": [{"kind": "execution", "ref": "research/imo_study/benchmark_9x3.json"}],
        "test_oracle": "tests/test_r499_imo_real_solver.py",
        "observed_inferred_separated": True,
    }
    res = gates.score(claim=claim)
    assert res["feg_01_06_score"] > 0


def test_feynman_teachback_fora_do_score():
    gates = FeynmanGates()
    tb = gates.teachback(human_text="explica o mecanismo", transfer="variante")
    assert isinstance(tb, TeachbackResult)
    assert tb.status in ("HUMAN-VALIDATED", "HUMAN-PARTIAL", "HUMAN-CONFLICT")
    # FEG-07 não entra no score base
    assert tb.status == "HUMAN-VALIDATED"


# ── OfflinePolicyEvaluator ─────────────────────────────────────────────────

def _mk_record(decided_at, confidence, outcome, shadow_match=True,
               shadow_action="a", executed_action="a"):
    return DecisionRecord(
        event_id=f"ev-{decided_at}",
        decided_at=decided_at,
        confidence=confidence,
        outcome=outcome,
        shadow_action=shadow_action,
        executed_action=executed_action,
        shadow_match=shadow_match,
    )


def test_decide_observe_sem_lookahead():
    ev = OfflinePolicyEvaluator(seed=42)
    ev.record(_mk_record(1, 0.9, 1))
    ev.record(_mk_record(2, 0.7, 1))
    # decide() para o evento 3 não pode enxergar outcome do evento 3
    decision = ev.decide({"stage": "x"}, event_id="ev-3")
    assert decision["mode"] == "shadow"
    assert ev._hist_len() == 2  # histórico ainda não tem o evento 3
    ev.observe({"stage": "x"}, {"event_id": "ev-3"}, outcome=0)
    assert ev._hist_len() == 3


def test_holdout_temporal_e_brier_ece():
    ev = OfflinePolicyEvaluator(seed=7, train_fraction=0.70)
    for i in range(1, 11):
        conf = 0.9 if i % 2 else 0.5
        outcome = 1 if conf >= 0.7 else 0
        ev.record(_mk_record(i, conf, outcome))
    report = ev.evaluate()
    assert report["n_train"] + report["n_holdout"] == 10
    assert report["n_holdout"] >= 2
    assert 0.0 <= report["brier_shadow_matched"] <= 1.0
    assert 0.0 <= report["ece_shadow_matched"] <= 1.0
    # Brier conhecido: pred 0.9 vs out 1 => 0.01; 0.5 vs 0 => 0.25 => média binomial ~0.13 no treino
    assert report["brier_shadow_matched"] > 0.0


def test_bootstrap_ic95_deterministico():
    ev1 = OfflinePolicyEvaluator(seed=123)
    ev2 = OfflinePolicyEvaluator(seed=123)
    recs = [_mk_record(i, 0.8, 1 if i % 3 else 0) for i in range(1, 40)]
    for ev in (ev1, ev2):
        for r in recs:
            ev.record(r)
    r1 = ev1.evaluate(bootstrap_seed=99)
    r2 = ev2.evaluate(bootstrap_seed=99)
    assert r1["delta_ic95"] == r2["delta_ic95"]
    assert r1["delta_ic95"][0] <= r1["delta_ic95"][1]


def test_contrafactual_nao_inventa_outcome():
    ev = OfflinePolicyEvaluator(seed=1)
    # shadow_action diferente de executed_action → outcome do shadow não observado
    for i in range(1, 6):
        ev.record(_mk_record(i, 0.8, 1, shadow_match=False,
                             shadow_action="b", executed_action="a"))
    report = ev.evaluate()
    # todos não-matched → matched-only sample vazio → brier/ece None, sem invento
    assert report["brier_shadow_matched"] is None
    assert report["n_shadow_matched"] == 0


def test_drift_detector():
    dd = DriftDetector(window_ref=6, window_recent=6)
    # estável: mesma acurácia nas duas janelas
    for i in range(18):
        dd.add(reward=0.8 if i < 12 else 0.79, confidence=0.9, observed=True)
    assert dd.state() == "stable"
    dd2 = DriftDetector(window_ref=6, window_recent=6)
    for i in range(18):
        dd2.add(reward=0.9 if i < 12 else 0.2, confidence=0.95 if i < 12 else 0.4,
                observed=True)
    assert dd2.state() == "drift"


def test_readiness_nunca_auto_ativa():
    ev = OfflinePolicyEvaluator(seed=3)
    # histórico pequeno → readiness blocked
    ev.record(_mk_record(1, 0.9, 1))
    readiness = ev.promotion_readiness()
    assert readiness.eligible == False
    assert readiness.auto_activate == False


def test_readiness_elegivel_so_pede_ativacao():
    ev = OfflinePolicyEvaluator(seed=3)
    for i in range(1, 45):
        conf = 0.9 if i % 4 else 0.5
        outcome = 1 if conf >= 0.7 else 0
        ev.record(_mk_record(i, conf, outcome))
    readiness = ev.promotion_readiness()
    if readiness.eligible:
        req = readiness.request_policy_activation(requester="test", reason="rd")
        assert req["auto_activate"] == False
        assert req["status"] == "activation_requested"
        assert req["requester"] == "test"


# ── AuditLedger ────────────────────────────────────────────────────────────

def test_ledger_integridade_e_dedupe():
    ledger = AuditLedger()
    l1 = ledger.append("decision", {"model": "mimo", "acc": 0.44})
    ledger.append("decision", {"model": "big-pickle", "acc": 0.11})
    l3 = ledger.append("decision", {"model": "mimo", "acc": 0.44})  # duplicado event payload
    assert l1 != l3  # timestamps/seq diferentes → hashes diferentes
    assert ledger.verify() is True
    # adulteração
    ledger._entries[0]["payload"]["acc"] = 0.99
    assert ledger.verify() is False
    assert ledger.dedupe_count("decision", {"model": "mimo", "acc": 0.44})


def test_ledger_export_jsonl(tmp_path):
    ledger = AuditLedger()
    ledger.append("test", {"ok": True})
    out = tmp_path / "ledger.jsonl"
    ledger.export_jsonl(str(out))
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["type"] == "test"


# ── CalibratedRoutingAdvisor ───────────────────────────────────────────────

def test_advisor_recomenda_reducao_de_score_r503():
    advisor = CalibratedRoutingAdvisor()
    catalog = [
        {"model_id": "opencode/mimo-v2.5-free", "score": 0.987, "outcomes_ok": 4,
         "outcomes_n": 9, "latency_s": 39.9},
        {"model_id": "opencode/big-pickle", "score": 0.923, "outcomes_ok": 1,
         "outcomes_n": 9, "latency_s": 31.2},
    ]
    advice = advisor.advise(catalog)
    # big-pickle: acurácia real 0.11 → recomendação forte de redução
    bp = next(a for a in advice if a["model_id"] == "opencode/big-pickle")
    mimo = next(a for a in advice if a["model_id"] == "opencode/mimo-v2.5-free")
    assert bp["recommended_score"] < mimo["recommended_score"]
    assert bp["calibrated_accuracy"] == pytest.approx(1 / 9, abs=1e-6)
    # recomendação não altera o catálogo sozinha
    assert bp["applied"] == False
    assert bp["requires_activation"] == True