# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R365 / OCB-AUTHOR-VOICE-001."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from translation.author_voice import (  # noqa: E402
    ContractError,
    review_segment,
    validate_voice_profile,
)


def _profile(**overrides):
    profile = {
        "schema_version": "1.0.0",
        "profile_id": "voice-molambudos-001",
        "work_id": "molambudos",
        "register": "oral, memorialístico, sertanejo, primeira pessoa",
        "voice_markers": [
            {"marker": "retirante", "kind": "regionalism", "strategy": "preserve"},
            {"marker": "oxente", "kind": "orality", "strategy": "gloss"},
            {
                "marker": "Currais do Governo",
                "kind": "institution",
                "strategy": "adapt",
                "approved_renderings": {
                    "en": ["Government Corrals"],
                    "zh_cn": ["政府围栏营"],
                },
            },
        ],
        "forbidden_modernisms": ["smartphone", "ok", "stress"],
        "provenance": [
            {
                "source": "briefing autoral R358",
                "author": "equipe editorial",
                "date": "2026-08-01",
                "limitations": "perfil inicial; revisar com o autor",
            }
        ],
    }
    profile.update(overrides)
    return profile


# ═══════════════════════════════════════════════════════════════════════
# 1. Contrato do perfil
# ═══════════════════════════════════════════════════════════════════════

class TestPerfilContrato:
    def test_perfil_valido(self):
        validated = validate_voice_profile(_profile())
        assert validated["profile_id"] == "voice-molambudos-001"
        assert len(validated["voice_markers"]) == 3

    def test_campos_ausentes_falham(self):
        incompleto = _profile()
        del incompleto["voice_markers"]
        with pytest.raises(ContractError):
            validate_voice_profile(incompleto)

    def test_marcadores_vazios_falham(self):
        with pytest.raises(ContractError):
            validate_voice_profile(_profile(voice_markers=[]))

    def test_adapt_sem_renderings_falha(self):
        markers = [
            {"marker": "Currais do Governo", "kind": "institution", "strategy": "adapt"}
        ]
        with pytest.raises(ContractError):
            validate_voice_profile(_profile(voice_markers=markers))

    def test_strategy_invalida_falha(self):
        markers = [{"marker": "x", "kind": "orality", "strategy": "delete"}]
        with pytest.raises(ContractError):
            validate_voice_profile(_profile(voice_markers=markers))

    def test_provenance_vazia_falha(self):
        with pytest.raises(ContractError):
            validate_voice_profile(_profile(provenance=[]))


# ═══════════════════════════════════════════════════════════════════════
# 2. Achados por regra
# ═══════════════════════════════════════════════════════════════════════

class TestAchados:
    def test_preserve_apagado_voice_shift_high(self):
        out = review_segment(
            _profile(),
            "O retirante chegou cansado.",
            "The migrant arrived tired.",
            "en-US",
        )
        shifts = [f for f in out["findings"] if f["code"] == "VOICE_SHIFT"]
        assert shifts and shifts[0]["severity"] == "high"
        assert out["human_gate"] == "required"

    def test_adapt_sem_rendering_aprovado_voice_shift(self):
        out = review_segment(
            _profile(),
            "Levaram todos aos Currais do Governo.",
            "They took everyone to the state pens.",
            "en-US",
        )
        assert any(
            f["code"] == "VOICE_SHIFT" and f["severity"] == "high"
            for f in out["findings"]
        )

    def test_gloss_ausente_voice_shift_medium(self):
        out = review_segment(
            _profile(),
            "Oxente, que fome danada.",
            "My, what a terrible hunger.",
            "en-US",
        )
        shifts = [f for f in out["findings"] if f["code"] == "VOICE_SHIFT"]
        assert shifts and shifts[0]["severity"] == "medium"

    def test_modernismo_proibido_anachronism(self):
        out = review_segment(
            _profile(),
            "Ele anotou tudo no caderno.",
            "He noted everything, feeling the stress.",
            "en-US",
        )
        assert any(f["code"] == "ANACHRONISM" for f in out["findings"])

    def test_deriva_pragmatica_register_shift(self):
        out = review_segment(
            _profile(),
            "Você vai voltar?! Não vá...",
            "You will come back. Do not go.",
            "en-US",
        )
        shifts = [f for f in out["findings"] if f["code"] == "REGISTER_SHIFT"]
        assert shifts and shifts[0]["severity"] == "medium"

    def test_segmento_fiel_sem_achados(self):
        out = review_segment(
            _profile(),
            "O retirante foi aos Currais do Governo.",
            "The retirante went to the Government Corrals.",
            "en-US",
        )
        assert out["findings"] == []
        assert out["human_gate"] == "recommended"
        assert out["analysis_status"] == "complete"


# ═══════════════════════════════════════════════════════════════════════
# 3. Fail-closed e determinismo
# ═══════════════════════════════════════════════════════════════════════

class TestEnvelope:
    def test_texto_vazio_insufficient_context(self):
        out = review_segment(_profile(), "", "Anything.", "en-US")
        assert out["analysis_status"] == "insufficient_context"
        assert out["findings"] == []

    def test_perfil_invalido_falha_fechado(self):
        with pytest.raises(ContractError):
            review_segment({"profile_id": "x"}, "a", "b", "en-US")

    def test_disclaimer_presente(self):
        out = review_segment(_profile(), "Texto.", "Text.", "en-US")
        assert "indício" in out["disclaimer"].lower()

    def test_determinismo(self):
        args = (
            _profile(),
            "O retirante chegou?! Oxente...",
            "The migrant arrived.",
            "en-US",
        )
        assert review_segment(*args) == review_segment(*args)


# ═══════════════════════════════════════════════════════════════════════
# 4. Agent card
# ═══════════════════════════════════════════════════════════════════════

class TestAgentCard:
    def test_card_no_catalogo_com_episteme(self):
        from marceloclaro.catalog_loader import load_catalog_definitions

        defs = load_catalog_definitions()
        card = [d for d in defs if d["agent_id"] == "author-voice-guardian"]
        assert len(card) == 1
        assert card[0]["episteme"] == "hermeneutico_interpretativo"
        assert card[0]["skills"]
