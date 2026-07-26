#!/usr/bin/env python3
"""
Testes TDD para Jinja2Templates Engine (SPEC-964)
==================================================
RED phase: testes falham antes da implementação.

Ciclo: RED → GREEN → REFACTOR
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─── Testes de Engine Básica ────────────────────────────────


class TestJinja2Engine:
    """RED: testes esperam módulo skills.tooling.jinja2_templates existir."""

    def test_module_exists(self):
        """Falha se módulo não existe (RED até implementar)."""
        try:
            from skills.tooling.jinja2_templates import Jinja2Engine
            assert Jinja2Engine is not None
        except ImportError:
            pytest.fail("Módulo skills.tooling.jinja2_templates não existe")

    def test_engine_initializes(self):
        """Engine deve inicializar com diretório de templates."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        assert engine is not None
        assert hasattr(engine, "render")
        assert hasattr(engine, "list_templates")
        assert hasattr(engine, "get_template_names")

    def test_render_simple_template(self):
        """Engine renderiza template Jinja2 básico com variáveis."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        result = engine.render_string("Olá {{ nome }}!", {"nome": "Mundo"})
        assert result == "Olá Mundo!"

    def test_render_with_list(self):
        """Engine renderiza template com loops."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        template = "{% for item in items %}- {{ item }}\n{% endfor %}"
        result = engine.render_string(template, {"items": ["A", "B", "C"]})
        assert "- A\n" in result
        assert "- B\n" in result
        assert "- C\n" in result

    def test_render_with_conditionals(self):
        """Engine renderiza template com condicionais."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        template = "{% if ativo %}ATIVO{% else %}INATIVO{% endif %}"
        assert engine.render_string(template, {"ativo": True}) == "ATIVO"
        assert engine.render_string(template, {"ativo": False}) == "INATIVO"

    def test_render_from_file(self):
        """Engine renderiza template a partir de arquivo .j2."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "teste.md.j2"
            template_path.write_text("# {{ titulo }}\n\nConteúdo: {{ conteudo }}")

            engine = Jinja2Engine(template_dirs=[tmpdir])
            result = engine.render("teste.md.j2", {
                "titulo": "Teste",
                "conteudo": "Olá Mundo",
            })
            assert "# Teste" in result
            assert "Conteúdo: Olá Mundo" in result


# ─── Testes de Templates Pré-definidos ──────────────────────


class TestPredefinedTemplates:
    """RED: testes esperam templates .j2 existirem no pacote."""

    def test_template_dir_exists(self):
        """Diretório de templates deve existir."""
        from skills.tooling.jinja2_templates import TEMPLATE_DIR

        assert TEMPLATE_DIR.exists(), f"Diretório {TEMPLATE_DIR} não existe"

    def test_fichamento_template_exists(self):
        """Template de fichamento deve existir."""
        from skills.tooling.jinja2_templates import TEMPLATE_DIR

        template = TEMPLATE_DIR / "fichamento.md.j2"
        assert template.exists(), f"Template {template} não encontrado"

    def test_render_fichamento(self):
        """Template de fichamento renderiza com dados mínimos."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        result = engine.render("fichamento.md.j2", {
            "titulo": "Teste de Fichamento",
            "autores": ["Autor A", "Autor B"],
            "ano": 2024,
            "resumo": "Este é um resumo de teste.",
            "palavras_chave": ["teste", "fichamento"],
        })
        assert "# Teste de Fichamento" in result
        assert "Autor A" in result
        assert "2024" in result
        assert "teste" in result.lower()

    def test_render_quality_report(self):
        """Template de relatório de qualidade renderiza."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        result = engine.render("quality_report.md.j2", {
            "projeto": "ecosystem-core",
            "cobertura": 85.5,
            "testes_passando": 42,
            "testes_falhando": 3,
            "data": "2024-01-01",
        })
        assert "ecosystem-core" in result
        assert "85.5" in result or "85,5" in result


# ─── Testes de Integração com LLMReductionLayer ─────────────


class TestIntegration:
    """RED: testes esperam integração com LLMReductionLayer."""

    def test_integration_with_llm_reduction(self):
        """LLMReductionLayer deve expor Jinja2Engine."""
        from skills.tooling.llm_reduction import get_reduction_layer

        layer = get_reduction_layer()
        assert hasattr(layer, "jinja2"), "LLMReductionLayer não tem atributo 'jinja2'"
        assert hasattr(layer.jinja2, "render"), "jinja2 não tem método 'render'"

    def test_llm_reduction_render_template(self):
        """Renderizar via LLMReductionLayer conta como LLM call evitada."""
        from skills.tooling.llm_reduction import get_reduction_layer

        layer = get_reduction_layer()
        stats_before = layer.stats["total_llm_calls_saved"]

        result = layer.render_string("Bem-vindo {{ nome }}!", {"nome": "Teste"})
        assert result == "Bem-vindo Teste!"

        stats_after = layer.stats["total_llm_calls_saved"]
        assert stats_after == stats_before + 1


# ─── Testes de Performance ──────────────────────────────────


class TestPerformance:
    """Templates devem renderizar em < 10ms."""

    def test_render_under_10ms(self):
        """Renderização de template simples deve levar < 10ms."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        import time

        engine = Jinja2Engine()
        start = time.time()
        for _ in range(100):
            engine.render_string("{{ nome }} tem {{ idade }} anos.", {
                "nome": "João",
                "idade": 30,
            })
        elapsed_ms = (time.time() - start) * 10  # média por chamada

        assert elapsed_ms < 10, f"Renderização muito lenta: {elapsed_ms:.2f}ms"


# ─── Testes de Substituição de Arquivos Reais ───────────────


class TestRealSubstitution:
    """Testes que validam substituição de arquivos reais do ecossistema."""

    def test_notebook_template_generates_valid_json(self):
        """Template de notebook deve gerar JSON .ipynb válido."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        result = engine.render("notebook.ipynb.j2", {
            "titulo": "Notebook Teste",
            "celulas": [
                {"tipo": "markdown", "conteudo": "# Título"},
                {"tipo": "code", "conteudo": "print('hello')"},
            ],
        })
        parsed = json.loads(result)
        assert parsed["nbformat"] == 4
        assert len(parsed["cells"]) == 2

    def test_scanner_report_template(self):
        """Template de relatório de scanner deve funcionar."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        result = engine.render("teleological.md.j2", {
            "titulo": "Scanner Teleológico",
            "score": 0.85,
            "status": "pass",
            "detalhes": [
                {"nome": "Alinhamento", "status": "ok", "observacao": "OK"},
            ],
        })
        assert "Scanner Teleológico" in result
        assert "85.0%" in result or "85%" in result


# ─── Testes de Filtros Customizados ─────────────────────────


class TestCustomFilters:
    """Filtros Jinja2 customizados devem funcionar."""

    def test_markdown_filter(self):
        """Filtro |markdown deve converter Markdown para HTML."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        result = engine.render_string(
            "{{ texto | markdown }}",
            {"texto": "# Título\n\n**negrito**"},
        )
        assert "<h1>" in result or "<strong>" in result

    def test_table_filter(self):
        """Filtro |table deve criar tabela Markdown."""
        from skills.tooling.jinja2_templates import Jinja2Engine

        engine = Jinja2Engine()
        dados = [
            {"nome": "A", "valor": 10},
            {"nome": "B", "valor": 20},
        ]
        result = engine.render_string(
            "{{ dados | table('nome', 'valor') }}",
            {"dados": dados},
        )
        assert "| A " in result or "| A |" in result
        assert "| 10 " in result or "| 10 |" in result
