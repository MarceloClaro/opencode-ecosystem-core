"""
Testes R-976.12/R-976.13 — Banca editorial ampliada:
peso do texto nas decisões, 12 critérios, 12+ revisores e
instituições de publicação (rótulos Qualis A1 de simulação).

Ciclo R584. TDD: RED (aqui) → GREEN (implementação em banca.py).
"""
import pytest

DOC = """
IA GENERATIVA NA EDUCAÇÃO JURÍDICA BRASILEIRA — ENTRE A REGULAÇÃO E A SALA DE AULA

Revisão de escopo Brasil-comparado sobre ética, governança algorítmica e
equidade (2020-2026).

RESUMO. Introdução. A difusão da inteligência artificial generativa (IAGen)
na educação jurídica amplia possibilidades de apoio à aprendizagem, mas
também intensifica questões de integridade acadêmica, proteção de dados,
transparência, supervisão humana e equidade. Objetivo. Mapear a literatura
científica publicada entre 2020 e 2026. Método. Revisão de escopo orientada
pelo Joanna Briggs Institute com protocolo registrado, relatada segundo
PRISMA-ScR, com critérios de inclusão e exclusão explícitos, buscas em
OpenAlex e DOAJ, triagem independente por dois revisores humanos (RH1 e
RH2), extração padronizada e síntese temática; 21 estudos incluídos após
consenso documentado (n=21; κ=1,000; Po=1,000; Pe=0,580; concordância 100%;
IC95%). Resultados. A literatura
concentra-se em marcos normativos (D1=95,2%) e fundamentos éticos
(E1=95,2%). Conclusão. A lacuna de equidade algorítmica no ensino jurídico
brasileiro permanece como agenda prioritária.

Palavras-chave: inteligência artificial generativa; educação jurídica; ética;
governança algorítmica; equidade; revisão de escopo.

Referências em ABNT; repositório com dados, código e seed no OSF/Zenodo (DOI
pendente); material suplementar PRISMA-ScR declarado.
"""


class TestTextSignals:
    def test_sinais_textuais_por_criterio(self):
        from mirofish.social.banca import text_signals
        sig = text_signals(DOC)
        # critérios ampliados presentes
        assert set(sig.keys()) >= {
            "metodologia", "estatística", "ética", "originalidade", "clareza",
            "relevância", "teoria", "reprodutibilidade", "evidências",
            "redação", "coerência", "impacto",
        }
        # manuscrito com método PRISMA/JBI forte
        assert sig["metodologia"] > 0.5
        # contém kappa/concordância/n=
        assert sig["estatística"] > 0.3
        # menciona OSF/Zenodo/DOI → reprodutibilidade forte
        assert sig["reprodutibilidade"] > 0.5

    def test_sinal_fraco_em_texto_vazio(self):
        from mirofish.social.banca import text_signals
        sig = text_signals("")
        assert all(0.0 <= v <= 1.0 for v in sig.values())

    def test_adjust_bias_suaviza_com_sinal_forte(self):
        from mirofish.social.banca import adjust_bias_by_signal
        # rigoroso (−0.25) + sinal forte 1.0 → menos severo
        assert adjust_bias_by_signal(-0.25, 1.0) > -0.25
        # rigoroso + sinal fraco 0.0 → mais severo
        assert adjust_bias_by_signal(-0.25, 0.0) < -0.25
        # sinal neutro 0.5 → mantém postura
        assert adjust_bias_by_signal(-0.25, 0.5) == pytest.approx(-0.25)


