# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R364 / OCB-TERMINOLOGY-GRAPH-001."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from translation.cultural_episteme import (  # noqa: E402
    ContractError,
    build_terminology_delta,
)
from translation.terminology_graph import TerminologyGraph  # noqa: E402


def _request(**overrides):
    request = {
        "schema_version": "1.0.0",
        "review_id": "review-molambudos-001",
        "segment_id": "MEM-01:L10",
        "source_language": "pt-BR",
        "target_language": "en-US",
        "source_text": "O retirante deixou a barraca nos Currais do Governo.",
        "translated_text": "The retirante left the tent in the Government Corrals.",
        "author_voice_profile": {
            "narrator_age": "child",
            "region": "Sertão do Ceará",
            "register": "oral, memorialístico e popular",
        },
        "terminology_graph": {
            "graph_id": "molambudos-terms",
            "revision": "0",
            "concepts": [],
        },
        "historical_context": {
            "period": "1915",
            "region": "Ceará",
            "support_status": "documented",
            "provenance": [
                {
                    "source": "dossiê histórico editorial",
                    "author": "equipe editorial",
                    "date": "2026-08-01",
                    "limitations": "requer revisão histórica independente",
                }
            ],
        },
        "cultural_dossier": {
            "target_variety": "English (United States)",
            "provenance": [
                {
                    "source": "glossário R355",
                    "author": "equipe editorial",
                    "date": "2026-07-31",
                    "limitations": "rascunho editorial",
                }
            ],
            "anachronism_markers": [],
        },
        "previous_translation_decisions": [],
    }
    request.update(overrides)
    return request


def _delta(revision="0", term="retirante", **concept_overrides):
    concept = {
        "source_term": term,
        "entity_type": "regional",
        "preferred_en": "retirante",
        "preferred_zh_cn": "逃荒者",
        "preserve_portuguese": True,
        "forbidden_translations": ["migrant", "refugee"],
    }
    concept.update(concept_overrides)
    request = _request(
        terminology_graph={
            "graph_id": "molambudos-terms",
            "revision": revision,
            "concepts": [],
        }
    )
    return build_terminology_delta(
        request, concept, "termo cultural central; não domesticar"
    )


def _graph():
    return TerminologyGraph("molambudos-terms")


# ═══════════════════════════════════════════════════════════════════════
# 1. Aceita o delta real do CulturalEpistemeAgent
# ═══════════════════════════════════════════════════════════════════════

class TestApplyDelta:
    def test_aceita_delta_do_cultural_episteme(self):
        g = _graph()
        result = g.apply_delta(_delta())
        assert result["applied"] is True
        assert g.revision == 1
        entry = g.get_term("retirante")
        assert entry["approval_state"] == "proposed"
        assert entry["preferred_en"] == "retirante"

    def test_idempotente_por_delta_id(self):
        g = _graph()
        d = _delta()
        g.apply_delta(d)
        result = g.apply_delta(d)
        assert result["applied"] is False
        assert g.revision == 1

    def test_rejeita_graph_id_divergente(self):
        g = TerminologyGraph("outro-grafo")
        with pytest.raises(ContractError):
            g.apply_delta(_delta())

    def test_rejeita_revisao_obsoleta(self):
        g = _graph()
        g.apply_delta(_delta())  # revision 0 -> 1
        with pytest.raises(ContractError):
            g.apply_delta(_delta(revision="0", term="vala"))

    def test_nunca_ativa_sozinho(self):
        g = _graph()
        g.apply_delta(_delta())
        assert g.get_term("retirante")["approval_state"] == "proposed"


# ═══════════════════════════════════════════════════════════════════════
# 2. Decisão humana obrigatória
# ═══════════════════════════════════════════════════════════════════════

class TestAprovacaoHumana:
    def test_aprovacao_com_revisor(self):
        g = _graph()
        g.apply_delta(_delta())
        g.approve("retirante", reviewer="revisora-en-01")
        entry = g.get_term("retirante")
        assert entry["approval_state"] == "approved"
        assert entry["decided_by"] == "revisora-en-01"

    def test_reviewer_vazio_ou_agente_falha(self):
        g = _graph()
        g.apply_delta(_delta())
        with pytest.raises(ContractError):
            g.approve("retirante", reviewer="")
        with pytest.raises(ContractError):
            g.approve("retirante", reviewer="agent")

    def test_aprovar_inexistente_falha(self):
        with pytest.raises(ContractError):
            _graph().approve("fantasma", reviewer="revisora-en-01")

    def test_decidir_duas_vezes_falha(self):
        g = _graph()
        g.apply_delta(_delta())
        g.approve("retirante", reviewer="revisora-en-01")
        with pytest.raises(ContractError):
            g.reject("retirante", reviewer="revisora-en-01")


# ═══════════════════════════════════════════════════════════════════════
# 3. Detecção de conflito em segmentos
# ═══════════════════════════════════════════════════════════════════════

