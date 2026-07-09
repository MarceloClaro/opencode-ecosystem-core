"""Testes TDD para Discovery Dashboard (SPEC-935 R87)."""

import pytest
import os
import json
import tempfile
from synthetic_university.dashboard_generator import (
    DashboardGenerator,
    load_cycles_data,
    load_validation_data,
    build_evolution_chart_data,
    build_proximity_chart_data,
    build_benchmark_chart_data,
)


class TestR87DashboardData:
    """Testes para extracao de dados do dashboard."""

    def test_load_cycles_data(self):
        """R87: Dados de ciclos sao carregados."""
        data = load_cycles_data()
        assert data is not None
        assert len(data) > 0
        # Verificar estrutura
        assert 'round_id' in data[0]
        assert 'objective' in data[0]
        assert 'score' in data[0]

    def test_load_validation_data(self):
        """R87: Dados de validacao sao carregados."""
        data = load_validation_data()
        if data:  # pode nao existir se nao foi executado
            assert 'theses_ranked' in data
            assert 'aggregate_scores' in data

    def test_build_evolution_chart_data(self):
        """R87: Dados para grafico de evolucao sao extraidos."""
        cycles = load_cycles_data()
        chart = build_evolution_chart_data(cycles)
        assert 'labels' in chart
        assert 'scores' in chart
        assert len(chart['labels']) == len(chart['scores'])
        # Scores devem ser valores numericos
        for s in chart['scores']:
            assert isinstance(s, (int, float))

    def test_build_proximity_chart_data(self):
        """R87: Dados da matriz de proximidade."""
        chart = build_proximity_chart_data()
        assert 'faculties' in chart
        assert 'matrix' in chart
        assert len(chart['faculties']) > 0
        assert len(chart['matrix']) == len(chart['faculties'])

    def test_build_benchmark_chart_data(self):
        """R87: Dados do benchmark."""
        chart = build_benchmark_chart_data()
        if chart:  # pode nao existir
            assert 'labels' in chart
            assert 'coherence' in chart
            assert 'composite' in chart


class TestR87DashboardGenerator:
    """Testes para o gerador de dashboard."""

    def test_generator_creates(self):
        """R87: DashboardGenerator e criado."""
        gen = DashboardGenerator()
        assert gen is not None

    def test_generator_produces_html(self):
        """R87: DashboardGenerator produz HTML valido."""
        gen = DashboardGenerator()
        html = gen.generate()
        assert html is not None
        assert len(html) > 500
        assert '<!DOCTYPE html>' in html
        assert '</html>' in html

    def test_html_contains_sections(self):
        """R87: HTML contem secoes esperadas."""
        gen = DashboardGenerator()
        html = gen.generate()
        sections = [
            'evolution',
            'proximity',
            'coherence',
            'benchmark',
            'theses',
            'professors',
        ]
        for section in sections:
            assert section in html.lower() or section.replace('_', ' ') in html.lower()

    def test_html_contains_data(self):
        """R87: HTML contem dados embutidos."""
        import json, os
        gen = DashboardGenerator()
        html = gen.generate()
        # Deve conter dados dos ciclos (IDs variaveis conforme evolution/cycles.json)
        cycles_path = "evolution/cycles.json"
        if os.path.exists(cycles_path):
            with open(cycles_path) as f:
                data = json.load(f)
            ids = [c['round_id'] for c in data.get('cycles', []) if c.get('round_id')]
            if ids:
                assert any(rid in html for rid in ids), \
                    f"Nenhum ID de ciclo {ids[:5]} encontrado no HTML"
        else:
            # Fallback: verificar se ha dados de ciclo no HTML
            assert 'round_id' not in html  # nao ha dados de ciclo para verificar

    def test_generator_write_file(self):
        """R87: Generator escreve arquivo HTML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = DashboardGenerator()
            filepath = gen.write(tmpdir)
            assert os.path.exists(filepath)
            assert filepath.endswith('.html')
            with open(filepath) as f:
                content = f.read()
            assert len(content) > 500
