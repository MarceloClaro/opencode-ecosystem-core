"""Testes TDD para Integracao Academica (SPEC-935 R86)."""

import pytest
import json
from unittest.mock import patch, MagicMock
from synthetic_university.academic_integration import (
    AcademicIntegrator,
    search_arxiv,
    search_semantic_scholar,
    check_sci_hub,
    LiteratureBacking,
)


class TestR86Arxiv:
    """Testes para integracao com arXiv API."""

    def test_search_arxiv_returns_results(self):
        """R86: arXiv search returns paper results."""
        # Mock XML de resposta do arXiv (namespaces corretos no root)
        mock_xml = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2301.12345</id>
    <title>Quantum Ethics: A Framework for Moral AI</title>
    <summary>This paper explores the intersection of quantum computing and ethics.</summary>
    <author><name>John Doe</name></author>
    <arxiv:primary_category term="cs.AI"/>
  </entry>
</feed>"""
        
        with patch('urllib.request.urlopen') as mock:
            mock_response = MagicMock()
            mock_response.read.return_value = mock_xml.encode()
            mock_response.status = 200
            mock.return_value = mock_response
            mock.return_value.__enter__.return_value = mock_response
            
            results = search_arxiv("quantum ethics", max_results=5)
            
        assert len(results) > 0
        assert results[0]['title'] is not None
        assert results[0]['id'] is not None

    def test_search_arxiv_empty_on_error(self):
        """R86: arXiv retorna lista vazia em caso de erro."""
        with patch('urllib.request.urlopen') as mock:
            mock.side_effect = Exception("Connection error")
            results = search_arxiv("nonexistent", max_results=5)
        assert results == []

    def test_search_arxiv_query_format(self):
        """R86: Query do arXiv e formatada corretamente."""
        with patch('urllib.request.urlopen') as mock:
            mock_response = MagicMock()
            mock_response.read.return_value = b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
            mock_response.status = 200
            mock.return_value = mock_response
            mock.return_value.__enter__.return_value = mock_response
            
            search_arxiv("machine learning ethics", max_results=3)
            
            # Verificar URL chamada (acessar via get_full_url)
            called_req = mock.call_args[0][0]
            called_url = called_req.get_full_url() if hasattr(called_req, 'get_full_url') else str(called_req)
            assert 'http://export.arxiv.org/api/query' in called_url
            assert 'machine' in called_url and 'learning' in called_url and 'ethics' in called_url
            assert 'max_results=3' in called_url


class TestR86SemanticScholar:
    """Testes para integracao com Semantic Scholar API."""

    def test_search_semantic_scholar(self):
        """R86: Semantic Scholar search returns results."""
        mock_response = {
            'data': [
                {
                    'paperId': 'abc123',
                    'title': 'Quantum Ethics in AI Systems',
                    'citationCount': 42,
                    'venue': 'Nature Machine Intelligence',
                    'year': 2024,
                    'externalIds': {'DOI': '10.1234/example'},
                }
            ]
        }
        
        with patch('urllib.request.urlopen') as mock:
            mock.return_value.read.return_value = json.dumps(mock_response).encode()
            mock.return_value.__enter__.return_value = mock.return_value
            mock.return_value.status = 200
            
            results = search_semantic_scholar("quantum ethics")
            
        assert len(results) > 0
        assert results[0]['title'] == 'Quantum Ethics in AI Systems'
        assert results[0]['citationCount'] == 42
        assert results[0]['doi'] == '10.1234/example'

    def test_semantic_scholar_empty_on_error(self):
        """R86: Semantic Scholar retorna lista vazia em caso de erro."""
        with patch('urllib.request.urlopen') as mock:
            mock.side_effect = Exception("API error")
            results = search_semantic_scholar("test query")
        assert results == []


class TestR86SciHub:
    """Testes para integracao com Sci-Hub."""

    def test_check_sci_hub_available(self):
        """R86: Sci-Hub verifica disponibilidade de paper por DOI."""
        # Retornar conteudo com mais de 1000 bytes
        pdf_content = b'PDF content ' * 200  # > 1000 bytes
        
        with patch('urllib.request.urlopen') as mock:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.read.return_value = pdf_content
            mock.return_value = mock_response
            mock.return_value.__enter__.return_value = mock_response
            
            result = check_sci_hub("10.1234/example")
            
        assert result['available'] is True
        assert result['doi'] == '10.1234/example'

    def test_check_sci_hub_unavailable(self):
        """R86: Sci-Hub retorna indisponivel para DOI inexistente."""
        with patch('urllib.request.urlopen') as mock:
            mock.side_effect = Exception("404 Not Found")
            result = check_sci_hub("10.9999/nonexistent")
        assert result['available'] is False

    def test_check_sci_hub_tries_multiple(self):
        """R86: Sci-Hub tenta dominios em sequencia."""
        import synthetic_university.academic_integration as ai
        default_domains = ai.SCI_HUB_DOMAINS
        # Teste estrutural: verificar que ha dominios configurados
        assert len(default_domains) >= 2
        assert all('sci-hub' in d for d in default_domains)


class TestR86LiteratureBacking:
    """Testes para LiteratureBacking score."""

    def test_literature_backing_creates(self):
        """R86: LiteratureBacking e criado com query."""
        lb = LiteratureBacking("quantum ethics")
        assert lb is not None
        assert lb.query == "quantum ethics"

    def test_literature_backing_score_calculation(self):
        """R86: LiteratureBacking calcula score."""
        lb = LiteratureBacking("quantum ethics")
        
        # Simular resultados
        lb.arxiv_results = [{'title': 'Paper 1'}, {'title': 'Paper 2'}]
        lb.semantic_results = [
            {'title': 'Paper A', 'citationCount': 50},
            {'title': 'Paper B', 'citationCount': 30},
        ]
        lb.sci_hub_results = [
            {'available': True, 'doi': '10.1'},
            {'available': False, 'doi': '10.2'},
        ]
        
        score = lb.calculate_score()
        assert 0 <= score <= 1.0

    def test_literature_backing_calculate(self):
        """R86: LiteratureBacking com arxiv e semantic."""
        lb = LiteratureBacking("quantum computing")
        lb.arxiv_results = [{'title': 'Q1'}, {'title': 'Q2'}]
        lb.semantic_results = [{'title': 'S1', 'citationCount': 100}]
        lb.sci_hub_results = [{'available': True, 'doi': '10.1'}]
        
        score = lb.calculate_score()
        assert score > 0.1  # com papers reais, score > 0


class TestR86AcademicIntegrator:
    """Testes para o AcademicIntegrator completo."""

    def test_integrator_creates(self):
        """R86: AcademicIntegrator e criado."""
        integrator = AcademicIntegrator()
        assert integrator is not None

    def test_integrator_search_thesis_concepts(self):
        """R86: Integrator busca papers para conceitos de tese."""
        integrator = AcademicIntegrator()
        
        # Mock para evitar chamadas de rede
        with patch('synthetic_university.academic_integration.search_arxiv') as mock_arxiv:
            mock_arxiv.return_value = [{'title': 'Test', 'id': '1234'}]
            
            with patch('synthetic_university.academic_integration.search_semantic_scholar') as mock_s2:
                mock_s2.return_value = [{'title': 'Test S2', 'citationCount': 10}]
                
                with patch('synthetic_university.academic_integration.check_sci_hub') as mock_sh:
                    mock_sh.return_value = {'available': True, 'doi': '10.1234/test'}
                    
                    result = integrator.search("quantum ethics")
                    
        assert result is not None
        assert 'backing_score' in result
        assert 'papers' in result
        assert len(result['papers']) > 0

    def test_integrator_in_memory(self):
        """R86: Integrator funciona sem chamadas de rede (modo offline)."""
        integrator = AcademicIntegrator()
        result = integrator.search("test query", offline=True)
        assert result is not None
        assert result['backing_score'] == 0.5  # offline = score medio
        assert result['offline'] is True
