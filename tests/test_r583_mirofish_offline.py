# -*- coding: utf-8 -*-
"""
Testes TDD — SPEC-976: Integração MiroFish-Offline (simulação social).

Cobrem: contratos de dados (R-976.1/R-976.2), geração determinística de perfis
(R-976.3), motor de simulação (R-976.4), evolução de opinião (R-976.5),
persistência (R-976.6), ReportAgent (R-976.7), integração orquestrador
(R-976.8) e driver externo fail-closed (R-976.9).
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DOC = """
Prefeitura anuncia plano de mobilidade urbana com faixas exclusivas para
ônibus elétricos no centro da cidade. Empresas de transporte avaliam impacto
nos custos. Moradores divergem: comerciantes temem queda de vendas, enquanto
estudantes apoiam a redução de poluição. A votação ocorrerá em sessão pública.
"""


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path):
    """Estado fica em /tmp — nunca no .mci_state do checkout durante testes."""
    import mirofish.social.engine as engine_mod
    monkeypatch.setattr(engine_mod, "_STATE_DIR", str(tmp_path))


# ─────────────────────────────────────────────────────────────────────
# R-976.1 — Contratos de dados (OasisAgentProfile)
# ─────────────────────────────────────────────────────────────────────

class TestContracts:
    def test_profile_campos_essenciais(self):
        from mirofish.social.contracts import OasisAgentProfile
        p = OasisAgentProfile(user_id=1, user_name="u1", name="Ana",
                              bio="bio", persona="persona")
        assert p.karma == 1000
        assert p.follower_count == 150
        assert p.statuses_count == 500

    def test_to_twitter_format_username(self):
        from mirofish.social.contracts import OasisAgentProfile
        p = OasisAgentProfile(user_id=7, user_name="user_007", name="Bruno",
                              bio="b", persona="p", follower_count=999)
        tw = p.to_twitter_format()
        assert tw["username"] == "user_007"
        assert tw["follower_count"] == 999

    def test_to_reddit_karma(self):
        from mirofish.social.contracts import OasisAgentProfile
        p = OasisAgentProfile(user_id=3, user_name="u3", name="Carla",
                              bio="b", persona="p", karma=4321)
        rd = p.to_reddit_format()
        assert rd["karma"] == 4321
        assert rd["username"] == "u3"

    def test_simulation_parameters_roundtrip(self):
        from mirofish.social.contracts import SimulationParameters
        sp = SimulationParameters(
            simulation_id="sim_x",
            simulation_requirement="teste",
            agent_configs=[],
        )
        data = sp.to_dict()
        back = SimulationParameters.from_dict(data)
        assert back.simulation_id == "sim_x"
        assert back.time_config.total_simulation_hours == 72


# ─────────────────────────────────────────────────────────────────────
# R-976.3 — Geração determinística de perfis
# ─────────────────────────────────────────────────────────────────────

class TestProfileGenerator:
    def test_extract_topics(self):
        from mirofish.social.profiles import SimulationProfileGenerator
        g = SimulationProfileGenerator(DOC, n_agents=5, seed=1)
        topics = g.extract_topics()
        assert isinstance(topics, list) and topics

    def test_generate_n_heterogeneos(self):
        from mirofish.social.profiles import SimulationProfileGenerator
        g = SimulationProfileGenerator(DOC, n_agents=8, seed=42)
        profiles = g.generate()
        assert len(profiles) == 8
        stances = {p.stance for p in profiles}
        # 4 posturas cíclicas com 8 agentes → pelo menos 3 distintas
        assert len(stances) >= 3
        assert all(-1.0 <= p.sentiment_bias <= 1.0 for p in profiles)

    def test_determinismo_seed(self):
        from mirofish.social.profiles import SimulationProfileGenerator
        g1 = SimulationProfileGenerator(DOC, n_agents=10, seed=42)
        g2 = SimulationProfileGenerator(DOC, n_agents=10, seed=42)
        p1 = g1.generate()
        p2 = g2.generate()
        assert [p.to_dict() for p in p1] == [p.to_dict() for p in p2]


# ─────────────────────────────────────────────────────────────────────
# R-976.4 / R-976.5 — Motor: rounds, ações, sentimento, polarização
# ─────────────────────────────────────────────────────────────────────

def _make_result(seed=42, echo=0.5, n_agents=6, rounds=10):
    from mirofish.social.contracts import (
        EventConfig, PlatformConfig, SimulationParameters, TimeSimulationConfig,
    )
    from mirofish.social.profiles import SimulationProfileGenerator
    from mirofish.social.engine import SocialSimulationEngine

    g = SimulationProfileGenerator(DOC, n_agents=n_agents, seed=seed)
    profiles = g.generate()
    params = SimulationParameters(
        simulation_id=f"sim_p_{seed}",
        event_config=EventConfig(hot_topics=g.extract_topics()),
        twitter_config=PlatformConfig(platform="twitter", echo_chamber_strength=echo),
        time_config=TimeSimulationConfig(total_simulation_hours=rounds, minutes_per_round=60),
    )
    engine = SocialSimulationEngine(profiles, params, seed=seed)
    return engine, engine.run(rounds=rounds)


class TestEngine:
    def test_rounds_e_acoes(self):
        engine, result = _make_result()
        assert len(result.rounds) == 10
        all_actions = [a for r in result.rounds for a in r.actions]
        assert all_actions
        kinds = {a.action_type for a in all_actions}
        assert kinds <= set(["CREATE_POST", "LIKE_POST", "REPOST", "QUOTE_POST", "DO_NOTHING"])

    def test_sentimento_no_intervalo(self):
        engine, result = _make_result()
        for r in result.rounds:
            if r.actions:
                assert -1.0 <= r.avg_sentiment <= 1.0
        for v in result.final_opinions.values():
            assert -1.0 <= v <= 1.0

    def test_determinismo_engine(self):
        r1 = _make_result(seed=7)[1]
        r2 = _make_result(seed=7)[1]
        # INV-976.2: ações e opiniões determinísticas (não timestamps decorativos)
        assert [x.to_dict() for x in r1.rounds] == [x.to_dict() for x in r2.rounds]
        assert r1.final_opinions == r2.final_opinions

    def test_polarizacao_echo_alta(self):
        # Echo alto + janelas separadas → desvio aumenta (polarização)
        _, low = _make_result(seed=11, echo=0.1, n_agents=12, rounds=20)
        _, high = _make_result(seed=11, echo=0.9, n_agents=12, rounds=20)
        sd_low = _std(list(low.final_opinions.values()))
        sd_high = _std(list(high.final_opinions.values()))
        assert sd_high > sd_low

    def test_persistencia(self):
        engine, result = _make_result()
        path = engine.save(result)
        assert os.path.isfile(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["simulation_id"] == result.simulation_id
        loaded = engine.load(result.simulation_id)
        assert loaded.completed is True
        assert len(loaded.rounds) == len(result.rounds)


def _std(values):
    n = len(values)
    if n == 0:
        return 0.0
    mean = sum(values) / n
    return (sum((v - mean) ** 2 for v in values) / n) ** 0.5


# ─────────────────────────────────────────────────────────────────────
# R-976.7 — ReportAgent
# ─────────────────────────────────────────────────────────────────────

class TestReport:
    def test_markdown_secoes(self):
        from mirofish.social.report import SocialReportGenerator
        _, result = _make_result()
        md = SocialReportGenerator(result).generate()
        for section in ["# Relatório", "## Objetivo", "## Metodologia",
                        "## Agentes", "## Linha do Tempo", "## Sentimento",
                        "## Conclusão"]:
            assert section in md

    def test_conclusao_sem_invencao(self):
        from mirofish.social.report import SocialReportGenerator
        _, result = _make_result()
        md = SocialReportGenerator(result).generate()
        # Anti-overclaim: o relatório declara que NÃO é pesquisa com humanos
        assert "não constitui pesquisa empírica" in md


# ─────────────────────────────────────────────────────────────────────
# R-976.8 — Integração orquestrador
# ─────────────────────────────────────────────────────────────────────

class TestOrchestrator:
    def test_mirofish_simulate_resumo(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator()
        resumo = orch.mirofish_simulate(DOC, n_agents=4, rounds=5, seed=9,
                                        requirement="teste integração")
        assert resumo["simulation_id"]
        assert resumo["agents"] == 4
        assert resumo["rounds"] == 5
        assert "final_sentiment" in resumo
        assert "## Conclusão" in resumo["report_md"]


# ─────────────────────────────────────────────────────────────────────
# R-976.9 — Driver externo fail-closed
# ─────────────────────────────────────────────────────────────────────

class TestDriver:
    def test_unavailable_reason_clara(self, monkeypatch):
        import integrations.mirofish_offline as driver_mod
        monkeypatch.setattr(driver_mod, "DEFAULT_DIR", "")
        monkeypatch.setattr(driver_mod, "FALLBACK_DIRS", [])
        st = driver_mod.detect_service()
        assert st.available is False
        assert "não encontrado" in st.reason or "MIROFISH_OFFLINE_DIR" in st.reason

    def test_driver_check_fail_closed(self, monkeypatch):
        import integrations.mirofish_offline as driver_mod
        monkeypatch.setattr(driver_mod, "DEFAULT_DIR", "")
        monkeypatch.setattr(driver_mod, "FALLBACK_DIRS", [])
        driver = driver_mod.MiroFishOfflineDriver()
        check = driver.check()
        assert check["ok"] is False
        assert check["available"] is False
        assert check["local_engine_available"] is True

    def test_prepare_exige_servico_real(self, monkeypatch):
        import integrations.mirofish_offline as driver_mod
        monkeypatch.setattr(driver_mod, "DEFAULT_DIR", "")
        monkeypatch.setattr(driver_mod, "FALLBACK_DIRS", [])
        driver = driver_mod.MiroFishOfflineDriver()
        with pytest.raises(RuntimeError):
            driver.prepare(DOC)

    def test_detecta_servico_informado(self, tmp_path, monkeypatch):
        import integrations.mirofish_offline as driver_mod
        backend = tmp_path / "backend"
        backend.mkdir()
        (backend / "run.py").write_text("pass")
        driver = driver_mod.MiroFishOfflineDriver(service_dir=str(tmp_path))
        st = driver.status
        assert st.available is True
        assert st.backend_entry == str(backend / "run.py")


# ─────────────────────────────────────────────────────────────────────
# R-976.11 — Banca editorial (revisores especialistas)
# ─────────────────────────────────────────────────────────────────────

class TestBanca:
    def test_gera_membros_por_criterio(self):
        from mirofish.social.banca import BancaProfileGenerator, CRITERIA
        g = BancaProfileGenerator(DOC, n_members=6, seed=42)
        members = g.generate()
        assert len(members) == 6
        criteria = {m.criterion for m in members}
        assert len(criteria) >= 4  # cíclico sobre 6 critérios
        assert all(m.position in ("rigoroso", "equilibrado", "entusiasta", "cético")
                   for m in members)

    def test_verdict_faixas(self):
        from mirofish.social.banca import banca_verdict
        assert banca_verdict(0.9)[0] == "ACEITAR"
        assert banca_verdict(0.4)[0] == "REVISÕES MENORES"
        assert banca_verdict(0.0)[0] == "REVISÕES MAIORES"
        assert banca_verdict(-0.9)[0] == "REJEITAR"

    def test_simulacao_banca_completa(self):
        """Banca simula opinião sobre o manuscrito → sentimento + veredito."""
        from mirofish.social.banca import BancaProfileGenerator, summarize_banca
        from mirofish.social.contracts import (
            EventConfig, PlatformConfig, SimulationParameters, TimeSimulationConfig,
        )
        from mirofish.social.engine import SocialSimulationEngine

        g = BancaProfileGenerator(DOC, n_members=8, seed=7)
        members = g.generate()
        profiles = [m.profile for m in members]
        params = SimulationParameters(
            simulation_id="banca_sim_1",
            simulation_requirement="avaliar manuscrito de pesquisa",
            event_config=EventConfig(hot_topics=["metodologia", "estatística"]),
            twitter_config=PlatformConfig(platform="twitter", echo_chamber_strength=0.4),
            time_config=TimeSimulationConfig(total_simulation_hours=10, minutes_per_round=60),
        )
        engine = SocialSimulationEngine(profiles, params, seed=7)
        result = engine.run(rounds=10)
        resumo = summarize_banca(members, result.final_opinions)
        assert "verdict" in resumo
        assert resumo["final_sentiment"] is not None
        assert "disclaimer" in resumo          # anti-overclaim obrigatório
        assert "SIMULAÇÃO" in resumo["disclaimer"]

    def test_verdict_rigoroso_tende_mais_baixo(self):
        """Banca inteira rigorosa tende a sentimento menor que entusiasta."""
        from mirofish.social.banca import BancaProfileGenerator, summarize_banca
        from mirofish.social.contracts import (
            EventConfig, PlatformConfig, SimulationParameters, TimeSimulationConfig,
        )
        from mirofish.social.engine import SocialSimulationEngine

        def run_banca(positions):
            members = []
            g = BancaProfileGenerator(DOC, n_members=7, seed=5)
            generated = g.generate()
            # reatribui posições dos critérios cíclicos
            for i, m in enumerate(generated):
                pos = positions[i % len(positions)]
                from mirofish.social.banca import _bias_from_position, _stance_from_position
                m.position = pos
                m.profile.sentiment_bias = _bias_from_position(pos)
                m.profile.stance = _stance_from_position(pos)
                members.append(m)
            profiles = [m.profile for m in members]
            params = SimulationParameters(
                simulation_id="banca_pos",
                event_config=EventConfig(hot_topics=["m"]),
                twitter_config=PlatformConfig(platform="twitter", echo_chamber_strength=0.3),
                time_config=TimeSimulationConfig(total_simulation_hours=8, minutes_per_round=60),
            )
            result = SocialSimulationEngine(profiles, params, seed=5).run(rounds=8)
            return summarize_banca(members, result.final_opinions)

        ent = run_banca(["entusiasta"] * 7)
        rig = run_banca(["rigoroso"] * 7)
        assert rig["final_sentiment"] < ent["final_sentiment"]