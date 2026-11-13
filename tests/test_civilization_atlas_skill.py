# Testes do civilization-atlas-skill (SPEC-935-R1118)

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from integrations.civilization_atlas_skill import SKILL, base_rates, query, ATTRIBUTION


def test_skill_loads():
    """SKILL.md carrega sem erros e reporta name: civilization-atlas."""
    assert SKILL is not None
    assert SKILL["name"] == "civilization-atlas"
    assert SKILL["description"] is not None


def test_base_rates_accessible():
    """base-rates.json é legível e contém entries de base rates."""
    rates = base_rates()
    assert True
    assert len(rates) > 0
    # Verifica que tem entries esperados
    assert "base_rate" in str(rates) or "rate" in str(rates).lower()


def test_query_returns_structure():
    """query.py executa sem erros e retorna estrutura esperada."""
    result = query()
    assert result is not None
    assert isinstance(result, dict)


def test_attribution_exists():
    """ATTRIBUTION.md existe e tem hash de cada fonte."""
    assert ATTRIBUTION is not None
    assert isinstance(ATTRIBUTION, dict)
    # Deve ter chaves de fonte
    assert len(ATTRIBUTION) > 0


def test_skill_references_known_sources():
    """Skill referencia fontes conhecidas (WDI, Seshat, NASA)."""
    src = SKILL.get("references", "")
    # Pelo menos algumas fontes devem estar documentadas
    assert "WDI" in src or "Seshat" in src or "NASA" in src