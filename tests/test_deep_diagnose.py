# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-020 Diagnóstico Profundo.

Cobre: roadmap evolutivo M1–M5, priorização epistemológica,
gerador de sucessores plausíveis e integração com o orquestrador.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanners.pipeline import DiagnosticPipeline  # noqa: E402
from scanners.epistemic_prioritizer import (  # noqa: E402
    EpistemicPrioritizer, EpistemicOpportunity)
from scanners.successor_generator import (  # noqa: E402
    SuccessorGenerator, SuccessorHypothesis)


CORPUS = (
    "Este manuscrito investiga metacognição em sistemas multiagentes com "
    "arquitetura transformer, atenção multi-cabeça, memória hierárquica, "
    "teoria dos jogos e economia de tokens. Faltam análises estatísticas "
    "e validação empírica com dados reais. TODO: adicionar experimentos."
)

GOALS = [
    {"name": "publicar_qualis",
     "description": "Publicar artigo Qualis A1 sobre metacognição multiagente",
     "weight": 2.0, "goal_type": "strategic"},
    {"name": "validar",
     "description": "Validar empiricamente o roteamento por atenção",
     "weight": 1.5, "goal_type": "evaluative"},
]


@pytest.fixture(scope="module")
def deep_report():
    pipeline = DiagnosticPipeline()
    return pipeline.run(CORPUS, domain="multiagent_systems",
                        goals=GOALS, deep=True)


@pytest.fixture(scope="module")
def shallow_report():
    pipeline = DiagnosticPipeline()
    return pipeline.run(CORPUS, domain="multiagent_systems", goals=GOALS)


# ---------------------------------------------------------------- R1
def test_deep_roadmap(deep_report):
    """R1: deep=True executa o roadmap M1–M5 completo quando há metas."""
    rm = deep_report.get("roadmap", {})
    assert rm, "roadmap ausente no modo deep"
    assert "error" not in rm, f"roadmap com erro: {rm.get('error')}"
    assert rm.get("total_gaps", 0) > 0
    assert isinstance(rm.get("logical_sequence"), list)
    assert len(rm["logical_sequence"]) > 0, "sequenciamento vazio"


# ---------------------------------------------------------------- R2
def test_prioritizer(deep_report):
    """R2: modo deep produz oportunidades epistemológicas com tiers."""
    eo = deep_report.get("epistemic_opportunities", {})
    assert eo.get("total", 0) > 0
    tiers = {o["tier"] for o in eo.get("top", [])}
    assert tiers <= {"breakthrough", "promissora", "marginal"}


# ---------------------------------------------------------------- R3
def test_successors(deep_report):
    """R3: modo deep produz sucessores plausíveis a partir do DNA."""
    su = deep_report.get("successors", {})
    assert su.get("total", 0) > 0
    tiers = {s["tier"] for s in su.get("top", [])}
    assert tiers <= {"imediato", "proximo_horizonte", "especulativo"}


# ---------------------------------------------------------------- R4
def test_opportunity_score():
    """R4/INV1: score composto de 4 fatores dentro de [0, 1]."""
    pri = EpistemicPrioritizer()
    noo = {"gaps": [{"dimension": "metodos", "category": "Meta-análise"}],
           "overall_coverage": 0.4}
    opps = pri.prioritize(noo)
    assert opps, "nenhuma oportunidade gerada"
    for o in opps:
        assert isinstance(o, EpistemicOpportunity)
        assert 0.0 <= o.opportunity_score <= 1.0
        # fatores individuais também normalizados
        for f in (o.centrality, o.rarity, o.interdisciplinarity,
                  o.feasibility):
            assert 0.0 <= f <= 1.0


# ---------------------------------------------------------------- R5
def test_successor_score():
    """R5/INV1/INV3: score dentro de [0,1]; genes vêm do DNA fornecido."""
    gen = SuccessorGenerator()
    dna = {"capabilities": ["cross_validation", "mcp_bridge", "polymathic"]}
    succ = gen.generate(dna, theme="multiagent")
    gene_names = ["cross_validation", "mcp_bridge", "polymathic"]
    assert succ, "nenhum sucessor gerado"
    gene_set = set(gene_names)
    for s in succ:
        assert isinstance(s, SuccessorHypothesis)
        assert 0.0 <= s.successor_score <= 1.0
        # INV3: recombinação apenas de genes existentes
        assert set(s.genes) <= gene_set, (
            f"sucessor inventou genes: {set(s.genes) - gene_set}")


# ---------------------------------------------------------------- R6
def test_reports_md(deep_report):
    """R6: relatórios Markdown auditáveis presentes."""
    eo = deep_report.get("epistemic_opportunities", {})
    su = deep_report.get("successors", {})
    assert isinstance(eo.get("report_md"), str) and eo["report_md"].strip()
    assert isinstance(su.get("report_md"), str) and su["report_md"].strip()
    assert "#" in eo["report_md"], "report não parece Markdown"


# ---------------------------------------------------------------- R7
def test_orchestrator_deep(tmp_path, monkeypatch):
    """R7: orch.diagnose(deep=True) registra reflexão com síntese profunda."""
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from mci.metabus import metabus

    orch = MarceloClaroOrchestrator()
    report = orch.diagnose(CORPUS, domain="multiagent_systems",
                           goals=GOALS, deep=True)
    assert "epistemic_opportunities" in report
    assert "successors" in report
    # reflexão registrada na memória episódica global (Global Workspace)
    recent = metabus.memory.get_recent_context(limit=10)
    assert any("Camada profunda" in str(e.get("reflection", ""))
               for e in recent), \
        "reflexão da camada profunda não registrada"


# ---------------------------------------------------------------- R8 / INV2
def test_isolation_and_backcompat(shallow_report):
    """R8/INV2: deep=False mantém comportamento anterior (sem chaves novas)."""
    assert "epistemic_opportunities" not in shallow_report
    assert "successors" not in shallow_report
    assert "roadmap" not in shallow_report
    # chaves clássicas preservadas
    for key in ("noological", "teleological", "potentiality",
                "evolutionary", "reversa"):
        assert key in shallow_report


def test_deep_without_goals():
    """R8: deep sem metas não derruba o pipeline (roadmap é pulado)."""
    pipeline = DiagnosticPipeline()
    report = pipeline.run(CORPUS, domain="x", deep=True)
    # sem metas: roadmap ausente ou vazio, mas prioritizer/successors rodam
    assert report.get("epistemic_opportunities", {}).get("total", 0) >= 0
    assert report.get("successors", {}).get("total", 0) >= 0
    assert "duration_s" in report
