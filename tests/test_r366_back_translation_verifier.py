# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R366 / OCB-BACK-TRANSLATION-001."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from translation.back_translation import (  # noqa: E402
    ContractError,
    verify,
)


def _payload(**overrides):
    payload = {
        "schema_version": "1.0.0",
        "review_id": "review-molambudos-002",
        "segment_id": "MEM-02:L4",
        "source_text": "Em 1915, Joaquim viu a vala. Não esqueceu nunca.",
        "back_translated_text": "Em 1915, Joaquim viu a vala. Não esqueceu nunca.",
        "translated_text": "In 1915, Joaquim saw the ditch. He never forgot.",
        "source_language": "pt-BR",
        "pivot_language": "en-US",
        "declared_entities": ["Joaquim"],
        "glossary_terms": [
            {"source_term": "retirante", "preserve_portuguese": True},
        ],
        "provenance": [
            {
                "source": "retrotradução revisora EN",
                "author": "revisora-en-01",
                "date": "2026-08-02",
                "limitations": "retrotradução humana de amostra",
            }
        ],
    }
    payload.update(overrides)
    return payload


# ═══════════════════════════════════════════════════════════════════════
# 1. Contrato
# ═══════════════════════════════════════════════════════════════════════

class TestContrato:
    def test_envelope_valido_completa(self):
        out = verify(_payload())
        assert out["analysis_status"] == "complete"
        assert out["review_id"] == "review-molambudos-002"

    def test_campos_ausentes_falham(self):
        payload = _payload()
        del payload["provenance"]
        with pytest.raises(ContractError):
            verify(payload)

    def test_provenance_vazia_falha(self):
        with pytest.raises(ContractError):
            verify(_payload(provenance=[]))

    def test_texto_vazio_insufficient(self):
        out = verify(_payload(back_translated_text="  "))
        assert out["analysis_status"] == "insufficient_context"
        assert out["findings"] == []


# ═══════════════════════════════════════════════════════════════════════
# 2. As seis verificações
# ═══════════════════════════════════════════════════════════════════════

class TestVerificacoes:
    def test_numero_perdido_cultural_loss_high(self):
        out = verify(_payload(
            back_translated_text="Joaquim viu a vala. Não esqueceu nunca.",
        ))
        hits = [f for f in out["findings"]
                if f["code"] == "CULTURAL_LOSS" and "1915" in f["detail"]]
        assert hits and hits[0]["severity"] == "high"
        assert out["human_gate"] == "required"

    def test_entidade_ausente_cultural_loss(self):
        out = verify(_payload(
            back_translated_text="Em 1915, o menino viu a vala. Não esqueceu nunca.",
        ))
        assert any(
            f["code"] == "CULTURAL_LOSS" and "Joaquim" in f["detail"]
            for f in out["findings"]
        )

    def test_negacao_removida_pragmatic_failure_high(self):
        out = verify(_payload(
            back_translated_text="Em 1915, Joaquim viu a vala. Esqueceu depois.",
        ))
        hits = [f for f in out["findings"] if f["code"] == "PRAGMATIC_FAILURE"]
        assert any(f["severity"] == "high" for f in hits)

    def test_pontuacao_pragmatica_medium(self):
        out = verify(_payload(
            source_text="Você viu?! Não vá...",
            back_translated_text="Você viu. Não vá.",
        ))
        hits = [f for f in out["findings"]
                if f["code"] == "PRAGMATIC_FAILURE" and f["severity"] == "medium"]
        assert hits

    def test_comprimento_anomalo_cultural_loss_medium(self):
        out = verify(_payload(
            back_translated_text="Em 1915, Joaquim viu a vala e não esqueceu "
            "nunca, porque a vala ficou na memória dele por toda a vida, "
            "acompanhando cada noite, cada silêncio e cada retorno ao sertão "
            "durante décadas inteiras de lembrança e de medo repetido.",
        ))
        assert any(
            f["code"] == "CULTURAL_LOSS" and "razão de comprimento" in f["detail"]
            for f in out["findings"]
        )

    def test_termo_preserve_perdido_term_conflict(self):
        out = verify(_payload(
            source_text="O retirante não parou em 1915.",
            back_translated_text="O migrante não parou em 1915.",
        ))
        hits = [f for f in out["findings"] if f["code"] == "TERM_CONFLICT"]
        assert hits and hits[0]["severity"] == "high"


# ═══════════════════════════════════════════════════════════════════════
# 3. Ciclo limpo e determinismo
# ═══════════════════════════════════════════════════════════════════════

class TestCicloLimpo:
    def test_ciclo_limpo_sem_achados(self):
        out = verify(_payload())
        assert out["findings"] == []
        assert out["human_gate"] == "recommended"

    def test_disclaimer_nega_prova_de_equivalencia(self):
        out = verify(_payload())
        assert "não prova" in out["disclaimer"].lower()

    def test_determinismo(self):
        payload = _payload(back_translated_text="Joaquim viu. Esqueceu?")
        assert verify(payload) == verify(payload)


# ═══════════════════════════════════════════════════════════════════════
# 4. Agent card
# ═══════════════════════════════════════════════════════════════════════

class TestAgentCard:
    def test_card_no_catalogo_com_episteme(self):
        from marceloclaro.catalog_loader import load_catalog_definitions

        defs = load_catalog_definitions()
        card = [d for d in defs if d["agent_id"] == "back-translation-verifier"]
        assert len(card) == 1
        assert card[0]["episteme"] == "hermeneutico_interpretativo"
        assert card[0]["skills"]
