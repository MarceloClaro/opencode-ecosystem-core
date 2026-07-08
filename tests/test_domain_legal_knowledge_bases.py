# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-931: knowledge bases jurídicas segmentadas por ramo."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_domain_legal_documents_cover_all_7_domains():
    from legal.knowledge_base import DOMAIN_LEGAL_DOCUMENTS

    assert set(DOMAIN_LEGAL_DOCUMENTS.keys()) == {
        "penal",
        "trabalhista",
        "tributario",
        "empresarial",
        "administrativo",
        "ambiental",
        "digital_lgpd",
    }


def test_build_domain_knowledge_base_digital_lgpd():
    from legal.knowledge_base import build_domain_knowledge_base

    kb = build_domain_knowledge_base("digital_lgpd")
    docs = kb.list_documents(domain_id="digital_lgpd")

    assert len(docs) >= 1
    assert any("lgpd" in " ".join(doc.keywords).lower() or "lgpd" in doc.content.lower() for doc in docs)


def test_domain_search_filters_tributario_documents():
    from legal.knowledge_base import build_domain_knowledge_base

    kb = build_domain_knowledge_base("tributario")
    results = kb.search("execução fiscal crédito tributário", domain_id="tributario")

    assert len(results) >= 1
    top_doc = results[0][0]
    joined = " ".join(top_doc.keywords).lower() + " " + top_doc.content.lower()
    assert "tribut" in joined or "execução fiscal" in joined


def test_route_domain_knowledge_base_uses_router():
    from legal.knowledge_base import route_domain_knowledge_base

    routed = route_domain_knowledge_base("habeas corpus e prisão preventiva com nulidade da prova")
    assert routed["domain_id"] == "penal"
    assert routed["knowledge_base"].count() >= 1


def test_general_knowledge_base_remains_backward_compatible():
    from legal import LegalKnowledgeBase

    kb = LegalKnowledgeBase()
    assert kb.count() >= 6
    results = kb.search("responsabilidade civil dano moral")
    assert len(results) >= 1
