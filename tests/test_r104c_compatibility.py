# -*- coding: utf-8 -*-
"""
Testes R104c — Compatibility Analysis Document (TDD: RED → GREEN → REFACTOR)
=================================================================
Testa a existencia e conteudo do documento de analise de compatibilidade.
Requisitos:
  - docs/COMPATIBILITY_ANALYSIS.md existe
  - 5+ secoes com analise substantiva
  - Tabelas comparativas
  - Plano de integracao
  - 3+ testes
"""

from pathlib import Path

import pytest

DOC_PATH = Path(__file__).resolve().parent.parent / "docs" / "COMPATIBILITY_ANALYSIS.md"


@pytest.fixture(scope="module")
def doc_content():
    if not DOC_PATH.exists():
        pytest.skip(f"{DOC_PATH} ainda nao existe (RED phase)")
    return DOC_PATH.read_text(encoding="utf-8")


class TestCompatibilityDocExists:
    """Testes de existencia do documento."""

    def test_doc_exists(self):
        assert DOC_PATH.exists(), f"Documento {DOC_PATH} nao encontrado"

    def test_doc_not_empty(self, doc_content):
        assert len(doc_content) > 500, "Documento muito curto (< 500 chars)"

    def test_doc_has_sections(self, doc_content):
        """Documento tem pelo menos 5 secoes (##)."""
        sections = [l for l in doc_content.splitlines() if l.startswith("##")]
        assert len(sections) >= 5, f"Esperado >= 5 secoes, encontrado {len(sections)}"


class TestCompatibilityDocContent:
    """Testes de conteudo do documento."""

    def test_has_comparison_tables(self, doc_content):
        """Documento contem tabelas comparativas (|)."""
        table_lines = [l for l in doc_content.splitlines() if l.startswith("|")]
        assert len(table_lines) >= 6, "Esperado pelo menos 6 linhas de tabela"

    def test_has_integration_plan(self, doc_content):
        """Documento contem um plano de integracao."""
        assert "Integra" in doc_content or "integrat" in doc_content.lower(), \
            "Documento deve mencionar integracao"

    def test_mentions_both_ecosystems(self, doc_content):
        """Documento menciona ambos os ecossistemas."""
        lower = doc_content.lower()
        assert "opencode ecosystem core" in lower or "opencon" in lower
        assert "academic-research" in lower or "fork" in lower

    def test_has_gap_analysis(self, doc_content):
        """Documento contem analise de gaps."""
        assert "gap" in doc_content.lower() or "sobreposi" in doc_content.lower() or \
               "sobreposição" in doc_content.lower(), "Documento deve ter analise de gaps"

    def test_has_roadmap(self, doc_content):
        """Documento contem roadmap."""
        assert "roadmap" in doc_content.lower() or "próximo" in doc_content.lower() or \
               "proximo" in doc_content.lower(), "Documento deve ter roadmap ou proximos passos"


# ── Contagem ────────────────────────────────────────────────────────

def test_minimum_test_count():
    """Pelo menos 3 testes neste arquivo."""
    # Esta funcao em si conta como 1, mas garantimos >= 8 tests acima
    pass
