"""Testes RED/GREEN da SPEC-935-R476 — Autonomia, Raciocínio e Pesquisa Open Science
na Research Factory (extensão da R471/M1).

Herméticos: sem rede, sem LLM real, sem z3/sympy obrigatórios (fallback determinístico).
"""
import pytest

from research_factory.autonomy import AutonomyCore, SelfSupervisionReport
from research_factory.reasoning import PlanConsistencyChecker, PlanValidationReport
from research_factory.search import (
    OPEN_SCIENCE_SOURCES,
    OpenScienceSearchOrchestrator,
    SearchReceipt,
)


# ---------------------------------------------------------------------------
# AUTONOMIA
# ---------------------------------------------------------------------------
class FakeMemory:
    def __init__(self, lessons=None):
        self.lessons = lessons or []

    def search_memory(self, topic=None, limit=None):
        return [{"id": f"lesson-{i}", "content": l} for i, l in enumerate(self.lessons)]


class TestAutonomyCore:
    def test_self_supervise_gera_plano_quando_ha_licoes(self):
        core = AutonomyCore(memory=FakeMemory(["não usar shell=True em execução externa"]))
        report = core.self_supervise(
            executed_actions=["research_factory.run(dataset=coorte)"],
        )
        assert isinstance(report, SelfSupervisionReport)
        assert report.actionable >= 0.5
        assert len(report.next_action_plan) >= 1
        assert report.lessons_found == 1

    def test_self_supervise_sem_licoes_plano_minimo(self):
        core = AutonomyCore(memory=FakeMemory([]))
        report = core.self_supervise(executed_actions=["a"])
        assert report.actionable == 0.0
        assert report.next_action_plan == []

    def test_rank_agents_ordenados_por_trust(self):
        core = AutonomyCore(trust_scores={"agent-a": 0.9, "agent-b": 0.4, "agent-c": 0.7})
        ranked = core.rank_agents(["agent-a", "agent-b", "agent-c"])
        assert ranked == ["agent-a", "agent-c", "agent-b"]

    def test_rank_agents_usa_trust_default_para_desconhecidos(self):
        core = AutonomyCore(trust_scores={"agent-a": 0.1}, default_trust=0.8)
        ranked = core.rank_agents(["agent-a", "agent-z"])
        assert ranked == ["agent-z", "agent-a"]

    def test_rank_agents_preserva_ordem_sem_preferencia_trust(self):
        core = AutonomyCore(trust_scores={"agent-a": 0.9, "agent-b": 0.1})
        ranked = core.rank_agents(["agent-a", "agent-b"], prefer_trust=False)
        assert ranked == ["agent-a", "agent-b"]

    def test_report_nao_declara_merito_qualitativo(self):
        core = AutonomyCore(memory=FakeMemory(["lição"]))
        payload = core.self_supervise(executed_actions=["a"]).to_dict()
        blob = " ".join(str(v) for v in payload.values()).lower()
        for banned in ("superhuman", "verificado", "qualis a1", "superação"):
            assert banned not in blob


