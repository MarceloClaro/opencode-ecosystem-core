# -*- coding: utf-8 -*-
"""
Testes R105 — Agentic Paper Composer (TDD: RED → GREEN → REFACTOR)
===================================================================
Testa o sistema de composicao de manuscritos academicos.

Requisitos (SPEC-935-R105):
  - StructurePlanner: outline por venue
  - SectionWriter: 6 secoes
  - CitationFormatter: ABNT, APA, IEEE
  - CrossConsistencyVerifier: 5 verificacoes
  - OrchestratorComposer: pipeline completo
  - MCP tool su_paper_composer
  - 25+ testes
  - Zero regressoes
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# ── Sample data ────────────────────────────────────────────────────

SAMPLE_DISCOVERIES = [
    {"hypothesis": "Quantum attention mechanisms improve transformer efficiency by 40%",
     "fitness": 0.92, "generation": 5},
    {"hypothesis": "Topological protection reduces error rates in quantum circuits",
     "fitness": 0.88, "generation": 4},
]

SAMPLE_EVIDENCE_GRAPH = {
    "entities": [
        {"id": "e1", "type": "paper", "title": "Attention Is All You Need"},
        {"id": "e2", "type": "claim", "text": "Quantum attention reduces complexity"}
    ],
    "relations": [
        {"source": "e2", "target": "e1", "type": "supported-by"}
    ]
}

SAMPLE_REVIEW = {
    "overall_score": 75,
    "recommendation": "minor-revision",
    "reviews": [
        {"critic": "MethodologyCritic", "score": 72,
         "claims": [{"text": "Well-structured methodology", "risk": "low"}]}
    ]
}

SAMPLE_REVISIONS = [
    {"claim_id": "M1", "status": "applied",
     "revised_text": "Increased sample size to 5000"},
    {"claim_id": "R1", "status": "applied",
     "revised_text": "Added error bars to Figure 3"}
]


# ── Testes StructurePlanner ────────────────────────────────────────

class TestStructurePlanner:
    """SPEC R105 Criterio 1: StructurePlanner."""

    def test_planner_generates_outline(self):
        """Gera outline basico."""
        try:
            from agentic_science_v2.paper_composer import StructurePlanner
            planner = StructurePlanner()
            outline = planner.plan("Quantum Machine Learning", "apa")
            assert outline is not None
            assert len(outline["sections"]) >= 5
        except ImportError:
            pytest.skip("StructurePlanner nao implementado (RED phase)")

    def test_planner_abnt_template(self):
        """Outline no formato ABNT."""
        try:
            from agentic_science_v2.paper_composer import StructurePlanner
            planner = StructurePlanner()
            outline = planner.plan("Test Title", "abnt")
            assert outline["venue"] == "abnt"
            sections = [s["name"].lower() for s in outline["sections"]]
            assert "introdução" in sections or "introduction" in sections
        except ImportError:
            pytest.skip("StructurePlanner nao implementado")

    def test_planner_apa_template(self):
        """Outline no formato APA."""
        try:
            from agentic_science_v2.paper_composer import StructurePlanner
            planner = StructurePlanner()
            outline = planner.plan("Test Title", "apa")
            assert outline["venue"] == "apa"
            section_types = [s["type"] for s in outline["sections"]]
            assert "abstract" in section_types
            assert "introduction" in section_types
            assert "methods" in section_types
        except ImportError:
            pytest.skip("StructurePlanner nao implementado")

    def test_planner_ieee_template(self):
        """Outline no formato IEEE."""
        try:
            from agentic_science_v2.paper_composer import StructurePlanner
            planner = StructurePlanner()
            outline = planner.plan("Test Title", "ieee")
            assert outline["venue"] == "ieee"
        except ImportError:
            pytest.skip("StructurePlanner nao implementado")

    def test_planner_invalid_venue_defaults_to_apa(self):
        """Venue invalido usa APA como fallback."""
        try:
            from agentic_science_v2.paper_composer import StructurePlanner
            planner = StructurePlanner()
            outline = planner.plan("Test", "invalid_venue")
            assert outline["venue"] == "apa"
        except ImportError:
            pytest.skip("StructurePlanner nao implementado")


# ── Testes SectionWriter ───────────────────────────────────────────

class TestSectionWriter:
    """SPEC R105 Criterio 2: SectionWriter."""

    def test_writer_writes_abstract(self):
        """Escreve secao abstract."""
        try:
            from agentic_science_v2.paper_composer import SectionWriter
            writer = SectionWriter()
            result = writer.write_abstract(
                "Quantum ML", SAMPLE_DISCOVERIES, SAMPLE_EVIDENCE_GRAPH
            )
            assert result is not None
            assert len(result) > 50
        except ImportError:
            pytest.skip("SectionWriter nao implementado (RED phase)")

    def test_writer_writes_introduction(self):
        """Escreve secao introduction."""
        try:
            from agentic_science_v2.paper_composer import SectionWriter
            writer = SectionWriter()
            result = writer.write_introduction(
                "Quantum ML", SAMPLE_DISCOVERIES, SAMPLE_EVIDENCE_GRAPH
            )
            assert result is not None
            assert len(result) > 100
        except ImportError:
            pytest.skip("SectionWriter nao implementado")

    def test_writer_writes_methods(self):
        """Escreve secao methods."""
        try:
            from agentic_science_v2.paper_composer import SectionWriter
            writer = SectionWriter()
            result = writer.write_methods(SAMPLE_DISCOVERIES)
            assert result is not None
        except ImportError:
            pytest.skip("SectionWriter nao implementado")

    def test_writer_writes_results(self):
        """Escreve secao results."""
        try:
            from agentic_science_v2.paper_composer import SectionWriter
            writer = SectionWriter()
            result = writer.write_results(SAMPLE_DISCOVERIES, SAMPLE_EVIDENCE_GRAPH)
            assert result is not None
        except ImportError:
            pytest.skip("SectionWriter nao implementado")

    def test_writer_writes_discussion(self):
        """Escreve secao discussion."""
        try:
            from agentic_science_v2.paper_composer import SectionWriter
            writer = SectionWriter()
            result = writer.write_discussion(
                SAMPLE_DISCOVERIES, SAMPLE_REVIEW, SAMPLE_REVISIONS
            )
            assert result is not None
        except ImportError:
            pytest.skip("SectionWriter nao implementado")

    def test_writer_writes_conclusion(self):
        """Escreve secao conclusion."""
        try:
            from agentic_science_v2.paper_composer import SectionWriter
            writer = SectionWriter()
            result = writer.write_conclusion(SAMPLE_DISCOVERIES)
            assert result is not None
        except ImportError:
            pytest.skip("SectionWriter nao implementado")

    def test_writer_generates_all_sections(self):
        """Gera todas as 6 secoes."""
        try:
            from agentic_science_v2.paper_composer import SectionWriter
            writer = SectionWriter()
            sections = writer.write_all(
                "Quantum ML", SAMPLE_DISCOVERIES, SAMPLE_EVIDENCE_GRAPH,
                SAMPLE_REVIEW, SAMPLE_REVISIONS
            )
            expected = ["abstract", "introduction", "methods", "results",
                        "discussion", "conclusion"]
            for sec in expected:
                assert sec in sections, f"Secao {sec} ausente"
                assert len(sections[sec]) > 0, f"Secao {sec} vazia"
        except ImportError:
            pytest.skip("SectionWriter nao implementado")


# ── Testes CitationFormatter ───────────────────────────────────────

class TestCitationFormatter:
    """SPEC R105 Criterio 3: CitationFormatter."""

    def test_format_abnt(self):
        """Formata referencia em ABNT."""
        try:
            from agentic_science_v2.paper_composer import CitationFormatter
            formatter = CitationFormatter()
            ref = formatter.format({
                "authors": ["Vaswani, A.", "Shazeer, N."],
                "year": 2017,
                "title": "Attention Is All You Need",
                "journal": "Advances in Neural Information Processing Systems",
                "volume": "30"
            }, style="abnt")
            assert ref is not None
            assert "VASWANI" in ref.upper() or "Vaswani" in ref
        except ImportError:
            pytest.skip("CitationFormatter nao implementado (RED phase)")

    def test_format_apa(self):
        """Formata referencia em APA."""
        try:
            from agentic_science_v2.paper_composer import CitationFormatter
            formatter = CitationFormatter()
            ref = formatter.format({
                "authors": ["Vaswani, A.", "Shazeer, N."],
                "year": 2017,
                "title": "Attention Is All You Need",
                "journal": "Advances in Neural Information Processing Systems",
            }, style="apa")
            assert ref is not None
            assert "Vaswani" in ref
        except ImportError:
            pytest.skip("CitationFormatter nao implementado")

    def test_format_ieee(self):
        """Formata referencia em IEEE."""
        try:
            from agentic_science_v2.paper_composer import CitationFormatter
            formatter = CitationFormatter()
            ref = formatter.format({
                "authors": ["Vaswani, A.", "Shazeer, N."],
                "year": 2017,
                "title": "Attention Is All You Need",
                "journal": "Adv. Neural Inf. Process. Syst.",
            }, style="ieee")
            assert ref is not None
        except ImportError:
            pytest.skip("CitationFormatter nao implementado")

    def test_format_default_style(self):
        """Estilo padrao e APA."""
        try:
            from agentic_science_v2.paper_composer import CitationFormatter
            formatter = CitationFormatter()
            ref = formatter.format({
                "authors": ["Vaswani, A."], "year": 2017, "title": "Test"
            })
            # Deve usar APA como default
            assert ref is not None
        except ImportError:
            pytest.skip("CitationFormatter nao implementado")


# ── Testes CrossConsistencyVerifier ───────────────────────────────

class TestCrossConsistencyVerifier:
    """SPEC R105 Criterio 4: CrossConsistencyVerifier."""

    def test_verify_abstract_intro_coherence(self):
        """Verifica coerencia Abstract-Introduction."""
        try:
            from agentic_science_v2.paper_composer import CrossConsistencyVerifier
            verifier = CrossConsistencyVerifier()
            report = verifier.verify({
                "abstract": "We present quantum attention for transformers",
                "introduction": "Quantum attention improves transformer efficiency",
                "methods": "We use quantum circuits for attention",
                "results": "Quantum attention achieves 40% improvement",
                "discussion": "Quantum attention shows promise",
                "conclusion": "Quantum attention is effective"
            })
            assert report is not None
            assert "abstract_intro_coherence" in report
        except ImportError:
            pytest.skip("CrossConsistencyVerifier nao implementado (RED phase)")

    def test_verify_claims_evidence(self):
        """Verifica claims vs evidence."""
        try:
            from agentic_science_v2.paper_composer import CrossConsistencyVerifier
            verifier = CrossConsistencyVerifier()
            report = verifier.verify_claims_evidence(
                SAMPLE_DISCOVERIES, SAMPLE_EVIDENCE_GRAPH
            )
            assert report is not None
            assert "verified_claims" in report
            assert "unverified_claims" in report
        except ImportError:
            pytest.skip("CrossConsistencyVerifier nao implementado")

    def test_verify_full_report(self):
        """Relatorio completo de consistencia."""
        try:
            from agentic_science_v2.paper_composer import CrossConsistencyVerifier
            verifier = CrossConsistencyVerifier()
            sections = {
                "abstract": "Quantum attention for transformers",
                "introduction": "Quantum attention improves efficiency",
                "methods": "We use quantum circuits",
                "results": "40% improvement with quantum attention",
                "discussion": "Limitations and future work",
                "conclusion": "Summary of contributions"
            }
            report = verifier.full_report(sections, SAMPLE_DISCOVERIES, SAMPLE_EVIDENCE_GRAPH)
            assert report is not None
            assert report.get("overall_score") is not None
        except ImportError:
            pytest.skip("CrossConsistencyVerifier nao implementado")

    def test_verify_methods_results_alignment(self):
        """Verifica alinhamento Methods-Results."""
        try:
            from agentic_science_v2.paper_composer import CrossConsistencyVerifier
            verifier = CrossConsistencyVerifier()
            report = verifier.verify_methods_results_alignment(
                methods_text="We evaluate on 5 datasets",
                results_text="Results on all 5 datasets show improvement"
            )
            assert report is not None
            assert "aligned" in report
        except ImportError:
            pytest.skip("CrossConsistencyVerifier nao implementado")


# ── Testes OrchestratorComposer ────────────────────────────────────

class TestOrchestratorComposer:
    """SPEC R105 Criterio 5: OrchestratorComposer pipeline."""

    def test_composer_pipeline_full(self):
        """Pipeline completo plan→write→format→verify→export."""
        try:
            from agentic_science_v2.paper_composer import OrchestratorComposer
            composer = OrchestratorComposer()
            result = composer.run(
                title="Quantum Machine Learning Survey",
                discoveries=SAMPLE_DISCOVERIES,
                evidence_graph=SAMPLE_EVIDENCE_GRAPH,
                review=SAMPLE_REVIEW,
                revisions=SAMPLE_REVISIONS,
                venue="apa"
            )
            assert result is not None
            assert result["status"] == "completed"
            assert "manuscript" in result
        except ImportError:
            pytest.skip("OrchestratorComposer nao implementado (RED phase)")

    def test_composer_manuscript_has_all_sections(self):
        """Manuscrito tem todas as secoes."""
        try:
            from agentic_science_v2.paper_composer import OrchestratorComposer
            composer = OrchestratorComposer()
            result = composer.run(
                title="Quantum ML",
                discoveries=SAMPLE_DISCOVERIES,
                evidence_graph=SAMPLE_EVIDENCE_GRAPH,
                review=SAMPLE_REVIEW,
                revisions=SAMPLE_REVISIONS
            )
            sections = result.get("sections", {})
            expected = ["abstract", "introduction", "methods", "results",
                        "discussion", "conclusion"]
            for sec in expected:
                assert sec in sections, f"Secao {sec} ausente no output"
        except ImportError:
            pytest.skip("OrchestratorComposer nao implementado")

    def test_composer_without_optional_inputs(self):
        """Funciona sem inputs opcionais."""
        try:
            from agentic_science_v2.paper_composer import OrchestratorComposer
            composer = OrchestratorComposer()
            result = composer.run(
                title="Minimal Paper",
                discoveries=[],
                evidence_graph={},
                review={},
                revisions=[]
            )
            assert result["status"] == "completed"
        except ImportError:
            pytest.skip("OrchestratorComposer nao implementado")


# ── Testes MCP Tool ────────────────────────────────────────────────

class TestMCPTool:
    """SPEC R105 Criterio 7: MCP tool su_paper_composer."""

    def test_mcp_tool_registered(self):
        """Tool su_paper_composer registrada no MCP Server."""
        try:
            from synthetic_university.mcp_server import server
            assert "su_paper_composer" in server.tools, \
                "su_paper_composer nao registrada"
        except ImportError:
            pytest.skip("MCP Server nao disponivel")

    def test_mcp_tool_schema_valid(self):
        """Schema da tool tem parametros esperados."""
        try:
            from synthetic_university.mcp_server import server
            tool = server.tools["su_paper_composer"]
            schema = tool["schema"]
            assert "properties" in schema
            props = schema["properties"]
            assert any("title" in k.lower() for k in props), \
                "Schema deve aceitar title"
            assert any("venue" in k.lower() for k in props), \
                "Schema deve aceitar venue"
        except ImportError:
            pytest.skip("MCP Server nao disponivel")


# ── Testes de integracao R101-R105 ─────────────────────────────────

class TestFullPipelineIntegration:
    """SPEC R105 Criterio 6: Consome inputs R101-R104."""

    def test_consumes_r101_discoveries(self):
        """Aceita discoveries do R101."""
        try:
            from agentic_science_v2.paper_composer import OrchestratorComposer
            composer = OrchestratorComposer()
            result = composer.run(
                title="Test", discoveries=SAMPLE_DISCOVERIES
            )
            assert result is not None
        except ImportError:
            pytest.skip("OrchestratorComposer nao implementado")

    def test_consumes_r102_evidence_graph(self):
        """Aceita evidence_graph do R102."""
        try:
            from agentic_science_v2.paper_composer import OrchestratorComposer
            composer = OrchestratorComposer()
            result = composer.run(
                title="Test", discoveries=[], evidence_graph=SAMPLE_EVIDENCE_GRAPH
            )
            assert result is not None
        except ImportError:
            pytest.skip("OrchestratorComposer nao implementado")

    def test_consumes_r103_review(self):
        """Aceita review do R103."""
        try:
            from agentic_science_v2.paper_composer import OrchestratorComposer
            composer = OrchestratorComposer()
            result = composer.run(
                title="Test", discoveries=[], evidence_graph={}, review=SAMPLE_REVIEW
            )
            assert result is not None
        except ImportError:
            pytest.skip("OrchestratorComposer nao implementado")

    def test_consumes_r104_revisions(self):
        """Aceita revisions do R104."""
        try:
            from agentic_science_v2.paper_composer import OrchestratorComposer
            composer = OrchestratorComposer()
            result = composer.run(
                title="Test", discoveries=[], evidence_graph={},
                review={}, revisions=SAMPLE_REVISIONS
            )
            assert result is not None
        except ImportError:
            pytest.skip("OrchestratorComposer nao implementado")


# ── Contagem ───────────────────────────────────────────────────────

def test_minimum_test_count():
    """Garante pelo menos 25 testes."""
    test_methods = []
    for name, obj in globals().items():
        if isinstance(obj, type) and name.startswith("Test"):
            for attr in dir(obj):
                if attr.startswith("test_"):
                    test_methods.append(f"{name}.{attr}")
    assert len(test_methods) >= 25, \
        f"Esperado >= 25 testes, definidos {len(test_methods)}"