def _graph_aprovado():
    g = _graph()
    g.apply_delta(_delta())
    g.apply_delta(
        _delta(
            revision="1",
            term="olho",
            entity_type="symbol",
            preferred_en="the eye",
            preserve_portuguese=False,
            forbidden_translations=[],
        )
    )
    g.approve("retirante", reviewer="revisora-en-01")
    g.approve("olho", reviewer="revisora-en-01")
    return g


class TestCheckSegment:
    def test_traducao_proibida_gera_term_conflict(self):
        g = _graph_aprovado()
        findings = g.check_segment(
            "O retirante caminhou.", "The migrant walked.", "en-US"
        )
        codes = {f["code"] for f in findings}
        assert "TERM_CONFLICT" in codes
        conflict = [f for f in findings if f["code"] == "TERM_CONFLICT"][0]
        assert conflict["severity"] == "high"

    def test_preserve_portuguese_ausente_gera_conflict(self):
        g = _graph_aprovado()
        findings = g.check_segment(
            "O retirante caminhou.", "The traveler walked on.", "en-US"
        )
        assert any(f["code"] == "TERM_CONFLICT" for f in findings)

    def test_simbolo_sem_preferida_gera_symbol_drift(self):
        g = _graph_aprovado()
        findings = g.check_segment(
            "O olho na parede vigiava.", "The gaze on the wall watched.", "en-US"
        )
        assert any(f["code"] == "SYMBOL_DRIFT" for f in findings)

    def test_termo_proposto_nao_gera_achado(self):
        g = _graph()
        g.apply_delta(_delta())  # proposed, sem aprovação
        findings = g.check_segment(
            "O retirante caminhou.", "The migrant walked.", "en-US"
        )
        assert findings == []

    def test_segmento_consistente_sem_achados(self):
        g = _graph_aprovado()
        findings = g.check_segment(
            "O retirante viu o olho.", "The retirante saw the eye.", "en-US"
        )
        assert findings == []


# ═══════════════════════════════════════════════════════════════════════
# 4. Relatório medido e gate fail-closed
# ═══════════════════════════════════════════════════════════════════════

class TestRelatorioEGate:
    def test_relatorio_traz_numeros_medidos(self):
        g = _graph_aprovado()
        report = g.consistency_report([
            ("O retirante viu o olho.", "The retirante saw the eye.", "en-US"),
            ("O retirante caminhou.", "The migrant walked.", "en-US"),
        ])
        assert report["measured"] is True
        assert report["claim"] == "internal-fixture-measurement"
        assert report["term_occurrences"] >= 2
        assert 0.0 <= report["consistency_ratio"] <= 1.0
        assert report["findings_by_code"]["TERM_CONFLICT"] >= 1

    def test_relatorio_sem_ocorrencias_ratio_none(self):
        g = _graph_aprovado()
        report = g.consistency_report([("Sem termos aqui.", "No terms here.", "en-US")])
        assert report["consistency_ratio"] is None

    def test_gate_bloqueia_com_conflito_aberto(self):
        g = _graph_aprovado()
        g.check_segment("O retirante caminhou.", "The migrant walked.", "en-US")
        gate = g.release_gate()
        assert gate["blocked"] is True

    def test_gate_bloqueia_simbolo_sem_decisao_humana(self):
        g = _graph()
        g.apply_delta(_delta(term="vala", entity_type="symbol"))
        gate = g.release_gate()
        assert gate["blocked"] is True
        assert any("vala" in reason for reason in gate["reasons"])

    def test_gate_libera_sem_pendencias(self):
        g = _graph_aprovado()
        g.check_segment("O retirante viu o olho.", "The retirante saw the eye.", "en-US")
        assert g.release_gate()["blocked"] is False


# ═══════════════════════════════════════════════════════════════════════
# 5. Persistência round-trip
# ═══════════════════════════════════════════════════════════════════════

class TestPersistencia:
    def test_round_trip(self, tmp_path):
        g = _graph_aprovado()
        path = tmp_path / "graph.json"
        g.save(str(path))
        g2 = TerminologyGraph.load(str(path))
        assert g2.graph_id == g.graph_id
        assert g2.revision == g.revision
        assert g2.get_term("retirante")["approval_state"] == "approved"
        assert g2.get_term("olho")["entity_type"] == "symbol"


# ═══════════════════════════════════════════════════════════════════════
# 6. Agent card registrável
# ═══════════════════════════════════════════════════════════════════════

class TestAgentCard:
    def test_card_no_catalogo_com_episteme(self):
        from marceloclaro.catalog_loader import load_catalog_definitions

        defs = load_catalog_definitions()
        card = [d for d in defs if d["agent_id"] == "terminology-graph-agent"]
        assert len(card) == 1
        assert card[0]["episteme"] == "hermeneutico_interpretativo"
        assert card[0]["skills"], "card deve declarar skills A2A"