# ---------------------------------------------------------------------------
# RACIOCÍNIO
# ---------------------------------------------------------------------------
class TestPlanConsistencyChecker:
    def test_grafo_aciclico_valido(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.check_acyclic({"a": ["b"], "b": ["c"], "c": []})
        assert report.valid is True
        assert report.cycles == [] or report.cycles == set()

    def test_ciclo_detectado(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.check_acyclic({"a": ["b"], "b": ["a"]})
        assert report.valid is False
        assert len(report.cycles) >= 1

    def test_auto_ciclo_detectado(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.check_acyclic({"a": ["a"]})
        assert report.valid is False

    def test_estatisticas_validas(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.validate_stats({
            "idade": {"n": 10, "min": 18, "max": 65, "mean": 40.0, "std": 12.0},
        })
        assert report.valid is True

    def test_media_fora_do_intervalo_invalida(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.validate_stats({
            "idade": {"n": 10, "min": 18, "max": 65, "mean": 80.0},
        })
        assert report.valid is False

    def test_desvio_negativo_invalido(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.validate_stats({"x": {"n": 5, "mean": 1.0, "std": -2.0}})
        assert report.valid is False

    def test_n_nao_positivo_invalido(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.validate_stats({"x": {"n": 0}})
        assert report.valid is False

    def test_deadlines_monotonicas_ok(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.check_deadlines({"a": 10, "b": 20, "c": 30})
        assert report.valid is True

    def test_deadline_regressiva_falha(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        report = chk.check_deadlines({"a": 30, "b": 20})
        assert report.valid is False

    def test_capabilities_reportam_reasoners(self):
        chk = PlanConsistencyChecker(use_z3=False, use_sympy=False)
        caps = chk.capabilities()
        assert caps["acyclic_checker"] == "dfs"
        assert "z3" in caps
        assert "sympy" in caps


# ---------------------------------------------------------------------------
# PESQUISA OPEN SCIENCE
# ---------------------------------------------------------------------------
class _FakeSearcher:
    def __init__(self, source, records, fail=False):
        self.source = source
        self.records = records
        self.fail = fail

    def search(self, query, limit_per_platform=5):
        if self.fail:
            raise RuntimeError(f"falhou fonte {self.source}")
        return [dict(r, source=self.source) for r in self.records][:limit_per_platform]


class _FakeFactory:
    def __init__(self, mapping):
        self.mapping = mapping

    def __call__(self, source):
        return self.mapping[source]


def _rec(title, source):
    return {"title": title, "source": source, "doi": f"10.1/{title}"}


class TestOpenScienceSearchOrchestrator:
    def test_failover_fonte_primaria_para_segunda(self):
        factory = _FakeFactory({
            "openalex": _FakeSearcher("openalex", [_rec("A", "openalex")], fail=True),
            "crossref": _FakeSearcher("crossref", [_rec("B", "crossref")]),
            "europepmc": _FakeSearcher("europepmc", [_rec("C", "europepmc")]),
            "arxiv": _FakeSearcher("arxiv", [_rec("D", "arxiv")]),
        })
        orch = OpenScienceSearchOrchestrator(searcher_factory=factory)
        receipt, records = orch.search("tema", limit_per_platform=2)
        assert isinstance(receipt, SearchReceipt)
        assert receipt.succeeded_source == "crossref"
        assert "openalex" in receipt.failed
        assert {"crossref", "europepmc", "arxiv"} <= set(receipt.succeeded)
        assert len(records) >= 1

    def test_agrega_registros_de_multiplas_fontes(self):
        factory = _FakeFactory({
            "openalex": _FakeSearcher("openalex", [_rec("A", "openalex")]),
            "crossref": _FakeSearcher("crossref", [_rec("B", "crossref")]),
            "europepmc": _FakeSearcher("europepmc", [_rec("C", "europepmc")]),
            "arxiv": _FakeSearcher("arxiv", [_rec("D", "arxiv")]),
        })
        orch = OpenScienceSearchOrchestrator(searcher_factory=factory)
        receipt, records = orch.search("tema", limit_per_platform=1)
        assert receipt.policy == "open_science_only"
        assert len(records) >= 3
        sources = {r["source"] for r in records}
        assert sources <= set(OPEN_SCIENCE_SOURCES)

    def test_fonte_fora_da_politica_bloqueada(self):
        factory = _FakeFactory({})
        orch = OpenScienceSearchOrchestrator(
            searcher_factory=factory,
            allowlist={"openalex"},
        )
        receipt, records = orch.search_with_sources("tema", sources=["sci-hub.org"])
        assert receipt.policy == "open_science_only"
        assert "sci-hub.org" in receipt.blocked
        assert records == []
        assert receipt.permitted_sources == {"openalex"}

    def test_politica_padrao_nunca_inclui_resolvedor_restrito(self):
        assert OPEN_SCIENCE_SOURCES == {"openalex", "crossref", "europepmc", "arxiv"}
        assert "sci-hub" not in OPEN_SCIENCE_SOURCES
        assert "scihub" not in OPEN_SCIENCE_SOURCES

    def test_receita_nao_declara_merito_qualitativo(self):
        factory = _FakeFactory({
            "openalex": _FakeSearcher("openalex", [_rec("A", "openalex")]),
        })
        orch = OpenScienceSearchOrchestrator(searcher_factory=factory, allowlist={"openalex"})
        receipt, _ = orch.search("tema")
        blob = " ".join(str(v) for v in receipt.to_dict().values()).lower()
        for banned in ("superhuman", "verificado", "qualis a1", "superação"):
            assert banned not in blob


# ---------------------------------------------------------------------------
# INTEGRAÇÃO NA FÁBRICA
# ---------------------------------------------------------------------------
class TestResearchFactoryExtensions:
    def _factory(self, tmp_path):
        from research_factory.audit import AuditLog
        from research_factory.graph import ResearchFactory
        from research_factory.scheduler import ResearchScheduler
        from research_factory.threads import ThreadStore

        return ResearchFactory(
            thread_store=ThreadStore(root=tmp_path / "threads"),
            researcher=lambda topic, question=None: {"topic": topic, "ok": True},
            composer=lambda report: "# Manuscrito\n" + report["topic"],
            reviewer=lambda ms: {"decision": "approve", "comments": []},
            audit=AuditLog(root=tmp_path / "audit"),
            scheduler=ResearchScheduler(root=tmp_path / "scheduler"),
        )

    def test_factory_expõe_autonomia_raciocinio_pesquisa(self, tmp_path):
        from research_factory.autonomy import AutonomyCore
        from research_factory.graph import ResearchFactory
        from research_factory.reasoning import PlanConsistencyChecker
        from research_factory.search import OpenScienceSearchOrchestrator

        factory = self._factory(tmp_path)
        assert isinstance(factory.autonomy, AutonomyCore)
        assert isinstance(factory.reasoning, PlanConsistencyChecker)
        assert isinstance(factory.search, OpenScienceSearchOrchestrator)
        assert factory.self_supervise is not None

    def test_factory_self_supervise_apos_execucao(self, tmp_path):
        factory = self._factory(tmp_path)
        factory.autonomy = AutonomyCore(memory=FakeMemory(["lição pós-teste"]))
        report = factory.self_supervise(executed_actions=["run(research)"])
        assert report.lessons_found >= 1
        assert len(report.next_action_plan) >= 1