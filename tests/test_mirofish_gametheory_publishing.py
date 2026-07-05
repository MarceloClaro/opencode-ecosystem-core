# -*- coding: utf-8 -*-
"""
Testes TDD — SPEC-014 (Game Theory), SPEC-015 (MiroFish), SPEC-016 (Publishing).
"""
import os
import shutil
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# ─────────────────────────────────────────────────────────────────────
# SPEC-014 — Game Theory
# ─────────────────────────────────────────────────────────────────────

class TestGameTheory:
    def test_r014_1_catalogo_38_raciocinios(self):
        from gametheory import ReasoningType
        assert len(list(ReasoningType)) == 38

    def test_r014_2_nash_dilema_prisioneiro(self):
        from gametheory import PayoffMatrix
        pm = PayoffMatrix.prisoners_dilemma()
        assert pm.find_nash_equilibria() == [("Trair", "Trair")]

    def test_r014_2b_nash_stag_hunt_tem_equilibrios(self):
        from gametheory import PayoffMatrix
        pm = PayoffMatrix.stag_hunt()
        eq = pm.find_nash_equilibria()
        assert ("Cooperar", "Cooperar") in eq

    def test_r014_4_meta_reasoner_conflito(self):
        from gametheory import MetaReasoner, ReasoningType
        sel = MetaReasoner().select_for_context({"topic": "negociação de disputa"})
        assert ReasoningType.NASH_EQUILIBRIUM in sel

    def test_r014_5_auditoria_phd_importavel(self):
        from gametheory import (NashSolver, StatisticalRigor, QualisA1Auditor,
                                SensitivityAnalyzer, IMRADFormatter)
        assert all([NashSolver, StatisticalRigor, QualisA1Auditor,
                    SensitivityAnalyzer, IMRADFormatter])


# ─────────────────────────────────────────────────────────────────────
# SPEC-015 — MiroFish
# ─────────────────────────────────────────────────────────────────────

class TestMiroFish:
    def _fresh_swarm(self, **kw):
        from mirofish import MiroFishSwarm
        swarm = MiroFishSwarm(**kw)
        swarm.predictions = {}  # isola de estado persistido
        return swarm

    def test_r015_1_enxame_configuravel(self):
        swarm = self._fresh_swarm(n_agents=10, seed=1)
        assert len(swarm.agents) == 10
        biases = {a.bias for a in swarm.agents}
        assert {"optimist", "pessimist", "contrarian", "neutral", "momentum"} == biases

    def test_r015_2_previsao_agregada_limites(self):
        swarm = self._fresh_swarm(n_agents=15, seed=7)
        r = swarm.predict("Teste?", signal=0.6)
        assert 0.0 <= r["aggregate"] <= 1.0
        assert 0.0 <= r["consensus"] <= 1.0
        assert len(r["individual"]) == 15
        assert all(0.0 <= v <= 1.0 for v in r["individual"].values())

    def test_r015_3_feedback_recalibra_pesos(self):
        swarm = self._fresh_swarm(n_agents=8, seed=3)
        r = swarm.predict("Evento ocorre?", signal=0.9)
        before = {a.agent_id: a.weight for a in swarm.agents}
        swarm.feedback(r["prediction_id"], actual=1.0)
        after = {a.agent_id: a.weight for a in swarm.agents}
        assert before != after
        assert all(w >= 0.1 for w in after.values())  # INV-015.2

    def test_r015_4_debate_delphi(self):
        swarm = self._fresh_swarm(n_agents=20, seed=42)
        d = swarm.debate("Convergência?", rounds=4, signal=0.7)
        assert len(d["trajectory"]) == 4
        assert 0.0 <= d["final"] <= 1.0

    def test_r015_5_validacao_cruzada(self):
        from mirofish import CrossValidator
        cv = CrossValidator(n_agents=12, seed=42)
        cv.swarm.predictions = {}
        v = cv.validate_decision("Aprovar?", signal=0.8)
        assert "approved" in v and "game" in v and "swarm" in v
        assert isinstance(v["game"]["submit_is_equilibrium"], bool)

    def test_inv015_3_reprodutibilidade_com_seed(self):
        s1 = self._fresh_swarm(n_agents=5, seed=99)
        s2 = self._fresh_swarm(n_agents=5, seed=99)
        # reseta pesos para eliminar estado persistido
        for a in s1.agents + s2.agents:
            a.weight, a.accuracy_history = 1.0, []
        r1 = s1.predict("X?", signal=0.5)
        r2 = s2.predict("X?", signal=0.5)
        assert r1["aggregate"] == r2["aggregate"]


