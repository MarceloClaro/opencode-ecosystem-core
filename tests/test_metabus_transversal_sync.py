# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-934: integração transversal ao MetaBus."""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_oqs_publishes_metabus_event():
    from mci.metabus import metabus
    from mci.oqs import run_oqs_scanner

    marker = str(uuid.uuid4())
    run_oqs_scanner(f"Problema com lacunas conceituais {marker}", context={"marker": marker})
    events = metabus.get_recent_events(limit=30, topic_prefix="oqs.")
    assert any(e["payload"].get("marker") == marker for e in events)


def test_vsee_publishes_metabus_event():
    from mci.metabus import metabus
    from mci.vsee import run_vsee_router

    marker = str(uuid.uuid4())
    run_vsee_router(lambda ctx: {"ok": True, "marker": marker}, context={"marker": marker})
    events = metabus.get_recent_events(limit=30, topic_prefix="vsee.")
    assert any(e["payload"].get("marker") == marker for e in events)


def test_egs_publishes_metabus_event():
    from mci.metabus import metabus
    from mci.egs import run_egs_scanner

    marker = str(uuid.uuid4())
    run_egs_scanner(f"conteúdo com tensão ética {marker}", context={"marker": marker, "critical_domain": True})
    events = metabus.get_recent_events(limit=30, topic_prefix="egs.")
    assert any(e["payload"].get("marker") == marker for e in events)


def test_scientific_rag_publishes_event_and_memory_search_works():
    from mci.metabus import metabus
    from rag import ScientificDocument, ScientificRAG

    rag = ScientificRAG(min_score=0.05)
    rag.index([
        ScientificDocument(
            doc_id="pearl-2009",
            title="Causality",
            authors=["Pearl"],
            year=2009,
            source="book",
            text="Correlação não implica causalidade; intervenção e confounders importam.",
        )
    ])
    answer = rag.answer("como distinguir correlação de causalidade?")
    events = metabus.get_recent_events(limit=30, topic_prefix="rag.")
    assert any(e["topic"] == "rag.answer.generated" for e in events)

    metabus.memory.add_reflection(
        agent_id="test.rag",
        task_context="grounding científico",
        reflection=answer["answer"],
        score=0.8,
    )
    found = metabus.search_memory("correlação causalidade", limit=5)
    assert len(found) >= 1


def test_superhuman_suite_publishes_event():
    from mci.metabus import metabus
    from benchmarks.scientific_reasoning.superhuman_suite import run_superhuman_suite

    marker = str(uuid.uuid4())
    report = run_superhuman_suite(rag=None, external_validation=False, context={"marker": marker})
    events = metabus.get_recent_events(limit=30, topic_prefix="superhuman.")
    assert report["tier"] in {"base", "research_grade", "superhuman_candidate", "superhuman_verified"}
    assert any(e["payload"].get("marker") == marker for e in events)


def test_mirofish_publishes_prediction_event():
    from mci.metabus import metabus
    from mirofish.swarm import MiroFishSwarm

    marker = str(uuid.uuid4())
    swarm = MiroFishSwarm(n_agents=5, seed=42)
    swarm.predict(f"Pergunta de teste {marker}", signal=0.6)
    events = metabus.get_recent_events(limit=30, topic_prefix="mirofish.")
    assert any(marker in str(e["payload"].get("question", "")) for e in events)


def test_gametheory_publishes_events():
    from mci.metabus import metabus
    from gametheory import PayoffMatrix, MetaReasoner

    PayoffMatrix.prisoners_dilemma().find_nash_equilibria()
    MetaReasoner().select_for_context({"topic": "conflito e negociação estratégica"})
    events = metabus.get_recent_events(limit=50, topic_prefix="gametheory.")
    topics = {e["topic"] for e in events}
    assert "gametheory.nash.computed" in topics
    assert "gametheory.meta_reason.selected" in topics


def test_publishing_and_research_publish_events(tmp_path, monkeypatch):
    from mci.metabus import metabus
    from publishing.production import ScientificProduction
    from research.hub import ResearchHub

    # Publishing
    monkeypatch.setattr("publishing.production._ensure_desktop_shortcut", lambda *_args, **_kwargs: "")
    prod = ScientificProduction("Teste MetaBus", template="artigo", output_root=str(tmp_path / "prod"))
    prod.build("Conteúdo mínimo para produção científica.")

    # Research (sem rede)
    hub = ResearchHub("tema de teste", production_folder=str(tmp_path / "research"), platforms=[])
    monkeypatch.setattr(hub.searcher, "search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(hub, "_write_references", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(hub, "_write_repos", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(hub, "_hunt_figures", lambda *_args, **_kwargs: {"figuras_extraidas": 0, "catalogo": ""})
    monkeypatch.setattr(hub.osint, "analyze_references", lambda *_args, **_kwargs: {})
    hub.run(max_papers=1, limit_per_platform=1, download=False)

    events = metabus.get_recent_events(limit=80)
    topics = {e["topic"] for e in events}
    assert "publishing.build.completed" in topics
    assert "research.pipeline.completed" in topics


def test_spec_registry_and_verifier_publish_events():
    from mci.metabus import metabus
    from sdd.spec_engine import spec_registry, spec_verifier

    spec = spec_registry.create_task_spec(
        title="Teste MetaBus SDD",
        objective="Verificar publicação de eventos SDD",
        criteria_descriptions=["output contém ok"],
    )
    spec.criteria[0].check_fn = lambda output: isinstance(output, str) and "ok" in output
    spec_verifier.verify(spec.spec_id, "ok")
    events = metabus.get_recent_events(limit=50, topic_prefix="sdd.")
    topics = {e["topic"] for e in events}
    assert "sdd.spec.created" in topics
    assert "sdd.spec.verified" in topics
