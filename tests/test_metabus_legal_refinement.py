# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-933: refinamento jurídico do MetaBus."""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_publish_legal_event_and_recent_events_filtering():
    from mci.metabus import metabus

    marker = str(uuid.uuid4())
    metabus.publish_legal_event(
        "impact_assessed",
        domain_id="digital_lgpd",
        payload={"marker": marker},
        source_agent="test.suite",
    )

    recent = metabus.get_recent_events(limit=20, topic_prefix="legal.", source="test.suite")
    assert any(e["payload"].get("marker") == marker for e in recent)
    assert all(e["topic"].startswith("legal.") for e in recent)


def test_upsert_semantic_topic_accumulates_lessons():
    from mci.metabus import metabus

    topic = f"test.topic.{uuid.uuid4()}"
    metabus.memory.upsert_semantic_topic(topic, lesson="lição 1", metadata={"a": 1})
    metabus.memory.upsert_semantic_topic(topic, lesson="lição 2", metadata={"b": 2})

    semantic = metabus.memory.semantic[topic]
    assert "lição 1" in semantic["lessons"]
    assert "lição 2" in semantic["lessons"]
    assert semantic["metadata"]["a"] == 1
    assert semantic["metadata"]["b"] == 2


def test_update_domain_confidence_ledger():
    from mci.metabus import metabus

    key = "legal:digital_lgpd"
    before = metabus.memory.confidence_ledger.get(key, 0.5)
    updated = metabus.memory.update_domain_confidence("digital_lgpd", 0.9)
    assert 0.0 <= updated <= 1.0
    assert metabus.memory.confidence_ledger[key] == updated
    assert updated != before or before == 0.9


def test_orchestrator_diagnose_publishes_legal_event():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from mci.metabus import metabus

    orch = MarceloClaroOrchestrator()
    marker = str(uuid.uuid4())
    orch.diagnose(
        corpus="Dados pessoais, consentimento, base legal, revisão jurídica e cautela.",
        domain="direito digital",
        include_legal_impact=True,
        legal_params={
            "titulo": "Teste Legal Event",
            "resumo": "LGPD e compliance.",
            "metodologia": "anonimização",
            "resultados": "mitigação",
            "conclusoes": "abstenção quando necessário",
            "palavras_chave": ["lgpd"],
            "domain_id": "digital_lgpd",
            "marker": marker,
        },
    )
    recent = metabus.get_recent_events(limit=50, topic_prefix="legal.impact_assessed")
    assert any(e["payload"].get("marker") == marker for e in recent)
