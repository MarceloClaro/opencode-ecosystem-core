# -*- coding: utf-8 -*-
"""
R596 — Auto-registro de agentes do catálogo no Blackboard (A2A)
================================================================
Objetivo: popular o Blackboard (protocolo A2A) com os Agent Cards derivados
do catálogo de agentes (`agents/catalog/*.md`) para que o orquestrador possa
usar matching real de capacidades (CFP) em vez de um blackboard vazio.

Cobertura:
- extração de metadados (frontmatter YAML + fallbacks) de um arquivo do catálogo
- idempotência de registro (2x não duplica)
- pulo seguro de arquivos malformados (sem frontmatter válido)
- capabilities derivadas (skills + tags + defaults)
- integração com o catálogo real (>= 100 agentes registrados com campos preenchidos)
"""
import json
import shutil
import tempfile
from pathlib import Path

import pytest

from mci.blackboard import blackboard
from mci.agent_registry_bootstrap import (
    parse_agent_catalog_md,
    load_catalog_agents,
    register_catalog_agents,
)

CATALOG_REAL = Path("agents/catalog")

FIXTURE_GOOD = """---
name: Agente Fixture Alfa
description: >-
  Especialista em testes determinísticos e verificação formal.
skills:
  - id: test-design
    name: Test Design
tags: [verificacao, testes]
version: '1.0.0'
---
Conteúdo a ignorar.
"""

FIXTURE_MINIMAL = """---
name: Fixture Beta
---
Sem descrição estruturada.
"""

FIXTURE_BROKEN = """---
name: 'quebrado sem fechamento
description: isso não é yaml válido
: [ : 
conteúdo solto
"""

FIXTURE_NO_FRONTMATTER = """Apenas texto, sem frontmatter YAML delimitado.
"""


@pytest.fixture(autouse=True)
def _limpa_blackboard():
    """Isola o singleton entre testes, preservando tasks existentes."""
    snapshot = dict(blackboard.registry)
    blackboard.registry.clear()
    yield
    blackboard.registry.clear()
    blackboard.registry.update(snapshot)


@pytest.fixture()
def mini_catalog(tmp_path: Path):
    (tmp_path / "alfa.md").write_text(FIXTURE_GOOD, encoding="utf-8")
    (tmp_path / "beta.md").write_text(FIXTURE_MINIMAL, encoding="utf-8")
    (tmp_path / "quebrado.md").write_text(FIXTURE_BROKEN, encoding="utf-8")
    (tmp_path / "sem_frontmatter.md").write_text(FIXTURE_NO_FRONTMATTER, encoding="utf-8")
    return tmp_path


class TestParseAgentCatalogMd:
    def test_extrai_metadados_do_frontmatter(self):
        info = parse_agent_catalog_md(Path("fake") / "alfa.md", FIXTURE_GOOD)
        assert info is not None
        assert info["agent_id"] == "alfa"
        assert info["name"] == "Agente Fixture Alfa"
        assert "testes determinísticos" in info["description"]
        assert "test-design" in info["capabilities"]
        assert "verificacao" in info["capabilities"]

    def test_minimal_sem_caps_tem_default(self):
        info = parse_agent_catalog_md(Path("fake") / "beta.md", FIXTURE_MINIMAL)
        assert info is not None
        assert info["name"] == "Fixture Beta"
        assert info["capabilities"]  # default preenchido

    def test_frontmatter_quebrado_retorna_none(self):
        assert parse_agent_catalog_md(Path("fake") / "quebrado.md", FIXTURE_BROKEN) is None

    def test_sem_frontmatter_retorna_none(self):
        assert parse_agent_catalog_md(Path("fake") / "sem.md", FIXTURE_NO_FRONTMATTER) is None


class TestLoadCatalogAgents:
    def test_carrega_apenas_validos(self, mini_catalog):
        agents = load_catalog_agents(mini_catalog)
        ids = {a["agent_id"] for a in agents}
        assert ids == {"alfa", "beta"}
        assert all(a["name"] and a["description"] for a in agents)

    def test_catálogo_real_tem_mais_de_100(self):
        agents = load_catalog_agents(CATALOG_REAL)
        assert len(agents) >= 100
        assert all(a["agent_id"] and a["name"] for a in agents)


class TestRegisterCatalogAgents:
    def test_registra_todos_do_fixture(self, mini_catalog):
        summary = register_catalog_agents(catalog_dir=mini_catalog)
        assert summary["registered"] == 2
        assert summary["skipped"] == 2
        for agent_id in ("alfa", "beta"):
            assert agent_id in blackboard.registry
            card = blackboard.registry[agent_id]
            assert card.to_dict()["capabilities"]

    def test_idempotente_nao_duplica(self, mini_catalog):
        register_catalog_agents(catalog_dir=mini_catalog)
        n1 = len(blackboard.registry)
        register_catalog_agents(catalog_dir=mini_catalog)
        assert len(blackboard.registry) == n1

    def test_nao_registra_arquivos_quebrados(self, mini_catalog):
        register_catalog_agents(catalog_dir=mini_catalog)
        assert "quebrado" not in blackboard.registry
        assert "sem_frontmatter" not in blackboard.registry

    def test_catalogo_real_registra_agentes_com_caps(self):
        summary = register_catalog_agents(catalog_dir=CATALOG_REAL)
        assert summary["registered"] >= 100
        cards = list(blackboard.registry.values())
        assert all(card.to_dict()["capabilities"] for card in cards)
        assert all(card.to_dict()["status"] == "available" for card in cards)
        # Confiança vem do ledger (padrão 0.5 quando ausente)
        assert all(0.0 <= card.to_dict()["confidence_score"] <= 1.0 for card in cards)