# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R363 — Camada Epistêmica de Roteamento."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from transformer.episteme import (  # noqa: E402
    AFFINITY,
    EPISTEMES,
    EpistemeProfile,
    episteme_affinity,
    infer_agent_episteme,
    infer_episteme_from_text,
    infer_task_episteme,
)
from transformer.semantic_matcher import (  # noqa: E402
    EmbeddingEngine,
    SkillHandbook,
    _cosine_similarity,
)


REGIMES = [
    "empirico_analitico",
    "formal_dedutivo",
    "hermeneutico_interpretativo",
    "critico_reflexivo",
    "pragmatico_tecnico",
    "regulatorio_normativo",
]


# ═══════════════════════════════════════════════════════════════════════
# 1. Taxonomia íntegra
# ═══════════════════════════════════════════════════════════════════════

class TestTaxonomia:
    def test_seis_regimes(self):
        assert sorted(EPISTEMES.keys()) == sorted(REGIMES)

    def test_regimes_tem_nome_descricao_sinais(self):
        for chave, regime in EPISTEMES.items():
            assert regime.get("nome"), chave
            assert regime.get("descricao"), chave
            assert len(regime.get("sinais", [])) >= 5, chave

    def test_afinidade_diagonal_um(self):
        for regime in REGIMES:
            assert episteme_affinity(regime, regime) == 1.0

    def test_afinidade_simetrica_e_no_intervalo(self):
        for a in REGIMES:
            for b in REGIMES:
                aff = episteme_affinity(a, b)
                assert 0.0 <= aff <= 1.0
                assert aff == episteme_affinity(b, a)

    def test_afinidade_desconhecida_neutra(self):
        assert episteme_affinity("inexistente", REGIMES[0]) == 0.5
        assert episteme_affinity(REGIMES[0], "inexistente") == 0.5

    def test_matriz_explicita_cobre_pares(self):
        # A matriz explícita deve ser consultável em qualquer ordem
        assert isinstance(AFFINITY, dict)
        assert len(AFFINITY) > 0


# ═══════════════════════════════════════════════════════════════════════
# 2. Inferência de agentes representativos (metadados reais do catálogo)
# ═══════════════════════════════════════════════════════════════════════

class TestInferenciaAgentes:
    def test_estatistica_empirico(self):
        p = infer_agent_episteme(
            category="academic",
            agent_type="maswos-agent",
            tags=["statistics", "inference", "hypothesis-testing"],
            name="07_agente_estatistica_analise",
        )
        assert p is not None
        assert p.episteme == "empirico_analitico"

    def test_abnt_regulatorio(self):
        p = infer_agent_episteme(
            category="academic",
            agent_type="maswos-agent",
            tags=["abnt", "citations", "references"],
            name="12_agente_auditoria_bibliografica_abnt",
        )
        assert p is not None
        assert p.episteme == "regulatorio_normativo"

    def test_traducao_cultural_hermeneutico(self):
        p = infer_agent_episteme(
            category="literary",
            agent_type="literary-agent",
            tags=["translation", "culture", "literary-voice"],
            name="cultural-episteme-agent",
        )
        assert p is not None
        assert p.episteme == "hermeneutico_interpretativo"

    def test_peer_review_critico(self):
        p = infer_agent_episteme(
            category="academic",
            agent_type="maswos-agent",
            tags=["peer-review", "ethics", "bias"],
            name="31_agente_blind_peer_review_emulado",
        )
        assert p is not None
        assert p.episteme == "critico_reflexivo"

    def test_tooling_pragmatico(self):
        p = infer_agent_episteme(
            category="engineering",
            agent_type="specialist",
            tags=["tooling", "integration", "devops"],
            name="agente_integracao_cli",
        )
        assert p is not None
        assert p.episteme == "pragmatico_tecnico"

    def test_matematica_formal(self):
        p = infer_agent_episteme(
            category="academic",
            agent_type="maswos-agent",
            tags=["mathematics", "formal-modeling", "proofs"],
            name="21_agente_matematica_aplicada_modelagem_formal",
        )
        assert p is not None
        assert p.episteme == "formal_dedutivo"

    def test_perfil_tem_confianca_e_sinais(self):
        p = infer_agent_episteme(
            category="academic",
            agent_type="",
            tags=["statistics", "regression", "sample"],
            name="estatistico",
        )
        assert isinstance(p, EpistemeProfile)
        assert 0.0 < p.confianca <= 1.0
        assert len(p.sinais) >= 1


