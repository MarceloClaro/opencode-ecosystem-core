# -*- coding: utf-8 -*-
"""
Testes TDD para R95 — Continuous Discovery Loop (SPEC-935-R95).

Ciclo: RED → GREEN → REFACTOR.
Requisitos: 8+ testes, sem rede externa nem LLM real.
"""

import json
import os
import tempfile
import time
from unittest.mock import patch, MagicMock

import pytest

from synthetic_university.continuous_discovery import ContinuousDiscoveryLoop


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def loop(tmpdir):
    """ContinuousDiscoveryLoop com output_dir temporário."""
    return ContinuousDiscoveryLoop(
        output_dir=tmpdir,
        interval_hours=0,  # sem intervalo real
        lang="en",
    )


# ============================================================
# Testes
# ============================================================

class TestR95ContinuousDiscovery:
    """Suíte TDD para ContinuousDiscoveryLoop."""

    # --- CA1: Estrutura do módulo ---

    def test_ca1_instantiation(self, tmpdir):
        """CA1: Deve criar instância com atributos corretos."""
        loop = ContinuousDiscoveryLoop(
            output_dir=tmpdir,
            interval_hours=24,
            lang="pt",
        )
        assert loop.output_dir == tmpdir
        assert loop.interval_hours == 24
        assert loop.lang == "pt"
        assert loop.cycle_history == []

    def test_ca1_default_values(self, tmpdir):
        """CA1: Valores padrão devem ser aplicados."""
        loop = ContinuousDiscoveryLoop(output_dir=tmpdir)
        assert loop.interval_hours == 24
        assert loop.lang == "en"

    # --- CA2: Execução de ciclo único ---

    def test_ca2_run_cycle_returns_dict(self, loop):
        """CA2: run_cycle() deve retornar um dicionário com metadados."""
        result = loop.run_cycle()
        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "duration_seconds" in result
        assert "theses_count" in result
        assert "avg_novelty" in result
        assert "avg_enrichment" in result

    def test_ca2_run_cycle_generates_theses(self, loop):
        """CA2: O ciclo deve gerar 3-5 teses."""
        result = loop.run_cycle()
        assert 3 <= result["theses_count"] <= 5
        assert "theses" in result
        assert len(result["theses"]) == result["theses_count"]

    def test_ca2_run_cycle_scores_reasonable(self, loop):
        """CA2: Scores de novidade devem estar em faixa plausível (0-100)."""
        result = loop.run_cycle()
        assert 0 <= result["avg_novelty"] <= 100
        for thesis in result["theses"]:
            assert 0 <= thesis.get("novelty_score", 0) <= 100
            assert thesis.get("thesis_id", "").startswith("thesis_")

    # --- CA3: Acumulação histórica ---

    def test_ca3_cycle_history(self, loop):
        """CA3: Cada ciclo deve ser registrado no histórico."""
        assert len(loop.cycle_history) == 0
        loop.run_cycle()
        assert len(loop.cycle_history) == 1
        loop.run_cycle()
        assert len(loop.cycle_history) == 2

    def test_ca3_get_summary(self, loop):
        """CA3: get_summary() deve retornar métricas acumuladas."""
        loop.run_cycle()
        loop.run_cycle()
        summary = loop.get_summary()
        assert summary["total_cycles"] == 2
        assert 0 <= summary["avg_novelty"] <= 100
        assert 0 <= summary["avg_enrichment"] <= 10  # max conceitos por tese
        assert "top_theses" in summary
        assert len(summary["top_theses"]) <= 5
        assert "latest_cycle" in summary

    # --- CA4: Exportação ---

    def test_ca4_export_report(self, loop, tmpdir):
        """CA4: export_report() deve salvar relatório JSON do ciclo."""
        loop.run_cycle()
        path = loop.export_report(cycle_index=0)
        assert os.path.exists(path)
        with open(path, "r") as f:
            data = json.load(f)
        assert "timestamp" in data
        assert "theses" in data

    def test_ca4_export_all(self, loop, tmpdir):
        """CA4: export_all() deve salvar consolidado."""
        loop.run_cycle()
        loop.run_cycle()
        path = loop.export_all()
        assert os.path.exists(path)
        with open(path, "r") as f:
            data = json.load(f)
        assert "total_cycles" in data
        assert "cycles" in data
        assert data["total_cycles"] == 2

    # --- CA5: Robustez ---

    def test_ca5_no_network_no_llm(self, loop):
        """CA5: Deve funcionar sem rede externa nem LLM real (fallbacks)."""
        result = loop.run_cycle()
        assert result["status"] == "ok"

    def test_ca5_multiple_cycles_safe(self, loop):
        """CA5: Múltiplas execuções não devem causar erro."""
        for _ in range(5):
            r = loop.run_cycle()
            assert r["status"] == "ok"
        assert len(loop.cycle_history) == 5
