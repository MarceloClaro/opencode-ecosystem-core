# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R372 — Protocolo de Pré-registro."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mci.preregistration_protocol import (  # noqa: E402
    ContractError,
    register_protocol,
    verify_protocol,
)
from mci.experiment_designer import design_experiment  # noqa: E402


def _protocol(**overrides):
    base = dict(
        hypothesis="Retirantes preservados aumentam aceitação do leitor.",
        method="Comparação Welch-t entre grupo controle e grupo experimental.",
        falsification_criterion="p >= 0.05 rejeita a hipótese.",
        alpha=0.05,
    )
    base.update(overrides)
    return register_protocol(**base)


# ═══════════════════════════════════════════════════════════════════════
# 1. register_protocol — contrato fail-closed
# ═══════════════════════════════════════════════════════════════════════

class TestRegisterProtocol:
    def test_registro_valido(self):
        p = _protocol()
        assert p["protocol_id"].startswith("prereg-")
        assert "registered_at" in p

    def test_campos_vazios_falham(self):
        with pytest.raises(ContractError):
            register_protocol("", "método", "critério", 0.05)
        with pytest.raises(ContractError):
            register_protocol("hipótese", "", "critério", 0.05)
        with pytest.raises(ContractError):
            register_protocol("hipótese", "método", "", 0.05)

    def test_alpha_fora_do_intervalo_falha(self):
        with pytest.raises(ContractError):
            register_protocol("h", "m", "c", 0.0)
        with pytest.raises(ContractError):
            register_protocol("h", "m", "c", 1.0)
        with pytest.raises(ContractError):
            register_protocol("h", "m", "c", -0.1)

    def test_protocol_id_deterministico_para_mesmo_conteudo(self):
        p1 = register_protocol("Hipótese X", "Método Y", "Critério Z", 0.05)
        p2 = register_protocol("hipótese x", " Método Y ", "Critério Z", 0.05)
        assert p1["protocol_id"] == p2["protocol_id"]

    def test_protocol_id_diferente_para_conteudo_diferente(self):
        p1 = register_protocol("Hipótese X", "Método Y", "Critério Z", 0.05)
        p2 = register_protocol("Hipótese diferente", "Método Y", "Critério Z", 0.05)
        assert p1["protocol_id"] != p2["protocol_id"]


# ═══════════════════════════════════════════════════════════════════════
# 2. verify_protocol — desvio bloqueia
# ═══════════════════════════════════════════════════════════════════════

class TestVerifyProtocol:
    def test_protocolo_honrado(self):
        p = _protocol()
        result = verify_protocol(
            p,
            actual_hypothesis=p["hypothesis"],
            actual_method=p["method"],
            actual_alpha=p["alpha"],
        )
        assert result["honored"] is True
        assert result["findings"] == []
        assert result["human_gate"] == "recommended"

    def test_normalizacao_case_espacos_nao_conta_como_desvio(self):
        p = _protocol()
        result = verify_protocol(
            p,
            actual_hypothesis=f"  {p['hypothesis'].upper()}  ",
            actual_method=p["method"],
            actual_alpha=p["alpha"],
        )
        assert result["honored"] is True

    def test_hipotese_trocada_e_desvio(self):
        p = _protocol()
        result = verify_protocol(
            p,
            actual_hypothesis="Uma hipótese completamente diferente descoberta depois dos dados.",
            actual_method=p["method"],
            actual_alpha=p["alpha"],
        )
        assert result["honored"] is False
        codes = [f["code"] for f in result["findings"]]
        assert "PROTOCOL_DEVIATION" in codes
        deviation = [f for f in result["findings"] if f["code"] == "PROTOCOL_DEVIATION"][0]
        assert "hypothesis" in deviation["detail"].lower()
        assert result["human_gate"] == "required"

    def test_alpha_trocado_e_desvio(self):
        p = _protocol()
        result = verify_protocol(
            p, actual_hypothesis=p["hypothesis"], actual_method=p["method"],
            actual_alpha=0.10,
        )
        assert result["honored"] is False
        assert any("alpha" in f["detail"].lower() for f in result["findings"])

    def test_metodo_trocado_e_desvio(self):
        p = _protocol()
        result = verify_protocol(
            p, actual_hypothesis=p["hypothesis"], actual_method="Método totalmente novo",
            actual_alpha=p["alpha"],
        )
        assert result["honored"] is False
        assert any("method" in f["detail"].lower() for f in result["findings"])

    def test_protocolo_invalido_falha(self):
        with pytest.raises(ContractError):
            verify_protocol({"nao": "e um protocolo"}, "h", "m", 0.05)

    def test_disclaimer_presente(self):
        p = _protocol()
        result = verify_protocol(p, p["hypothesis"], p["method"], p["alpha"])
        assert "disclaimer" in result and len(result["disclaimer"]) > 20


# ═══════════════════════════════════════════════════════════════════════
# 3. Correção do bug em design_experiment
# ═══════════════════════════════════════════════════════════════════════

class TestCorrecaoDesignExperiment:
    def _claim(self):
        return {"experimental_design": {}, "limitations": [], "domain": "ml",
                "hypothesis": "x", "sesoi": 0.3}

    def test_sem_protocolo_pre_registered_e_false(self):
        """Regressão do bug: antes, pre_registered=True sem NADA declarado."""
        result = design_experiment(self._claim(), {})
        assert result["experimental_design"]["pre_registered"] is False
        assert any(
            "pré-registro" in lim.lower() or "pre-registro" in lim.lower()
            for lim in result["limitations"]
        )

    def test_com_protocolo_honrado_pre_registered_e_true(self):
        p = _protocol()
        claim = self._claim()
        context = {
            "registered_protocol": p,
            "actual_hypothesis": p["hypothesis"],
            "actual_method": p["method"],
            "actual_alpha": p["alpha"],
        }
        result = design_experiment(claim, context)
        assert result["experimental_design"]["pre_registered"] is True
        assert "protocol_verification" in result["experimental_design"]

    def test_com_protocolo_violado_pre_registered_e_false(self):
        p = _protocol()
        claim = self._claim()
        context = {
            "registered_protocol": p,
            "actual_hypothesis": "hipótese trocada após ver os dados",
            "actual_method": p["method"],
            "actual_alpha": p["alpha"],
        }
        result = design_experiment(claim, context)
        assert result["experimental_design"]["pre_registered"] is False


# ═══════════════════════════════════════════════════════════════════════
# 4. Integração com o R103 (ReviewLedger)
# ═══════════════════════════════════════════════════════════════════════

class TestIntegracaoR103:
    def test_claim_com_protocolo_honrado_e_verificada(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim("Alegação pré-registrada.", section="methods")
        p = _protocol()
        orch = OrchestratorReviewer()
        result = orch.verify_preregistered_claim(
            claim.id, p, p["hypothesis"], p["method"], p["alpha"], ledger
        )
        assert result["honored"] is True
        assert ledger.claims[claim.id].verified is True

    def test_claim_com_desvio_fica_pendente(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim("Alegação suspeita de HARKing.", section="methods")
        p = _protocol()
        orch = OrchestratorReviewer()
        result = orch.verify_preregistered_claim(
            claim.id, p, "hipótese reformulada depois dos resultados",
            p["method"], p["alpha"], ledger,
        )
        assert result["honored"] is False
        assert ledger.claims[claim.id].verified is False
        pending_ids = {item["claim_id"] for item in ledger.get_pending_verifications()}
        assert claim.id in pending_ids