# ═══════════════════════════════════════════════════════════════════════
# 3. Nunca chuta
# ═══════════════════════════════════════════════════════════════════════

class TestNuncaChuta:
    def test_texto_sem_sinais_retorna_none(self):
        assert infer_episteme_from_text("xyzzy blorb quux") is None

    def test_texto_vazio_retorna_none(self):
        assert infer_episteme_from_text("") is None
        assert infer_episteme_from_text(None) is None

    def test_agente_sem_sinais_retorna_none(self):
        p = infer_agent_episteme(
            category="", agent_type="", tags=[], name="blorb"
        )
        assert p is None

    def test_determinismo(self):
        texto = "auditar conformidade abnt das referencias e normas"
        p1 = infer_task_episteme(texto)
        p2 = infer_task_episteme(texto)
        assert p1 is not None and p2 is not None
        assert p1.episteme == p2.episteme
        assert p1.confianca == p2.confianca
        assert p1.sinais == p2.sinais


# ═══════════════════════════════════════════════════════════════════════
# 4. Fail-open: sem episteme, score idêntico ao comportamento anterior
# ═══════════════════════════════════════════════════════════════════════

class TestFailOpen:
    def test_score_identico_sem_epistemes(self):
        engine = EmbeddingEngine()
        handbook = SkillHandbook(engine=engine)
        handbook.register_skill(
            agent_id="blorb-agent",
            skill_id="blorb-skill",
            name="Blorb",
            description="quux xyzzy frobnicate",
            tags=["blorb"],
        )
        task = "frobnicate o quux xyzzy"
        results = handbook.match(task, top_k=5, min_confidence=0.0)
        assert len(results) == 1
        r = results[0]
        # Fórmula anterior: 0.6*similaridade + 0.4*confiança, sem ajuste
        profile = handbook._profiles[("blorb-agent", "blorb-skill")]
        assert profile.episteme is None
        task_vec = engine.embed(task)
        expected_sim = _cosine_similarity(task_vec, profile.vector)
        expected = round(0.6 * expected_sim + 0.4 * profile.confidence, 4)
        assert r["score"] == expected
        assert r["episteme_affinity"] is None

    def test_task_sem_episteme_nao_ajusta(self):
        handbook = SkillHandbook(engine=EmbeddingEngine())
        handbook.register_skill(
            agent_id="agente-abnt",
            skill_id="auditoria-abnt",
            name="Auditoria ABNT",
            description="conformidade com normas abnt",
            tags=["abnt", "normas"],
        )
        profile = handbook._profiles[("agente-abnt", "auditoria-abnt")]
        assert profile.episteme == "regulatorio_normativo"
        results = handbook.match("frobnicate o quux xyzzy", min_confidence=0.0)
        assert results[0]["episteme_affinity"] is None


# ═══════════════════════════════════════════════════════════════════════
# 5. Peso brando: reordena, limita a ±10%, nunca exclui
# ═══════════════════════════════════════════════════════════════════════

