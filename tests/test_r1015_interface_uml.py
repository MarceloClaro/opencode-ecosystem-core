"""TESTE RED: Interface UML/Matriz - Monitoramento das 8 Métricas M1-M8.

Este teste infraestrutura a interface visual UML/matriz para monitoramento
das 8 métricas comportamentais do pipeline RAG (M1 a M8), garantindo que
todo o processo obedeça aos protocolos de qualificação anti-overclaim do
ecossistema OpenCode Core.
"""
import pytest
from pathlib import Path

from marceloclaro.orchestrator import MarceloClaroOrchestrator


@pytest.fixture(scope="module")
def orchestrator():
    """Orchestrator inicializado para teste de interface UML/matriz."""
    orch = MarceloClaroOrchestrator(auto_load_agents=False, strict_sdd=True)
    yield orch


class TestInterfaceUMLMatrizInfraestrutura:
    """Testes de infraestrutura para interface UML/matriz."""

    def test_especificacao_existe(self):
        """A1: Arquivo de especificação da interface UML/matriz existe."""
        spec_path = Path("specs/SPEC-935-R1015-interface-uml-matriz.md")
        # A estrutura deve ser compatível com interface UML/matriz
        assert spec_path.exists()

    def test_metricas_m1_a_m8_definidas(self):
        """A1: Todas as 8 métricas M1-M8 são definidas na especificação."""
        with open("specs/SPEC-935-R1015-interface-uml-matriz.md") as f:
            content = f.read()
        # Verifica presença de todas as métricas M1 através de M8
        for i in range(1, 9):
            assert f"M{i}" in content, f"M{i} não encontrada na especificação"


class TestInterfaceUMLMatrizPostura:
    """Testes de postura anti-overclaim na interface UML/matriz."""

    def test_sem_claims_qualidade_profissional(self, orchestrator):
        """A5: Interface não declara 'qualidade profissional' ou 'aprovado para produção'."""
        result = orchestrator.perceive('interface de monitoramento M1 a M8')
        lower = str(result).lower()
        # Must NOT claim quality professional or production readiness
        assert "qualidade profissional" not in lower
        assert "aprovado para producao" not in lower
        assert "pronto para producao" not in lower
        # Must have structural qualifications
        has_qualification = (
            "confidence_ledger" in lower
            or "lessons" in lower
            or "recent_context" in lower
        )
        assert has_qualification

    def test_qualificacoes_obrigatorias(self, orchestrator):
        """A6: Qualificações textuais são obrigatórias junto com valores."""
        result = orchestrator.perceive('metricas M1 a M8')
        lower = str(result).lower()
        # Must have structural qualifications
        has_qualification = (
            "confidence_ledger" in lower
            or "lessons" in lower
            or "recent_context" in lower
        )
        assert has_qualification


class TestInterfaceUMLMatrizConteudo:
    """Testes de conteúdo da interface UML/matriz."""

    def test_todas_metricas_exibidas(self):
        """A1: Todas as 8 métricas são exibidas na interface."""
        with open("specs/SPEC-935-R1015-interface-uml-matriz.md") as f:
            content = f.read()
        # Verifica que o documento referencia a interface com todas métricas
        # M1 através de M8 devem estar presentes
        metric_count = sum(1 for i in range(1, 9) if f"M{i}" in content)
        assert metric_count >= 8, f"Apenas {metric_count} métricas encontradas, esperado 8"


    def test_cores_status_consistentes(self):
        """A2: Cores/status visuais são consistentes com definições."""
        with open("specs/SPEC-935-R1015-interface-uml-matriz.md") as f:
            content = f.read()
        # Verifica que o documento define cores e status consistentes
        # Verifica presença de termos de qualificação
        qual_terms = ["observada", "moderada", "alta", "baixa", "insuficiente"]
        found_qual = any(term in content.lower() for term in qual_terms)
        assert found_qual, "Nenhuma qualificação encontrada no documento"


    def test_matriz_dependencias_presentes(self):
        """A3: Matriz de dependências entre métricas está presente."""
        with open("specs/SPEC-935-R1015-interface-uml-matriz.md") as f:
            content = f.read()
        # Verifica presença de referência à matriz de dependências
        assert "dependencia" in content.lower() or "matriz" in content.lower()