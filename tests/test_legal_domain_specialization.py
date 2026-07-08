# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-927: especialização jurídica por domínio."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_legal_domain_profiles_count_and_keys():
    from legal.specializations import LEGAL_DOMAIN_PROFILES

    assert set(LEGAL_DOMAIN_PROFILES.keys()) == {
        "penal",
        "trabalhista",
        "tributario",
        "empresarial",
        "administrativo",
        "ambiental",
        "digital_lgpd",
    }


def test_route_legal_domain_examples():
    from legal.specializations import route_legal_domain

    assert route_legal_domain("habeas corpus, prisão preventiva e dosimetria da pena").domain_id == "penal"
    assert route_legal_domain("verbas rescisórias, justa causa e horas extras").domain_id == "trabalhista"
    assert route_legal_domain("execução fiscal, crédito tributário e ICMS").domain_id == "tributario"
    assert route_legal_domain("sociedade limitada, recuperação judicial e governança corporativa").domain_id == "empresarial"
    assert route_legal_domain("licitação, ato administrativo e improbidade").domain_id == "administrativo"
    assert route_legal_domain("licenciamento ambiental, dano ecológico e EIA/RIMA").domain_id == "ambiental"
    assert route_legal_domain("dados pessoais, consentimento, controlador e lgpd").domain_id == "digital_lgpd"


def test_get_legal_domain_profile_contains_core_statutes():
    from legal.specializations import get_legal_domain_profile

    penal = get_legal_domain_profile("penal")
    digital = get_legal_domain_profile("digital_lgpd")

    assert penal is not None and any("código penal" in s.lower() for s in penal.core_statutes)
    assert digital is not None and any("lgpd" in s.lower() for s in digital.core_statutes)


def test_build_domain_specialist_agent():
    from legal.specializations import build_domain_specialist_agent

    agent = build_domain_specialist_agent("tributario")
    assert agent.id == "auxjuris_tributario_specialist"
    assert "tributário" in agent.name.lower() or "tributario" in agent.name.lower()
    assert "legal" in agent.to_a2a_card()["capabilities"]
    assert "tributario" in agent.to_a2a_card()["capabilities"]


def test_assess_domain_coverage_bounds():
    from legal.specializations import assess_domain_coverage

    score = assess_domain_coverage(
        "A pesquisa discute compliance, consentimento, dados pessoais e base legal na LGPD.",
        "digital_lgpd",
    )
    assert 0.0 <= score <= 100.0


def test_digital_lgpd_coverage_beats_neutral_text():
    from legal.specializations import assess_domain_coverage

    legal_score = assess_domain_coverage(
        "Tratamento de dados pessoais, consentimento, controlador, operador e anonimização conforme LGPD.",
        "digital_lgpd",
    )
    neutral_score = assess_domain_coverage(
        "Sistema geral de software com foco em performance e escalabilidade.",
        "digital_lgpd",
    )
    assert legal_score > neutral_score
