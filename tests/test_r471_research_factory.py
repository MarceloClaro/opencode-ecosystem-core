"""SPEC-935-R471 (M1) — Research Factory: meta-graph de fábrica de pesquisa.

Suíte RED/GREEN: somente mocks/fachadas in-memory; sem download real de
conteúdo sob paywall, sem credenciais, sem subprocess real, sem shell.
Cobre CA1, CA2, CA8, CA9, CA10 da SPEC-935-R471 (módulo M1).

Entrypoints do meta-graph (inspirado no open-swe, langchain-ai/open-swe):
  - research  : planeja e executa estudo (investigar -> compor manuscrito)
  - review    : revisão grounded no manuscrito gerado
  - analyze   : aprende preferências de revisão a partir de feedback histórico
  - chat      : QA read-only sobre o estado da thread, sem modificar artefatos
  - schedule  : tarefas recorrentes de pesquisa com execução por vencimento
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from research_factory.analyzer import ReviewStyleAnalyzer
from research_factory.audit import AuditLog, AuditEntry
from research_factory.graph import ResearchFactory
from research_factory.scheduler import ResearchScheduler
from research_factory.threads import ResearchThread, ThreadStore

ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# FIXTURES (mocks determinísticos — sem rede, sem credenciais)
# ============================================================

def build_manuscript(sections=("Introdução", "Método", "Resultados", "Discussão")):
    return "\n\n".join(f"## {s}\n\nConteúdo de {s.lower()}." for s in sections)


def build_researcher():
    """Fachada de investigação que devolve seções determinísticas (mock)."""
    def researcher(topic, question=None):
        return {
            "topic": topic,
            "question": question or f"Pergunta sobre {topic}",
            "sections": [
                {"heading": "Introdução", "text": f"Contexto de {topic}."},
                {"heading": "Método", "text": "Pipeline descrito com passos."},
                {"heading": "Resultados", "text": "Achados do estudo."},
            ],
            "citations": [{"authors": ["A", "B"], "year": 2026, "title": "Fonte"}
                          for _ in range(3)],
            "sources_used": ["mock-scholar"],
        }
    return researcher


def build_composer():
    """Fachada que monta o manuscrito a partir do relatório da investigação."""
    def composer(report):
        parts = [f"# {report['topic']} — Manuscrito", ""]
        for sec in report["sections"]:
            parts.append(f"## {sec['heading']}")
            parts.append(sec["text"])
        parts.append("## Referências")
        for i, c in enumerate(report["citations"], 1):
            parts.append(
                f"[{i}] {', '.join(c['authors'])} ({c['year']}). {c['title']}."
            )
        return "\n".join(parts)
    return composer


def build_reviewer():
    """Revisor grounded: consome apenas o manuscrito e devolve comentários."""
    def reviewer(manuscript):
        comments = []
        if "## Resultados" not in manuscript:
            comments.append({"severity": "blocker",
                             "section": "Resultados",
                             "text": "A seção de resultados está ausente."})
        if "## Referências" not in manuscript:
            comments.append({"severity": "blocker",
                             "section": "Referências",
                             "text": "Referências ausentes."})
        if len(manuscript) < 200:
            comments.append({"severity": "minor",
                             "section": "geral",
                             "text": "Manuscrito muito curto."})
        return {"decision": "reject" if any(c["severity"] == "blocker"
                                            for c in comments)
                             else "approve",
                "comments": comments,
                "score": 0.0 if comments else 10.0}
    return reviewer


@pytest.fixture
def factory(tmp_path):
    return ResearchFactory(
        thread_store=ThreadStore(root=tmp_path / "threads"),
        researcher=build_researcher(),
        composer=build_composer(),
        reviewer=build_reviewer(),
        audit=AuditLog(root=tmp_path / "audit"),
        scheduler=ResearchScheduler(root=tmp_path / "scheduler"),
    )


# ============================================================
# CA: Thread e estado durável
# ============================================================

def test_thread_creation_persists_and_reloads(tmp_path):
    store = ThreadStore(root=tmp_path / "threads")
    thread = store.create(topic="Resiliência em pesquisa científica",
                          workspace=str(tmp_path / "ws"))
    assert thread.id
    assert thread.topic == "Resiliência em pesquisa científica"
    assert thread.invocations == []

    # Persistência em disco e reload preservando estado
    assert (tmp_path / "threads" / f"{thread.id}.json").exists()
    reloaded = store.load(thread.id)
    assert reloaded.id == thread.id
    assert reloaded.topic == thread.topic
    assert reloaded.invocations == []

    # Invocações subsequentes persistem
    thread.add_invocation(entrypoint="research", status="ok")
    saved = store.save(thread)
    again = store.load(thread.id)
    assert len(again.invocations) == 1
    assert again.invocations[0]["entrypoint"] == "research"


def test_thread_store_lists_and_unknown_load_raises(tmp_path):
    store = ThreadStore(root=tmp_path / "threads")
    store.create(topic="T1")
    store.create(topic="T2")
    assert len(store.list_all()) == 2
    with pytest.raises(KeyError):
        store.load("nao-existe")


# ============================================================
# CA: Entrypoint research (Agent)
# ============================================================

def test_research_entrypoint_produces_manuscript_and_audit(factory):
    thread = factory.thread_store.create(topic="IA para revisão de literatura")
    result = factory.research(thread.id, question="Qual o estado da arte?")
    assert result["manuscript"].startswith("# IA para revisão de literatura")
    assert "## Resultados" in result["manuscript"]
    assert "## Referências" in result["manuscript"]
    # Auditoria registrou a etapa
    entries = factory.audit.entries(thread_id=thread.id)
    assert any(e.entrypoint == "research" and e.stage == "investigate"
               for e in entries)
    assert any(e.entrypoint == "research" and e.stage == "compose"
               for e in entries)


def test_research_entrypoint_second_invocation_same_thread(factory):
    thread = factory.thread_store.create(topic="Tópico A")
    factory.research(thread.id, question="Q1")
    factory.research(thread.id, question="Q2")
    loaded = factory.thread_store.load(thread.id)
    assert len(loaded.invocations) == 2


# ============================================================
# CA: Entrypoint review (Reviewer grounded)
# ============================================================

def test_review_entrypoint_is_grounded_and_decides(factory):
    thread = factory.thread_store.create(topic="Estudo")
    r = factory.research(thread.id, question="Q")
    review = factory.review(thread.id, manuscript=r["manuscript"])
    # Manuscrito completo -> aprovação; faltando -> rejeição
    assert review["decision"] in {"approve", "reject"}
    assert "comments" in review
    assert isinstance(review["score"], (int, float))
    # Revisão registrada como invocação e auditoria
    loaded = factory.thread_store.load(thread.id)
    assert loaded.invocations[-1]["entrypoint"] == "review"


def test_review_entrypoint_rejects_incomplete_manuscript(factory):
    thread = factory.thread_store.create(topic="Estudo")
    incomplete = "## Introdução\napenas isso."
    review = factory.review(thread.id, manuscript=incomplete)
    assert review["decision"] == "reject"
    assert any(c["severity"] == "blocker" for c in review["comments"])


# ============================================================
# CA: Entrypoint analyze (Analyzer aprende preferências)
# ============================================================

def test_analyzer_learns_rules_from_feedback(tmp_path):
    analyzer = ReviewStyleAnalyzer(root=tmp_path / "analyzer")
    analyzer.add_example(
        manuscript=build_manuscript(sections=("Introdução", "Método")),
        feedback={"decision": "reject",
                  "comments": [{
                      "severity": "blocker",
                      "section": "Resultados",
                      "text": "Resultados ausentes — obrigatório em manuscrito.",
                  }]},
        accepted="sim",
    )
    analyzer.add_example(
        manuscript=build_manuscript(),
        feedback={"decision": "approve", "comments": []},
        accepted="sim",
    )
    rules = analyzer.rules()
    assert any("Resultados" in r["section"]
               for r in rules if r["kind"] == "required_section")
    # Regra aplicada: manuscrito sem Resultados é marcado
    flagged = analyzer.flag(build_manuscript(sections=("Introdução",)))
    assert any(r["kind"] == "required_section" for r in flagged)


def test_analyzer_persists_rules(tmp_path):
    analyzer = ReviewStyleAnalyzer(root=tmp_path / "analyzer")
    analyzer.add_example(
        manuscript=build_manuscript(),
        feedback={"decision": "approve", "comments": []},
        accepted="sim",
    )
    analyzer2 = ReviewStyleAnalyzer(root=tmp_path / "analyzer")
    assert len(analyzer2.rules()) == len(analyzer.rules())


# ============================================================
# CA: Entrypoint chat (read-only)
# ============================================================

def test_chat_entrypoint_is_readonly(factory):
    thread = factory.thread_store.create(topic="Estudo read-only")
    before = factory.thread_store.save(thread)
    answer = factory.chat(thread.id, question="Qual é o estado atual?")
    assert isinstance(answer, dict)
    assert "answer" in answer
    # Thread e artefatos inalterados (fora a invocação de QA)
    loaded = factory.thread_store.load(thread.id)
    assert len(loaded.invocations) == 1
    assert loaded.invocations[0]["entrypoint"] == "chat"


# ============================================================
# CA: Entrypoint schedule (recorrente)
# ============================================================

def test_scheduler_runs_due_tasks_once(tmp_path):
    scheduler = ResearchScheduler(root=tmp_path / "scheduler")
    calls = []

    def task():
        calls.append("run")

    scheduler.add(name="litreview", fn=task, interval_seconds=60.0)
    assert scheduler.run_due(now=10.0) == 1
    assert len(calls) == 1
    # Tarefa executada não roda de novo no mesmo instante
    assert scheduler.run_due(now=10.0) == 0
    assert len(calls) == 1


def test_scheduler_runs_again_after_interval(tmp_path):
    scheduler = ResearchScheduler(root=tmp_path / "scheduler")
    calls = []

    def task():
        calls.append("run")

    scheduler.add(name="litreview", fn=task, interval_seconds=60.0)
    scheduler.run_due(now=0.0)
    scheduler.run_due(now=59.0)
    assert len(calls) == 1
    scheduler.run_due(now=60.0)
    assert len(calls) == 2


def test_scheduler_persists_jobs(tmp_path):
    scheduler = ResearchScheduler(root=tmp_path / "scheduler")
    scheduler.add(name="jobpersist", fn=lambda: None, interval_seconds=10.0)
    scheduler2 = ResearchScheduler(root=tmp_path / "scheduler")
    assert any(j["name"] == "jobpersist" for j in scheduler2.jobs())


# ============================================================
# CA: Auditoria do ciclo completo (CA2) e anti-overclaim (CA10)
# ============================================================

def test_full_cycle_audit_covers_five_stages(factory):
    thread = factory.thread_store.create(topic="Ciclo completo")
    r = factory.research(thread.id, question="Q")
    factory.review(thread.id, manuscript=r["manuscript"])
    factory.analyze(thread.id, feedback={"decision": "approve",
                                         "comments": []},
                    accepted="sim")
    factory.chat(thread.id, question="Resumo?")
    factory.schedule(thread.id, name="diario", interval_seconds=3600.0,
                     fn=lambda: None)
    report = factory.audit.report(thread_id=thread.id)
    stages = {e["stage"] for e in report["entries"]}
    assert {"investigate", "compose", "review", "analyze", "chat",
            "schedule"} <= stages
    for e in report["entries"]:
        assert e["thread_id"] == thread.id
        assert e["timestamp_utc"] > 0
        assert e["hash_sha256"]
        # Nunca declarar superação/Qualis/verificado sem validação externa
        text = json.dumps(e).lower()
        for banned in ("qualis a1", "verificado", "superhuman", "superação"):
            assert banned not in text


def test_audit_sha256_is_deterministic():
    entry = AuditEntry(stage="compose", entrypoint="research",
                       thread_id="t1", artifact=b"abc")
    assert entry.hash_sha256 == hashlib.sha256(b"abc").hexdigest()


# ============================================================
# CA 1/8/9/10: política e higiene do módulo
# ============================================================

def test_factory_ca1_defaults_do_not_change_research_policy():
    """Criação da factory não altera fontes/padrões do pipeline nativo.

    O núcleo aberto permanece registrado e nenhum resolvedor Sci-Hub entra
    como fonte padrão (mesmo espírito da R470, ancorado no módulo nativo:
    as fontes vivem em ``ALL_SEARCHERS`` no Core atual).
    """
    from research import searchers
    assert "openalex" in searchers.ALL_SEARCHERS
    assert "crossref" in searchers.ALL_SEARCHERS
    assert "europepmc" in searchers.ALL_SEARCHERS
    assert "arxiv" in searchers.ALL_SEARCHERS
    assert "sci-hub" not in searchers.ALL_SEARCHERS
    assert "scihub" not in searchers.ALL_SEARCHERS


def test_factory_hard_hygiene_no_shell_no_network_in_code():
    """Higiene estática: nenhum shell=True/subprocess/credencial no módulo."""
    from research_factory import analyzer, audit, graph, scheduler, threads
    for mod in (analyzer, audit, graph, scheduler, threads):
        tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            assert not isinstance(node, ast.Call) or not (
                isinstance(node.func, ast.Name)
                and node.func.id == "subprocess"
            )
            if isinstance(node, ast.keyword) and node.arg == "shell":
                assert node.value is None or node.value.value is False
        src = Path(mod.__file__).read_text(encoding="utf-8").lower()
        assert "api_key" not in src and "apikey" not in src
        assert "requests.get(" not in src and "urlopen(" not in src
        assert "token" not in src


def test_factory_imports_without_runtime_deps(factory):
    """Módulo importa sem depender de LLM/rede (uso com mocks)."""
    assert factory.thread_store is not None
    assert factory.audit is not None
    assert factory.scheduler is not None