class TestPesoBrando:
    def _handbook_com_par(self):
        """Duas skills do mesmo agente, mesma descrição/tags (mesmo vetor,
        mesma confiança) e epistemes explícitas diferentes."""
        handbook = SkillHandbook(engine=EmbeddingEngine())
        comum = dict(
            agent_id="agente-duplo",
            name="Verificacao",
            description="verificacao geral de documentos",
            tags=["docs"],
        )
        handbook.register_skill(
            skill_id="skill-regulatoria",
            episteme="regulatorio_normativo",
            **comum,
        )
        handbook.register_skill(
            skill_id="skill-empirica",
            episteme="empirico_analitico",
            **comum,
        )
        return handbook

    def test_afinidade_reordena_par_com_mesmo_score_base(self):
        handbook = self._handbook_com_par()
        task = "auditar conformidade abnt e normas das referencias"
        results = handbook.match(task, min_confidence=0.0)
        assert len(results) == 2
        assert results[0]["skill_id"] == "skill-regulatoria"
        assert results[0]["score"] > results[1]["score"]

    def test_formula_do_ajuste(self):
        handbook = self._handbook_com_par()
        task = "auditar conformidade abnt e normas das referencias"
        results = handbook.match(task, min_confidence=0.0)
        for r in results:
            key = ("agente-duplo", r["skill_id"])
            profile = handbook._profiles[key]
            task_vec = handbook.engine.embed(task)
            base = 0.6 * _cosine_similarity(task_vec, profile.vector) \
                + 0.4 * profile.confidence
            aff = r["episteme_affinity"]
            assert aff is not None
            expected = round(base * (1 + 0.20 * (aff - 0.5)), 4)
            assert r["score"] == expected
            # Ajuste limitado a ±10%
            assert abs(r["score"] - round(base, 4)) <= round(0.1 * base, 4) + 1e-4

    def test_nao_exclui_candidato_de_regime_distante(self):
        handbook = self._handbook_com_par()
        results = handbook.match(
            "auditar conformidade abnt e normas", min_confidence=0.0
        )
        skill_ids = {r["skill_id"] for r in results}
        assert skill_ids == {"skill-regulatoria", "skill-empirica"}


# ═══════════════════════════════════════════════════════════════════════
# 6. Override de frontmatter e parser do catálogo
# ═══════════════════════════════════════════════════════════════════════

class TestOverrideECatalogo:
    def test_override_explicito_vence_heuristica(self):
        handbook = SkillHandbook(engine=EmbeddingEngine())
        handbook.register_skill(
            agent_id="agente-x",
            skill_id="skill-x",
            name="Estatistica",
            description="statistics regression sample",
            tags=["statistics"],
            episteme="formal_dedutivo",
        )
        profile = handbook._profiles[("agente-x", "skill-x")]
        assert profile.episteme == "formal_dedutivo"

    def test_frontmatter_episteme_lido(self, tmp_path):
        from marceloclaro.catalog_loader import load_catalog_definitions

        agent_md = tmp_path / "agente-teste.md"
        agent_md.write_text(
            "---\n"
            "name: agente-teste\n"
            "description: Agente de teste\n"
            "category: academic\n"
            "episteme: hermeneutico_interpretativo\n"
            "---\n\n# Agente de teste\n",
            encoding="utf-8",
        )
        defs = load_catalog_definitions(catalog_dir=str(tmp_path))
        assert len(defs) == 1
        assert defs[0]["episteme"] == "hermeneutico_interpretativo"

    def test_frontmatter_sem_episteme_none(self, tmp_path):
        from marceloclaro.catalog_loader import load_catalog_definitions

        agent_md = tmp_path / "agente-sem.md"
        agent_md.write_text(
            "---\nname: agente-sem\ncategory: general\n---\n\n# X\n",
            encoding="utf-8",
        )
        defs = load_catalog_definitions(catalog_dir=str(tmp_path))
        assert defs[0]["episteme"] is None

    def test_catalogo_real_carrega_com_chave_episteme(self):
        from marceloclaro.catalog_loader import load_catalog_definitions

        defs = load_catalog_definitions()
        assert len(defs) > 100
        for d in defs:
            assert "episteme" in d


# ═══════════════════════════════════════════════════════════════════════
# 7. Explicabilidade
# ═══════════════════════════════════════════════════════════════════════

class TestExplicabilidade:
    def test_match_expoe_episteme_e_afinidade(self):
        handbook = SkillHandbook(engine=EmbeddingEngine())
        handbook.register_skill(
            agent_id="agente-abnt",
            skill_id="auditoria-abnt",
            name="Auditoria ABNT",
            description="conformidade com normas abnt",
            tags=["abnt", "normas"],
        )
        results = handbook.match(
            "auditar conformidade abnt das referencias", min_confidence=0.0
        )
        r = results[0]
        assert "episteme" in r
        assert "episteme_affinity" in r
        assert r["episteme"] == "regulatorio_normativo"
        assert r["episteme_affinity"] is not None
        assert 0.0 <= r["episteme_affinity"] <= 1.0
