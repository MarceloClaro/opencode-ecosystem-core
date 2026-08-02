# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R371 — Triangulação Multidisciplinar."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mci.multidisciplinary_triangulation import (  # noqa: E402
    ContractError,
    multidisciplinary_triangulation,
)


def _item(source, domain, stance):
    return {"source": source, "domain": domain, "stance": stance}


# ═══════════════════════════════════════════════════════════════════════
# 1. Contrato de entrada (fail-closed)
# ═══════════════════════════════════════════════════════════════════════

class TestContrato:
    def test_stance_invalido_falha(self):
        with pytest.raises(ContractError):
            multidisciplinary_triangulation("claim", [
                _item("doi:1", "medicina", "invalido")
            ])

    def test_source_vazio_falha(self):
        with pytest.raises(ContractError):
            multidisciplinary_triangulation("claim", [
                _item("", "medicina", "supports")
            ])

    def test_domain_vazio_falha(self):
        with pytest.raises(ContractError):
            multidisciplinary_triangulation("claim", [
                _item("doi:1", "", "supports")
            ])

    def test_item_nao_dict_falha(self):
        with pytest.raises(ContractError):
            multidisciplinary_triangulation("claim", ["not-a-dict"])

    def test_lista_vazia_insufficient_context(self):
        out = multidisciplinary_triangulation("claim", [])
        assert out["analysis_status"] == "insufficient_context"
        assert out["triangulated"] is False
        assert out["findings"] == []


# ═══════════════════════════════════════════════════════════════════════
# 2. Convergência entre domínios independentes
# ═══════════════════════════════════════════════════════════════════════

class TestConvergencia:
    def test_dois_dominios_concordantes_triangula(self):
        out = multidisciplinary_triangulation("O tratamento X funciona.", [
            _item("doi:1", "medicina", "supports"),
            _item("dataset:2", "ciencia_dados", "supports"),
        ])
        assert out["triangulated"] is True
        assert set(out["supporting_domains"]) == {"medicina", "ciencia_dados"}
        assert out["contesting_domains"] == []
        assert out["findings"] == []
        assert out["human_gate"] == "recommended"

    def test_um_unico_dominio_nao_triangula(self):
        out = multidisciplinary_triangulation("Alegação X.", [
            _item("doi:1", "medicina", "supports"),
            _item("doi:2", "medicina", "supports"),
            _item("doi:3", "medicina", "supports"),
        ])
        assert out["triangulated"] is False
        codes = {f["code"] for f in out["findings"]}
        assert "SINGLE_DOMAIN_EVIDENCE" in codes

    def test_nenhum_dominio_favoravel_nao_triangula(self):
        out = multidisciplinary_triangulation("Alegação X.", [
            _item("doi:1", "medicina", "neutral"),
        ])
        assert out["triangulated"] is False
        codes = {f["code"] for f in out["findings"]}
        assert "SINGLE_DOMAIN_EVIDENCE" in codes


# ═══════════════════════════════════════════════════════════════════════
# 3. Contestação bloqueia (não é resolvida por maioria)
# ═══════════════════════════════════════════════════════════════════════

class TestContestacaoBloqueia:
    def test_tres_concordam_um_contesta_nao_triangula(self):
        out = multidisciplinary_triangulation("Alegação X.", [
            _item("doi:1", "medicina", "supports"),
            _item("doi:2", "direito", "supports"),
            _item("doi:3", "financeiro", "supports"),
            _item("doi:4", "ciencia_dados", "contradicts"),
        ])
        assert out["triangulated"] is False
        highs = [f for f in out["findings"]
                 if f["code"] == "CONTESTED_MULTIDISCIPLINARY"]
        assert highs and highs[0]["severity"] == "high"
        assert "ciencia_dados" in highs[0]["detail"]
        assert out["human_gate"] == "required"

    def test_dominio_misto_conta_como_contestador(self):
        out = multidisciplinary_triangulation("Alegação X.", [
            _item("doi:1", "medicina", "supports"),
            _item("doi:2", "medicina", "contradicts"),  # mesmo domínio: misto
            _item("doi:3", "direito", "supports"),
        ])
        assert out["domain_verdicts"]["medicina"] == "mixed"
        assert out["triangulated"] is False
        assert "medicina" in out["contesting_domains"]


# ═══════════════════════════════════════════════════════════════════════
# 4. Normalização de domínio
# ═══════════════════════════════════════════════════════════════════════

class TestNormalizacao:
    def test_case_e_espacos_normalizados(self):
        out = multidisciplinary_triangulation("Alegação X.", [
            _item("doi:1", "Medicina", "supports"),
            _item("doi:2", " medicina ", "supports"),
            _item("doi:3", "direito", "supports"),
        ])
        # "Medicina" e " medicina " contam como o MESMO domínio
        assert out["domain_verdicts"]["medicina"] == "supports"
        assert len(out["supporting_domains"]) == 2  # medicina + direito


# ═══════════════════════════════════════════════════════════════════════
# 5. Determinismo e envelope
# ═══════════════════════════════════════════════════════════════════════

class TestEnvelope:
    def test_determinismo(self):
        items = [
            _item("doi:1", "medicina", "supports"),
            _item("doi:2", "direito", "supports"),
        ]
        r1 = multidisciplinary_triangulation("claim", items)
        r2 = multidisciplinary_triangulation("claim", items)
        assert r1 == r2

    def test_disclaimer_presente(self):
        out = multidisciplinary_triangulation("claim", [
            _item("doi:1", "medicina", "supports"),
            _item("doi:2", "direito", "supports"),
        ])
        assert "disclaimer" in out and len(out["disclaimer"]) > 20

    def test_claim_text_truncado(self):
        out = multidisciplinary_triangulation("x" * 500, [
            _item("doi:1", "medicina", "supports"),
            _item("doi:2", "direito", "supports"),
        ])
        assert len(out["claim_text"]) <= 200


# ═══════════════════════════════════════════════════════════════════════
# 6. Integração com o R103 (ReviewLedger)
# ═══════════════════════════════════════════════════════════════════════

class TestIntegracaoR103:
    def test_claim_triangulada_e_verificada(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim("Alegação multidisciplinar X.", section="discussion")
        orch = OrchestratorReviewer()
        result = orch.verify_multidisciplinary_claim(
            claim.id,
            [_item("doi:1", "medicina", "supports"), _item("doi:2", "direito", "supports")],
            ledger,
        )
        assert result["triangulated"] is True
        assert ledger.claims[claim.id].verified is True

    def test_claim_contestada_fica_pendente(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim("Alegação contestada Y.", section="discussion")
        orch = OrchestratorReviewer()
        result = orch.verify_multidisciplinary_claim(
            claim.id,
            [
                _item("doi:1", "medicina", "supports"),
                _item("doi:2", "direito", "supports"),
                _item("doi:3", "financeiro", "contradicts"),
            ],
            ledger,
        )
        assert result["triangulated"] is False
        assert ledger.claims[claim.id].verified is False
        pending_ids = {item["claim_id"] for item in ledger.get_pending_verifications()}
        assert claim.id in pending_ids