class TestBancaAmpliada:
    def test_12_revisores_padrao_e_12_criterios(self):
        from mirofish.social.banca import BancaProfileGenerator, CRITERIA
        assert len(CRITERIA) == 12
        g = BancaProfileGenerator(DOC, n_members=12, seed=42)
        members = g.generate()
        assert len(members) == 12
        criteria = {m.criterion for m in members}
        assert len(criteria) == 12  # um PhD por critério

    def test_sinais_modulam_bias(self):
        from mirofish.social.banca import BancaProfileGenerator
        g = BancaProfileGenerator(DOC, n_members=12, seed=42)
        members = g.generate()
        for m in members:
            if m.criterion == "reprodutibilidade":
                # sinal forte → adjusted != base para rigoroso/entusiasta
                assert m.adjusted_bias != m.base_bias
                assert m.text_signal > 0.5
                assert m.profile.sentiment_bias == m.adjusted_bias

    def test_instituicoes_rotulo_qualis_a1(self):
        from mirofish.social.banca import BancaProfileGenerator
        from mirofish.social.banca import _INSTITUTIONS
        assert len(set(_INSTITUTIONS)) >= 10
        g = BancaProfileGenerator(DOC, n_members=12, seed=1)
        members = g.generate()
        inst = {m.institution for m in members}
        assert len(inst) >= 10
        assert any("Qualis A1" in i for i in inst)

    def test_verdict_faixas_inalteradas(self):
        from mirofish.social.banca import banca_verdict
        assert banca_verdict(0.9)[0] == "ACEITAR"
        assert banca_verdict(0.4)[0] == "REVISÕES MENORES"
        assert banca_verdict(0.0)[0] == "REVISÕES MAIORES"
        assert banca_verdict(-0.9)[0] == "REJEITAR"


class TestVereditoPonderado:
    def test_weighted_score_0_100(self):
        from mirofish.social.banca import banca_weighted_score
        by = {"metodologia": {"avg": 0.5}, "ética": {"avg": 0.8}}
        score = banca_weighted_score(0.6, by)
        assert 0 <= score <= 100
        assert score > 60  # médias positivas → nota alta

    def test_recommendation_faixas(self):
        from mirofish.social.banca import recommendation_from_score
        assert "Aceitar" in recommendation_from_score(85)
        assert "revisões menores" in recommendation_from_score(70).lower()
        assert "Revisões maiores" in recommendation_from_score(50)
        assert "Rejeitar" in recommendation_from_score(20)

    def test_summarize_banca_com_sinais(self):
        from mirofish.social.banca import BancaProfileGenerator, summarize_banca
        from mirofish.social import (
            EventConfig, PlatformConfig, SimulationParameters, TimeSimulationConfig,
            SocialSimulationEngine,
        )
        g = BancaProfileGenerator(DOC, n_members=12, seed=7)
        members = g.generate()
        params = SimulationParameters(
            simulation_id="banca_amp",
            event_config=EventConfig(hot_topics=["ética", "metodologia"]),
            twitter_config=PlatformConfig(echo_chamber_strength=0.4),
            time_config=TimeSimulationConfig(
                total_simulation_hours=12, minutes_per_round=60),
        )
        res = SocialSimulationEngine(
            [m.profile for m in members], params, seed=7).run(rounds=8)
        s = summarize_banca(members, res.final_opinions, signals=g.signals())
        assert set(s.keys()) >= {
            "final_sentiment", "verdict", "weighted_score",
            "recommendation", "by_criterion", "text_signals",
            "strengths", "weaknesses", "disclaimer",
        }
        assert 0 <= s["weighted_score"] <= 100
        assert "SIMULAÇÃO" in s["disclaimer"]
        assert "não representa parecer" in s["disclaimer"]


class TestOrquestradorBanca:
    def test_banca_simulate_retorna_resumo(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator()
        r = orch.banca_simulate(DOC, n_members=12, rounds=6, seed=3,
                                requirement="avaliar revisão de escopo")
        assert r["verdict"] in ("ACEITAR", "REVISÕES MENORES",
                                "REVISÕES MAIORES", "REJEITAR")
        assert 0 <= r["weighted_score"] <= 100
        assert len(r["text_signals"]) >= 6
        assert "state_path" in r