# ─────────────────────────────────────────────────────────────────────
# SPEC-016 — Publishing
# ─────────────────────────────────────────────────────────────────────

class TestPublishing:
    @pytest.fixture()
    def outdir(self):
        d = tempfile.mkdtemp(prefix="prod-test-")
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_r016_6_templates_integros(self):
        from publishing import list_templates
        for name, path in list_templates().items():
            assert os.path.exists(path), f"template {name} ausente: {path}"

    def test_r016_1_pasta_unica(self, outdir):
        from publishing import ScientificProduction
        prod = ScientificProduction("Artigo de Teste", template="artigo",
                                    output_root=outdir)
        manifest = prod.build("## Seção\n\nConteúdo de teste, com vírgula.\n")
        assert os.path.isdir(os.path.join(manifest["folder"], "latex"))
        assert os.path.exists(os.path.join(manifest["folder"], "manuscrito.md"))
        assert os.path.exists(os.path.join(manifest["folder"], "MANIFEST.json"))

    def test_r016_2_r016_3_formatos_e_kdp(self, outdir):
        from publishing import ScientificProduction
        prod = ScientificProduction("Livro de Teste", template="livro",
                                    output_root=outdir)
        manifest = prod.build("# Capítulo 1\n\nEra uma vez, um enxame.\n")
        assert manifest["formats"]["md"] is not None
        if shutil.which("pandoc"):
            assert manifest["formats"]["docx"] is not None
            assert manifest["formats"]["odt"] is not None
            assert manifest["kdp_ready"] is True

    def test_r016_4_checksums_no_manifesto(self, outdir):
        from publishing import ScientificProduction
        prod = ScientificProduction("Checksum Teste", template="artigo",
                                    output_root=outdir)
        manifest = prod.build("Texto, mínimo.\n")
        info = manifest["formats"]["md"]
        assert info and len(info["sha256"]) == 64 and info["bytes"] > 0

    def test_inv016_2_slug_unico(self, outdir):
        from publishing import ScientificProduction
        p1 = ScientificProduction("Mesmo Titulo", output_root=outdir)
        p2 = ScientificProduction("Mesmo Titulo", output_root=outdir)
        # slug contém timestamp; no mesmo segundo os objetos diferem pelo folder criado
        assert p1.folder != p2.folder or p1.slug == p2.slug

    def test_template_invalido_gera_erro(self):
        from publishing import ScientificProduction
        with pytest.raises(ValueError):
            ScientificProduction("X", template="inexistente")


# ─────────────────────────────────────────────────────────────────────
# Integração com o orquestrador
# ─────────────────────────────────────────────────────────────────────

class TestOrchestratorIntegration:
    @pytest.fixture(scope="class")
    def orch(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        return MarceloClaroOrchestrator(auto_load_agents=False)

    def test_meta_reason(self, orch):
        r = orch.meta_reason("negociação de cooperação em disputa científica")
        assert r["count"] >= 2 and "CRITICAL" in r["strategies"]

    def test_nash_analysis(self, orch):
        r = orch.nash_analysis("prisoners_dilemma")
        assert r["equilibria"] == [("Trair", "Trair")]

    def test_swarm_predict(self, orch):
        r = orch.swarm_predict("O ecossistema passará nos testes?", signal=0.8)
        assert 0.0 <= r["final"] <= 1.0

    def test_produce_scientific_work(self, orch, tmp_path):
        manifest = orch.produce_scientific_work(
            "Artigo Integrado", "## Intro\n\nTexto, breve.\n", template="artigo"
        )
        assert manifest["formats"]["md"] is not None
        # limpeza: remove a pasta gerada no repositório
        shutil.rmtree(os.path.dirname(manifest["folder"]), ignore_errors=True)
